from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[3]

DATA_DIR = PROJECT_ROOT / "data" / "synthetic"


def load_sales_data():
    customers = pd.read_csv(
        DATA_DIR / "customers.csv"
    )

    orders = pd.read_csv(
        DATA_DIR / "orders.csv"
    )

    order_items = pd.read_csv(
        DATA_DIR / "order_items.csv"
    )

    products = pd.read_csv(
        DATA_DIR / "products.csv"
    )

    orders["order_date"] = pd.to_datetime(
        orders["order_date"]
    )

    return (
        customers,
        orders,
        order_items,
        products
    )

# completed sales


def get_completed_sales():
    (
        customers,
        orders,
        order_items,
        products
    ) = load_sales_data()

    completed_orders = orders[
        orders["order_status"] == "Completed"
    ].copy()

    sales = order_items.merge(
        completed_orders[
            [
                "order_id",
                "customer_id",
                "order_date"
            ]
        ],
        on="order_id",
        how="inner"
    )

    sales = sales.merge(
        products[
            [
                "product_id",
                "product_name",
                "category",
                "unit_cost"
            ]
        ],
        on="product_id",
        how="left"
    )

    sales["revenue"] = (
        sales["quantity"]
        * sales["unit_price"]
    )

    sales["product_cost"] = (
        sales["quantity"]
        * sales["unit_cost"]
    )

    return sales

# Total Revenue


def get_total_revenue():
    sales = get_completed_sales()

    return sales["revenue"].sum()

# Revenue by Month

def get_revenue_by_month():
    sales = get_completed_sales()

    sales["month"] = (
        sales["order_date"]
        .dt.to_period("M")
    )

    result = (
        sales
        .groupby("month")["revenue"]
        .sum()
        .reset_index()
    )

    result["month"] = (
        result["month"]
        .astype(str)
    )

    return result

# Revenue by Customer Segment

def get_revenue_by_segment():
    sales = get_completed_sales()

    customers = pd.read_csv(
        DATA_DIR / "customers.csv"
    )

    sales = sales.merge(
        customers[
            [
                "customer_id",
                "customer_segment"
            ]
        ],
        on="customer_id",
        how="left"
    )

    return (
        sales
        .groupby("customer_segment")["revenue"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )


# Top Products

def get_top_products(limit=10):
    sales = get_completed_sales()

    result = (
        sales
        .groupby(
            [
                "product_id",
                "product_name"
            ]
        )
        .agg(
            revenue=("revenue", "sum"),
            units_sold=("quantity", "sum")
        )
        .sort_values(
            "revenue",
            ascending=False
        )
        .head(limit)
        .reset_index()
    )

    return result


def get_average_order_value():
    sales = get_completed_sales()

    order_revenue = (
        sales
        .groupby("order_id")["revenue"]
        .sum()
    )

    return order_revenue.mean()


# Units Sold


def get_units_sold():
    sales = get_completed_sales()

    return sales["quantity"].sum()


# Revenue by Category

def get_revenue_by_category():
    sales = get_completed_sales()

    return (
        sales
        .groupby("category")["revenue"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )

# 8. Revenue by City

def get_revenue_by_city():
    sales = get_completed_sales()

    customers = pd.read_csv(
        DATA_DIR / "customers.csv"
    )

    sales = sales.merge(
        customers[
            [
                "customer_id",
                "city"
            ]
        ],
        on="customer_id",
        how="left"
    )

    return (
        sales
        .groupby("city")["revenue"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )


# Orders by Month

def get_orders_by_month():
    (
        _,
        orders,
        _,
        _
    ) = load_sales_data()

    completed_orders = orders[
        orders["order_status"] == "Completed"
    ].copy()

    completed_orders["month"] = (
        completed_orders["order_date"]
        .dt.to_period("M")
    )

    return (
        completed_orders
        .groupby("month")
        .size()
        .reset_index(name="orders")
    )

# Repeat Customer Rate

def get_repeat_customer_rate():
    sales = get_completed_sales()

    orders_per_customer = (
        sales
        .groupby("customer_id")["order_id"]
        .nunique()
    )

    repeat_customers = (
        orders_per_customer >= 2
    ).sum()

    total_customers = (
        orders_per_customer.shape[0]
    )

    if total_customers == 0:
        return 0.0

    return (
        repeat_customers
        / total_customers
    )

# Customer Lifetime Value

def get_customer_lifetime_value(limit=10):
    sales = get_completed_sales()

    result = (
        sales
        .groupby("customer_id")
        .agg(
            lifetime_value=("revenue", "sum"),
            orders=("order_id", "nunique"),
            units_purchased=("quantity", "sum")
        )
        .sort_values(
            "lifetime_value",
            ascending=False
        )
        .head(limit)
        .reset_index()
    )

    return result


if __name__ == "__main__":

    print("\nTOTAL REVENUE")
    print(get_total_revenue())

    print("\nREVENUE BY MONTH")
    print(get_revenue_by_month())

    print("\nREVENUE BY SEGMENT")
    print(get_revenue_by_segment())

    print("\nTOP PRODUCTS")
    print(get_top_products())

    print("\nAVERAGE ORDER VALUE")
    print(get_average_order_value())

    print("\nUNITS SOLD")
    print(get_units_sold())

    print("\nREVENUE BY CATEGORY")
    print(get_revenue_by_category())

    print("\nREVENUE BY CITY")
    print(get_revenue_by_city())

    print("\nORDERS BY MONTH")
    print(get_orders_by_month())

    print("\nREPEAT CUSTOMER RATE")
    print(get_repeat_customer_rate())

    print("\nTOP CUSTOMERS BY LIFETIME VALUE")
    print(get_customer_lifetime_value())