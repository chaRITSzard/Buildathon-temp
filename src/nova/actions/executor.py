from nova.actions.models import ActionStatus, ActionType


class ActionExecutionError(RuntimeError):
    pass


def execute_action(action):

    if action.status != ActionStatus.APPROVED:
        raise ActionExecutionError(
            "Only approved actions can be executed."
        )

    if action.action_type == ActionType.REALLOCATE_MARKETING_BUDGET:
        return execute_marketing_reallocation(action)

    if action.action_type == ActionType.INCREASE_CAMPAIGN_BUDGET:
        return execute_campaign_budget_increase(action)

    raise ActionExecutionError(
        f"Unsupported action type: {action.action_type}"
    )


def execute_marketing_reallocation(action):

    if action.amount <= 0:
        raise ActionExecutionError(
            "Invalid reallocation amount."
        )

    if not action.source:
        raise ActionExecutionError(
            "Marketing reallocation requires a source."
        )

    if not action.destination:
        raise ActionExecutionError(
            "Marketing reallocation requires a destination."
        )

    return {
        "success": True,
        "message": "Marketing budget reallocation executed successfully.",
        "action": action.action_type.value,
        "amount": action.amount,
        "source": action.source,
        "destination": action.destination,
    }


def execute_campaign_budget_increase(action):

    if action.amount <= 0:
        raise ActionExecutionError(
            "Invalid campaign budget amount."
        )

    if not action.destination:
        raise ActionExecutionError(
            "Campaign budget increase requires a destination."
        )

    return {
        "success": True,
        "message": "Campaign budget increase executed successfully.",
        "action": action.action_type.value,
        "amount": action.amount,
        "destination": action.destination,
    }