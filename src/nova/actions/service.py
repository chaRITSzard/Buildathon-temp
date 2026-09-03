from nova.actions.models import ActionStatus
from nova.actions.policies import validate_action


class ActionService:

    def propose(self, action):
        valid, reason = validate_action(action)

        if not valid:
            action.status = ActionStatus.REJECTED
            return action, reason

        action.status = ActionStatus.PENDING_APPROVAL

        return action, None

    def approve(self, action):
        if action.status != ActionStatus.PENDING_APPROVAL:
            raise ValueError(
                "Only pending actions can be approved."
            )

        action.status = ActionStatus.APPROVED

        return action

    def reject(self, action):
        if action.status != ActionStatus.PENDING_APPROVAL:
            raise ValueError(
                "Only pending actions can be rejected."
            )

        action.status = ActionStatus.REJECTED

        return action