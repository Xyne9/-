#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智慧场馆数字孪生 - 数据清洗脚本
读取 raw/ 目录下5个CSV原始数据文件，执行清洗、标准化、派生列计算，
输出到 processed/ 目录，并打印数据质量报告。
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime

# ============================================================
# 路径配置
# ============================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DIR = os.path.join(BASE_DIR, 'raw')
PROCESSED_DIR = os.path.join(BASE_DIR, 'processed')

os.makedirs(PROCESSED_DIR, exist_ok=True)

# ============================================================
# 工具函数
# ============================================================

def load_csv(filename: str) -> pd.DataFrame:
    """读取CSV文件，处理BOM头"""
    filepath = os.path.join(RAW_DIR, filename)
    df = pd.read_csv(filepath, encoding='utf-8-sig')
    # 去除列名前后空白
    df.columns = df.columns.str.strip()
    print(f"  [读取] {filename}: {len(df)} 行, {len(df.columns)} 列")
    return df


def save_csv(df: pd.DataFrame, filename: str):
    """保存清洗后的CSV文件"""
    filepath = os.path.join(PROCESSED_DIR, filename)
    df.to_csv(filepath, index=False, encoding='utf-8-sig')
    print(f"  [保存] {filename}: {len(df)} 行, {len(df.columns)} 列")


def report_quality(df: pd.DataFrame, name: str):
    """打印单表数据质量报告"""
    print(f"\n{'='*60}")
    print(f"  数据质量报告: {name}")
    print(f"{'='*60}")
    print(f"  行数: {len(df)}")
    print(f"  列数: {len(df.columns)}")

    # 空值统计
    null_counts = df.isnull().sum()
    null_pct = (null_counts / len(df) * 100).round(2)
    null_info = pd.DataFrame({'空值数': null_counts, '空值占比%': null_pct})
    null_info = null_info[null_info['空值数'] > 0]
    if len(null_info) > 0:
        print(f"\n  空值分布:")
        print(null_info.to_string())
    else:
        print(f"\n  空值分布: 无空值")

    # 数值列范围
    print(f"\n  数值列范围:")
    for col in df.select_dtypes(include=[np.number]).columns:
        print(f"    {col}: [{df[col].min()}, {df[col].max()}]")

    # 重复行
    dup_count = df.duplicated().sum()
    print(f"\n  重复行数: {dup_count}")


# ============================================================
# 1. 票务收入数据清洗
# ============================================================
def clean_ticket_revenue(df: pd.DataFrame) -> pd.DataFrame:
    """清洗票务收入数据"""
    print("\n[清洗] ticket_revenue...")

    # --- 去除重复行 ---
    before = len(df)
    df = df.drop_duplicates()
    print(f"  去重: {before} -> {len(df)} (删除 {before - len(df)} 行)")

    # --- 日期类型转换 ---
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    # 删除无法解析的日期行
    invalid_dates = df['date'].isnull().sum()
    if invalid_dates > 0:
        print(f"  警告: {invalid_dates} 行日期无效，已删除")
        df = df.dropna(subset=['date'])

    # --- 数值列类型修正 ---
    numeric_cols = ['total_tickets', 'sold_tickets', 'avg_ticket_price',
                    'total_revenue', 'vip_revenue', 'merchandise_revenue', 'sponsor_revenue']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # --- 缺失值处理 ---
    # 数值列：用中位数填充
    for col in numeric_cols:
        if df[col].isnull().any():
            median_val = df[col].median()
            df[col] = df[col].fillna(median_val)
            print(f"  填充缺失值: {col} -> 中位数 {median_val}")

    # 分类列：用众数填充
    cat_cols = ['event_type', 'event_name']
    for col in cat_cols:
        if col in df.columns and df[col].isnull().any():
            mode_val = df[col].mode()[0]
            df[col] = df[col].fillna(mode_val)
            print(f"  填充缺失值: {col} -> 众数 '{mode_val}'")

    # --- 标准化分类值 ---
    df['event_type'] = df['event_type'].str.strip()
    # 统一活动类型名称
    event_type_mapping = {
        '演唱会': '演唱会',
        '体育赛事': '体育赛事',
        '文化活动': '文化活动',
        '展览': '展览',
        '商业活动': '商业活动',
    }
    df['event_type'] = df['event_type'].map(event_type_mapping).fillna(df['event_type'])
    df['event_name'] = df['event_name'].str.strip()

    # --- 数值范围校验 ---
    # 票数不能为负
    for col in ['total_tickets', 'sold_tickets']:
        df[col] = df[col].clip(lower=0)
    # 售出票数不能超过总票数
    df['sold_tickets'] = df[['sold_tickets', 'total_tickets']].min(axis=1)
    # 价格和收入不能为负
    for col in ['avg_ticket_price', 'total_revenue', 'vip_revenue',
                'merchandise_revenue', 'sponsor_revenue']:
        df[col] = df[col].clip(lower=0)

    # --- 派生列 ---
    # 年/月/季度（从日期派生，确保一致性）
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    df['quarter'] = df['date'].dt.quarter
    # 售票率
    df['sell_rate'] = np.where(
        df['total_tickets'] > 0,
        (df['sold_tickets'] / df['total_tickets']).round(4),
        0
    )
    # 人均收入（每张售出票的平均收入）
    df['revenue_per_ticket'] = np.where(
        df['sold_tickets'] > 0,
        (df['total_revenue'] / df['sold_tickets']).round(2),
        0
    )
    # VIP收入占比
    df['vip_revenue_ratio'] = np.where(
        df['total_revenue'] > 0,
        (df['vip_revenue'] / df['total_revenue']).round(4),
        0
    )
    # 赞助收入占比
    df['sponsor_revenue_ratio'] = np.where(
        df['total_revenue'] > 0,
        (df['sponsor_revenue'] / df['total_revenue']).round(4),
        0
    )
    # 是否周末活动
    df['is_weekend'] = df['date'].dt.weekday >= 5

    return df


# ============================================================
# 2. 客流交通数据清洗
# ============================================================
def clean_daily_foot_traffic(df: pd.DataFrame) -> pd.DataFrame:
    """清洗每日客流交通数据"""
    print("\n[清洗] daily_foot_traffic...")

    # --- 去除重复行 ---
    before = len(df)
    df = df.drop_duplicates()
    print(f"  去重: {before} -> {len(df)} (删除 {before - len(df)} 行)")

    # --- 日期类型转换 ---
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    invalid_dates = df['date'].isnull().sum()
    if invalid_dates > 0:
        print(f"  警告: {invalid_dates} 行日期无效，已删除")
        df = df.dropna(subset=['date'])

    # --- 数值列类型修正 ---
    numeric_cols = ['hour', 'total_visitors', 'north_gate', 'south_gate',
                    'east_gate', 'west_gate', 'metro_ridership', 'bus_ridership',
                    'taxi_count', 'private_car_count', 'parking_occupancy_rate',
                    'nearby_hotel_avg_price', 'nearby_restaurant_revenue_index', 'temperature']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # --- 缺失值处理 ---
    # 数值列用中位数填充
    for col in numeric_cols:
        if col in df.columns and df[col].isnull().any():
            median_val = df[col].median()
            df[col] = df[col].fillna(median_val)
            print(f"  填充缺失值: {col} -> 中位数 {median_val}")

    # 分类列用众数填充
    for col in ['weather_condition', 'event_type']:
        if col in df.columns and df[col].isnull().any():
            mode_val = df[col].mode()[0] if len(df[col].mode()) > 0 else ''
            df[col] = df[col].fillna(mode_val)
            print(f"  填充缺失值: {col} -> 众数 '{mode_val}'")

    # --- 标准化分类值 ---
    df['weather_condition'] = df['weather_condition'].str.strip()
    df['event_type'] = df['event_type'].str.strip()
    # 布尔列转换
    df['is_event_day'] = df['is_event_day'].map(
        {True: True, False: False, 'True': True, 'False': False, 'true': True, 'false': False}
    ).fillna(False)

    # --- 数值范围校验 ---
    # 小时范围 0-23
    df['hour'] = df['hour'].clip(0, 23).astype(int)
    # 客流数不能为负
    for col in ['total_visitors', 'north_gate', 'south_gate', 'east_gate', 'west_gate',
                'metro_ridership', 'bus_ridership', 'taxi_count', 'private_car_count']:
        if col in df.columns:
            df[col] = df[col].clip(lower=0).astype(int)
    # 停车场占用率范围 0-1
    df['parking_occupancy_rate'] = df['parking_occupancy_rate'].clip(0, 1)
    # 价格和指数不能为负
    for col in ['nearby_hotel_avg_price', 'nearby_restaurant_revenue_index']:
        if col in df.columns:
            df[col] = df[col].clip(lower=0)

    # --- 派生列 ---
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    df['quarter'] = df['date'].dt.quarter
    df['weekday'] = df['date'].dt.weekday  # 0=周一, 6=周日
    df['is_weekend'] = df['weekday'] >= 5
    # 各门客流占比
    df['north_gate_ratio'] = np.where(
        df['total_visitors'] > 0,
        (df['north_gate'] / df['total_visitors']).round(4),
        0
    )
    df['south_gate_ratio'] = np.where(
        df['total_visitors'] > 0,
        (df['south_gate'] / df['total_visitors']).round(4),
        0
    )
    # 公共交通占比
    df['public_transport_ratio'] = np.where(
        df['total_visitors'] > 0,
        ((df['metro_ridership'] + df['bus_ridership']) / df['total_visitors']).round(4),
        0
    )
    # 时间段分类
    def classify_time_period(hour):
        if 6 <= hour < 9:
            return '早高峰'
        elif 9 <= hour < 12:
            return '上午'
        elif 12 <= hour < 14:
            return '午间'
        elif 14 <= hour < 17:
            return '下午'
        elif 17 <= hour < 20:
            return '晚高峰'
        elif 20 <= hour < 23:
            return '晚间'
        else:
            return '深夜'
    df['time_period'] = df['hour'].apply(classify_time_period)

    return df


# ============================================================
# 3. 设备巡检数据清洗
# ============================================================
def clean_equipment_inspection(df: pd.DataFrame) -> pd.DataFrame:
    """清洗设备巡检数据"""
    print("\n[清洗] equipment_inspection...")

    # --- 去除重复行 ---
    before = len(df)
    df = df.drop_duplicates()
    print(f"  去重: {before} -> {len(df)} (删除 {before - len(df)} 行)")

    # --- 日期类型转换 ---
    for col in ['date', 'last_maintenance_date', 'next_maintenance_date']:
        df[col] = pd.to_datetime(df[col], errors='coerce')
    invalid_dates = df['date'].isnull().sum()
    if invalid_dates > 0:
        print(f"  警告: {invalid_dates} 行巡检日期无效，已删除")
        df = df.dropna(subset=['date'])

    # --- 数值列类型修正 ---
    numeric_cols = ['health_score', 'temperature_reading', 'vibration_reading',
                    'power_consumption', 'estimated_lifespan_days']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # --- 缺失值处理 ---
    # 数值列用中位数填充
    for col in numeric_cols:
        if col in df.columns and df[col].isnull().any():
            median_val = df[col].median()
            df[col] = df[col].fillna(median_val)
            print(f"  填充缺失值: {col} -> 中位数 {median_val}")

    # 分类列用众数或默认值填充
    for col in ['zone', 'equipment_name', 'equipment_type', 'status', 'risk_level']:
        if col in df.columns and df[col].isnull().any():
            mode_val = df[col].mode()[0] if len(df[col].mode()) > 0 else '未知'
            df[col] = df[col].fillna(mode_val)
            print(f"  填充缺失值: {col} -> 众数 '{mode_val}'")

    # 异常类型空值表示无异常，填充为空字符串
    df['anomaly_type'] = df['anomaly_type'].fillna('')
    # 巡检ID空值生成
    if df['inspection_id'].isnull().any():
        mask = df['inspection_id'].isnull()
        df.loc[mask, 'inspection_id'] = [f'INS{i:06d}' for i in range(mask.sum())]

    # --- 标准化分类值 ---
    df['zone'] = df['zone'].str.strip()
    df['equipment_name'] = df['equipment_name'].str.strip()
    df['equipment_type'] = df['equipment_type'].str.strip()
    df['status'] = df['status'].str.strip()
    df['risk_level'] = df['risk_level'].str.strip()
    df['anomaly_type'] = df['anomaly_type'].str.strip()

    # 统一状态名称
    status_mapping = {'正常': '正常', '预警': '预警', '故障': '故障', '维修中': '维修中'}
    df['status'] = df['status'].map(status_mapping).fillna(df['status'])
    # 统一风险等级
    risk_mapping = {'低': '低', '中': '中', '高': '高', '严重': '严重'}
    df['risk_level'] = df['risk_level'].map(risk_mapping).fillna(df['risk_level'])

    # --- 数值范围校验 ---
    # 健康分数范围 0-100
    df['health_score'] = df['health_score'].clip(0, 100)
    # 预估寿命不能为负
    df['estimated_lifespan_days'] = df['estimated_lifespan_days'].clip(lower=0)

    # --- 逻辑一致性校验 ---
    # 下次维护日期应晚于巡检日期
    invalid_maint = df['next_maintenance_date'] <= df['date']
    if invalid_maint.any():
        print(f"  警告: {invalid_maint.sum()} 行下次维护日期早于巡检日期，已修正为巡检后30天")
        df.loc[invalid_maint, 'next_maintenance_date'] = df.loc[invalid_maint, 'date'] + pd.Timedelta(days=30)

    # --- 派生列 ---
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    df['quarter'] = df['date'].dt.quarter
    # 距上次维护天数
    df['days_since_last_maintenance'] = (df['date'] - df['last_maintenance_date']).dt.days
    df['days_since_last_maintenance'] = df['days_since_last_maintenance'].clip(lower=0)
    # 距下次维护天数
    df['days_to_next_maintenance'] = (df['next_maintenance_date'] - df['date']).dt.days
    df['days_to_next_maintenance'] = df['days_to_next_maintenance'].clip(lower=0)
    # 健康等级分类
    def classify_health(score):
        if score >= 90:
            return '优秀'
        elif score >= 70:
            return '良好'
        elif score >= 50:
            return '一般'
        elif score >= 30:
            return '较差'
        else:
            return '危险'
    df['health_grade'] = df['health_score'].apply(classify_health)
    # 是否有异常
    df['has_anomaly'] = df['anomaly_type'] != ''

    return df


# ============================================================
# 4. 宏观经济数据清洗
# ============================================================
def clean_macro_economic(df: pd.DataFrame) -> pd.DataFrame:
    """清洗宏观经济数据"""
    print("\n[清洗] macro_economic...")

    # --- 去除重复行 ---
    before = len(df)
    df = df.drop_duplicates()
    print(f"  去重: {before} -> {len(df)} (删除 {before - len(df)} 行)")

    # --- 解析季度日期 ---
    # date 列格式为 "2016-Q1"，解析为该季度起始日期
    def parse_quarter_date(date_str):
        try:
            parts = str(date_str).split('-Q')
            year = int(parts[0])
            quarter = int(parts[1])
            month = (quarter - 1) * 3 + 1
            return pd.Timestamp(year=year, month=month, day=1)
        except (ValueError, IndexError):
            return pd.NaT

    df['date'] = df['date'].apply(parse_quarter_date)
    invalid_dates = df['date'].isnull().sum()
    if invalid_dates > 0:
        print(f"  警告: {invalid_dates} 行季度日期无效，已删除")
        df = df.dropna(subset=['date'])

    # --- 数值列类型修正 ---
    numeric_cols = ['quarter', 'gdp_growth_rate', 'cpi_index', 'tourism_index',
                    'hotel_price_index', 'restaurant_revenue_index',
                    'transport_demand_index', 'event_count', 'total_revenue',
                    'employment_index', 'real_estate_nearby_index',
                    'consumer_confidence_index']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # --- 缺失值处理 ---
    for col in numeric_cols:
        if col in df.columns and df[col].isnull().any():
            median_val = df[col].median()
            df[col] = df[col].fillna(median_val)
            print(f"  填充缺失值: {col} -> 中位数 {median_val}")

    # --- 数值范围校验 ---
    # 季度范围 1-4
    df['quarter'] = df['quarter'].clip(1, 4).astype(int)
    # 活动数量不能为负
    df['event_count'] = df['event_count'].clip(lower=0).astype(int)
    # 总收入不能为负
    df['total_revenue'] = df['total_revenue'].clip(lower=0)

    # --- 派生列 ---
    df['year'] = df['date'].dt.year
    # 季度标签
    df['quarter_label'] = df['year'].astype(str) + '-Q' + df['quarter'].astype(str)
    # 综合经济指数（加权平均）
    df['composite_economic_index'] = (
        df['gdp_growth_rate'] * 0.2 +
        df['tourism_index'] * 0.2 +
        df['consumer_confidence_index'] * 0.2 +
        df['employment_index'] * 0.2 +
        df['transport_demand_index'] * 0.2
    ).round(2)
    # 是否受COVID影响（2020-2022年）
    df['is_covid_period'] = df['year'].between(2020, 2022)

    return df


# ============================================================
# 5. 客源流向数据清洗
# ============================================================
def clean_event_source_flow(df: pd.DataFrame) -> pd.DataFrame:
    """清洗客源流向数据"""
    print("\n[清洗] event_source_flow...")

    # --- 去除重复行 ---
    before = len(df)
    df = df.drop_duplicates()
    print(f"  去重: {before} -> {len(df)} (删除 {before - len(df)} 行)")

    # --- 日期类型转换 ---
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    invalid_dates = df['date'].isnull().sum()
    if invalid_dates > 0:
        print(f"  警告: {invalid_dates} 行日期无效，已删除")
        df = df.dropna(subset=['date'])

    # --- 数值列类型修正 ---
    numeric_cols = ['source_lat', 'source_lng', 'visitor_count',
                    'avg_stay_days', 'avg_spending', 'dest_lat', 'dest_lng']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # --- 缺失值处理 ---
    for col in numeric_cols:
        if col in df.columns and df[col].isnull().any():
            median_val = df[col].median()
            df[col] = df[col].fillna(median_val)
            print(f"  填充缺失值: {col} -> 中位数 {median_val}")

    # 分类列
    for col in ['source_city', 'source_province', 'transport_mode']:
        if col in df.columns and df[col].isnull().any():
            mode_val = df[col].mode()[0] if len(df[col].mode()) > 0 else '未知'
            df[col] = df[col].fillna(mode_val)
            print(f"  填充缺失值: {col} -> 众数 '{mode_val}'")

    # --- 标准化分类值 ---
    df['source_city'] = df['source_city'].str.strip()
    df['source_province'] = df['source_province'].str.strip()
    df['transport_mode'] = df['transport_mode'].str.strip()

    # 统一交通方式名称
    transport_mapping = {'高铁': '高铁', '飞机': '飞机', '自驾': '自驾', '大巴': '大巴'}
    df['transport_mode'] = df['transport_mode'].map(transport_mapping).fillna(df['transport_mode'])

    # --- 数值范围校验 ---
    # 客流量不能为负
    df['visitor_count'] = df['visitor_count'].clip(lower=0).astype(int)
    # 停留天数和消费不能为负
    df['avg_stay_days'] = df['avg_stay_days'].clip(lower=0)
    df['avg_spending'] = df['avg_spending'].clip(lower=0)
    # 经纬度范围校验
    df['source_lat'] = df['source_lat'].clip(-90, 90)
    df['source_lng'] = df['source_lng'].clip(-180, 180)

    # --- 派生列 ---
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    df['quarter'] = df['date'].dt.quarter
    # 计算到鸟巢的距离（km，Haversine公式）
    def haversine(lat1, lng1, lat2, lng2):
        """计算两点间球面距离（km）"""
        R = 6371  # 地球半径
        lat1_rad = np.radians(lat1)
        lat2_rad = np.radians(lat2)
        dlat = np.radians(lat2 - lat1)
        dlng = np.radians(lng2 - lng1)
        a = np.sin(dlat / 2) ** 2 + np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(dlng / 2) ** 2
        c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
        return R * c

    df['distance_km'] = haversine(
        df['source_lat'], df['source_lng'],
        df['dest_lat'], df['dest_lng']
    ).round(1)
    # 总消费贡献 = 客流量 × 人均消费
    df['total_spending'] = (df['visitor_count'] * df['avg_spending']).round(2)
    # 客流等级
    def classify_visitor_count(count):
        if count >= 100:
            return '高'
        elif count >= 50:
            return '中'
        elif count >= 20:
            return '低'
        else:
            return '极少'
    df['visitor_level'] = df['visitor_count'].apply(classify_visitor_count)

    return df


# ============================================================
# 6. 跨表一致性校验
# ============================================================
def cross_validate(df_ticket: pd.DataFrame, df_traffic: pd.DataFrame,
                   df_equipment: pd.DataFrame, df_macro: pd.DataFrame,
                   df_flow: pd.DataFrame):
    """跨表一致性校验"""
    print("\n" + "=" * 60)
    print("  跨表一致性校验")
    print("=" * 60)

    # 获取各表日期范围
    ticket_dates = set(df_ticket['date'].dt.strftime('%Y-%m-%d'))
    traffic_dates = set(df_traffic['date'].dt.strftime('%Y-%m-%d'))
    equipment_dates = set(df_equipment['date'].dt.strftime('%Y-%m-%d'))
    flow_dates = set(df_flow['date'].dt.strftime('%Y-%m-%d'))

    # 票务与客流日期交集
    common_ticket_traffic = ticket_dates & traffic_dates
    print(f"\n  票务日期数: {len(ticket_dates)}")
    print(f"  客流日期数: {len(traffic_dates)}")
    print(f"  票务∩客流日期数: {len(common_ticket_traffic)}")

    # 票务活动日期应在客流数据中存在
    ticket_only = ticket_dates - traffic_dates
    if ticket_only:
        print(f"  警告: {len(ticket_only)} 个票务日期在客流表中无对应记录")
    else:
        print(f"  ✓ 票务活动日期与客流日期完全一致")

    # 设备巡检日期校验
    common_equip_traffic = equipment_dates & traffic_dates
    print(f"\n  设备巡检日期数: {len(equipment_dates)}")
    print(f"  设备∩客流日期数: {len(common_equip_traffic)}")

    # 宏观经济季度与票务季度一致性
    macro_quarters = set(df_macro['quarter_label'])
    ticket_quarters = set(df_ticket['date'].dt.to_period('Q').astype(str))
    print(f"\n  宏观经济季度数: {len(macro_quarters)}")
    print(f"  票务季度数: {len(ticket_quarters)}")
    print(f"  宏观经济∩票务季度数: {len(macro_quarters & ticket_quarters)}")

    # 客源流向日期校验
    common_flow_traffic = flow_dates & traffic_dates
    print(f"\n  客源流向日期数: {len(flow_dates)}")
    print(f"  客源流向∩客流日期数: {len(common_flow_traffic)}")


# ============================================================
# 主函数
# ============================================================
def main():
    print("=" * 60)
    print("  智慧场馆数字孪生 - 数据清洗流程")
    print("=" * 60)
    print(f"  原始数据目录: {RAW_DIR}")
    print(f"  输出目录: {PROCESSED_DIR}")
    print(f"  执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # ========== 读取原始数据 ==========
    print("\n" + "-" * 60)
    print("  第一步：读取原始数据")
    print("-" * 60)
    df_ticket = load_csv('ticket_revenue.csv')
    df_traffic = load_csv('daily_foot_traffic.csv')
    df_equipment = load_csv('equipment_inspection.csv')
    df_macro = load_csv('macro_economic.csv')
    df_flow = load_csv('event_source_flow.csv')

    # ========== 数据清洗 ==========
    print("\n" + "-" * 60)
    print("  第二步：数据清洗")
    print("-" * 60)
    df_ticket_clean = clean_ticket_revenue(df_ticket)
    df_traffic_clean = clean_daily_foot_traffic(df_traffic)
    df_equipment_clean = clean_equipment_inspection(df_equipment)
    df_macro_clean = clean_macro_economic(df_macro)
    df_flow_clean = clean_event_source_flow(df_flow)

    # ========== 跨表一致性校验 ==========
    cross_validate(df_ticket_clean, df_traffic_clean, df_equipment_clean,
                   df_macro_clean, df_flow_clean)

    # ========== 保存清洗后数据 ==========
    print("\n" + "-" * 60)
    print("  第三步：保存清洗后数据")
    print("-" * 60)
    save_csv(df_ticket_clean, 'ticket_revenue.csv')
    save_csv(df_traffic_clean, 'daily_foot_traffic.csv')
    save_csv(df_equipment_clean, 'equipment_inspection.csv')
    save_csv(df_macro_clean, 'macro_economic.csv')
    save_csv(df_flow_clean, 'event_source_flow.csv')

    # ========== 数据质量报告 ==========
    print("\n" + "-" * 60)
    print("  第四步：数据质量报告")
    print("-" * 60)
    report_quality(df_ticket_clean, 'ticket_revenue (票务收入)')
    report_quality(df_traffic_clean, 'daily_foot_traffic (客流交通)')
    report_quality(df_equipment_clean, 'equipment_inspection (设备巡检)')
    report_quality(df_macro_clean, 'macro_economic (宏观经济)')
    report_quality(df_flow_clean, 'event_source_flow (客源流向)')

    # ========== 汇总统计 ==========
    print("\n" + "=" * 60)
    print("  清洗汇总")
    print("=" * 60)
    datasets = {
        'ticket_revenue (票务收入)': df_ticket_clean,
        'daily_foot_traffic (客流交通)': df_traffic_clean,
        'equipment_inspection (设备巡检)': df_equipment_clean,
        'macro_economic (宏观经济)': df_macro_clean,
        'event_source_flow (客源流向)': df_flow_clean,
    }
    for name, df in datasets.items():
        print(f"  {name}: {len(df):>8,} 行, {len(df.columns):>3} 列")

    print("\n✅ 数据清洗流程完成！")


if __name__ == '__main__':
    main()
