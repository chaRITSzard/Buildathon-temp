from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = PROJECT_ROOT / "data" / "synthetic"


def load_inventory_data():
    inventory = pd.read_csv(
        DATA_DIR / "inventory.csv"
    )

    inventory["date"] = pd.to_datetime(
        inventory["date"]
    )

    return inventory


def get_current_inventory():
    inventory = load_inventory_data()

    latest_date = inventory["date"].max()

    return (
        inventory[
            inventory["date"] == latest_date
        ]
        .sort_values(
            "closing_stock",
            ascending=True
        )
        .reset_index(drop=True)
    )


def get_total_stock():
    inventory = get_current_inventory()

    return inventory["closing_stock"].sum()


def get_low_stock_products(threshold=300):
    inventory = get_current_inventory()

    return (
        inventory[
            inventory["closing_stock"] <= threshold
        ]
        .sort_values(
            "closing_stock",
            ascending=True
        )
        .reset_index(drop=True)
    )


def get_out_of_stock_products():
    inventory = get_current_inventory()

    return (
        inventory[
            inventory["closing_stock"] == 0
        ]
        .reset_index(drop=True)
    )


def get_inventory_by_product():
    inventory = get_current_inventory()

    products = pd.read_csv(
        DATA_DIR / "products.csv"
    )

    result = inventory.merge(
        products[
            [
                "product_id",
                "product_name",
                "category",
                "selling_price"
            ]
        ],
        on="product_id",
        how="left"
    )

    return result[
        [
            "product_id",
            "product_name",
            "category",
            "closing_stock",
            "selling_price"
        ]
    ]


def get_fast_moving_products(limit=10):
    inventory = load_inventory_data()

    result = (
        inventory
        .groupby("product_id")
        .agg(
            units_sold=(
                "units_sold",
                "sum"
            )
        )
        .sort_values(
            "units_sold",
            ascending=False
        )
        .head(limit)
        .reset_index()
    )

    products = pd.read_csv(
        DATA_DIR / "products.csv"
    )

    return result.merge(
        products[
            [
                "product_id",
                "product_name",
                "category"
            ]
        ],
        on="product_id",
        how="left"
    )


def get_inventory_turnover():
    inventory = load_inventory_data()

    total_units_sold = inventory["units_sold"].sum()

    daily_inventory = (
        inventory
        .groupby("date")["closing_stock"]
        .sum()
    )

    average_inventory = daily_inventory.mean()

    if average_inventory == 0:
        return 0.0

    return total_units_sold / average_inventory


def get_inventory_summary():
    current = get_current_inventory()

    total_stock = (
        current["closing_stock"].sum()
    )

    low_stock = (
        current["closing_stock"] <= 300
    ).sum()

    out_of_stock = (
        current["closing_stock"] == 0
    ).sum()

    return {
        "total_stock": total_stock,
        "low_stock_products": low_stock,
        "out_of_stock_products": out_of_stock,
        "inventory_turnover": get_inventory_turnover()
    }


if __name__ == "__main__":

    print("\nCURRENT INVENTORY")
    print(get_current_inventory())

    print("\nTOTAL STOCK")
    print(get_total_stock())

    print("\nLOW STOCK PRODUCTS")
    print(get_low_stock_products())

    print("\nOUT OF STOCK PRODUCTS")
    print(get_out_of_stock_products())

    print("\nFAST MOVING PRODUCTS")
    print(get_fast_moving_products())

    print("\nINVENTORY TURNOVER")
    print(get_inventory_turnover())

    print("\nINVENTORY SUMMARY")
    print(get_inventory_summary())