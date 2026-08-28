from nova.agents.base_agent import BaseAgent

from nova.agents.sales_agent import sales_agent
from nova.agents.marketing_agent import marketing_agent
from nova.agents.finance_agent import finance_agent
from nova.agents.inventory_agent import inventory_agent


def consult_sales(question: str) -> str:
    """Consult the Sales Agent for revenue, customers, products, orders, segments, categories, cities, and sales trends."""
    return sales_agent.run(question)


def consult_marketing(question: str) -> str:
    """Consult the Marketing Agent for campaigns, channels, marketing spend, ROAS, ROI, conversions, and marketing performance."""
    return marketing_agent.run(question)


def consult_finance(question: str) -> str:
    """Consult the Finance Agent for revenue, expenses, gross profit, operating profit, margins, costs, and financial health."""
    return finance_agent.run(question)


def consult_inventory(question: str) -> str:
    """Consult the Inventory Agent for stock levels, low-stock products, out-of-stock products, fast-moving products, and inventory turnover."""
    return inventory_agent.run(question)


CEO_TOOLS = [
    consult_sales,
    consult_marketing,
    consult_finance,
    consult_inventory,
]


CEO_SYSTEM_PROMPT = """
You are NOVA's CEO Intelligence Orchestrator.

You are the strategic decision-making layer of NOVA.

You have access to four specialist business intelligence agents:

- Sales Agent
- Marketing Agent
- Finance Agent
- Inventory Agent

Your job is to determine which specialists are relevant to
the CEO's question, consult them, and synthesize their findings
into one executive-level answer.

DELEGATION RULES:

1. Decide which specialists are necessary based on the actual
   business question.
2. You may consult multiple specialists.
3. Do not consult a specialist merely because its department
   name appears in the question.
4. For strategic questions involving growth, expansion,
   major spending, or operational changes, consider whether
   multiple departments are required.
5. Use specialist results as the source of business evidence.
6. Never invent metrics.
7. Never claim that a specialist provided evidence that it
   did not actually provide.
8. Distinguish facts from interpretations and recommendations.
9. Look for dependencies between departments.
10. If the available evidence is insufficient to answer
    confidently, say so.
11. If specialists disagree, explicitly identify the conflict.
12. Do not hide uncertainty.
13. Recommendations should consider the company's overall
    business position rather than optimizing one department
    in isolation.

IMPORTANT:

A specialist's recommendation is not automatically a fact.

Treat specialist output as analysis that must be evaluated
in the broader business context.

FINAL RESPONSE FORMAT:

### Executive Assessment
Give the overall conclusion.

### Cross-Department Evidence
Summarize the most important findings from the specialists
you consulted.

### Strategic Recommendation
Give the most important action the CEO should consider.

### Risks
Identify important risks, dependencies, or unknowns.

### Confidence
State High, Medium, or Low confidence and briefly explain why.
"""


ceo_agent = BaseAgent(
    name="CEO Orchestrator",
    system_prompt=CEO_SYSTEM_PROMPT,
    tools=CEO_TOOLS,
)


if __name__ == "__main__":

    question = (
        "Can NOVA safely accelerate growth right now?"
    )

    answer = ceo_agent.run(question)

    print("\nCEO ORCHESTRATOR\n")
    print(answer)