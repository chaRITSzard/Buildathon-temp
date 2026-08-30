import logging

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from nova.llm.client import (
    FallbackLLMFailure,
    LLMConfigurationError,
    PrimaryLLMFailure,
    RateLimitError,
)
from nova.router import route_and_run


logger = logging.getLogger(__name__)

MAX_QUESTION_LENGTH = 2000

app = FastAPI(
    title="NOVA Intelligence API",
    description="Backend API for NOVA business intelligence.",
    version="1.0.0",
)


class AskRequest(BaseModel):
    question: str


class AskResponse(BaseModel):
    question: str
    agent: str
    answer: str


def _error_response(status_code: int, message: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"error": message},
    )


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "nova"
    }


@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest):

    question = request.question.strip()

    if not question:
        return _error_response(400, "Question cannot be empty.")

    if len(question) > MAX_QUESTION_LENGTH:
        return _error_response(400, "Question is too long.")

    try:
        agent, answer = route_and_run(question)

        return AskResponse(
            question=question,
            agent=agent,
            answer=answer
        )

    except (RateLimitError, PrimaryLLMFailure, FallbackLLMFailure, LLMConfigurationError) as error:
        logger.exception("LLM request failed while processing /ask.")
        return _error_response(503, "LLM service temporarily unavailable.")

    except Exception:
        logger.exception("Unexpected error while processing /ask.")
        return _error_response(500, "Request could not be processed.")