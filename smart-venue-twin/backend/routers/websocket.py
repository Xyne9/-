"""
WebSocket实时推送路由 - 模拟实时数据流
每2秒推送一次数据，包含客流、设备告警、收入、密度等
"""

import asyncio
import random
import time
from datetime import datetime

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter(tags=["实时推送"])

# 模拟实时数据的状态
_current_visitors = 3850
_revenue_tick = 0
_base_time = time.time()


def _generate_visitor_count() -> int:
    """生成当前访客数（带波动）"""
    global _current_visitors
    # 根据当前时间模拟日间波动
    hour = datetime.now().hour
    if 9 <= hour <= 11:
        base = 4500
    elif 14 <= hour <= 17:
        base = 5200
    elif 19 <= hour <= 22:
        base = 3800
    else:
        base = 800

    # 添加随机波动
    fluctuation = random.randint(-200, 200)
    _current_visitors = max(100, base + fluctuation)
    return _current_visitors


def _generate_equipment_alert() -> dict:
    """随机生成设备告警"""
    zones = ["A区-主会场", "B区-展览馆", "C区-体育馆", "D区-会议中心", "E区-商业区"]
    eq_types = ["空调系统", "照明系统", "消防系统", "安防监控", "电梯", "通风系统"]
    alert_types = ["温度异常", "功率波动", "信号弱", "响应延迟", "传感器偏移"]

    # 20%概率产生告警
    if random.random() < 0.2:
        return {
            "has_alert": True,
            "alert": {
                "equipment_id": f"EQ-{random.choice(zones)[0]}-{random.randint(1,7):03d}",
                "zone": random.choice(zones),
                "equipment_type": random.choice(eq_types),
                "alert_type": random.choice(alert_types),
                "severity": random.choice(["警告", "严重"]),
                "timestamp": datetime.now().isoformat(),
            }
        }
    return {"has_alert": False, "alert": None}


def _generate_revenue_tick() -> dict:
    """生成收入增量数据"""
    global _revenue_tick
    _revenue_tick += 1
    # 模拟每次收入增量（万元）
    increment = round(random.uniform(0.5, 3.5), 2)
    return {
        "tick": _revenue_tick,
        "increment": increment,
        "timestamp": datetime.now().isoformat(),
    }


def _generate_traffic_density() -> dict:
    """生成各区域实时客流密度"""
    zones = ["A区-主会场", "B区-展览馆", "C区-体育馆", "D区-会议中心", "E区-商业区"]
    densities = {}
    for zone in zones:
        densities[zone] = round(random.uniform(0.1, 1.0), 3)
    return {
        "densities": densities,
        "timestamp": datetime.now().isoformat(),
    }


@router.websocket("/ws/realtime")
async def websocket_realtime(websocket: WebSocket):
    """
    WebSocket实时数据推送端点
    每2秒推送一次综合实时数据
    """
    await websocket.accept()
    try:
        while True:
            # 组装实时数据包
            data = {
                "type": "realtime_update",
                "timestamp": datetime.now().isoformat(),
                "visitors": {
                    "current_count": _generate_visitor_count(),
                },
                "equipment": _generate_equipment_alert(),
                "revenue": _generate_revenue_tick(),
                "traffic": _generate_traffic_density(),
            }

            await websocket.send_json(data)
            await asyncio.sleep(2)  # 每2秒推送一次

    except WebSocketDisconnect:
        # 客户端主动断开连接
        pass
    except Exception:
        # 其他异常也退出循环
        pass
