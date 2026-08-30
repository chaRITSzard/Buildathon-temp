from nova.analytics.finance import (
    get_total_revenue,
    get_total_expenses,
    get_gross_profit,
    get_operating_profit,
    get_profit_margin,
    get_monthly_profit,
    get_expense_breakdown,
    get_financial_summary,
    
)


def finance_summary():
    """
    Return a comprehensive financial summary for strategic analysis,
    including revenue, expenses, gross profit, operating profit,
    profit margin, monthly profitability, expense breakdown,
    and overall financial health.
    """

    return {
        "total_revenue": get_total_revenue(),

        "total_expenses": get_total_expenses(),

        "gross_profit": get_gross_profit(),

        "operating_profit": get_operating_profit(),

        "profit_margin": get_profit_margin(),

        "monthly_profit": get_monthly_profit().to_dict(
            orient="records"
        ),

        "expense_breakdown": get_expense_breakdown().to_dict(
            orient="records"
        ),

        "financial_summary": get_financial_summary()
    }