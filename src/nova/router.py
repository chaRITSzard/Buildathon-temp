from nova.agents.sales_agent import sales_agent
from nova.agents.marketing_agent import marketing_agent
from nova.agents.finance_agent import finance_agent
from nova.agents.inventory_agent import inventory_agent
from nova.agents.ceo_orchestrator import ceo_analysis


def route_question(question: str) -> str:
    """
    Determine which NOVA agent should handle a question.
    """

    text = question.lower()

    # Strategic / cross-department questions
    strategic_keywords = [
        "should we",
        "should nova",
        "scale",
        "scaling",
        "expand",
        "expansion",
        "growth strategy",
        "business strategy",
        "overall business",
        "company performance",
        "executive",
        "ceo",
    ]

    if any(keyword in text for keyword in strategic_keywords):
        return "ceo"

    # Marketing
    marketing_keywords = [
        "marketing",
        "campaign",
        "campaigns",
        "roas",
        "roi",
        "advertising",
        "advertisement",
        "ad spend",
        "marketing spend",
        "conversion",
        "conversions",
        "channel",
        "channels",
    ]

    if any(keyword in text for keyword in marketing_keywords):
        return "marketing"

    # Inventory
    inventory_keywords = [
        "inventory",
        "stock",
        "stocks",
        "low stock",
        "out of stock",
        "stockout",
        "stockout risk",
        "warehouse",
        "replenish",
        "replenishment",
        "fast moving",
        "turnover",
    ]

    if any(keyword in text for keyword in inventory_keywords):
        return "inventory"

    # Finance
    finance_keywords = [
    "finance",
    "financial",
    "profit",
    "profitability",
    "expense",
    "expenses",
    "cost",
    "costs",
    "margin",
    "margins",
    "gross profit",
    "operating profit",
    "cash",
]

    if any(keyword in text for keyword in finance_keywords):
        return "finance"

    # Sales
    sales_keywords = [
    "sales",
    "revenue",
    "customer",
    "customers",
    "product",
    "products",
    "orders",
    "order",
    "segment",
    "segments",
    "units sold",
    "aov",
    "average order",
    "lifetime value",
    "ltv",
]

    if any(keyword in text for keyword in sales_keywords):
        return "sales"

    # Default to CEO for ambiguous questions
    return "ceo"


def route_and_run(question: str) -> tuple[str, str]:
    agent_name = route_question(question)

    if agent_name == "sales":
        return agent_name, sales_agent.run(question)

    if agent_name == "marketing":
        return agent_name, marketing_agent.run(question)

    if agent_name == "finance":
        return agent_name, finance_agent.run(question)

    if agent_name == "inventory":
        return agent_name, inventory_agent.run(question)

    if agent_name == "ceo":
        return agent_name, ceo_analysis.run(question)

    raise ValueError(f"Unknown route: {agent_name}")

if __name__ == "__main__":

    tests = [
        "What is our ROAS?",
        "Which products are low stock?",
        "What is our operating profit?",
        "Which customer segment generates the most revenue?",
        "Should NOVA aggressively scale the business?",
        "Should we increase marketing spend?",
    ]

    for question in tests:
        print(
            f"{question}\n"
            f"→ {route_question(question)}\n"
        )