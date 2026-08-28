import os
import numpy as np
import pandas as pd
from faker import Faker

SEED = 42
NUM_CUSTOMERS = 10_000
NUM_PRODUCTS = 100
NUM_ORDERS = 100_000
NUM_CAMPAIGNS = 50

np.random.seed(SEED)
fake = Faker("en_IN")
Faker.seed(SEED)

OUTPUT_DIR = "data/synthetic"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def generate_customers():
    channels = [
        "Instagram",
        "Google",
        "YouTube",
        "Referral",
        "Organic Search",
        "Direct"
    ]

    segments = [
        "Budget",
        "Regular",
        "Premium",
        "VIP"
    ]

    cities = [
        "Mumbai",
        "Delhi",
        "Bangalore",
        "Hyderabad",
        "Chennai",
        "Pune",
        "Kolkata",
        "Ahmedabad",
        "Jaipur",
        "Lucknow"
    ]

    customers = []

    for i in range(NUM_CUSTOMERS):
        customers.append({
            "customer_id": f"C{i + 1:05d}",
            "signup_date": fake.date_between(
                start_date="-3y",
                end_date="today"
            ),
            "age": np.random.randint(18, 65),
            "gender": np.random.choice(
                ["Male", "Female", "Other"],
                p=[0.48, 0.48, 0.04]
            ),
            "city": np.random.choice(cities),
            "acquisition_channel": np.random.choice(
                channels,
                p=[0.22, 0.20, 0.10, 0.15, 0.18, 0.15]
            ),
            "customer_segment": np.random.choice(
                segments,
                p=[0.25, 0.45, 0.22, 0.08]
            )
        })

    df = pd.DataFrame(customers)

    df.to_csv(
        f"{OUTPUT_DIR}/customers.csv",
        index=False
    )

    print(f"✓ Generated {len(df):,} customers")


def generate_products():
    categories = {
        "Footwear": [
            "Sneakers",
            "Running Shoes",
            "Casual Shoes"
        ],
        "Apparel": [
            "T-Shirts",
            "Hoodies",
            "Jackets"
        ],
        "Accessories": [
            "Backpacks",
            "Caps",
            "Wallets"
        ],
        "Lifestyle": [
            "Water Bottles",
            "Sunglasses",
            "Watches"
        ]
    }

    products = []

    product_id = 1

    for category, subcategories in categories.items():

        for subcategory in subcategories:

            products_per_subcategory = NUM_PRODUCTS // 12

            for _ in range(products_per_subcategory):

                unit_cost = round(
                    np.random.uniform(300, 2500),
                    2
                )

                selling_price = round(
                    unit_cost * np.random.uniform(1.4, 2.4),
                    2
                )

                products.append({
                    "product_id": f"P{product_id:04d}",
                    "product_name": (
                        f"NOVA {subcategory} "
                        f"{product_id:03d}"
                    ),
                    "category": category,
                    "subcategory": subcategory,
                    "unit_cost": unit_cost,
                    "selling_price": selling_price
                })

                product_id += 1

    df = pd.DataFrame(products)

    df.to_csv(
        f"{OUTPUT_DIR}/products.csv",
        index=False
    )

    print(f"✓ Generated {len(df):,} products")


def generate_orders():
    customers = pd.read_csv(f"{OUTPUT_DIR}/customers.csv")
    customers["signup_date"] = pd.to_datetime(customers["signup_date"])

    segment_weights = {
        "Budget": 0.45,
        "Regular": 1.0,
        "Premium": 1.8,
        "VIP": 3.0 
    }

    customers["purchase_weight"] = (
        customers["customer_segment"].map(segment_weights)
    )

    probab = (
        customers["purchase_weight"]/customers["purchase_weight"].sum()
    )

    selected_customers = np.random.choice(
        customers["customer_id"],
        size = NUM_ORDERS,
        p = probab
    )
    start_date = pd.Timestamp("2025-01-01")
    end_date = pd.Timestamp("2026-08-31")

    orders = []

    for i, customer_id in enumerate(selected_customers):
        customer = customers[
            customers["customer_id"] == customer_id
        ].iloc[0]

        earliest_date = max(
            start_date,
            customer["signup_date"]
        )

        order_date = pd.Timestamp(
            np.random.randint(
                earliest_date.value // 10**9,
                end_date.value // 10**9
            ),
            unit="s"
        )

        if order_date.dayofweek >= 5:
            weekend_probability = 0.6
            if np.random.random() > weekend_probability:
                continue

        status = np.random.choice(
            ["Completed", "Cancelled", "Returned", "In Transit"],
            p = [0.78, 0.03, 0.05, 0.14]
        )

        payment_method = np.random.choice(
            ["UPI", "Credit Card", "Debit Card", "COD"],
            p=[0.40, 0.30, 0.20, 0.10]
        )

        discount_rate = {
            "Budget": 0.05,
            "Regular": 0.07,
            "Premium": 0.10,
            "VIP": 0.12
        }[customer["customer_segment"]]

        discount_amount = round(
            np.random.uniform(
                0,
                discount_rate * 1500
            ),
            2
        )

        shipping_cost = round(
            np.random.uniform(40, 150),
            2
        )

        orders.append({
            "order_id": f"O{i + 1:06d}",
            "customer_id": customer_id,
            "order_date": order_date.date(),
            "order_status": status,
            "payment_method": payment_method,
            "discount_amount": discount_amount,
            "shipping_cost": shipping_cost
        })

    df = pd.DataFrame(orders)

    df.to_csv(
        f"{OUTPUT_DIR}/orders.csv",
        index=False
    )

    print(f"✓ Generated {len(df):,} orders")

    return df


def generate_order_items(orders):
    products = pd.read_csv(
        f"{OUTPUT_DIR}/products.csv"
    )

    items = []

    item_id = 1

    for _, order in orders.iterrows():

        num_products = np.random.choice(
            [1, 2, 3],
            p=[0.60, 0.30, 0.10]
        )

        selected_products = products.sample(
            n=num_products,
            replace=False
        )

        for _, product in selected_products.iterrows():

            quantity = np.random.choice(
                [1, 2, 3],
                p=[0.75, 0.20, 0.05]
            )

            unit_price = round(
                product["selling_price"]
                * np.random.uniform(0.95, 1.0),
                2
            )

            items.append({
                "order_item_id": f"OI{item_id:07d}",
                "order_id": order["order_id"],
                "product_id": product["product_id"],
                "quantity": quantity,
                "unit_price": unit_price
            })

            item_id += 1

    df = pd.DataFrame(items)

    df.to_csv(
        f"{OUTPUT_DIR}/order_items.csv",
        index=False
    )

    print(f"✓ Generated {len(df):,} order items")

    return df

def generate_campaigns():
    channels = [
        "Instagram",
        "Google",
        "YouTube",
        "Email",
        "Influencer",
        "Facebook"
    ]

    campaign_types = [
        "Acquisition",
        "Retention",
        "Product"
    ]

    campaign_names = [
        "Summer Sale",
        "Monsoon Revival",
        "Festival Rush",
        "Weekend Essentials",
        "Back to College",
        "Premium Collection",
        "Flash Sale",
        "New Season",
        "Mega Savings",
        "NOVA Spotlight"
    ]

    performance_profiles = [
        "Excellent",
        "Good",
        "Average",
        "Poor"
    ]

    campaigns = []

    start_date = pd.Timestamp("2025-01-01")
    end_date = pd.Timestamp("2026-08-15")

    for i in range(NUM_CAMPAIGNS):

        campaign_start = pd.Timestamp(
            np.random.randint(
                start_date.value // 10**9,
                end_date.value // 10**9
            ),
            unit="s"
        )

        duration = np.random.randint(7, 22)

        campaign_end = campaign_start + pd.Timedelta(
            days=duration
        )

        channel = np.random.choice(
            channels,
            p=[
                0.25,
                0.20,
                0.10,
                0.20,
                0.10,
                0.15
            ]
        )

        campaign_type = np.random.choice(
            campaign_types,
            p=[
                0.45,
                0.30,
                0.25
            ]
        )

        if campaign_type == "Acquisition":

            target_segment = np.random.choice(
                [
                    "New Customers",
                    "Budget",
                    "Regular"
                ],
                p=[
                    0.50,
                    0.25,
                    0.25
                ]
            )

        elif campaign_type == "Retention":

            target_segment = np.random.choice(
                [
                    "Returning Customers",
                    "Premium",
                    "VIP"
                ],
                p=[
                    0.50,
                    0.30,
                    0.20
                ]
            )

        else:

            target_segment = np.random.choice(
                [
                    "All Customers",
                    "Regular",
                    "Premium"
                ],
                p=[
                    0.50,
                    0.30,
                    0.20
                ]
            )

        budget = round(
            np.random.uniform(
                50_000,
                500_000
            ),
            2
        )

        profile = np.random.choice(
            performance_profiles,
            p=[
                0.15,
                0.35,
                0.40,
                0.10
            ]
        )

        campaigns.append({
            "campaign_id": f"CAM{i + 1:03d}",
            "campaign_name": (
                f"{np.random.choice(campaign_names)} "
                f"{i + 1}"
            ),
            "channel": channel,
            "campaign_type": campaign_type,
            "start_date": campaign_start.date(),
            "end_date": campaign_end.date(),
            "budget": budget,
            "target_segment": target_segment,
            "performance_profile": profile
        })

    df = pd.DataFrame(campaigns)

    public_campaigns = df[
        [
            "campaign_id",
            "campaign_name",
            "channel",
            "campaign_type",
            "start_date",
            "end_date",
            "budget",
            "target_segment"
        ]
    ]

    public_campaigns.to_csv(
        f"{OUTPUT_DIR}/marketing_campaigns.csv",
        index=False
    )

    print(
        f"✓ Generated {len(df):,} marketing campaigns"
    )

    return df

def generate_marketing_performance(campaigns, orders):
    performance = []

    channel_cpm = {
        "Instagram": 320,
        "Google": 450,
        "YouTube": 280,
        "Email": 800,
        "Influencer": 380,
        "Facebook": 300
    }

    channel_ctr = {
        "Instagram": 0.025,
        "Google": 0.035,
        "YouTube": 0.018,
        "Email": 0.060,
        "Influencer": 0.022,
        "Facebook": 0.020
    }

    channel_conversion = {
        "Instagram": 0.045,
        "Google": 0.070,
        "YouTube": 0.035,
        "Email": 0.090,
        "Influencer": 0.050,
        "Facebook": 0.040
    }

    profile_multiplier = {
        "Excellent": 1.35,
        "Good": 1.15,
        "Average": 1.00,
        "Poor": 0.70
    }

    segment_aov = {
        "Budget": 1800,
        "Regular": 2400,
        "Premium": 3200,
        "VIP": 4200,
        "New Customers": 2100,
        "Returning Customers": 3000,
        "All Customers": 2600
    }

    for _, campaign in campaigns.iterrows():

        dates = pd.date_range(
            campaign["start_date"],
            campaign["end_date"]
        )

        daily_budget = campaign["budget"] / len(dates)

        for date in dates:

            spend = daily_budget * np.random.uniform(
                0.90,
                1.10
            )

            cpm = channel_cpm[campaign["channel"]]

            impressions = int(
                (spend / cpm) * 1000
            )

            ctr = (
                channel_ctr[campaign["channel"]]
                * profile_multiplier[
                    campaign["performance_profile"]
                ]
            )

            ctr *= np.random.uniform(
                0.90,
                1.10
            )

            clicks = int(
                impressions * ctr
            )

            conversion_rate = (
                channel_conversion[
                    campaign["channel"]
                ]
                * profile_multiplier[
                    campaign["performance_profile"]
                ]
            )

            conversion_rate *= np.random.uniform(
                0.90,
                1.10
            )

            conversions = int(
                clicks * conversion_rate
            )

            aov = segment_aov[
                campaign["target_segment"]
            ]

            channel_revenue_mult = {
                "Instagram": 0.85,
                "Google": 1.00,
                "YouTube": 0.90,
                "Email": 0.75,
                "Influencer": 0.95,
                "Facebook": 0.80
            }

            aov *= channel_revenue_mult[
                campaign["channel"]
            ]

            aov *= np.random.uniform(
                0.85,
                1.15
            )

            revenue_generated = round(
                conversions * aov,
                2
            )

            performance.append({
                "campaign_id": campaign["campaign_id"],
                "date": date.date(),
                "impressions": impressions,
                "clicks": clicks,
                "conversions": conversions,
                "spend": round(spend, 2),
                "revenue_generated": revenue_generated
            })

    df = pd.DataFrame(performance)

    df.to_csv(
        f"{OUTPUT_DIR}/marketing_performance.csv",
        index=False
    )

    print(
        f"✓ Generated {len(df):,} marketing performance records"
    )

    return df

def generate_financials(orders, order_items):
    products = pd.read_csv(
        f"{OUTPUT_DIR}/products.csv"
    )

    marketing = pd.read_csv(
        f"{OUTPUT_DIR}/marketing_performance.csv"
    )

    orders = orders.copy()
    order_items = order_items.copy()

    orders["order_date"] = pd.to_datetime(
        orders["order_date"]
    )

    marketing["date"] = pd.to_datetime(
        marketing["date"]
    )

    items = order_items.merge(
        orders[
            [
                "order_id",
                "customer_id",
                "order_date",
                "order_status"
            ]
        ],
        on="order_id",
        how="left"
    )

    items = items.merge(
        products[
            [
                "product_id",
                "unit_cost"
            ]
        ],
        on="product_id",
        how="left"
    )

    completed_items = items[
        items["order_status"] == "Completed"
    ].copy()

    completed_items["revenue"] = (
        completed_items["quantity"]
        * completed_items["unit_price"]
    )

    completed_items["product_cost"] = (
        completed_items["quantity"]
        * completed_items["unit_cost"]
    )

    daily_sales = (
        completed_items
        .groupby("order_date")
        .agg(
            revenue=("revenue", "sum"),
            product_cost=("product_cost", "sum")
        )
        .reset_index()
    )

    daily_marketing = (
        marketing
        .groupby("date")["spend"]
        .sum()
        .reset_index()
        .rename(
            columns={
                "date": "order_date",
                "spend": "marketing_expense"
            }
        )
    )

    financials = daily_sales.merge(
        daily_marketing,
        on="order_date",
        how="outer"
    )

    financials = financials.fillna(0)

    financials["operating_expense"] = (
        financials["revenue"] * 0.12
    )

    financials["shipping_expense"] = (
        financials["revenue"] * 0.04
    )

    financials["other_expense"] = (
        financials["revenue"] * 0.02
    )

    financials["gross_profit"] = (
        financials["revenue"]
        - financials["product_cost"]
    )

    financials["operating_profit"] = (
        financials["gross_profit"]
        - financials["marketing_expense"]
        - financials["operating_expense"]
        - financials["shipping_expense"]
        - financials["other_expense"]
    )

    financials["profit_margin"] = (
        financials["operating_profit"]
        / financials["revenue"]
    ).fillna(0)

    financials = financials.rename(
        columns={
            "order_date": "date"
        }
    )

    financials.to_csv(
        f"{OUTPUT_DIR}/financials.csv",
        index=False
    )

    print(
        f"✓ Generated {len(financials):,} financial records"
    )

    return financials


def generate_inventory(orders, order_items):
    products = pd.read_csv(
        f"{OUTPUT_DIR}/products.csv"
    )

    orders = orders.copy()
    order_items = order_items.copy()

    orders["order_date"] = pd.to_datetime(
        orders["order_date"]
    )

    items = order_items.merge(
        orders[
            [
                "order_id",
                "order_date",
                "order_status"
            ]
        ],
        on="order_id",
        how="left"
    )

    completed_items = items[
        items["order_status"] == "Completed"
    ].copy()

    daily_sales = (
        completed_items
        .groupby(
            [
                "order_date",
                "product_id"
            ]
        )["quantity"]
        .sum()
        .reset_index()
        .rename(
            columns={
                "order_date": "date",
                "quantity": "units_sold"
            }
        )
    )

    dates = pd.date_range(
        "2025-01-01",
        "2026-08-31"
    )

    grid = pd.MultiIndex.from_product(
        [
            dates,
            products["product_id"]
        ],
        names=[
            "date",
            "product_id"
        ]
    ).to_frame(index=False)

    inventory = grid.merge(
        daily_sales,
        on=[
            "date",
            "product_id"
        ],
        how="left"
    )

    inventory["units_sold"] = (
        inventory["units_sold"]
        .fillna(0)
        .astype(int)
    )

    initial_stock = {
        product_id: np.random.randint(
            500,
            1800
        )
        for product_id in products["product_id"]
    }

    inventory["opening_stock"] = 0
    inventory["units_received"] = 0
    inventory["closing_stock"] = 0

    for product_id in products["product_id"]:

        product_mask = (
            inventory["product_id"] == product_id
        )

        product_rows = (
            inventory.loc[product_mask]
            .sort_values("date")
        )

        stock = initial_stock[product_id]

        reorder_point = np.random.randint(
            250,
            600
        )

        reorder_quantity = np.random.randint(
            500,
            1200
        )

        lead_time = np.random.randint(
            2,
            8
        )

        pending_orders = []

        for idx in product_rows.index:

            current_date = inventory.at[
                idx,
                "date"
            ]

            units_sold = inventory.at[
                idx,
                "units_sold"
            ]

            arrivals_today = 0

            remaining_orders = []

            for arrival_date, quantity in pending_orders:

                if arrival_date <= current_date:
                    arrivals_today += quantity
                else:
                    remaining_orders.append(
                        (
                            arrival_date,
                            quantity
                        )
                    )

            pending_orders = remaining_orders

            opening_stock = stock

            stock += arrivals_today

            stock -= units_sold

            if stock < 0:
                stock = 0

            inventory.at[
                idx,
                "opening_stock"
            ] = opening_stock

            inventory.at[
                idx,
                "units_received"
            ] = arrivals_today

            inventory.at[
                idx,
                "closing_stock"
            ] = stock

            if (
                stock <= reorder_point
                and not pending_orders
            ):

                if np.random.random() >= 0.15:

                    quantity = int(
                        reorder_quantity
                        * np.random.uniform(
                            0.8,
                            1.2
                        )
                    )

                    arrival_date = (
                        current_date
                        + pd.Timedelta(
                            days=lead_time
                        )
                    )

                    pending_orders.append(
                        (
                            arrival_date,
                            quantity
                        )
                    )

    inventory.to_csv(
        f"{OUTPUT_DIR}/inventory.csv",
        index=False
    )

    print(
        f"✓ Generated {len(inventory):,} inventory records"
    )

    return inventory

if __name__ == "__main__":
    generate_customers()
    generate_products()

    orders = generate_orders()
    order_items = generate_order_items(orders)

    campaigns = generate_campaigns()

    marketing_performance = (
        generate_marketing_performance(
            campaigns,
            orders
        )
    )

    financials = generate_financials(
        orders,
        order_items
    )

    inventory = generate_inventory(
        orders,
        order_items
    )