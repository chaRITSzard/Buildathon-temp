from nova.llm.client import completion_with_fallback

from nova.tools.sales_summary import sales_summary
from nova.tools.marketing_summary import marketing_summary
from nova.tools.finance_summary import finance_summary
from nova.tools.inventory_tools import inventory_summary


CEO_SYSTEM_PROMPT = """
You are NOVA's CEO Intelligence Orchestrator.

You are the strategic decision-making layer of NOVA.

You have been provided with structured data from four business
departments:

- Sales
- Marketing
- Finance
- Inventory

Your job is to analyze all four datasets together and produce
one executive-level recommendation.

IMPORTANT RULES:

1. Use ONLY the data provided in the department summaries.
2. Never invent metrics or facts.
3. Do not claim that an agent said something that is not present
   in the provided data.
4. Distinguish facts from interpretations and recommendations.
5. Look for dependencies between departments.
6. Consider the company's overall position rather than
   optimizing one department in isolation.
7. If the evidence is insufficient, explicitly say so.
8. Do not hide uncertainty.
9. If there are conflicting signals between departments,
   explicitly identify them.
10. Recommendations must be supported by the available data.

FINAL RESPONSE FORMAT:

### Executive Assessment
Give the overall conclusion.

### Cross-Department Evidence
Summarize the most important findings from Sales, Marketing,
Finance, and Inventory.

### Strategic Recommendation
Give the most important action the CEO should consider.

### Risks
Identify important risks, dependencies, or unknowns.

### Confidence
State High, Medium, or Low confidence and briefly explain why.
"""


def ceo_analysis(question: str) -> str:

    # Collect structured data directly from the analytics tools.
    # No specialist LLM calls are made here.

    sales_data = sales_summary()
    marketing_data = marketing_summary()
    finance_data = finance_summary()
    inventory_data = inventory_summary()

    department_data = {
        "sales": sales_data,
        "marketing": marketing_data,
        "finance": finance_data,
        "inventory": inventory_data,
    }

    messages = [
        {
            "role": "system",
            "content": CEO_SYSTEM_PROMPT
        },
        {
            "role": "user",
            "content": (
                f"CEO QUESTION:\n{question}\n\n"
                "DEPARTMENT DATA:\n"
                f"{department_data}\n\n"
                "Analyze the department data and provide the "
                "executive response using the required format."
            )
        }
    ]

    response = completion_with_fallback(
        messages=messages
    )

    content = response.choices[0].message.content

    if content is None:
        raise ValueError("CEO LLM returned no content.")

    return content


if __name__ == "__main__":

    question = (
        "Should NOVA aggressively scale the business right now? "
        "Analyze sales, marketing, finance, and inventory before "
        "making an executive recommendation."
    )

    answer = ceo_analysis(question)

    print("\nCEO ORCHESTRATOR\n")
    print(answer)