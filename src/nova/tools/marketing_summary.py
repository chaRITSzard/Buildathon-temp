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


def marketing_summary():
    """
    Return a comprehensive marketing summary for strategic analysis,
    including spend, revenue, ROAS, ROI, campaign performance,
    channel performance, and campaign-type performance.
    """

    return {
        "total_marketing_spend": get_total_marketing_spend(),

        "total_marketing_revenue": get_total_marketing_revenue(),

        "overall_roas": get_overall_roas(),

        "overall_roi": get_overall_roi(),

        "best_campaigns": get_best_campaigns().to_dict(
            orient="records"
        ),

        "worst_campaigns": get_worst_campaigns().to_dict(
            orient="records"
        ),

        "performance_by_channel": get_performance_by_channel().to_dict(
            orient="records"
        ),

        "performance_by_campaign_type": get_performance_by_campaign_type().to_dict(
            orient="records"
        )
    }