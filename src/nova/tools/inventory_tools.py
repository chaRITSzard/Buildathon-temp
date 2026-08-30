from nova.analytics.inventory import (
    get_current_inventory,
    get_total_stock,
    get_low_stock_products,
    get_out_of_stock_products,
    get_fast_moving_products,
    get_inventory_turnover,
    get_inventory_summary,
)


def current_inventory():
    """Return current stock levels for all products, including opening stock, units received, and closing stock."""
    return get_current_inventory().to_dict(
        orient="records"
    )


def total_stock():
    """Return the total number of units currently held in inventory."""
    return {
        "total_stock": get_total_stock()
    }


def low_stock_products():
    """Return products whose current stock is below the low-stock threshold."""
    return get_low_stock_products().to_dict(
        orient="records"
    )


def out_of_stock_products():
    """Return products that currently have zero available stock."""
    return get_out_of_stock_products().to_dict(
        orient="records"
    )


def fast_moving_products():
    """Return the products with the highest recent unit sales."""
    return get_fast_moving_products().to_dict(
        orient="records"
    )


def inventory_turnover():
    """Return the inventory turnover ratio."""
    return {
        "inventory_turnover": get_inventory_turnover()
    }


def inventory_summary():

    """
    Return a comprehensive inventory summary for strategic analysis,
    including total stock, low-stock products, out-of-stock products,
    fast-moving products, and inventory turnover.
    """

    return {
        "total_stock": get_total_stock(),

        "low_stock_products": get_low_stock_products().to_dict(
            orient="records"
        ),

        "out_of_stock_products": get_out_of_stock_products().to_dict(
            orient="records"
        ),

        "fast_moving_products": get_fast_moving_products().to_dict(
            orient="records"
        ),

        "inventory_turnover": get_inventory_turnover(),
    }