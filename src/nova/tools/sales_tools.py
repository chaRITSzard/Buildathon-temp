from nova.analytics.sales import (
    get_total_revenue,
    get_revenue_by_month,
    get_revenue_by_segment,
    get_top_products,
    get_average_order_value,
    get_units_sold,
    get_revenue_by_category,
    get_revenue_by_city,
    get_orders_by_month,
    get_repeat_customer_rate,
    get_customer_lifetime_value,
)


def total_revenue():
    """Return total company revenue from completed sales."""
    return {
        "total_revenue": get_total_revenue()
    }


def revenue_by_month():
    """Return total revenue broken down by month."""
    return get_revenue_by_month().to_dict(
        orient="records"
    )


def revenue_by_segment():
    """Return revenue broken down by customer segment."""
    return get_revenue_by_segment().to_dict(
        orient="records"
    )


def top_products():
    """Return the highest-revenue products with revenue and units sold."""
    return get_top_products().to_dict(
        orient="records"
    )


def average_order_value():
    """Return the company's average order value."""
    return {
        "average_order_value": get_average_order_value()
    }


def units_sold():
    """Return the total number of units sold."""
    return {
        "units_sold": get_units_sold()
    }


def revenue_by_category():
    """Return revenue broken down by product category."""
    return get_revenue_by_category().to_dict(
        orient="records"
    )


def revenue_by_city():
    """Return revenue broken down by customer city."""
    return get_revenue_by_city().to_dict(
        orient="records"
    )


def orders_by_month():
    """Return the number of orders placed each month."""
    return get_orders_by_month().to_dict(
        orient="records"
    )


def repeat_customer_rate():
    """Return the percentage of customers who make repeat purchases."""
    return {
        "repeat_customer_rate": get_repeat_customer_rate()
    }

def customer_lifetime_value():
    """Return customer lifetime value data for identifying the highest-value customers."""
    return get_customer_lifetime_value().to_dict(
        orient="records"
    )