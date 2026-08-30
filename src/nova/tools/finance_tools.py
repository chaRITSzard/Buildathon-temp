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
from nova.tools.finance_summary import finance_summary


def total_revenue():
    """Return total company revenue used in the financial model."""
    return {
        "total_revenue": get_total_revenue()
    }


def total_expenses():
    """Return total company expenses across all expense categories."""
    return {
        "total_expenses": get_total_expenses()
    }


def gross_profit():
    """Return total gross profit after product costs."""
    return {
        "gross_profit": get_gross_profit()
    }


def operating_profit():
    """Return total operating profit after operating expenses, shipping, marketing, and other expenses."""
    return {
        "operating_profit": get_operating_profit()
    }


def profit_margin():
    """Return the company's operating profit margin."""
    return {
        "profit_margin": get_profit_margin()
    }


def monthly_profit():
    """Return monthly revenue, gross profit, and operating profit."""
    return get_monthly_profit().to_dict(
        orient="records"
    )


def expense_breakdown():
    """Return total spending by expense category, ranked from highest to lowest."""
    return get_expense_breakdown().to_dict(
        orient="records"
    )


def financial_summary():
    """Return the company's overall revenue, expenses, gross profit, operating profit, and profit margin."""
    return get_financial_summary()