from nova.tools.marketing_tools import (
    total_marketing_spend,
    total_marketing_revenue,
    overall_roas,
    overall_roi,
    best_campaigns,
    worst_campaigns,
    performance_by_channel,
    performance_by_campaign_type,
    marketing_summary
)

from nova.tools.sales_tools import (
    total_revenue,
    revenue_by_month,
    revenue_by_segment,
    top_products,
    average_order_value,
    units_sold,
    revenue_by_category,
    revenue_by_city,
    orders_by_month,
    repeat_customer_rate,
    customer_lifetime_value,
    sales_summary
)
from nova.tools.finance_tools import (
    total_revenue,
    total_expenses,
    gross_profit,
    operating_profit,
    profit_margin,
    monthly_profit,
    expense_breakdown,
    financial_summary,
    finance_summary
)

from nova.tools.inventory_tools import (
    current_inventory,
    total_stock,
    low_stock_products,
    out_of_stock_products,
    fast_moving_products,
    inventory_turnover,
    inventory_summary,
)

INVENTORY_TOOLS = [
    current_inventory,
    total_stock,
    low_stock_products,
    out_of_stock_products,
    fast_moving_products,
    inventory_turnover,
    inventory_summary,
]

MARKETING_TOOLS = [
    total_marketing_spend,
    total_marketing_revenue,
    overall_roas,
    overall_roi,
    best_campaigns,
    worst_campaigns,
    performance_by_channel,
    performance_by_campaign_type,
    marketing_summary
]

SALES_TOOLS = [
    total_revenue,
    revenue_by_month,
    revenue_by_segment,
    top_products,
    average_order_value,
    units_sold,
    revenue_by_category,
    revenue_by_city,
    orders_by_month,
    repeat_customer_rate,
    customer_lifetime_value,
    sales_summary
]

FINANCE_TOOLS = [
    total_revenue,
    total_expenses,
    gross_profit,
    operating_profit,
    profit_margin,
    monthly_profit,
    expense_breakdown,
    financial_summary,
    finance_summary
]