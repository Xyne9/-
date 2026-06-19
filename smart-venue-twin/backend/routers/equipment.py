"""
设备状态路由 - 提供设备健康状态和3D模型元数据
适配真实CSV数据列名 (equipment_inspection.csv)
"""

from fastapi import APIRouter

from data_loader import get_data

router = APIRouter(prefix="/api/equipment", tags=["设备监控"])


@router.get("/status")
async def get_equipment_status():
    """
    获取各区域设备健康状态概览
    返回按区域分组的设备状态统计
    """
    equipment_df = get_data("equipment")

    if equipment_df.empty:
        return {"zones": []}

    # 按区域聚合设备状态
    zones = []
    for zone_name, group in equipment_df.groupby("zone"):
        total = len(group)
        # 状态统计
        status_col = "status" if "status" in group.columns else None
        if status_col:
            normal = len(group[group["status"] == "正常"])
            warning = len(group[group["status"] == "预警"])
            fault = len(group[group["status"] == "故障"])
            maintenance = len(group[group["status"] == "维修中"])
        else:
            normal = total
            warning = fault = maintenance = 0

        # 平均健康分数
        avg_health = round(float(group["health_score"].mean()), 2) if "health_score" in group.columns else 100.0

        zones.append({
            "zone": zone_name,
            "total_equipment": total,
            "normal_count": normal,
            "warning_count": warning,
            "fault_count": fault,
            "maintenance_count": maintenance,
            "avg_health_score": avg_health,
        })

    return {"zones": zones}


@router.get("/alerts")
async def get_equipment_alerts():
    """
    获取有预警或故障的设备列表
    返回需要关注的设备详细信息
    """
    equipment_df = get_data("equipment")

    if equipment_df.empty:
        return {"alerts": []}

    # 筛选非正常状态的设备
    if "status" in equipment_df.columns:
        alert_df = equipment_df[equipment_df["status"].isin(["预警", "故障", "维修中"])].copy()
    elif "health_score" in equipment_df.columns:
        alert_df = equipment_df[equipment_df["health_score"] < 70].copy()
    else:
        return {"alerts": []}

    alert_df = alert_df.sort_values("health_score" if "health_score" in alert_df.columns else "zone")

    alerts = []
    for _, row in alert_df.head(50).iterrows():  # 限制返回数量
        alert = {
            "equipment_name": row.get("equipment_name", "未知"),
            "equipment_type": row.get("equipment_type", "未知"),
            "zone": row.get("zone", "未知"),
            "status": row.get("status", "未知"),
            "health_score": round(float(row.get("health_score", 0)), 1),
            "risk_level": row.get("risk_level", "低"),
        }
        if "anomaly_type" in row and row["anomaly_type"]:
            alert["anomaly_type"] = row["anomaly_type"]
        alerts.append(alert)

    return {"alerts": alerts, "total_alerts": len(alert_df)}


@router.get("/3d-model")
async def get_3d_model():
    """
    获取3D模型元数据
    返回各区域位置和设备健康数据叠加信息
    用于前端3D场景渲染
    """
    equipment_df = get_data("equipment")

    if equipment_df.empty:
        return {"model": {"zones": [], "equipment": []}}

    # 区域3D位置定义（模拟国家体育场3D模型中的区域坐标）
    zone_positions = {
        "A区": {"x": -3, "y": 0.5, "z": 2, "color": "#00f0ff"},
        "B区": {"x": 3, "y": 0.5, "z": 2, "color": "#00f0ff"},
        "C区": {"x": -3, "y": 0.5, "z": -2, "color": "#00f0ff"},
        "VIP区": {"x": 0, "y": 1, "z": 3, "color": "#ffaa00"},
        "舞台区": {"x": 0, "y": 0.3, "z": 0, "color": "#ff44ff"},
        "灯光区": {"x": -2, "y": 2.5, "z": 0, "color": "#00f0ff"},
        "音响区": {"x": 2, "y": 2.5, "z": 0, "color": "#00f0ff"},
        "安防区": {"x": 0, "y": 0.3, "z": -3, "color": "#00f0ff"},
        "消防区": {"x": -4, "y": 0.3, "z": -1, "color": "#ff4444"},
        "电力区": {"x": 4, "y": 0.3, "z": -1, "color": "#ffaa00"},
    }

    # 构建区域数据
    zones = []
    for zone_name, pos in zone_positions.items():
        zone_equipment = equipment_df[equipment_df["zone"] == zone_name] if "zone" in equipment_df.columns else equipment_df.iloc[0:0]
        avg_health = round(float(zone_equipment["health_score"].mean()), 2) if not zone_equipment.empty and "health_score" in zone_equipment.columns else 100.0

        # 根据健康分数确定区域颜色
        if avg_health >= 90:
            color = "#4CAF50"  # 绿色-健康
            alert_level = "正常"
        elif avg_health >= 70:
            color = "#FF9800"  # 橙色-预警
            alert_level = "预警"
        else:
            color = "#F44336"  # 红色-故障
            alert_level = "告警"

        zones.append({
            "name": zone_name,
            "position": pos,
            "health_score": avg_health,
            "color": color,
            "alert_level": alert_level,
            "equipment_count": len(zone_equipment),
        })

    # 构建设备点位数据（取每个区域代表性设备）
    equipment_list = []
    if "zone" in equipment_df.columns:
        for zone_name, group in equipment_df.groupby("zone"):
            # 每个区域取健康分最低的3个设备
            sample = group.nsmallest(3, "health_score") if "health_score" in group.columns else group.head(3)
            for _, row in sample.iterrows():
                pos_info = zone_positions.get(zone_name, {"x": 0, "y": 0, "z": 0})
                equipment_list.append({
                    "equipment_name": row.get("equipment_name", "未知"),
                    "equipment_type": row.get("equipment_type", "未知"),
                    "zone": zone_name,
                    "status": row.get("status", "未知"),
                    "health_score": round(float(row.get("health_score", 100)), 1),
                    "risk_level": row.get("risk_level", "低"),
                    "position": {
                        "x": pos_info["x"] + __import__("random").uniform(-0.5, 0.5),
                        "y": pos_info["y"] + __import__("random").uniform(-0.3, 0.3),
                        "z": pos_info["z"] + __import__("random").uniform(-0.5, 0.5),
                    },
                })

    return {
        "model": {
            "zones": zones,
            "equipment": equipment_list[:30],  # 限制数量
        }
    }
