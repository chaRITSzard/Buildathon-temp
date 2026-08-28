from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = PROJECT_ROOT / "data" / "synthetic"


def load_financial_data():
    financials = pd.read_csv(
        DATA_DIR / "financials.csv"
    )

    financials["date"] = pd.to_datetime(
        financials["date"]
    )

    return financials


def get_total_revenue():
    financials = load_financial_data()

    return financials["revenue"].sum()


def get_total_expenses():
    financials = load_financial_data()

    expense_columns = [
        "product_cost",
        "marketing_expense",
        "operating_expense",
        "shipping_expense",
        "other_expense"
    ]

    return financials[expense_columns].sum().sum()


def get_gross_profit():
    financials = load_financial_data()

    return financials["gross_profit"].sum()


def get_operating_profit():
    financials = load_financial_data()

    return financials["operating_profit"].sum()


def get_profit_margin():
    revenue = get_total_revenue()
    profit = get_operating_profit()

    if revenue == 0:
        return 0.0

    return profit / revenue


def get_monthly_profit():
    financials = load_financial_data()

    financials["month"] = (
        financials["date"]
        .dt.to_period("M")
    )

    return (
        financials
        .groupby("month")
        .agg(
            revenue=("revenue", "sum"),
            gross_profit=("gross_profit", "sum"),
            operating_profit=("operating_profit", "sum")
        )
        .reset_index()
    )


def get_expense_breakdown():
    financials = load_financial_data()

    expense_columns = [
        "product_cost",
        "marketing_expense",
        "operating_expense",
        "shipping_expense",
        "other_expense"
    ]

    return (
        financials[expense_columns]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
        .rename(
            columns={
                "index": "expense_type",
                0: "amount"
            }
        )
    )


def get_financial_summary():
    revenue = get_total_revenue()
    expenses = get_total_expenses()
    gross_profit = get_gross_profit()
    operating_profit = get_operating_profit()

    return {
        "revenue": revenue,
        "total_expenses": expenses,
        "gross_profit": gross_profit,
        "operating_profit": operating_profit,
        "profit_margin": (
            operating_profit / revenue
            if revenue > 0
            else 0.0
        )
    }


if __name__ == "__main__":

    print("\nTOTAL REVENUE")
    print(get_total_revenue())

    print("\nTOTAL EXPENSES")
    print(get_total_expenses())

    print("\nGROSS PROFIT")
    print(get_gross_profit())

    print("\nOPERATING PROFIT")
    print(get_operating_profit())

    print("\nPROFIT MARGIN")
    print(get_profit_margin())

    print("\nMONTHLY PROFIT")
    print(get_monthly_profit())

    print("\nEXPENSE BREAKDOWN")
    print(get_expense_breakdown())

    print("\nFINANCIAL SUMMARY")
    print(get_financial_summary())