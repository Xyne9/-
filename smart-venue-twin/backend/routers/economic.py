"""
宏观经济关联路由 - 提供活动与地方经济的关联分析
适配真实CSV数据列名 (macro_economic.csv)
"""

from fastapi import APIRouter

import numpy as np

from data_loader import get_data

router = APIRouter(prefix="/api/economic", tags=["经济关联"])


@router.get("/correlation")
async def get_economic_correlation():
    """
    获取活动与地方经济的关联数据
    返回各指标间的相关系数和时序数据
    """
    economic_df = get_data("economic")

    if economic_df.empty:
        return {"correlations": {}, "timeline": []}

    # 真实CSV列名: date, quarter, gdp_growth_rate, cpi_index, tourism_index,
    # hotel_price_index, restaurant_revenue_index, transport_demand_index,
    # event_count, total_revenue, employment_index, real_estate_nearby_index, consumer_confidence_index
    numeric_cols = ["event_count", "gdp_growth_rate", "cpi_index", "tourism_index",
                    "hotel_price_index", "restaurant_revenue_index", "transport_demand_index",
                    "total_revenue", "employment_index", "real_estate_nearby_index",
                    "consumer_confidence_index"]

    available_cols = [c for c in numeric_cols if c in economic_df.columns]

    # 计算相关系数
    correlations = {}
    if len(available_cols) >= 2:
        corr_matrix = economic_df[available_cols].corr()
        if "event_count" in corr_matrix.columns:
            event_corr = corr_matrix["event_count"]
            for col in available_cols:
                if col != "event_count":
                    correlations[col] = round(float(event_corr[col]), 4)

    # 构建时序数据
    timeline = []
    for _, row in economic_df.sort_values("date").iterrows():
        item = {
            "date": str(row.get("date", "")),
            "quarter": str(row.get("quarter", "")),
            "event_count": int(row.get("event_count", 0)),
        }
        for col in available_cols:
            if col != "event_count":
                val = row.get(col)
                if val is not None:
                    try:
                        item[col] = round(float(val), 4)
                    except (ValueError, TypeError):
                        pass
        timeline.append(item)

    return {
        "correlations": correlations,
        "timeline": timeline,
    }


@router.get("/hotel-price")
async def get_hotel_price():
    """
    获取活动期间酒店价格波动数据
    返回各季度的酒店价格指数和活动影响分析
    """
    economic_df = get_data("economic")

    if economic_df.empty:
        return {"hotel_data": [], "event_impact": {}}

    # 按季度整理酒店数据
    hotel_data = []
    for _, row in economic_df.sort_values("date").iterrows():
        hotel_data.append({
            "date": str(row.get("date", "")),
            "quarter": str(row.get("quarter", "")),
            "hotel_price_index": round(float(row.get("hotel_price_index", 0)), 2),
            "restaurant_revenue_index": round(float(row.get("restaurant_revenue_index", 0)), 2),
            "event_count": int(row.get("event_count", 0)),
            "total_revenue": round(float(row.get("total_revenue", 0)), 2),
        })

    # 计算活动对酒店价格的影响
    event_impact = {}
    if "event_count" in economic_df.columns and "hotel_price_index" in economic_df.columns:
        median_events = economic_df["event_count"].median()
        high_event = economic_df[economic_df["event_count"] >= median_events]
        low_event = economic_df[economic_df["event_count"] < median_events]

        high_price = float(high_event["hotel_price_index"].mean()) if not high_event.empty else 0
        low_price = float(low_event["hotel_price_index"].mean()) if not low_event.empty else 0

        event_impact = {
            "high_event_avg_price": round(high_price, 2),
            "low_event_avg_price": round(low_price, 2),
            "price_premium": round((high_price - low_price) / low_price, 4) if low_price > 0 else 0,
            "high_event_avg_count": round(float(high_event["event_count"].mean()), 1) if not high_event.empty else 0,
            "low_event_avg_count": round(float(low_event["event_count"].mean()), 1) if not low_event.empty else 0,
        }

    return {
        "hotel_data": hotel_data,
        "event_impact": event_impact,
    }
