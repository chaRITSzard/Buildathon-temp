import logging
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from nova.actions.models import (
    ActionProposal,
    ActionStatus,
)
from nova.actions.service import ActionService
from nova.actions.executor import (
    ActionExecutionError,
    execute_action,
)
from nova.llm.client import (
    FallbackLLMFailure,
    LLMConfigurationError,
    PrimaryLLMFailure,
    RateLimitError,
)
from nova.actions.audit import (
    get_events,
    record_event,
)
from nova.router import route_and_run


logger = logging.getLogger(__name__)

MAX_QUESTION_LENGTH = 2000


app = FastAPI(
    title="NOVA Intelligence API",
    description="Backend API for NOVA business intelligence.",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# SERVICES
# ============================================================

action_service = ActionService()

# Temporary in-memory stores.
# These will be replaced with persistent storage later.
actions: dict[str, ActionProposal] = {}
decisions: dict[str, "DecisionRecord"] = {}


# ============================================================
# REQUEST / RESPONSE MODELS
# ============================================================

class AskRequest(BaseModel):
    question: str


class AskResponse(BaseModel):
    question: str
    agent: str
    answer: str
    action: ActionProposal | None = None


class ActionCreateRequest(BaseModel):
    action: ActionProposal


class ActionResponse(BaseModel):
    action_id: str
    action: ActionProposal


class ActionDecisionResponse(BaseModel):
    action_id: str
    action: ActionProposal

class ActionExecutionResponse(BaseModel):
    action_id: str
    status: str
    result: dict | None = None
    error: str | None = None

class DecisionRequest(BaseModel):
    question: str
    agent: str
    action: str


class DecisionRecord(BaseModel):
    decision_id: str
    question: str
    agent: str
    decision: str


# ============================================================
# HELPERS
# ============================================================

def _error_response(
    status_code: int,
    message: str,
) -> JSONResponse:

    return JSONResponse(
        status_code=status_code,
        content={"error": message},
    )


# ============================================================
# HEALTH
# ============================================================

@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "nova",
    }


# ============================================================
# INTELLIGENCE
# ============================================================

@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest):

    question = request.question.strip()

    if not question:
        return _error_response(
            400,
            "Question cannot be empty.",
        )

    if len(question) > MAX_QUESTION_LENGTH:
        return _error_response(
            400,
            "Question is too long.",
        )

    try:
        agent, answer = route_and_run(question)

        return AskResponse(
            question=question,
            agent=agent,
            answer=answer,
        )

    except (
        RateLimitError,
        PrimaryLLMFailure,
        FallbackLLMFailure,
        LLMConfigurationError,
    ):

        logger.exception(
            "LLM request failed while processing /ask."
        )

        return _error_response(
            503,
            "LLM service temporarily unavailable.",
        )

    except Exception:

        logger.exception(
            "Unexpected error while processing /ask."
        )

        return _error_response(
            500,
            "Request could not be processed.",
        )


# ============================================================
# DECISION HISTORY
# ============================================================

@app.post("/decision")
def decision(request: DecisionRequest):

    if request.action not in {"approved", "rejected"}:
        return _error_response(
            400,
            "Invalid decision.",
        )

    decision_id = f"dec_{uuid4().hex[:12]}"

    record = DecisionRecord(
        decision_id=decision_id,
        question=request.question,
        agent=request.agent,
        decision=request.action,
    )

    decisions[decision_id] = record

    logger.info(
        "DECISION RECORDED | id=%s | agent=%s | decision=%s",
        decision_id,
        request.agent,
        request.action,
    )

    return {
        "status": "recorded",
        "decision_id": decision_id,
        "agent": request.agent,
        "action": request.action,
    }


@app.get("/actions")
def get_actions():

    return {
        "actions": [
            {
                "action_id": decision_id,
                "action": {
                    "description": record.question,
                    "agent": record.agent,
                    "status": record.decision,
                },
            }
            for decision_id, record in decisions.items()
        ]
    }


# ============================================================
# ACTIONS
# ============================================================

@app.post(
    "/actions",
    response_model=ActionResponse,
    status_code=201,
)
def create_action(request: ActionCreateRequest):

    action_id = f"act_{uuid4().hex[:12]}"

    action, reason = action_service.propose(
        request.action
    )

    actions[action_id] = action
    record_event(
    action_id=action_id,
    event="ACTION_PROPOSED",
    status=action.status.value,
    message="Action proposed and awaiting approval.",
)
    logger.info(
        "Action %s proposed with status %s.",
        action_id,
        action.status,
    )

    return ActionResponse(
        action_id=action_id,
        action=action,
    )


@app.get(
    "/actions/{action_id}",
    response_model=ActionResponse,
)
def get_action(action_id: str):

    action = actions.get(action_id)

    if action is None:
        raise HTTPException(
            status_code=404,
            detail="Action not found.",
        )

    return ActionResponse(
        action_id=action_id,
        action=action,
    )


@app.post(
    "/actions/{action_id}/approve",
    response_model=ActionDecisionResponse,
)
def approve_action(action_id: str):

    action = actions.get(action_id)


    if action is None:
        raise HTTPException(
            status_code=404,
            detail="Action not found.",
        )

    try:

        action = action_service.approve(action)

        actions[action_id] = action
        record_event(
        action_id=action_id,
        event="ACTION_APPROVED",
        status=action.status.value,
        message="Action approved by executive.",
)

        logger.info(
            "Action %s approved.",
            action_id,
        )

        return ActionDecisionResponse(
            action_id=action_id,
            action=action,
        )

    except ValueError as error:

        raise HTTPException(
            status_code=409,
            detail=str(error),
        ) from error


@app.post(
    "/actions/{action_id}/reject",
    response_model=ActionDecisionResponse,
)
def reject_action(action_id: str):

    action = actions.get(action_id)

    if action is None:
        raise HTTPException(
            status_code=404,
            detail="Action not found.",
        )

    try:

        action = action_service.reject(action)

        actions[action_id] = action

        record_event(
            action_id=action_id,
            event="ACTION_REJECTED",
            status=action.status.value,
            message="Action rejected by executive.",
)

        logger.info(
            "Action %s rejected.",
            action_id,
        )

        return ActionDecisionResponse(
            action_id=action_id,
            action=action,
        )

    except ValueError as error:

        raise HTTPException(
            status_code=409,
            detail=str(error),
        ) from error

# ============================================================
# EXECUTION
# ============================================================

@app.post(
    "/actions/{action_id}/execute",
    response_model=ActionExecutionResponse,
)
def execute_action_endpoint(action_id: str):

    action = actions.get(action_id)

    if action is None:
        raise HTTPException(
            status_code=404,
            detail="Action not found.",
        )

    try:
        result = execute_action(action)

        action.status = ActionStatus.EXECUTED
        actions[action_id] = action

        record_event(
        action_id=action_id,
        event="ACTION_EXECUTED",
        status=action.status.value,
        message=result.get(
        "message",
        "Action executed successfully.",
    ),
)   

        logger.info(
            "Action %s executed successfully.",
            action_id,
        )

        return ActionExecutionResponse(
            action_id=action_id,
            status=action.status.value,
            result=result,
        )

    except ActionExecutionError as error:

        action.status = ActionStatus.FAILED
        actions[action_id] = action
        record_event(
        action_id=action_id,
        event="ACTION_EXECUTION_FAILED",
        status=action.status.value,
        message=str(error),
)

        logger.error(
            "Action %s execution failed: %s",
            action_id,
            error,
        )

        return ActionExecutionResponse(
            action_id=action_id,
            status=action.status.value,
            error=str(error),
        )

    except Exception as error:

        action.status = ActionStatus.FAILED
        actions[action_id] = action

        logger.exception(
            "Unexpected failure while executing action %s.",
            action_id,
        )

        return ActionExecutionResponse(
            action_id=action_id,
            status=action.status.value,
            error="Unexpected execution failure.",
        )

# ============================================================
# AUDIT
# ============================================================

@app.get("/actions/{action_id}/audit")
def get_action_audit(action_id: str):

    action = actions.get(action_id)

    if action is None:
        raise HTTPException(
            status_code=404,
            detail="Action not found.",
        )

    return {
    "action_id": action_id,
    "status": action.status.value,
    "action": action.model_dump(),
    "events": [
        event.model_dump()
        for event in get_events(action_id)
    ],
}