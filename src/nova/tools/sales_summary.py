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


def sales_summary():
    """
    Return a comprehensive sales summary for strategic analysis,
    including revenue trends, customer segments, products,
    order value, units, categories, cities, repeat customers,
    and customer lifetime value.
    """

    return {
        "total_revenue": get_total_revenue(),

        "revenue_by_month": get_revenue_by_month().to_dict(
            orient="records"
        ),

        "revenue_by_segment": get_revenue_by_segment().to_dict(
            orient="records"
        ),

        "top_products": get_top_products().to_dict(
            orient="records"
        ),

        "average_order_value": get_average_order_value(),

        "units_sold": get_units_sold(),

        "revenue_by_category": get_revenue_by_category().to_dict(
            orient="records"
        ),

        "revenue_by_city": get_revenue_by_city().to_dict(
            orient="records"
        ),

        "orders_by_month": get_orders_by_month().to_dict(
            orient="records"
        ),

        "repeat_customer_rate": get_repeat_customer_rate(),

        "customer_lifetime_value": get_customer_lifetime_value().to_dict(
            orient="records"
        )
    }