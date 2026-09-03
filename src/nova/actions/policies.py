MAX_MARKETING_REALLOCATION = 50000
MAX_CAMPAIGN_INCREASE_PERCENT = 10


def validate_action(action):
    if action.amount > MAX_MARKETING_REALLOCATION:
        return False, (
            f"Marketing reallocations cannot exceed "
            f"{MAX_MARKETING_REALLOCATION}."
        )

    if action.action_type.value == "reallocate_marketing_budget":
        if not action.source:
            return False, "Source campaign is required."

        if not action.destination:
            return False, "Destination campaign is required."

    return True, None