from nova.actions.models import (
    ActionProposal,
    ActionStatus,
    ActionType,
)


def create_marketing_reallocation(
    amount: float,
    source: str,
    destination: str,
    reason: str,
) -> ActionProposal:

    return ActionProposal(
        action_type=ActionType.REALLOCATE_MARKETING_BUDGET,
        description=(
            f"Move budget from {source} to {destination}"
        ),
        amount=amount,
        source=source,
        destination=destination,
        reason=reason,
        status=ActionStatus.PROPOSED,
    )