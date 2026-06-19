#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
国家体育场（鸟巢）10年模拟数据生成脚本
生成5个CSV数据集，涵盖票务收入、客流交通、设备巡检、宏观经济、客源流向
所有数据遵循真实统计分布，包含季节性模式、COVID影响、数据间关联性
"""

import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import warnings

warnings.filterwarnings('ignore')

# ============================================================
# 全局配置
# ============================================================
SEED = 42
np.random.seed(SEED)

# 日期范围：2016-01-01 至 2025-12-31
START_DATE = datetime(2016, 1, 1)
END_DATE = datetime(2025, 12, 31)

# 鸟巢坐标
BIRD_NEST_LAT = 39.9929
BIRD_NEST_LNG = 116.3966

# 输出目录
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'raw')
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 活动类型及权重
EVENT_TYPES = ['演唱会', '体育赛事', '文化活动', '展览', '商业活动']
EVENT_WEIGHTS = [0.30, 0.25, 0.15, 0.18, 0.12]

# 季节名称映射
SEASON_MAP = {1: '冬', 2: '冬', 3: '春', 4: '春', 5: '春',
              6: '夏', 7: '夏', 8: '夏', 9: '秋', 10: '秋',
              11: '秋', 12: '冬'}

# 季节性乘子（按月份，1-12）—— 夏季为旺季
SEASONAL_MULTIPLIER = [0.65, 0.60, 0.75, 0.85, 0.95, 1.15,
                       1.30, 1.25, 1.05, 0.90, 0.75, 0.70]


# ============================================================
# 工具函数
# ============================================================
def covid_impact_factor(date):
    """
    根据日期返回COVID影响因子（0~1，1=无影响）
    2020 Q1-Q2: 严重封锁（0.05~0.15）
    2020 Q3-Q4: 部分恢复（0.3~0.5）
    2021: 波动恢复（0.4~0.7）
    2022: 局部封锁（0.5~0.75）
    2023起: 完全恢复
    """
    if date.year < 2020:
        return 1.0
    elif date.year == 2020:
        if date.month <= 2:
            return 0.15
        elif date.month <= 6:
            return 0.05
        elif date.month <= 9:
            return 0.30
        else:
            return 0.50
    elif date.year == 2021:
        if date.month <= 3:
            return 0.40
        elif date.month <= 6:
            return 0.55
        elif date.month <= 9:
            return 0.65
        else:
            return 0.70
    elif date.year == 2022:
        if date.month <= 3:
            return 0.55
        elif date.month <= 6:
            return 0.50  # 上海封控波及
        elif date.month <= 9:
            return 0.65
        else:
            return 0.75
    else:
        return 1.0


def covid_recovery_curve(date):
    """COVID后恢复曲线，2023-2025逐步超过2019水平"""
    if date.year < 2020:
        return 1.0
    elif date.year == 2023:
        return 0.85 + 0.15 * (date.month / 12)
    elif date.year == 2024:
        return 1.02 + 0.05 * (date.month / 12)
    elif date.year == 2025:
        return 1.08 + 0.03 * (date.month / 12)
    else:
        return covid_impact_factor(date)


def seasonal_factor(month):
    """返回月份对应的季节性因子"""
    return SEASONAL_MULTIPLIER[month - 1]


def trend_factor(year):
    """年度增长趋势因子（基准年2016=1.0）"""
    return 1.0 + (year - 2016) * 0.03  # 年均3%增长


def generate_date_range():
    """生成完整日期范围"""
    dates = []
    current = START_DATE
    while current <= END_DATE:
        dates.append(current)
        current += timedelta(days=1)
    return dates


# ============================================================
# 1. 票务收入数据生成
# ============================================================
def generate_ticket_revenue():
    """
    生成票务收入数据（2016-2025，按季度细分）
    包含：演唱会高票价、体育赛事多票量、季节性模式、COVID影响、恢复曲线
    """
    print("📊 正在生成票务收入数据...")

    # 活动名称模板
    event_name_templates = {
        '演唱会': [
            '周杰伦巡回演唱会', '林俊杰圣所演唱会', '张学友经典世界巡演',
            '五月天人生无限公司', '陈奕迅Fear and Dreams', '薛之谦天外来物巡演',
            '邓紫棋启示录巡演', '华晨宇火星演唱会', '李荣浩纵横四海巡演',
            '王力宏龙的传人巡演', '张杰未LIVE巡演', '毛不易小王巡演',
            '刘德华My Love巡演', '蔡依林Ugly Beauty巡演', '孙燕姿克卜勒巡演',
            'Taylor Swift世界巡演北京站', 'Ed Sheeran中国巡演', 'Coldplay北京演唱会',
            'BLACKPINK世界巡演北京站', 'BTS巡演北京站'
        ],
        '体育赛事': [
            '中国足协杯决赛', '中超联赛北京德比', '国际足球友谊赛',
            '世界田径锦标赛', '国际田联钻石联赛', '全国田径锦标赛',
            'NFL中国赛', 'NBA中国赛北京站', '意大利超级杯',
            '法国超级杯北京站', '国际马术大师赛', '世界斯诺克中国公开赛',
            '北京马拉松起点仪式', '全国运动会田径项目', '亚洲田径锦标赛'
        ],
        '文化活动': [
            '鸟巢新年音乐会', '春节文化庙会', '中秋赏月晚会',
            '国庆文艺汇演', '非遗文化展示周', '北京国际电影节开幕式',
            '央视春晚分会场', '冰雪文化节', '国潮音乐节',
            '中国传统文化周', '鸟巢光影秀', '世界文化遗产日庆典'
        ],
        '展览': [
            '国际汽车展览会', '北京国际科技博览会', '国际消费电子展',
            '国际航空航天展', '当代艺术大展', '国际设计周',
            '数字艺术沉浸展', '国际摄影大展', '全球创新科技展',
            '中国品牌日展览', '国际文创博览会', '未来生活体验展'
        ],
        '商业活动': [
            '品牌新品发布会', '企业年会盛典', '行业峰会论坛',
            '互联网大会开幕式', '金融峰会', '创业大赛总决赛',
            '品牌周年庆典', '明星代言签约仪式', '电商购物节开幕式',
            '科技产品首发仪式', '国际商务大会', '世界500强企业峰会'
        ]
    }

    # 各活动类型的票务参数
    event_params = {
        '演唱会': {
            'total_tickets_range': (40000, 80000),
            'sell_rate_range': (0.85, 0.98),
            'avg_price_range': (680, 2200),
            'vip_ratio': (0.08, 0.15),
            'merch_ratio': (0.12, 0.25),
            'sponsor_ratio': (0.08, 0.18)
        },
        '体育赛事': {
            'total_tickets_range': (60000, 91000),
            'sell_rate_range': (0.60, 0.92),
            'avg_price_range': (280, 880),
            'vip_ratio': (0.04, 0.10),
            'merch_ratio': (0.05, 0.12),
            'sponsor_ratio': (0.15, 0.30)
        },
        '文化活动': {
            'total_tickets_range': (30000, 65000),
            'sell_rate_range': (0.65, 0.90),
            'avg_price_range': (180, 680),
            'vip_ratio': (0.03, 0.08),
            'merch_ratio': (0.06, 0.15),
            'sponsor_ratio': (0.10, 0.22)
        },
        '展览': {
            'total_tickets_range': (20000, 50000),
            'sell_rate_range': (0.55, 0.85),
            'avg_price_range': (80, 380),
            'vip_ratio': (0.02, 0.06),
            'merch_ratio': (0.08, 0.18),
            'sponsor_ratio': (0.12, 0.25)
        },
        '商业活动': {
            'total_tickets_range': (5000, 25000),
            'sell_rate_range': (0.75, 0.95),
            'avg_price_range': (500, 3000),
            'vip_ratio': (0.10, 0.25),
            'merch_ratio': (0.03, 0.08),
            'sponsor_ratio': (0.25, 0.45)
        }
    }

    rows = []
    all_dates = generate_date_range()

    for date in all_dates:
        month = date.month
        year = date.year
        sf = seasonal_factor(month)
        tf = trend_factor(year)
        cf = covid_impact_factor(date)

        # 每天活动场次：受季节和COVID影响
        # 基础概率较高，且一天可能有多场活动
        base_event_prob = 0.65 * sf * cf * tf
        # 周末活动概率更高
        if date.weekday() >= 5:
            base_event_prob *= 1.4

        # 决定当天有几场活动（0~5场）
        num_events = np.random.poisson(lam=max(base_event_prob, 0.05))
        num_events = min(num_events, 5)  # 最多5场

        if num_events == 0:
            continue

        for _ in range(num_events):
            # 选择活动类型（加权随机）
            event_type = np.random.choice(EVENT_TYPES, p=EVENT_WEIGHTS)

            # 选择活动名称
            name_pool = event_name_templates[event_type]
            event_name = np.random.choice(name_pool)
            # 添加年份后缀使名称更真实
            if np.random.random() > 0.3:
                event_name = f"{year}{event_name}"

            params = event_params[event_type]

            # 总票数
            total_tickets = int(np.random.uniform(*params['total_tickets_range']) * sf * tf)
            total_tickets = max(total_tickets, 1000)

            # 售出票数（受COVID影响）
            sell_rate = np.random.uniform(*params['sell_rate_range']) * cf
            sell_rate = min(sell_rate, 0.99)
            sold_tickets = int(total_tickets * sell_rate)

            # 平均票价（演唱会最高，受年份通胀影响）
            inflation = 1.0 + (year - 2016) * 0.025  # 年均2.5%通胀
            avg_ticket_price = np.random.uniform(*params['avg_price_range']) * inflation * sf
            avg_ticket_price = round(avg_ticket_price, 2)

            # 总收入
            total_revenue = round(sold_tickets * avg_ticket_price, 2)

            # VIP收入
            vip_ratio = np.random.uniform(*params['vip_ratio'])
            vip_revenue = round(total_revenue * vip_ratio * np.random.uniform(2.5, 4.5), 2)

            # 周边商品收入
            merch_ratio = np.random.uniform(*params['merch_ratio'])
            merchandise_revenue = round(sold_tickets * avg_ticket_price * merch_ratio * 0.1, 2)

            # 赞助收入
            sponsor_ratio = np.random.uniform(*params['sponsor_ratio'])
            sponsor_revenue = round(total_revenue * sponsor_ratio, 2)

            quarter = (month - 1) // 3 + 1

            rows.append({
                'date': date.strftime('%Y-%m-%d'),
                'quarter': quarter,
                'year': year,
                'event_type': event_type,
                'event_name': event_name,
                'total_tickets': total_tickets,
                'sold_tickets': sold_tickets,
                'avg_ticket_price': avg_ticket_price,
                'total_revenue': total_revenue,
                'vip_revenue': vip_revenue,
                'merchandise_revenue': merchandise_revenue,
                'sponsor_revenue': sponsor_revenue
            })

    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(OUTPUT_DIR, 'ticket_revenue.csv'), index=False, encoding='utf-8-sig')
    print(f"  ✅ ticket_revenue.csv 已生成，共 {len(df)} 行")
    return df


# ============================================================
# 2. 每日客流交通数据生成
# ============================================================
def generate_daily_foot_traffic():
    """
    生成每日客流与交通数据
    包含：小时级模式（19-21点活动高峰）、周末/工作日差异、季节性、活动关联、COVID封锁
    """
    print("🚶 正在生成每日客流交通数据...")

    # 天气条件及权重（按季节）
    weather_by_season = {
        '春': {'晴': 0.40, '多云': 0.30, '阴': 0.15, '小雨': 0.10, '大风': 0.05},
        '夏': {'晴': 0.35, '多云': 0.25, '阴': 0.10, '大雨': 0.12, '雷暴': 0.08, '闷热': 0.10},
        '秋': {'晴': 0.45, '多云': 0.28, '阴': 0.12, '小雨': 0.10, '大风': 0.05},
        '冬': {'晴': 0.30, '多云': 0.25, '阴': 0.15, '小雪': 0.12, '大雪': 0.05, '大风': 0.08, '雾霾': 0.05}
    }

    # 温度范围（按月份，北京气候）
    temp_ranges = {
        1: (-12, 3), 2: (-8, 7), 3: (-1, 15), 4: (7, 24),
        5: (13, 30), 6: (18, 35), 7: (22, 38), 8: (20, 36),
        9: (14, 30), 10: (5, 22), 11: (-3, 12), 12: (-10, 5)
    }

    # 小时级客流模式（24小时分布）
    # 工作日模式
    weekday_hourly_pattern = np.array([
        0.02, 0.01, 0.01, 0.01, 0.01, 0.02,  # 0-5点
        0.03, 0.05, 0.06, 0.05, 0.04, 0.04,  # 6-11点
        0.05, 0.04, 0.04, 0.05, 0.06, 0.08,  # 12-17点
        0.10, 0.12, 0.10, 0.05, 0.03, 0.02   # 18-23点
    ])
    # 周末模式（更均匀，下午和晚上更多）
    weekend_hourly_pattern = np.array([
        0.01, 0.01, 0.01, 0.01, 0.01, 0.01,  # 0-5点
        0.02, 0.03, 0.04, 0.05, 0.06, 0.07,  # 6-11点
        0.07, 0.06, 0.06, 0.06, 0.06, 0.07,  # 12-17点
        0.08, 0.10, 0.08, 0.04, 0.02, 0.01   # 18-23点
    ])
    # 活动日模式（19-21点高峰）
    event_hourly_pattern = np.array([
        0.01, 0.01, 0.01, 0.00, 0.00, 0.01,  # 0-5点
        0.02, 0.03, 0.03, 0.03, 0.03, 0.03,  # 6-11点
        0.04, 0.04, 0.04, 0.05, 0.06, 0.08,  # 12-17点
        0.12, 0.18, 0.12, 0.04, 0.02, 0.01   # 18-23点
    ])

    # 关键小时（减少数据量但保留模式）
    key_hours = list(range(6, 24))  # 6点-23点

    rows = []
    all_dates = generate_date_range()

    for date in all_dates:
        month = date.month
        year = date.year
        season = SEASON_MAP[month]
        is_weekend = date.weekday() >= 5
        cf = covid_impact_factor(date)
        sf = seasonal_factor(month)
        tf = trend_factor(year)

        # 判断是否为活动日
        event_day_prob = 0.25 * sf * cf * tf
        if is_weekend:
            event_day_prob *= 1.5
        is_event_day = np.random.random() < min(event_day_prob, 0.7)
        event_type = np.random.choice(EVENT_TYPES, p=EVENT_WEIGHTS) if is_event_day else None

        # 天气
        weather_probs = weather_by_season[season]
        weather = np.random.choice(list(weather_probs.keys()), p=list(weather_probs.values()))

        # 温度
        t_min, t_max = temp_ranges[month]
        temperature = round(np.random.normal((t_min + t_max) / 2, (t_max - t_min) / 6), 1)
        temperature = np.clip(temperature, t_min - 3, t_max + 3)

        # 天气影响因子
        weather_impact = 1.0
        if weather in ('大雨', '大雪', '雷暴'):
            weather_impact = 0.5
        elif weather in ('小雨', '小雪', '雾霾'):
            weather_impact = 0.75
        elif weather == '大风':
            weather_impact = 0.85

        # 基础日客流量
        base_daily_visitors = 5000 * sf * tf * cf * weather_impact
        if is_event_day:
            base_daily_visitors *= np.random.uniform(3.0, 6.0)
        elif is_weekend:
            base_daily_visitors *= 1.8

        # 选择小时模式
        if is_event_day:
            hourly_pattern = event_hourly_pattern
        elif is_weekend:
            hourly_pattern = weekend_hourly_pattern
        else:
            hourly_pattern = weekday_hourly_pattern

        for hour in key_hours:
            # 该小时客流量
            hour_visitors = int(base_daily_visitors * hourly_pattern[hour] * np.random.uniform(0.8, 1.2))
            hour_visitors = max(hour_visitors, 0)

            # 各门客流分布（南门为主入口）
            gate_ratios = {'north_gate': 0.20, 'south_gate': 0.35, 'east_gate': 0.25, 'west_gate': 0.20}
            gate_visitors = {}
            for gate, ratio in gate_ratios.items():
                gate_visitors[gate] = int(hour_visitors * ratio * np.random.uniform(0.85, 1.15))

            # 交通数据
            transport_total = max(int(hour_visitors * np.random.uniform(0.6, 0.9)), 0)
            metro_ridership = int(transport_total * np.random.uniform(0.40, 0.55))
            bus_ridership = int(transport_total * np.random.uniform(0.15, 0.25))
            taxi_count = int(transport_total * np.random.uniform(0.08, 0.15))
            private_car_count = int(transport_total * np.random.uniform(0.10, 0.20))

            # 停车场占用率
            parking_occupancy_rate = round(np.random.uniform(0.3, 0.7) * sf * tf, 2)
            if is_event_day:
                parking_occupancy_rate = min(parking_occupancy_rate * np.random.uniform(1.5, 2.0), 0.98)
            parking_occupancy_rate = np.clip(parking_occupancy_rate, 0.05, 0.99)

            # 周边酒店均价
            hotel_base = 450 * tf * sf
            if is_event_day:
                hotel_base *= np.random.uniform(1.3, 2.0)
            nearby_hotel_avg_price = round(hotel_base * np.random.uniform(0.85, 1.15), 0)

            # 周边餐饮收入指数
            restaurant_base = 100 * sf * tf * cf
            if is_event_day:
                restaurant_base *= np.random.uniform(1.5, 2.5)
            nearby_restaurant_revenue_index = round(restaurant_base * np.random.uniform(0.8, 1.2), 1)

            rows.append({
                'date': date.strftime('%Y-%m-%d'),
                'hour': hour,
                'total_visitors': hour_visitors,
                'north_gate': gate_visitors['north_gate'],
                'south_gate': gate_visitors['south_gate'],
                'east_gate': gate_visitors['east_gate'],
                'west_gate': gate_visitors['west_gate'],
                'metro_ridership': metro_ridership,
                'bus_ridership': bus_ridership,
                'taxi_count': taxi_count,
                'private_car_count': private_car_count,
                'parking_occupancy_rate': parking_occupancy_rate,
                'nearby_hotel_avg_price': nearby_hotel_avg_price,
                'nearby_restaurant_revenue_index': nearby_restaurant_revenue_index,
                'weather_condition': weather,
                'temperature': temperature,
                'is_event_day': is_event_day,
                'event_type': event_type if event_type else ''
            })

    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(OUTPUT_DIR, 'daily_foot_traffic.csv'), index=False, encoding='utf-8-sig')
    print(f"  ✅ daily_foot_traffic.csv 已生成，共 {len(df)} 行")
    return df


# ============================================================
# 3. 设备巡检数据生成
# ============================================================
def generate_equipment_inspection():
    """
    生成设备与设施巡检数据
    包含：退化曲线、季节效应（夏季空调压力）、关联故障
    """
    print("🔧 正在生成设备巡检数据...")

    zones = ['A区', 'B区', 'C区', 'VIP区', '舞台区', '灯光区', '音响区', '安防区', '消防区', '电力区']

    # 各区域设备配置（每个区域8-12个设备）
    zone_equipment = {
        'A区': [
            ('座椅系统', '结构'), ('空调机组', '暖通'), ('照明系统', '电气'), ('消防喷淋', '消防'),
            ('监控摄像头', '安防'), ('通风管道', '暖通'), ('应急照明', '电气'), ('排水系统', '结构'),
            ('隔音墙板', '结构'), ('电子显示屏', '电气')
        ],
        'B区': [
            ('座椅系统', '结构'), ('空调机组', '暖通'), ('照明系统', '电气'), ('消防喷淋', '消防'),
            ('监控摄像头', '安防'), ('通风管道', '暖通'), ('应急照明', '电气'), ('排水系统', '结构'),
            ('隔音墙板', '结构'), ('电子显示屏', '电气')
        ],
        'C区': [
            ('座椅系统', '结构'), ('空调机组', '暖通'), ('照明系统', '电气'), ('消防喷淋', '消防'),
            ('监控摄像头', '安防'), ('通风管道', '暖通'), ('应急照明', '电气'), ('排水系统', '结构'),
            ('隔音墙板', '结构'), ('电子显示屏', '电气')
        ],
        'VIP区': [
            ('座椅系统', '结构'), ('空调机组', '暖通'), ('照明系统', '电气'), ('消防喷淋', '消防'),
            ('监控摄像头', '安防'), ('电梯系统', '运输'), ('通风管道', '暖通'), ('应急照明', '电气'),
            ('排水系统', '结构'), ('电子显示屏', '电气'), ('贵宾接待系统', '控制')
        ],
        '舞台区': [
            ('液压升降台', '机械'), ('舞台灯光', '电气'), ('音响系统', '电气'), ('烟雾机', '特效'),
            ('吊挂系统', '机械'), ('旋转舞台', '机械'), ('LED地屏', '电气'), ('舞台幕布', '结构'),
            ('线缆卷扬机', '机械'), ('舞台监控', '安防')
        ],
        '灯光区': [
            ('主灯阵列', '电气'), ('追光灯', '电气'), ('灯光控制台', '控制'), ('配电柜', '电气'),
            ('散热系统', '暖通'), ('特效灯', '电气'), ('激光投影', '电气'), ('灯光桁架', '结构'),
            ('调光器', '电气'), ('信号放大器', '通信')
        ],
        '音响区': [
            ('主扩音箱', '电气'), ('低音炮阵列', '电气'), ('调音台', '控制'), ('无线麦克风', '通信'),
            ('功放系统', '电气'), ('音频处理器', '控制'), ('返听音箱', '电气'), ('信号分配器', '通信'),
            ('录音系统', '控制'), ('降噪系统', '电气')
        ],
        '安防区': [
            ('视频监控', '安防'), ('门禁系统', '安防'), ('X光安检机', '安防'), ('金属探测器', '安防'),
            ('报警系统', '安防'), ('人脸识别终端', '安防'), ('巡更系统', '安防'), ('对讲系统', '通信'),
            ('防入侵传感器', '安防'), ('安防控制台', '控制')
        ],
        '消防区': [
            ('火灾报警器', '消防'), ('自动喷淋', '消防'), ('消防水泵', '机械'), ('排烟风机', '暖通'),
            ('灭火器组', '消防'), ('气体灭火系统', '消防'), ('消防广播', '通信'), ('防火卷帘', '结构'),
            ('消防电话', '通信'), ('应急照明', '电气')
        ],
        '电力区': [
            ('主变压器', '电气'), ('备用发电机', '机械'), ('UPS电源', '电气'), ('配电柜', '电气'),
            ('电缆线路', '电气'), ('稳压器', '电气'), ('电容补偿柜', '电气'), ('接地系统', '电气'),
            ('电力监控', '控制'), ('柴油储罐', '机械')
        ]
    }

    # 设备类型对应的健康分数参数
    equipment_health_params = {
        '结构': {'base_health': 92, 'degradation_rate': 0.8, 'variance': 5},
        '暖通': {'base_health': 85, 'degradation_rate': 1.5, 'variance': 8},
        '电气': {'base_health': 88, 'degradation_rate': 1.2, 'variance': 6},
        '消防': {'base_health': 90, 'degradation_rate': 0.6, 'variance': 4},
        '安防': {'base_health': 87, 'degradation_rate': 1.0, 'variance': 5},
        '机械': {'base_health': 82, 'degradation_rate': 2.0, 'variance': 10},
        '控制': {'base_health': 86, 'degradation_rate': 1.3, 'variance': 7},
        '通信': {'base_health': 84, 'degradation_rate': 1.4, 'variance': 8},
        '特效': {'base_health': 80, 'degradation_rate': 2.5, 'variance': 12},
        '运输': {'base_health': 83, 'degradation_rate': 1.8, 'variance': 9}
    }

    # 异常类型映射
    anomaly_types = {
        '结构': ['裂纹', '松动', '变形', '锈蚀', '疲劳'],
        '暖通': ['制冷不足', '异响', '漏水', '温控失灵', '压缩机故障'],
        '电气': ['电压异常', '过热', '短路', '接触不良', '绝缘老化'],
        '消防': ['灵敏度下降', '管路堵塞', '压力不足', '误报', '阀门卡滞'],
        '安防': ['画面模糊', '信号中断', '存储异常', '识别率下降', '网络延迟'],
        '机械': ['磨损', '异响', '振动异常', '密封泄漏', '轴承过热'],
        '控制': ['程序异常', '响应延迟', '参数漂移', '通信中断', '死机'],
        '通信': ['信号弱', '频率偏移', '干扰', '电池衰减', '天线故障'],
        '特效': ['喷嘴堵塞', '泵压不足', '雾化不良', '控制失灵', '耗材耗尽'],
        '运输': ['运行卡顿', '门禁故障', '钢丝绳磨损', '制动异常', '平层不准']
    }

    # 状态映射
    status_map = {
        (90, 100): '正常',
        (70, 90): '正常',
        (50, 70): '预警',
        (30, 50): '故障',
        (0, 30): '维修中'
    }

    # 风险等级映射
    risk_map = {
        (80, 100): '低',
        (60, 80): '低',
        (40, 60): '中',
        (20, 40): '高',
        (0, 20): '严重'
    }

    rows = []
    inspection_id = 1

    # 生成巡检日期（每周一次巡检，部分区域更频繁）
    inspection_dates = []
    current = START_DATE
    while current <= END_DATE:
        inspection_dates.append(current)
        current += timedelta(days=int(np.random.choice([5, 7, 9])))  # 约1周间隔

    for date in inspection_dates:
        month = date.month
        year = date.year
        sf = seasonal_factor(month)

        # 夏季暖通设备额外压力
        summer_hvac_stress = 1.0
        if month in (6, 7, 8):
            summer_hvac_stress = 1.5

        # 使用年限（鸟巢2008年建成，2016年已使用8年）
        years_since_build = year - 2008
        # 使用年限退化加速因子
        age_factor = 1.0 + (years_since_build - 8) * 0.05

        for zone in zones:
            for equip_name, equip_type in zone_equipment[zone]:
                params = equipment_health_params[equip_type]

                # 计算健康分数（退化曲线）
                base = params['base_health']
                degradation = params['degradation_rate'] * age_factor

                # 随时间退化
                years_elapsed = (date - START_DATE).days / 365.25
                health = base - degradation * years_elapsed

                # 夏季暖通额外退化
                if equip_type == '暖通':
                    health -= (summer_hvac_stress - 1.0) * 10

                # 活动日额外磨损
                if np.random.random() < 0.3:
                    health -= np.random.uniform(1, 5)

                # 随机波动
                health += np.random.normal(0, params['variance'])

                # 维修后恢复（健康分数低于50时触发维修，恢复到80左右）
                if health < 50:
                    if np.random.random() < 0.7:  # 70%概率被修复
                        health = np.random.uniform(75, 88)

                health = int(np.clip(health, 5, 100))

                # 确定状态
                status = '正常'
                for (lo, hi), s in status_map.items():
                    if lo <= health < hi:
                        status = s
                        break
                if health >= 70:
                    status = '正常'

                # 确定风险等级
                risk = '低'
                for (lo, hi), r in risk_map.items():
                    if lo <= health < hi:
                        risk = r
                        break

                # 异常类型（仅当健康分数低于80时才可能产生异常）
                anomaly = ''
                if health < 80:
                    anomaly_prob = (80 - health) / 80
                    if np.random.random() < anomaly_prob:
                        anomaly = np.random.choice(anomaly_types[equip_type])

                # 上次维护日期（30-180天前）
                last_maint_days = np.random.randint(30, 180)
                last_maintenance_date = (date - timedelta(days=last_maint_days)).strftime('%Y-%m-%d')

                # 下次维护日期（30-90天后）
                next_maint_days = np.random.randint(30, 90)
                next_maintenance_date = (date + timedelta(days=next_maint_days)).strftime('%Y-%m-%d')

                # 温度读数
                temp_base = {'暖通': 45, '电气': 55, '机械': 60, '控制': 35, '其他': 30}
                temp_reading = round(np.random.normal(
                    temp_base.get(equip_type, 30) + (10 if month in (6, 7, 8) else 0),
                    8
                ), 1)

                # 振动读数
                vibration_base = {'机械': 4.5, '暖通': 3.0, '结构': 1.5, '其他': 2.0}
                vibration_reading = round(np.random.normal(
                    vibration_base.get(equip_type, 2.0),
                    0.8
                ), 2)

                # 功耗
                power_base = {'电气': 85, '暖通': 120, '灯光区': 95, '音响区': 75, '其他': 40}
                power_consumption = round(np.random.normal(
                    power_base.get(equip_type, 40) * sf,
                    15
                ), 1)

                # 预估剩余寿命（天）
                lifespan_base = {'结构': 3650, '暖通': 1825, '电气': 2190, '消防': 2555,
                                 '安防': 1460, '机械': 1095, '控制': 1278, '通信': 1095,
                                 '特效': 730, '运输': 1460}
                lifespan = int(lifespan_base.get(equip_type, 1460) * (health / 100) * np.random.uniform(0.7, 1.3))
                lifespan = max(lifespan, 30)

                rows.append({
                    'inspection_id': f'INS{inspection_id:06d}',
                    'date': date.strftime('%Y-%m-%d'),
                    'zone': zone,
                    'equipment_name': equip_name,
                    'equipment_type': equip_type,
                    'health_score': health,
                    'status': status,
                    'last_maintenance_date': last_maintenance_date,
                    'next_maintenance_date': next_maintenance_date,
                    'anomaly_type': anomaly,
                    'risk_level': risk,
                    'temperature_reading': temp_reading,
                    'vibration_reading': vibration_reading,
                    'power_consumption': power_consumption,
                    'estimated_lifespan_days': lifespan
                })
                inspection_id += 1

    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(OUTPUT_DIR, 'equipment_inspection.csv'), index=False, encoding='utf-8-sig')
    print(f"  ✅ equipment_inspection.csv 已生成，共 {len(df)} 行")
    return df


# ============================================================
# 4. 宏观经济数据生成
# ============================================================
def generate_macro_economic():
    """
    生成宏观经济关联数据（季度，2016-2025）
    包含：活动与地方经济关联、COVID影响、恢复模式
    """
    print("📈 正在生成宏观经济数据...")

    rows = []
    for year in range(2016, 2026):
        for quarter in range(1, 5):
            # 季度中间月份
            month = (quarter - 1) * 3 + 2
            date = datetime(year, month, 15)
            tf = trend_factor(year)
            cf = covid_impact_factor(date)
            sf = np.mean(SEASONAL_MULTIPLIER[(quarter - 1) * 3: quarter * 3])

            # GDP增长率（%）
            if year < 2020:
                gdp_growth = np.random.normal(6.5, 0.3)
            elif year == 2020:
                gdp_growth = np.random.normal(2.3 if quarter > 2 else -6.8, 0.5)
            elif year == 2021:
                gdp_growth = np.random.normal(8.4 if quarter <= 2 else 5.0, 0.4)
            elif year == 2022:
                gdp_growth = np.random.normal(3.0, 0.3)
            elif year == 2023:
                gdp_growth = np.random.normal(5.2, 0.3)
            else:
                gdp_growth = np.random.normal(4.8 + (year - 2024) * 0.1, 0.3)

            # CPI指数（2016=100基准）
            cpi_base = 100 + (year - 2016) * 2.5
            if year == 2020:
                cpi_base += 2.5  # 疫情初期通胀
            cpi_index = round(cpi_base + np.random.normal(0, 1.5), 1)

            # 旅游指数（2016=100基准）
            tourism_base = 100 * tf
            tourism_index = round(tourism_base * cf * np.random.uniform(0.92, 1.08), 1)

            # 酒店价格指数
            hotel_price_index = round(100 * tf * cf * sf * np.random.uniform(0.90, 1.10), 1)

            # 餐饮收入指数
            restaurant_revenue_index = round(100 * tf * cf * sf * np.random.uniform(0.88, 1.12), 1)

            # 交通需求指数
            transport_demand_index = round(100 * tf * cf * sf * np.random.uniform(0.90, 1.10), 1)

            # 活动数量（受季节和COVID影响）
            base_event_count = np.random.randint(15, 30) * sf
            event_count = max(int(base_event_count * cf * tf), 0)

            # 总收入（与活动数量和旅游指数相关）
            total_revenue = round(event_count * np.random.uniform(800, 2500) * (tourism_index / 100), 0)

            # 就业指数
            employment_base = 100 * tf
            if year == 2020:
                employment_base *= 0.88
            elif year == 2021:
                employment_base *= 0.93
            elif year == 2022:
                employment_base *= 0.96
            employment_index = round(employment_base * np.random.uniform(0.97, 1.03), 1)

            # 周边房地产指数
            real_estate_base = 100 * (1 + (year - 2016) * 0.06)
            if year == 2020:
                real_estate_base *= 0.95
            elif year == 2021:
                real_estate_base *= 0.98
            real_estate_nearby_index = round(real_estate_base * np.random.uniform(0.96, 1.04), 1)

            # 消费者信心指数
            confidence_base = 105 * tf
            if year == 2020:
                confidence_base *= 0.65
            elif year == 2021:
                confidence_base *= 0.78
            elif year == 2022:
                confidence_base *= 0.82
            elif year == 2023:
                confidence_base *= 0.90
            consumer_confidence_index = round(confidence_base * np.random.uniform(0.93, 1.07), 1)

            rows.append({
                'date': f'{year}-Q{quarter}',
                'quarter': quarter,
                'gdp_growth_rate': round(gdp_growth, 2),
                'cpi_index': cpi_index,
                'tourism_index': tourism_index,
                'hotel_price_index': hotel_price_index,
                'restaurant_revenue_index': restaurant_revenue_index,
                'transport_demand_index': transport_demand_index,
                'event_count': event_count,
                'total_revenue': total_revenue,
                'employment_index': employment_index,
                'real_estate_nearby_index': real_estate_nearby_index,
                'consumer_confidence_index': consumer_confidence_index
            })

    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(OUTPUT_DIR, 'macro_economic.csv'), index=False, encoding='utf-8-sig')
    print(f"  ✅ macro_economic.csv 已生成，共 {len(df)} 行")
    return df


# ============================================================
# 5. 客源流向数据生成
# ============================================================
def generate_event_source_flow():
    """
    生成客源流向数据（用于3D飞线可视化）
    包含50+中国城市作为客源地、距离衰减、主要城市贡献、季节性变化
    """
    print("✈️ 正在生成客源流向数据...")

    # 50+中国城市数据：城市名、省份、纬度、经度、人口(万)、GDP排名系数
    cities = [
        ('上海', '上海', 31.2304, 121.4737, 2487, 1.0),
        ('广州', '广东', 23.1291, 113.2644, 1868, 0.85),
        ('深圳', '广东', 22.5431, 114.0579, 1756, 0.90),
        ('成都', '四川', 30.5728, 104.0668, 2094, 0.70),
        ('重庆', '重庆', 29.4316, 106.9123, 3212, 0.60),
        ('杭州', '浙江', 30.2741, 120.1551, 1237, 0.75),
        ('武汉', '湖北', 30.5928, 114.3055, 1365, 0.65),
        ('南京', '江苏', 32.0603, 118.7969, 942, 0.72),
        ('天津', '天津', 39.3434, 117.3616, 1387, 0.68),
        ('苏州', '江苏', 31.2990, 120.5853, 1275, 0.70),
        ('西安', '陕西', 34.3416, 108.9398, 1295, 0.62),
        ('长沙', '湖南', 28.2282, 112.9388, 1024, 0.58),
        ('沈阳', '辽宁', 41.8057, 123.4315, 911, 0.50),
        ('青岛', '山东', 36.0671, 120.3826, 1007, 0.55),
        ('郑州', '河南', 34.7466, 113.6254, 1260, 0.58),
        ('大连', '辽宁', 38.9140, 121.6147, 745, 0.48),
        ('东莞', '广东', 23.0430, 113.7633, 1047, 0.52),
        ('宁波', '浙江', 29.8683, 121.5440, 954, 0.55),
        ('厦门', '福建', 24.4798, 118.0894, 528, 0.50),
        ('福州', '福建', 26.0745, 119.2965, 842, 0.48),
        ('合肥', '安徽', 31.8206, 117.2272, 937, 0.52),
        ('昆明', '云南', 25.0389, 102.7183, 846, 0.45),
        ('哈尔滨', '黑龙江', 45.8038, 126.5350, 1001, 0.40),
        ('济南', '山东', 36.6512, 116.9972, 920, 0.52),
        ('佛山', '广东', 23.0218, 113.1218, 950, 0.50),
        ('长春', '吉林', 43.8171, 125.3235, 907, 0.38),
        ('温州', '浙江', 28.0001, 120.6722, 957, 0.45),
        ('石家庄', '河北', 38.0428, 114.5149, 1103, 0.42),
        ('南宁', '广西', 22.8170, 108.3665, 874, 0.38),
        ('贵阳', '贵州', 26.6470, 106.6302, 599, 0.35),
        ('南昌', '江西', 28.6820, 115.8579, 644, 0.40),
        ('太原', '山西', 37.8706, 112.5489, 539, 0.38),
        ('烟台', '山东', 37.4638, 121.4479, 713, 0.42),
        ('无锡', '江苏', 31.4912, 120.3119, 746, 0.58),
        ('兰州', '甘肃', 36.0611, 103.8343, 436, 0.30),
        ('珠海', '广东', 22.2710, 113.5767, 244, 0.45),
        ('海口', '海南', 20.0440, 110.1999, 287, 0.35),
        ('呼和浩特', '内蒙古', 40.8422, 111.7491, 345, 0.28),
        ('乌鲁木齐', '新疆', 43.7930, 87.6168, 405, 0.25),
        ('拉萨', '西藏', 29.6500, 91.1000, 87, 0.12),
        ('银川', '宁夏', 38.4872, 106.2309, 229, 0.22),
        ('西宁', '青海', 36.6171, 101.7782, 247, 0.20),
        ('保定', '河北', 38.8739, 115.4646, 924, 0.30),
        ('唐山', '河北', 39.6309, 118.1802, 772, 0.32),
        ('廊坊', '河北', 39.5246, 116.6839, 546, 0.35),  # 临近北京
        ('秦皇岛', '河北', 39.9354, 119.6006, 314, 0.28),
        ('张家口', '河北', 40.7675, 114.8867, 443, 0.25),  # 冬奥关联
        ('承德', '河北', 40.9510, 117.9632, 378, 0.22),
        ('常州', '江苏', 31.8106, 119.9741, 528, 0.45),
        ('徐州', '江苏', 34.2614, 117.1847, 908, 0.35),
        ('扬州', '江苏', 32.3942, 119.4126, 456, 0.38),
        ('绍兴', '浙江', 30.0000, 120.5833, 527, 0.42),
        ('嘉兴', '浙江', 30.7469, 120.7555, 540, 0.40),
        ('泉州', '福建', 24.8741, 118.6757, 879, 0.38),
        ('洛阳', '河南', 34.6197, 112.4540, 707, 0.32),
        ('桂林', '广西', 25.2742, 110.2992, 534, 0.30),
        ('三亚', '海南', 18.2528, 109.5120, 103, 0.35),
        ('中山', '广东', 22.5171, 113.3926, 442, 0.42),
        ('惠州', '广东', 23.1116, 114.4160, 604, 0.38),
        ('潍坊', '山东', 36.7069, 119.1619, 939, 0.30),
        ('临沂', '山东', 35.1041, 118.3564, 1102, 0.25),
        ('南通', '江苏', 31.9800, 120.8943, 773, 0.40),
        ('盐城', '江苏', 33.3478, 120.1615, 671, 0.28),
        ('台州', '浙江', 28.6563, 121.4208, 666, 0.35),
        ('金华', '浙江', 29.0795, 119.6495, 705, 0.38),
        ('漳州', '福建', 24.5128, 117.6471, 518, 0.30),
    ]

    # 交通方式权重（与距离相关）
    transport_modes = ['高铁', '飞机', '自驾', '大巴']

    def distance_to_beijing(lat, lng):
        """粗略计算到北京的距离（km）"""
        from math import radians, sin, cos, sqrt, atan2
        R = 6371
        dlat = radians(BIRD_NEST_LAT - lat)
        dlng = radians(BIRD_NEST_LNG - lng)
        a = sin(dlat / 2) ** 2 + cos(radians(lat)) * cos(radians(BIRD_NEST_LAT)) * sin(dlng / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        return R * c

    rows = []
    # 按周生成（保留时间粒度，同时增加数据量）
    current = START_DATE

    while current <= END_DATE:
        year = current.year
        month = current.month
        sf = seasonal_factor(month)
        tf = trend_factor(year)
        cf = covid_impact_factor(current)

        for city_name, province, lat, lng, population, gdp_rank in cities:
            # 计算到北京的距离
            distance = distance_to_beijing(lat, lng)

            # 距离衰减因子（指数衰减）
            distance_decay = np.exp(-distance / 1500)

            # 客流量 = 人口基数 * GDP排名 * 距离衰减 * 季节因子 * 趋势因子 * COVID因子
            # 按周计算，所以基数除以4
            base_visitors = population * gdp_rank * distance_decay * 0.5 / 4
            visitor_count = int(base_visitors * sf * tf * cf * np.random.uniform(0.7, 1.3))
            visitor_count = max(visitor_count, 0)

            # 如果该周无访客则跳过
            if visitor_count == 0:
                continue

            # 平均停留天数（近距离1-2天，远距离2-4天）
            avg_stay_days = round(np.random.uniform(1.0, 2.5) + distance / 2000 * 2, 1)
            avg_stay_days = min(avg_stay_days, 5.0)

            # 平均消费（与城市GDP排名和停留天数相关）
            avg_spending = round(
                (300 + gdp_rank * 500 + avg_stay_days * 200) * sf * tf * np.random.uniform(0.8, 1.2),
                0
            )

            # 交通方式选择（与距离相关）
            if distance < 300:
                transport_probs = [0.20, 0.05, 0.55, 0.20]
            elif distance < 800:
                transport_probs = [0.50, 0.15, 0.20, 0.15]
            elif distance < 1500:
                transport_probs = [0.35, 0.40, 0.10, 0.15]
            else:
                transport_probs = [0.15, 0.65, 0.05, 0.15]

            transport_mode = np.random.choice(transport_modes, p=transport_probs)

            rows.append({
                'date': current.strftime('%Y-%m-%d'),
                'source_city': city_name,
                'source_province': province,
                'source_lat': lat,
                'source_lng': lng,
                'visitor_count': visitor_count,
                'avg_stay_days': avg_stay_days,
                'avg_spending': avg_spending,
                'transport_mode': transport_mode,
                'dest_lat': BIRD_NEST_LAT,
                'dest_lng': BIRD_NEST_LNG
            })

        current += timedelta(days=7)

    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(OUTPUT_DIR, 'event_source_flow.csv'), index=False, encoding='utf-8-sig')
    print(f"  ✅ event_source_flow.csv 已生成，共 {len(df)} 行")
    return df


# ============================================================
# 主函数
# ============================================================
def main():
    print("=" * 60)
    print("🏟️  国家体育场（鸟巢）10年模拟数据生成器")
    print("=" * 60)
    print(f"📅 数据范围：2016-01-01 至 2025-12-31")
    print(f"📁 输出目录：{OUTPUT_DIR}")
    print(f"🎲 随机种子：{SEED}")
    print("-" * 60)

    # 生成各数据集
    df_ticket = generate_ticket_revenue()
    df_traffic = generate_daily_foot_traffic()
    df_equipment = generate_equipment_inspection()
    df_macro = generate_macro_economic()
    df_flow = generate_event_source_flow()

    print("-" * 60)
    print("📊 数据生成汇总：")
    print(f"  ticket_revenue.csv      : {len(df_ticket):>8,} 行")
    print(f"  daily_foot_traffic.csv  : {len(df_traffic):>8,} 行")
    print(f"  equipment_inspection.csv: {len(df_equipment):>8,} 行")
    print(f"  macro_economic.csv      : {len(df_macro):>8,} 行")
    print(f"  event_source_flow.csv   : {len(df_flow):>8,} 行")
    print("=" * 60)
    print("✅ 所有数据生成完毕！")


if __name__ == '__main__':
    main()
