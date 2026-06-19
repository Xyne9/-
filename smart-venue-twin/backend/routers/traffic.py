"""
客流与热力图路由 - 提供客流量分布和3D飞线数据
适配真实CSV数据列名
"""

from fastapi import APIRouter

from data_loader import get_data

router = APIRouter(prefix="/api/traffic", tags=["客流分析"])


@router.get("/heatmap")
async def get_traffic_heatmap():
    """
    获取基于坐标的客流量热力图数据
    返回各入口的客流量分布
    """
    traffic_df = get_data("traffic")

    if traffic_df.empty:
        return {"heatmap": []}

    # 按小时聚合各入口客流量
    gates = ["north_gate", "south_gate", "east_gate", "west_gate"]
    available_gates = [g for g in gates if g in traffic_df.columns]

    if not available_gates:
        # 如果没有入口列，按小时聚合总客流
        hourly = (
            traffic_df
            .groupby("hour")
            .agg(avg_visitors=("total_visitors", "mean"))
            .reset_index()
        )
        result = []
        for _, row in hourly.iterrows():
            result.append({
                "hour": int(row["hour"]),
                "avg_visitors": int(round(row["avg_visitors"])),
            })
        return {"heatmap": result}

    # 按入口聚合
    heatmap_data = []
    gate_coords = {
        "north_gate": {"lat": 39.9930, "lng": 116.3965, "name": "北门"},
        "south_gate": {"lat": 39.9910, "lng": 116.3965, "name": "南门"},
        "east_gate":  {"lat": 39.9920, "lng": 116.3980, "name": "东门"},
        "west_gate":  {"lat": 39.9920, "lng": 116.3950, "name": "西门"},
    }

    for gate in available_gates:
        gate_info = gate_coords.get(gate, {"lat": 39.992, "lng": 116.396, "name": gate})
        avg_flow = round(float(traffic_df[gate].mean()), 1)
        max_flow = round(float(traffic_df[gate].max()), 1)
        heatmap_data.append({
            "gate": gate_info["name"],
            "lat": gate_info["lat"],
            "lng": gate_info["lng"],
            "avg_flow": avg_flow,
            "max_flow": max_flow,
        })

    return {"heatmap": heatmap_data}


@router.get("/hourly")
async def get_hourly_traffic():
    """
    获取24小时客流量分布
    返回各小时的平均客流量
    """
    traffic_df = get_data("traffic")

    if traffic_df.empty:
        return {"hourly": []}

    # 按小时聚合
    hourly = (
        traffic_df
        .groupby("hour")
        .agg(
            avg_visitors=("total_visitors", "mean"),
            total_visitors=("total_visitors", "sum"),
        )
        .reset_index()
        .sort_values("hour")
    )

    result = []
    for _, row in hourly.iterrows():
        result.append({
            "hour": int(row["hour"]),
            "avg_visitors": int(round(row["avg_visitors"])),
            "total_visitors": int(row["total_visitors"]),
        })

    return {"hourly": result}


@router.get("/flow-lines")
async def get_flow_lines():
    """
    获取3D飞线可视化数据
    返回源城市-目的地对，包含经纬度坐标和流量强度
    数据来源: event_source_flow.csv
    """
    flow_df = get_data("flow_lines")

    if flow_df.empty:
        return {"flow_lines": []}

    # 按源城市聚合，取Top30
    city_agg = (
        flow_df
        .groupby(["source_city", "source_province", "source_lat", "source_lng", "dest_lat", "dest_lng"])
        .agg(
            total_visitors=("visitor_count", "sum"),
            avg_spending=("avg_spending", "mean"),
        )
        .reset_index()
        .sort_values("total_visitors", ascending=False)
        .head(30)
    )

    max_visitors = city_agg["total_visitors"].max() if not city_agg.empty else 1

    result = []
    for _, row in city_agg.iterrows():
        result.append({
            "source": {
                "name": row["source_city"],
                "province": row["source_province"],
                "lat": round(float(row["source_lat"]), 4),
                "lng": round(float(row["source_lng"]), 4),
            },
            "destination": {
                "name": "国家体育场",
                "lat": round(float(row["dest_lat"]), 4),
                "lng": round(float(row["dest_lng"]), 4),
            },
            "visitor_count": int(row["total_visitors"]),
            "intensity": round(float(row["total_visitors"] / max_visitors), 3),
            "avg_spending": round(float(row["avg_spending"]), 2),
        })

    return {"flow_lines": result}
