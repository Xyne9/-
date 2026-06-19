"""
核心指标概览路由 - 提供聚合KPI数据
适配真实CSV数据列名
"""

from fastapi import APIRouter

from data_loader import get_data

router = APIRouter(prefix="/api/overview", tags=["概览"])


@router.get("")
async def get_overview():
    """
    获取核心KPI指标概览
    包括：10年总收入、年均访客、活动场次、设备健康率、同比增长、本季度摘要
    """
    # 获取收入数据 (ticket_revenue.csv)
    revenue_df = get_data("revenue")
    # 获取设备数据 (equipment_inspection.csv)
    equipment_df = get_data("equipment")
    # 获取客流数据 (daily_foot_traffic.csv)
    traffic_df = get_data("traffic")

    # 计算10年总收入（元）
    total_revenue_10y = round(float(revenue_df["total_revenue"].sum()), 2) if not revenue_df.empty else 0

    # 计算年均访客数
    if not traffic_df.empty and "total_visitors" in traffic_df.columns:
        traffic_df_copy = traffic_df.copy()
        traffic_df_copy["date"] = __import__("pandas").to_datetime(traffic_df_copy["date"])
        yearly_visitors = traffic_df_copy.groupby(traffic_df_copy["date"].dt.year)["total_visitors"].sum()
        avg_annual_visitors = int(yearly_visitors.mean())
    else:
        avg_annual_visitors = 0

    # 活动总场次（去重统计）
    total_event_count = 0
    if not revenue_df.empty:
        total_event_count = int(revenue_df["event_name"].nunique()) if "event_name" in revenue_df.columns else 0

    # 设备健康率（health_score >= 70 视为正常）
    equipment_health_rate = 0.0
    if not equipment_df.empty and "health_score" in equipment_df.columns:
        normal_count = len(equipment_df[equipment_df["health_score"] >= 70])
        equipment_health_rate = round(normal_count / len(equipment_df), 4)

    # 同比增长率（最近两年收入对比）
    yoy_growth = 0.0
    if not revenue_df.empty and "year" in revenue_df.columns:
        years = sorted(revenue_df["year"].unique())
        if len(years) >= 2:
            last_year = years[-1]
            prev_year = years[-2]
            last_year_revenue = revenue_df[revenue_df["year"] == last_year]["total_revenue"].sum()
            prev_year_revenue = revenue_df[revenue_df["year"] == prev_year]["total_revenue"].sum()
            if prev_year_revenue > 0:
                yoy_growth = round((last_year_revenue - prev_year_revenue) / prev_year_revenue, 4)

    # 本季度摘要
    this_quarter_summary = {}
    if not revenue_df.empty and "year" in revenue_df.columns:
        latest_year = revenue_df["year"].max()
        latest_quarter_data = revenue_df[revenue_df["year"] == latest_year]
        if not latest_quarter_data.empty and "quarter" in latest_quarter_data.columns:
            latest_quarter = latest_quarter_data["quarter"].max()
            q_data = latest_quarter_data[latest_quarter_data["quarter"] == latest_quarter]
            this_quarter_summary = {
                "year": int(latest_year),
                "quarter": str(latest_quarter),
                "revenue": round(float(q_data["total_revenue"].sum()), 2),
                "sold_tickets": int(q_data["sold_tickets"].sum()) if "sold_tickets" in q_data.columns else 0,
                "event_count": int(q_data["event_name"].nunique()) if "event_name" in q_data.columns else 0,
            }

    return {
        "total_revenue_10y": total_revenue_10y,
        "avg_annual_visitors": avg_annual_visitors,
        "event_count": total_event_count,
        "equipment_health_rate": equipment_health_rate,
        "yoy_growth": yoy_growth,
        "this_quarter_summary": this_quarter_summary,
    }
