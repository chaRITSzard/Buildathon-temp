from nova.analytics.marketing import (
    get_total_marketing_spend,
    get_total_marketing_revenue,
    get_overall_roas,
    get_overall_roi,
    get_best_campaigns,
    get_worst_campaigns,
    get_performance_by_channel,
    get_performance_by_campaign_type,
)


def total_marketing_spend():
    """Return total marketing spend across all campaigns."""
    return {
        "total_marketing_spend": get_total_marketing_spend()
    }


def total_marketing_revenue():
    """Return revenue attributed to marketing campaigns."""
    return {
        "total_marketing_revenue": get_total_marketing_revenue()
    }


def overall_roas():
    """Return overall marketing ROAS across all campaigns."""
    return {
        "overall_roas": get_overall_roas()
    }


def overall_roi():
    """Return overall marketing ROI across all campaigns."""
    return {
        "overall_roi": get_overall_roi()
    }


def best_campaigns():
    """Return the highest-performing individual campaigns ranked by ROAS."""
    return get_best_campaigns().to_dict(
        orient="records"
    )


def worst_campaigns():
    """Return the lowest-performing individual campaigns ranked by ROAS."""
    return get_worst_campaigns().to_dict(
        orient="records"
    )


def performance_by_channel():
    """Return marketing performance aggregated by channel, including spend, revenue, ROAS, CTR, and conversion rate."""
    return get_performance_by_channel().to_dict(
        orient="records"
    )


def performance_by_campaign_type():
    """Return marketing performance aggregated by campaign type, including spend, revenue, conversions, ROAS, and ROI."""
    return get_performance_by_campaign_type().to_dict(
        orient="records"
    )