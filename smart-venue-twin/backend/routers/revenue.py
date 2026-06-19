"""
收入趋势路由 - 提供收入相关数据分析
适配真实CSV数据列名 (ticket_revenue.csv)
"""

from fastapi import APIRouter

from data_loader import get_data

router = APIRouter(prefix="/api/revenue", tags=["收入分析"])


@router.get("/trend")
async def get_revenue_trend():
    """
    获取10年收入趋势（季度粒度）
    返回按年-季度聚合的收入数据，含票务/周边/赞助分项
    """
    revenue_df = get_data("revenue")

    if revenue_df.empty:
        return {"trend": []}

    # 按年和季度聚合收入
    trend = (
        revenue_df
        .groupby(["year", "quarter"])
        .agg(
            total_revenue=("total_revenue", "sum"),
            ticket_revenue=("total_revenue", "sum"),
            merchandise_revenue=("merchandise_revenue", "sum") if "merchandise_revenue" in revenue_df.columns else ("total_revenue", "sum"),
            sponsor_revenue=("sponsor_revenue", "sum") if "sponsor_revenue" in revenue_df.columns else ("total_revenue", "sum"),
            sold_tickets=("sold_tickets", "sum") if "sold_tickets" in revenue_df.columns else ("total_tickets", "sum"),
        )
        .reset_index()
        .sort_values(["year", "quarter"])
    )

    result = []
    for _, row in trend.iterrows():
        result.append({
            "year": int(row["year"]),
            "quarter": str(row["quarter"]),
            "total_revenue": round(float(row["total_revenue"]), 2),
            "ticket_revenue": round(float(row["ticket_revenue"]), 2),
            "merchandise_revenue": round(float(row.get("merchandise_revenue", 0)), 2),
            "sponsor_revenue": round(float(row.get("sponsor_revenue", 0)), 2),
            "sold_tickets": int(row.get("sold_tickets", 0)),
        })

    return {"trend": result}


@router.get("/by-type")
async def get_revenue_by_type():
    """
    获取按活动类型分组的收入明细
    返回各活动类型的总收入和占比
    """
    revenue_df = get_data("revenue")

    if revenue_df.empty:
        return {"breakdown": []}

    # 按活动类型聚合
    agg_dict = {"total_revenue": ("total_revenue", "sum")}
    if "sold_tickets" in revenue_df.columns:
        agg_dict["sold_tickets"] = ("sold_tickets", "sum")

    by_type = (
        revenue_df
        .groupby("event_type")
        .agg(**agg_dict)
        .reset_index()
        .sort_values("total_revenue", ascending=False)
    )

    grand_total = by_type["total_revenue"].sum()

    result = []
    for _, row in by_type.iterrows():
        item = {
            "event_type": row["event_type"],
            "total_revenue": round(float(row["total_revenue"]), 2),
            "percentage": round(float(row["total_revenue"] / grand_total), 4) if grand_total > 0 else 0,
        }
        if "sold_tickets" in row:
            item["sold_tickets"] = int(row["sold_tickets"])
        result.append(item)

    return {"breakdown": result}


@router.get("/quarterly-compare")
async def get_quarterly_compare():
    """
    获取年度间季度对比数据
    用于同比分析，按季度展示不同年份的收入对比
    """
    revenue_df = get_data("revenue")

    if revenue_df.empty:
        return {"comparison": []}

    # 按年、季度聚合
    quarterly = (
        revenue_df
        .groupby(["year", "quarter"])["total_revenue"]
        .sum()
        .reset_index()
    )

    # 按季度分组，构建对比结构
    comparison = {}
    for _, row in quarterly.iterrows():
        q = row["quarter"]
        if q not in comparison:
            comparison[q] = {}
        comparison[q][str(int(row["year"]))] = round(float(row["total_revenue"]), 2)

    result = []
    for quarter in sorted(comparison.keys()):
        result.append({
            "quarter": str(quarter),
            "years": comparison[quarter],
        })

    return {"comparison": result}
