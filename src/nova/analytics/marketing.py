from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[3]

DATA_DIR = PROJECT_ROOT / "data" / "synthetic"


def load_marketing_data():
    campaigns = pd.read_csv(
        DATA_DIR / "marketing_campaigns.csv"
    )

    performance = pd.read_csv(
        DATA_DIR / "marketing_performance.csv"
    )

    campaigns["start_date"] = pd.to_datetime(
        campaigns["start_date"]
    )

    campaigns["end_date"] = pd.to_datetime(
        campaigns["end_date"]
    )

    performance["date"] = pd.to_datetime(
        performance["date"]
    )

    return campaigns, performance


def get_campaign_performance():
    campaigns, performance = load_marketing_data()

    performance_summary = (
        performance
        .groupby("campaign_id")
        .agg(
            impressions=("impressions", "sum"),
            clicks=("clicks", "sum"),
            conversions=("conversions", "sum"),
            spend=("spend", "sum"),
            revenue_generated=("revenue_generated", "sum")
        )
        .reset_index()
    )

    result = campaigns.merge(
        performance_summary,
        on="campaign_id",
        how="left"
    )

    result["ctr"] = (
        result["clicks"]
        / result["impressions"]
    )

    result["conversion_rate"] = (
        result["conversions"]
        / result["clicks"]
    )

    result["cac"] = (
        result["spend"]
        / result["conversions"]
    )

    result["roas"] = (
        result["revenue_generated"]
        / result["spend"]
    )

    result["roi"] = (
        (result["revenue_generated"] - result["spend"])
        / result["spend"]
    )

    return result


def get_total_marketing_spend():
    _, performance = load_marketing_data()

    return performance["spend"].sum()


def get_total_marketing_revenue():
    _, performance = load_marketing_data()

    return performance[
        "revenue_generated"
    ].sum()


def get_overall_roas():
    spend = get_total_marketing_spend()
    revenue = get_total_marketing_revenue()

    if spend == 0:
        return 0.0

    return revenue / spend


def get_overall_roi():
    spend = get_total_marketing_spend()
    revenue = get_total_marketing_revenue()

    if spend == 0:
        return 0.0

    return (revenue - spend) / spend


def get_best_campaigns(limit=10):
    campaigns = get_campaign_performance()

    return (
        campaigns
        .sort_values(
            "roas",
            ascending=False
        )
        .head(limit)
        [
            [
                "campaign_id",
                "campaign_name",
                "channel",
                "campaign_type",
                "target_segment",
                "spend",
                "revenue_generated",
                "roas",
                "roi"
            ]
        ]
    )


def get_worst_campaigns(limit=10):
    campaigns = get_campaign_performance()

    return (
        campaigns
        .sort_values(
            "roas",
            ascending=True
        )
        .head(limit)
        [
            [
                "campaign_id",
                "campaign_name",
                "channel",
                "campaign_type",
                "target_segment",
                "spend",
                "revenue_generated",
                "roas",
                "roi"
            ]
        ]
    )


def get_performance_by_channel():
    campaigns = get_campaign_performance()

    result = (
        campaigns
        .groupby("channel")
        .agg(
            campaigns=("campaign_id", "count"),
            spend=("spend", "sum"),
            revenue=("revenue_generated", "sum"),
            conversions=("conversions", "sum"),
            clicks=("clicks", "sum"),
            impressions=("impressions", "sum")
        )
        .reset_index()
    )

    result["roas"] = (
        result["revenue"]
        / result["spend"]
    )

    result["ctr"] = (
        result["clicks"]
        / result["impressions"]
    )

    result["conversion_rate"] = (
        result["conversions"]
        / result["clicks"]
    )

    return result.sort_values(
        "roas",
        ascending=False
    )


def get_performance_by_campaign_type():
    campaigns = get_campaign_performance()

    result = (
        campaigns
        .groupby("campaign_type")
        .agg(
            campaigns=("campaign_id", "count"),
            spend=("spend", "sum"),
            revenue=("revenue_generated", "sum"),
            conversions=("conversions", "sum")
        )
        .reset_index()
    )

    result["roas"] = (
        result["revenue"]
        / result["spend"]
    )

    result["roi"] = (
        (result["revenue"] - result["spend"])
        / result["spend"]
    )

    return result.sort_values(
        "roas",
        ascending=False
    )


if __name__ == "__main__":

    print("\nTOTAL MARKETING SPEND")
    print(get_total_marketing_spend())

    print("\nTOTAL MARKETING REVENUE")
    print(get_total_marketing_revenue())

    print("\nOVERALL ROAS")
    print(get_overall_roas())

    print("\nOVERALL ROI")
    print(get_overall_roi())

    print("\nBEST CAMPAIGNS")
    print(get_best_campaigns())

    print("\nWORST CAMPAIGNS")
    print(get_worst_campaigns())

    print("\nPERFORMANCE BY CHANNEL")
    print(get_performance_by_channel())

    print("\nPERFORMANCE BY CAMPAIGN TYPE")
    print(get_performance_by_campaign_type())