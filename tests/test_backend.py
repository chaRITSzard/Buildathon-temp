import requests
import sys


BASE_URL = "http://127.0.0.1:8000"


# ============================================================
# TEST HELPERS
# ============================================================

def check(condition, message):
    if condition:
        print(f"  ✅ {message}")
    else:
        print(f"  ❌ {message}")
        raise AssertionError(message)


def post(path, payload=None):
    return requests.post(
        f"{BASE_URL}{path}",
        json=payload,
        timeout=30,
    )


def get(path):
    return requests.get(
        f"{BASE_URL}{path}",
        timeout=30,
    )


# ============================================================
# 1. HEALTH
# ============================================================

def test_health():

    print("\n[1] HEALTH")

    response = get("/health")

    check(
        response.status_code == 200,
        "Health endpoint returns 200",
    )

    data = response.json()

    check(
        data.get("status") == "ok",
        "Service status is OK",
    )


# ============================================================
# 2. ASK VALIDATION
# ============================================================

def test_empty_question():

    print("\n[2] ASK VALIDATION")

    response = post(
        "/ask",
        {"question": ""},
    )

    check(
        response.status_code == 400,
        "Empty question rejected",
    )


def test_long_question():

    response = post(
        "/ask",
        {"question": "x" * 2001},
    )

    check(
        response.status_code == 400,
        "Overly long question rejected",
    )


# ============================================================
# 3. AGENT ROUTING
# ============================================================

def test_routing():

    print("\n[3] AGENT ROUTING")

    from nova.router import route_question

    questions = [
        (
            "What is our ROAS?",
            "marketing",
        ),
        (
            "Which products are low stock?",
            "inventory",
        ),
        (
            "What is our operating profit?",
            "finance",
        ),
        (
            "Which customer segment generates the most revenue?",
            "sales",
        ),
        (
            "Should NOVA aggressively scale the business?",
            "ceo",
        ),
    ]

    for question, expected_agent in questions:

        actual_agent = route_question(question)

        check(
            actual_agent == expected_agent,
            f"{question} → {actual_agent}",
        )


# ============================================================
# 4. AGENT RESPONSE
# ============================================================

def test_agent_response():

    print("\n[4] AGENT RESPONSE")

    # Only one real LLM request is made here.
    # This confirms the /ask → router → agent → answer
    # pipeline without unnecessarily consuming the
    # free-tier LLM quota for every routing test.

    response = post(
        "/ask",
        {
            "question": "What is our ROAS?"
        },
    )

    check(
        response.status_code == 200,
        "Marketing question accepted",
    )

    data = response.json()

    check(
        data.get("agent") == "marketing",
        "Marketing agent handled the question",
    )

    check(
        bool(data.get("answer")),
        "Marketing agent returned an answer",
    )


# ============================================================
# 5. ACTION CREATION
# ============================================================

def test_action_creation():

    print("\n[5] ACTION CREATION")

    action = {
        "action_type": "reallocate_marketing_budget",
        "description": "Move budget from Meta Ads to Google Ads",
        "amount": 50000,
        "source": "Meta Ads",
        "destination": "Google Ads",
        "reason": "Google Ads currently has stronger ROAS",
    }

    response = post(
        "/actions",
        {"action": action},
    )

    check(
        response.status_code == 201,
        "Action created",
    )

    data = response.json()

    check(
        "action_id" in data,
        "Action ID generated",
    )

    check(
        data["action"]["status"] == "pending_approval",
        "Action enters PENDING_APPROVAL",
    )

    return data["action_id"]


# ============================================================
# 6. ACTION RETRIEVAL
# ============================================================

def test_action_retrieval(action_id):

    print("\n[6] ACTION RETRIEVAL")

    response = get(
        f"/actions/{action_id}",
    )

    check(
        response.status_code == 200,
        "Action can be retrieved",
    )

    data = response.json()

    check(
        data["action_id"] == action_id,
        "Correct action returned",
    )

    check(
        data["action"]["status"] == "pending_approval",
        "Action remains pending",
    )


# ============================================================
# 7. EXECUTION SAFETY
# ============================================================

def test_pending_execution_blocked(action_id):

    print("\n[7] EXECUTION SAFETY")

    response = post(
        f"/actions/{action_id}/execute",
    )

    check(
        response.status_code == 200,
        "Execution request handled gracefully",
    )

    data = response.json()

    check(
        data["status"] == "failed",
        "Pending action cannot execute",
    )

    check(
        data.get("error") is not None,
        "Execution failure contains an error",
    )


# ============================================================
# 8. APPROVAL
# ============================================================

def test_approval():

    print("\n[8] APPROVAL")

    action = {
        "action_type": "reallocate_marketing_budget",
        "description": "Move budget from Meta Ads to Google Ads",
        "amount": 50000,
        "source": "Meta Ads",
        "destination": "Google Ads",
        "reason": "Google Ads currently has stronger ROAS",
    }

    create_response = post(
        "/actions",
        {"action": action},
    )

    check(
        create_response.status_code == 201,
        "Fresh action created",
    )

    action_id = create_response.json()["action_id"]

    response = post(
        f"/actions/{action_id}/approve",
    )

    check(
        response.status_code == 200,
        "Action approved",
    )

    data = response.json()

    check(
        data["action"]["status"] == "approved",
        "Action status → APPROVED",
    )

    return action_id


# ============================================================
# 9. EXECUTION
# ============================================================

def test_execution(action_id):

    print("\n[9] EXECUTION")

    response = post(
        f"/actions/{action_id}/execute",
    )

    check(
        response.status_code == 200,
        "Execution endpoint responds",
    )

    data = response.json()

    check(
        data["status"] == "executed",
        "Action status → EXECUTED",
    )

    check(
        data["result"] is not None,
        "Execution returned a result",
    )

    result = data["result"]

    check(
        result.get("success") is True,
        "Executor reports success",
    )

    check(
        result.get("amount") == 50000,
        "Execution amount is preserved",
    )

    check(
        result.get("source") == "Meta Ads",
        "Execution source is preserved",
    )

    check(
        result.get("destination") == "Google Ads",
        "Execution destination is preserved",
    )


# ============================================================
# 10. REJECTION
# ============================================================

def test_rejection():

    print("\n[10] REJECTION")

    action = {
        "action_type": "increase_campaign_budget",
        "description": "Increase Google campaign budget",
        "amount": 25000,
        "destination": "Google Campaign A",
        "reason": "Campaign has strong conversion performance",
    }

    create_response = post(
        "/actions",
        {"action": action},
    )

    check(
        create_response.status_code == 201,
        "Action created",
    )

    action_id = create_response.json()["action_id"]

    response = post(
        f"/actions/{action_id}/reject",
    )

    check(
        response.status_code == 200,
        "Action rejected",
    )

    data = response.json()

    check(
        data["action"]["status"] == "rejected",
        "Action status → REJECTED",
    )

    # Rejected actions must not execute.
    execution_response = post(
        f"/actions/{action_id}/execute",
    )

    check(
        execution_response.status_code == 200,
        "Rejected execution handled gracefully",
    )

    execution_data = execution_response.json()

    check(
        execution_data["status"] == "failed",
        "Rejected action cannot execute",
    )


# ============================================================
# 11. DECISION HISTORY
# ============================================================

def test_decision_history():

    print("\n[11] DECISION HISTORY")

    approve_response = post(
        "/decision",
        {
            "question": "Should we increase marketing spend?",
            "agent": "marketing",
            "action": "approved",
        },
    )

    check(
        approve_response.status_code == 200,
        "Approval decision recorded",
    )

    reject_response = post(
        "/decision",
        {
            "question": "Should we pause Campaign B?",
            "agent": "marketing",
            "action": "rejected",
        },
    )

    check(
        reject_response.status_code == 200,
        "Rejection decision recorded",
    )

    response = get("/actions")

    check(
        response.status_code == 200,
        "Decision history endpoint responds",
    )

    data = response.json()

    history = data.get("actions", [])

    check(
        len(history) >= 2,
        "Decision history contains recorded decisions",
    )

    statuses = [
        item["action"]["status"]
        for item in history
    ]

    check(
        "approved" in statuses,
        "Approved decision appears in history",
    )

    check(
        "rejected" in statuses,
        "Rejected decision appears in history",
    )


# ============================================================
# 12. INVALID DECISION
# ============================================================

def test_invalid_decision():

    print("\n[12] INVALID DECISION")

    response = post(
        "/decision",
        {
            "question": "Test invalid decision",
            "agent": "marketing",
            "action": "maybe",
        },
    )

    check(
        response.status_code == 400,
        "Invalid decision rejected",
    )


# ============================================================
# 13. AUDIT
# ============================================================

def test_audit(action_id):

    print("\n[13] AUDIT")

    response = get(
        f"/actions/{action_id}/audit",
    )

    check(
        response.status_code == 200,
        "Audit endpoint responds",
    )

    data = response.json()

    check(
        data["action_id"] == action_id,
        "Audit references correct action",
    )

    check(
        data["status"] == "executed",
        "Audit shows EXECUTED status",
    )

    check(
        data.get("action") is not None,
        "Audit contains action data",
    )
def test_audit_history(action_id):

    print("\n[H4] AUDIT HISTORY")

    response = get(
        f"/actions/{action_id}/audit"
    )

    check(
        response.status_code == 200,
        "Audit history endpoint responds",
    )

    data = response.json()

    events = data.get("events", [])

    check(
        len(events) >= 3,
        "Audit contains lifecycle events",
    )

    event_names = [
        event["event"]
        for event in events
    ]

    check(
        "ACTION_PROPOSED" in event_names,
        "Proposal event recorded",
    )

    check(
        "ACTION_APPROVED" in event_names,
        "Approval event recorded",
    )

    check(
        "ACTION_EXECUTED" in event_names,
        "Execution event recorded",
    )

    for event in events:
        check(
            event.get("timestamp") is not None,
            f"Timestamp recorded for {event['event']}",
        )

# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)
    print("NOVA BACKEND INTEGRATION TEST")
    print("=" * 60)

    try:

        # ----------------------------------------------------
        # Core API
        # ----------------------------------------------------

        test_health()

        test_empty_question()
        test_long_question()

        # ----------------------------------------------------
        # Routing / LLM
        # ----------------------------------------------------

        test_routing()
        test_agent_response()

        # ----------------------------------------------------
        # Action lifecycle
        # ----------------------------------------------------

        pending_action_id = test_action_creation()

        test_action_retrieval(
            pending_action_id
        )

        test_pending_execution_blocked(
            pending_action_id
        )

        approved_action_id = test_approval()

        test_execution(
            approved_action_id
        )

        test_rejection()

        # ----------------------------------------------------
        # Decision history
        # ----------------------------------------------------

        test_decision_history()

        test_invalid_decision()

        # ----------------------------------------------------
        # Audit
        # ----------------------------------------------------

        test_audit(
            approved_action_id
        )
        

    except requests.exceptions.ConnectionError:

        print("\n❌ BACKEND NOT RUNNING")
        print(
            "Start FastAPI first, then run this test again."
        )

        sys.exit(1)

    except requests.exceptions.Timeout:

        print("\n❌ REQUEST TIMED OUT")
        print(
            "The backend or LLM took too long to respond."
        )

        sys.exit(1)

    except AssertionError:

        print("\n❌ TEST SUITE FAILED")
        sys.exit(1)

    except Exception as error:

        print("\n❌ UNEXPECTED TEST ERROR")
        print(error)

        sys.exit(1)

    print("\n" + "=" * 60)
    print("🔥 ALL NOVA BACKEND TESTS PASSED")
    print("=" * 60)


if __name__ == "__main__":
    main()