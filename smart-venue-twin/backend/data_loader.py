"""
数据加载模块 - 从CSV文件加载并缓存数据到内存
当CSV文件不存在时，自动生成模拟数据以保证API可用
"""

import os
import logging
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

# 数据目录路径
DATA_DIR = Path(os.environ.get("DATA_DIR", "/workspace/smart-venue-twin/data/raw"))

# 全局数据缓存
_data_cache: dict[str, pd.DataFrame] = {}


def _load_csv(filename: str) -> Optional[pd.DataFrame]:
    """尝试加载CSV文件，失败返回None"""
    filepath = DATA_DIR / filename
    if filepath.exists():
        try:
            df = pd.read_csv(filepath)
            logger.info(f"成功加载CSV文件: {filename}，共 {len(df)} 行")
            return df
        except Exception as e:
            logger.warning(f"加载CSV文件失败 {filename}: {e}")
            return None
    else:
        logger.info(f"CSV文件不存在: {filename}，将使用模拟数据")
        return None


def _generate_revenue_data() -> pd.DataFrame:
    """生成10年收入模拟数据（季度粒度）"""
    np.random.seed(42)
    years = list(range(2016, 2026))
    quarters = ["Q1", "Q2", "Q3", "Q4"]
    event_types = ["演唱会", "体育赛事", "展览", "会议", "文化活动"]

    records = []
    base_revenue = 800  # 万元
    for year in years:
        for quarter in quarters:
            # 模拟逐年增长趋势
            growth = 1 + (year - 2016) * 0.08 + np.random.normal(0, 0.05)
            seasonal = {"Q1": 0.85, "Q2": 1.0, "Q3": 1.15, "Q4": 1.05}[quarter]
            total = base_revenue * growth * seasonal

            for etype in event_types:
                ratio = np.random.uniform(0.1, 0.35)
                revenue = total * ratio
                visitors = int(revenue * np.random.uniform(8, 15))
                records.append({
                    "year": year,
                    "quarter": quarter,
                    "event_type": etype,
                    "revenue": round(revenue, 2),
                    "visitors": visitors,
                    "event_count": np.random.randint(2, 12),
                })
    return pd.DataFrame(records)


def _generate_traffic_data() -> pd.DataFrame:
    """生成客流量热力图模拟数据"""
    np.random.seed(123)
    # 场馆区域坐标（模拟经纬度）
    zones = {
        "A区-主会场": (31.2304, 121.4737),
        "B区-展览馆": (31.2310, 121.4745),
        "C区-体育馆": (31.2295, 121.4750),
        "D区-会议中心": (31.2308, 121.4760),
        "E区-商业区": (31.2315, 121.4725),
        "F区-停车场": (31.2290, 121.4720),
        "G区-入口广场": (31.2300, 121.4710),
        "H区-餐饮区": (31.2320, 121.4740),
    }

    records = []
    for zone_name, (lat, lng) in zones.items():
        for hour in range(24):
            # 模拟不同时段的客流密度
            if 9 <= hour <= 11:
                density = np.random.uniform(0.6, 1.0)
            elif 14 <= hour <= 17:
                density = np.random.uniform(0.7, 1.0)
            elif 19 <= hour <= 22:
                density = np.random.uniform(0.5, 0.9)
            else:
                density = np.random.uniform(0.05, 0.3)

            records.append({
                "zone": zone_name,
                "lat": lat + np.random.uniform(-0.0005, 0.0005),
                "lng": lng + np.random.uniform(-0.0005, 0.0005),
                "hour": hour,
                "density": round(density, 3),
                "visitor_count": int(density * 5000),
            })
    return pd.DataFrame(records)


def _generate_equipment_data() -> pd.DataFrame:
    """生成设备状态模拟数据"""
    np.random.seed(456)
    zones = ["A区-主会场", "B区-展览馆", "C区-体育馆", "D区-会议中心", "E区-商业区"]
    equipment_types = ["空调系统", "照明系统", "消防系统", "安防监控", "电梯", "通风系统", "供电系统"]

    records = []
    for zone in zones:
        for i, eq_type in enumerate(equipment_types):
            health = np.random.choice(
                ["正常", "警告", "故障"],
                p=[0.82, 0.13, 0.05]
            )
            health_rate = {
                "正常": np.random.uniform(0.90, 1.0),
                "警告": np.random.uniform(0.60, 0.85),
                "故障": np.random.uniform(0.10, 0.50),
            }[health]

            records.append({
                "zone": zone,
                "equipment_id": f"EQ-{zone[0]}-{i+1:03d}",
                "equipment_type": eq_type,
                "status": health,
                "health_rate": round(health_rate, 3),
                "last_maintenance": f"2025-{np.random.randint(1,13):02d}-{np.random.randint(1,29):02d}",
                "position_x": np.random.uniform(-50, 50),
                "position_y": np.random.uniform(-30, 30),
                "position_z": np.random.uniform(0, 20),
            })
    return pd.DataFrame(records)


def _generate_economic_data() -> pd.DataFrame:
    """生成宏观经济关联模拟数据"""
    np.random.seed(789)
    years = list(range(2016, 2026))
    quarters = ["Q1", "Q2", "Q3", "Q4"]

    records = []
    for year in years:
        for quarter in quarters:
            event_count = np.random.randint(15, 60)
            local_gdp_growth = round(np.random.uniform(3.5, 8.5), 2)
            hotel_avg_price = round(np.random.uniform(350, 880), 0)
            hotel_occupancy = round(np.random.uniform(0.55, 0.95), 3)
            restaurant_revenue = round(np.random.uniform(200, 600), 1)
            transport_flow = np.random.randint(50000, 200000)
            retail_sales = round(np.random.uniform(150, 450), 1)

            records.append({
                "year": year,
                "quarter": quarter,
                "event_count": event_count,
                "local_gdp_growth": local_gdp_growth,
                "hotel_avg_price": hotel_avg_price,
                "hotel_occupancy": hotel_occupancy,
                "restaurant_revenue": restaurant_revenue,
                "transport_flow": transport_flow,
                "retail_sales": retail_sales,
            })
    return pd.DataFrame(records)


def _generate_flow_line_data() -> pd.DataFrame:
    """生成3D飞线数据（源-目的地对）"""
    np.random.seed(321)
    # 模拟城市间客流来源
    sources = [
        ("上海本地", 31.2304, 121.4737),
        ("北京", 39.9042, 116.4074),
        ("广州", 23.1291, 113.2644),
        ("深圳", 22.5431, 114.0579),
        ("杭州", 30.2741, 120.1551),
        ("南京", 32.0603, 118.7969),
        ("成都", 30.5728, 104.0668),
        ("武汉", 30.5928, 114.3055),
        ("西安", 34.3416, 108.9398),
        ("重庆", 29.5630, 106.5516),
    ]
    destination = ("场馆", 31.2304, 121.4737)

    records = []
    for name, lat, lng in sources:
        flow = np.random.randint(500, 15000)
        records.append({
            "source_name": name,
            "source_lat": lat,
            "source_lng": lng,
            "dest_name": destination[0],
            "dest_lat": destination[1],
            "dest_lng": destination[2],
            "flow": flow,
            "intensity": round(flow / 15000, 3),
        })
    return pd.DataFrame(records)


def load_all_data() -> dict[str, pd.DataFrame]:
    """
    加载所有CSV数据到内存缓存
    优先从CSV文件读取，不存在则生成模拟数据
    """
    global _data_cache

    # 收入数据 - 对应 ticket_revenue.csv
    revenue_df = _load_csv("ticket_revenue.csv")
    _data_cache["revenue"] = revenue_df if revenue_df is not None else _generate_revenue_data()

    # 客流数据 - 对应 daily_foot_traffic.csv
    traffic_df = _load_csv("daily_foot_traffic.csv")
    _data_cache["traffic"] = traffic_df if traffic_df is not None else _generate_traffic_data()

    # 设备数据 - 对应 equipment_inspection.csv
    equipment_df = _load_csv("equipment_inspection.csv")
    _data_cache["equipment"] = equipment_df if equipment_df is not None else _generate_equipment_data()

    # 经济数据 - 对应 macro_economic.csv
    economic_df = _load_csv("macro_economic.csv")
    _data_cache["economic"] = economic_df if economic_df is not None else _generate_economic_data()

    # 飞线数据 - 对应 event_source_flow.csv
    flow_df = _load_csv("event_source_flow.csv")
    _data_cache["flow_lines"] = flow_df if flow_df is not None else _generate_flow_line_data()

    logger.info(f"数据加载完成，共缓存 {len(_data_cache)} 个数据集")
    for key, df in _data_cache.items():
        logger.info(f"  - {key}: {len(df)} 行, {len(df.columns)} 列")

    return _data_cache


def get_data(dataset_name: str) -> pd.DataFrame:
    """获取指定数据集的DataFrame"""
    if dataset_name not in _data_cache:
        logger.warning(f"数据集 '{dataset_name}' 未加载，尝试重新加载")
        load_all_data()
    return _data_cache.get(dataset_name, pd.DataFrame())


def get_all_data() -> dict[str, pd.DataFrame]:
    """获取所有缓存的数据集"""
    return _data_cache
