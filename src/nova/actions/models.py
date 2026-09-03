from enum import Enum

from pydantic import BaseModel, Field


class ActionStatus(str, Enum):
    PROPOSED = "proposed"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXECUTED = "executed"
    FAILED = "failed"


class ActionType(str, Enum):
    REALLOCATE_MARKETING_BUDGET = "reallocate_marketing_budget"
    INCREASE_CAMPAIGN_BUDGET = "increase_campaign_budget"


class ActionProposal(BaseModel):
    action_type: ActionType

    description: str

    amount: float = Field(gt=0)

    source: str | None = None
    destination: str | None = None

    reason: str

    status: ActionStatus = ActionStatus.PROPOSED