-- ============================================================
-- 智慧场馆数字孪生 - 数据仓库分层架构
-- PostgreSQL 兼容
-- 架构: ODS -> DWD -> DWS -> ADS
-- ============================================================

-- ============================================================
-- ETL 总体说明:
--   ODS层: 原始数据1:1映射，不做任何清洗，保留完整原始痕迹
--   DWD层: 从ODS清洗、标准化、关联维度，生成统一的事实表和维度表
--   DWS层: 按业务主题对DWD事实表进行轻度汇总，面向分析场景
--   ADS层: 面向具体应用场景的高度聚合数据，直接服务前端可视化
-- ============================================================


-- ============================================================
-- ODS层 (Operational Data Store) - 原始数据层
-- 说明: 与源系统1:1映射，仅做类型转换，不做业务清洗
-- 加载策略: 全量覆盖 / 增量追加
-- ============================================================

-- ODS: 票务收入原始数据
CREATE TABLE IF NOT EXISTS ods_ticket_revenue (
    id              BIGSERIAL       PRIMARY KEY,    -- 自增主键
    date            DATE            NOT NULL,       -- 活动日期
    quarter         INTEGER,                        -- 季度(1-4)
    year            INTEGER,                        -- 年份
    event_type      VARCHAR(50),                    -- 活动类型
    event_name      VARCHAR(200),                   -- 活动名称
    total_tickets   INTEGER,                        -- 总票数
    sold_tickets    INTEGER,                        -- 售出票数
    avg_ticket_price NUMERIC(12,2),                 -- 平均票价
    total_revenue   NUMERIC(15,2),                  -- 总收入
    vip_revenue     NUMERIC(15,2),                  -- VIP收入
    merchandise_revenue NUMERIC(15,2),              -- 周边商品收入
    sponsor_revenue NUMERIC(15,2),                  -- 赞助收入
    etl_load_time   TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- ETL加载时间
);
COMMENT ON TABLE ods_ticket_revenue IS 'ODS层-票务收入原始数据';
COMMENT ON COLUMN ods_ticket_revenue.date IS '活动日期';
COMMENT ON COLUMN ods_ticket_revenue.quarter IS '季度(1-4)';
COMMENT ON COLUMN ods_ticket_revenue.year IS '年份';
COMMENT ON COLUMN ods_ticket_revenue.event_type IS '活动类型(演唱会/体育赛事/文化活动/展览/商业活动)';
COMMENT ON COLUMN ods_ticket_revenue.event_name IS '活动名称';
COMMENT ON COLUMN ods_ticket_revenue.total_tickets IS '总票数';
COMMENT ON COLUMN ods_ticket_revenue.sold_tickets IS '售出票数';
COMMENT ON COLUMN ods_ticket_revenue.avg_ticket_price IS '平均票价(元)';
COMMENT ON COLUMN ods_ticket_revenue.total_revenue IS '总收入(元)';
COMMENT ON COLUMN ods_ticket_revenue.vip_revenue IS 'VIP收入(元)';
COMMENT ON COLUMN ods_ticket_revenue.merchandise_revenue IS '周边商品收入(元)';
COMMENT ON COLUMN ods_ticket_revenue.sponsor_revenue IS '赞助收入(元)';
COMMENT ON COLUMN ods_ticket_revenue.etl_load_time IS 'ETL加载时间';

CREATE INDEX IF NOT EXISTS idx_ods_ticket_date ON ods_ticket_revenue(date);
CREATE INDEX IF NOT EXISTS idx_ods_ticket_event_type ON ods_ticket_revenue(event_type);


-- ODS: 每日客流交通原始数据
CREATE TABLE IF NOT EXISTS ods_daily_foot_traffic (
    id                          BIGSERIAL   PRIMARY KEY,    -- 自增主键
    date                        DATE        NOT NULL,       -- 日期
    hour                        INTEGER,                    -- 小时(0-23)
    total_visitors              INTEGER,                    -- 总客流量
    north_gate                  INTEGER,                    -- 北门客流
    south_gate                  INTEGER,                    -- 南门客流
    east_gate                   INTEGER,                    -- 东门客流
    west_gate                   INTEGER,                    -- 西门客流
    metro_ridership             INTEGER,                    -- 地铁客流
    bus_ridership               INTEGER,                    -- 公交客流
    taxi_count                  INTEGER,                    -- 出租车数
    private_car_count           INTEGER,                    -- 私家车数
    parking_occupancy_rate      NUMERIC(5,4),               -- 停车场占用率(0-1)
    nearby_hotel_avg_price      NUMERIC(10,2),              -- 周边酒店均价
    nearby_restaurant_revenue_index NUMERIC(8,2),           -- 周边餐饮收入指数
    weather_condition           VARCHAR(20),                -- 天气状况
    temperature                 NUMERIC(5,1),               -- 温度(℃)
    is_event_day                BOOLEAN,                    -- 是否活动日
    event_type                  VARCHAR(50),                -- 活动类型
    etl_load_time               TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON TABLE ods_daily_foot_traffic IS 'ODS层-每日客流交通原始数据';
COMMENT ON COLUMN ods_daily_foot_traffic.date IS '日期';
COMMENT ON COLUMN ods_daily_foot_traffic.hour IS '小时(0-23)';
COMMENT ON COLUMN ods_daily_foot_traffic.total_visitors IS '总客流量';
COMMENT ON COLUMN ods_daily_foot_traffic.north_gate IS '北门客流';
COMMENT ON COLUMN ods_daily_foot_traffic.south_gate IS '南门客流';
COMMENT ON COLUMN ods_daily_foot_traffic.east_gate IS '东门客流';
COMMENT ON COLUMN ods_daily_foot_traffic.west_gate IS '西门客流';
COMMENT ON COLUMN ods_daily_foot_traffic.metro_ridership IS '地铁客流';
COMMENT ON COLUMN ods_daily_foot_traffic.bus_ridership IS '公交客流';
COMMENT ON COLUMN ods_daily_foot_traffic.taxi_count IS '出租车数';
COMMENT ON COLUMN ods_daily_foot_traffic.private_car_count IS '私家车数';
COMMENT ON COLUMN ods_daily_foot_traffic.parking_occupancy_rate IS '停车场占用率(0-1)';
COMMENT ON COLUMN ods_daily_foot_traffic.nearby_hotel_avg_price IS '周边酒店均价(元)';
COMMENT ON COLUMN ods_daily_foot_traffic.nearby_restaurant_revenue_index IS '周边餐饮收入指数';
COMMENT ON COLUMN ods_daily_foot_traffic.weather_condition IS '天气状况';
COMMENT ON COLUMN ods_daily_foot_traffic.temperature IS '温度(℃)';
COMMENT ON COLUMN ods_daily_foot_traffic.is_event_day IS '是否活动日';
COMMENT ON COLUMN ods_daily_foot_traffic.event_type IS '活动类型';

CREATE INDEX IF NOT EXISTS idx_ods_traffic_date ON ods_daily_foot_traffic(date);
CREATE INDEX IF NOT EXISTS idx_ods_traffic_hour ON ods_daily_foot_traffic(hour);
CREATE INDEX IF NOT EXISTS idx_ods_traffic_event_day ON ods_daily_foot_traffic(is_event_day);


-- ODS: 设备巡检原始数据
CREATE TABLE IF NOT EXISTS ods_equipment_inspection (
    id                      BIGSERIAL       PRIMARY KEY,    -- 自增主键
    inspection_id           VARCHAR(20)     NOT NULL,       -- 巡检编号
    date                    DATE            NOT NULL,       -- 巡检日期
    zone                    VARCHAR(20),                    -- 区域
    equipment_name          VARCHAR(100),                   -- 设备名称
    equipment_type          VARCHAR(30),                    -- 设备类型
    health_score            INTEGER,                        -- 健康分数(0-100)
    status                  VARCHAR(20),                    -- 状态
    last_maintenance_date   DATE,                           -- 上次维护日期
    next_maintenance_date   DATE,                           -- 下次维护日期
    anomaly_type            VARCHAR(50),                    -- 异常类型
    risk_level              VARCHAR(10),                    -- 风险等级
    temperature_reading     NUMERIC(6,1),                   -- 温度读数
    vibration_reading       NUMERIC(5,2),                   -- 振动读数
    power_consumption       NUMERIC(8,1),                   -- 功耗
    estimated_lifespan_days INTEGER,                        -- 预估剩余寿命(天)
    etl_load_time           TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON TABLE ods_equipment_inspection IS 'ODS层-设备巡检原始数据';
COMMENT ON COLUMN ods_equipment_inspection.inspection_id IS '巡检编号';
COMMENT ON COLUMN ods_equipment_inspection.date IS '巡检日期';
COMMENT ON COLUMN ods_equipment_inspection.zone IS '区域(A区/B区/C区/VIP区/舞台区等)';
COMMENT ON COLUMN ods_equipment_inspection.equipment_name IS '设备名称';
COMMENT ON COLUMN ods_equipment_inspection.equipment_type IS '设备类型(结构/暖通/电气/消防/安防/机械/控制/通信/特效/运输)';
COMMENT ON COLUMN ods_equipment_inspection.health_score IS '健康分数(0-100)';
COMMENT ON COLUMN ods_equipment_inspection.status IS '状态(正常/预警/故障/维修中)';
COMMENT ON COLUMN ods_equipment_inspection.last_maintenance_date IS '上次维护日期';
COMMENT ON COLUMN ods_equipment_inspection.next_maintenance_date IS '下次维护日期';
COMMENT ON COLUMN ods_equipment_inspection.anomaly_type IS '异常类型';
COMMENT ON COLUMN ods_equipment_inspection.risk_level IS '风险等级(低/中/高/严重)';
COMMENT ON COLUMN ods_equipment_inspection.temperature_reading IS '温度读数(℃)';
COMMENT ON COLUMN ods_equipment_inspection.vibration_reading IS '振动读数';
COMMENT ON COLUMN ods_equipment_inspection.power_consumption IS '功耗(kW)';
COMMENT ON COLUMN ods_equipment_inspection.estimated_lifespan_days IS '预估剩余寿命(天)';

CREATE INDEX IF NOT EXISTS idx_ods_equip_date ON ods_equipment_inspection(date);
CREATE INDEX IF NOT EXISTS idx_ods_equip_zone ON ods_equipment_inspection(zone);
CREATE INDEX IF NOT EXISTS idx_ods_equip_type ON ods_equipment_inspection(equipment_type);


-- ODS: 宏观经济原始数据
CREATE TABLE IF NOT EXISTS ods_macro_economic (
    id                          BIGSERIAL   PRIMARY KEY,    -- 自增主键
    date                        DATE        NOT NULL,       -- 季度起始日期
    quarter                     INTEGER,                    -- 季度(1-4)
    gdp_growth_rate             NUMERIC(6,2),               -- GDP增长率(%)
    cpi_index                   NUMERIC(8,1),               -- CPI指数
    tourism_index               NUMERIC(8,1),               -- 旅游指数
    hotel_price_index           NUMERIC(8,1),               -- 酒店价格指数
    restaurant_revenue_index    NUMERIC(8,1),               -- 餐饮收入指数
    transport_demand_index      NUMERIC(8,1),               -- 交通需求指数
    event_count                 INTEGER,                    -- 活动数量
    total_revenue               NUMERIC(15,2),              -- 总收入
    employment_index            NUMERIC(8,1),               -- 就业指数
    real_estate_nearby_index    NUMERIC(8,1),               -- 周边房地产指数
    consumer_confidence_index   NUMERIC(8,1),               -- 消费者信心指数
    etl_load_time               TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON TABLE ods_macro_economic IS 'ODS层-宏观经济原始数据(季度)';
COMMENT ON COLUMN ods_macro_economic.date IS '季度起始日期';
COMMENT ON COLUMN ods_macro_economic.quarter IS '季度(1-4)';
COMMENT ON COLUMN ods_macro_economic.gdp_growth_rate IS 'GDP增长率(%)';
COMMENT ON COLUMN ods_macro_economic.cpi_index IS 'CPI指数(2016=100)';
COMMENT ON COLUMN ods_macro_economic.tourism_index IS '旅游指数';
COMMENT ON COLUMN ods_macro_economic.hotel_price_index IS '酒店价格指数';
COMMENT ON COLUMN ods_macro_economic.restaurant_revenue_index IS '餐饮收入指数';
COMMENT ON COLUMN ods_macro_economic.transport_demand_index IS '交通需求指数';
COMMENT ON COLUMN ods_macro_economic.event_count IS '活动数量';
COMMENT ON COLUMN ods_macro_economic.total_revenue IS '总收入(万元)';
COMMENT ON COLUMN ods_macro_economic.employment_index IS '就业指数';
COMMENT ON COLUMN ods_macro_economic.real_estate_nearby_index IS '周边房地产指数';
COMMENT ON COLUMN ods_macro_economic.consumer_confidence_index IS '消费者信心指数';

CREATE INDEX IF NOT EXISTS idx_ods_macro_date ON ods_macro_economic(date);


-- ODS: 客源流向原始数据
CREATE TABLE IF NOT EXISTS ods_event_source_flow (
    id                  BIGSERIAL       PRIMARY KEY,    -- 自增主键
    date                DATE            NOT NULL,       -- 日期
    source_city         VARCHAR(50),                    -- 来源城市
    source_province     VARCHAR(50),                    -- 来源省份
    source_lat          NUMERIC(9,4),                   -- 来源纬度
    source_lng          NUMERIC(10,4),                  -- 来源经度
    visitor_count       INTEGER,                        -- 客流量
    avg_stay_days       NUMERIC(4,1),                   -- 平均停留天数
    avg_spending        NUMERIC(10,2),                  -- 人均消费
    transport_mode      VARCHAR(20),                    -- 交通方式
    dest_lat            NUMERIC(9,4),                   -- 目的地纬度
    dest_lng            NUMERIC(10,4),                  -- 目的地经度
    etl_load_time       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON TABLE ods_event_source_flow IS 'ODS层-客源流向原始数据';
COMMENT ON COLUMN ods_event_source_flow.date IS '日期';
COMMENT ON COLUMN ods_event_source_flow.source_city IS '来源城市';
COMMENT ON COLUMN ods_event_source_flow.source_province IS '来源省份';
COMMENT ON COLUMN ods_event_source_flow.source_lat IS '来源纬度';
COMMENT ON COLUMN ods_event_source_flow.source_lng IS '来源经度';
COMMENT ON COLUMN ods_event_source_flow.visitor_count IS '客流量(人)';
COMMENT ON COLUMN ods_event_source_flow.avg_stay_days IS '平均停留天数';
COMMENT ON COLUMN ods_event_source_flow.avg_spending IS '人均消费(元)';
COMMENT ON COLUMN ods_event_source_flow.transport_mode IS '交通方式(高铁/飞机/自驾/大巴)';
COMMENT ON COLUMN ods_event_source_flow.dest_lat IS '目的地纬度(鸟巢)';
COMMENT ON COLUMN ods_event_source_flow.dest_lng IS '目的地经度(鸟巢)';

CREATE INDEX IF NOT EXISTS idx_ods_flow_date ON ods_event_source_flow(date);
CREATE INDEX IF NOT EXISTS idx_ods_flow_city ON ods_event_source_flow(source_city);


-- ============================================================
-- DWD层 (Data Warehouse Detail) - 清洗明细层
-- 说明: 从ODS清洗、标准化、关联维度键，形成统一事实表
-- ETL转换逻辑:
--   1. 去重、空值处理、类型标准化
--   2. 关联维度表生成维度外键
--   3. 派生列计算(售票率、人均收入等)
--   4. 数据范围校验(health_score 0-100, occupancy_rate 0-1)
-- ============================================================

-- ---- 维度表 ----

-- 维度表: 日期维度
-- ETL: 从所有事实表的日期字段中提取唯一日期，生成完整日期维度
CREATE TABLE IF NOT EXISTS dim_date (
    date_key        SERIAL      PRIMARY KEY,    -- 日期代理键
    date_value      DATE        NOT NULL UNIQUE,-- 日期
    year            INTEGER     NOT NULL,       -- 年
    quarter         INTEGER     NOT NULL,       -- 季度(1-4)
    month           INTEGER     NOT NULL,       -- 月(1-12)
    week_of_year    INTEGER,                    -- 年内第几周
    day_of_week     INTEGER,                    -- 周几(1=周一,7=周日)
    day_of_month    INTEGER,                    -- 月内第几天
    day_of_year     INTEGER,                    -- 年内第几天
    is_weekend      BOOLEAN     DEFAULT FALSE,  -- 是否周末
    is_holiday      BOOLEAN     DEFAULT FALSE,  -- 是否法定假日
    holiday_name    VARCHAR(50),                -- 假日名称
    season          VARCHAR(10),                -- 季节(春/夏/秋/冬)
    quarter_label   VARCHAR(7),                 -- 季度标签(如2016-Q1)
    month_label     VARCHAR(7)                  -- 月份标签(如2016-01)
);
COMMENT ON TABLE dim_date IS 'DWD层-日期维度表';
COMMENT ON COLUMN dim_date.date_key IS '日期代理键';
COMMENT ON COLUMN dim_date.date_value IS '日期';
COMMENT ON COLUMN dim_date.year IS '年';
COMMENT ON COLUMN dim_date.quarter IS '季度(1-4)';
COMMENT ON COLUMN dim_date.month IS '月(1-12)';
COMMENT ON COLUMN dim_date.week_of_year IS '年内第几周';
COMMENT ON COLUMN dim_date.day_of_week IS '周几(1=周一,7=周日)';
COMMENT ON COLUMN dim_date.day_of_month IS '月内第几天';
COMMENT ON COLUMN dim_date.day_of_year IS '年内第几天';
COMMENT ON COLUMN dim_date.is_weekend IS '是否周末';
COMMENT ON COLUMN dim_date.is_holiday IS '是否法定假日';
COMMENT ON COLUMN dim_date.holiday_name IS '假日名称';
COMMENT ON COLUMN dim_date.season IS '季节(春/夏/秋/冬)';
COMMENT ON COLUMN dim_date.quarter_label IS '季度标签(如2016-Q1)';
COMMENT ON COLUMN dim_date.month_label IS '月份标签(如2016-01)';

CREATE INDEX IF NOT EXISTS idx_dim_date_value ON dim_date(date_value);
CREATE INDEX IF NOT EXISTS idx_dim_date_year ON dim_date(year);
CREATE INDEX IF NOT EXISTS idx_dim_date_quarter ON dim_date(year, quarter);


-- 维度表: 活动类型维度
-- ETL: 从票务和客流表中提取唯一活动类型
CREATE TABLE IF NOT EXISTS dim_event_type (
    event_type_key  SERIAL      PRIMARY KEY,    -- 活动类型代理键
    event_type_code VARCHAR(20) NOT NULL UNIQUE,-- 活动类型编码
    event_type_name VARCHAR(50) NOT NULL,       -- 活动类型名称
    category        VARCHAR(30),                -- 大类(文化/体育/商业)
    avg_ticket_price_range VARCHAR(30),          -- 典型票价区间
    description     TEXT                         -- 描述
);
COMMENT ON TABLE dim_event_type IS 'DWD层-活动类型维度表';
COMMENT ON COLUMN dim_event_type.event_type_key IS '活动类型代理键';
COMMENT ON COLUMN dim_event_type.event_type_code IS '活动类型编码';
COMMENT ON COLUMN dim_event_type.event_type_name IS '活动类型名称';
COMMENT ON COLUMN dim_event_type.category IS '大类(文化/体育/商业)';
COMMENT ON COLUMN dim_event_type.avg_ticket_price_range IS '典型票价区间';
COMMENT ON COLUMN dim_event_type.description IS '描述';

-- 初始化活动类型数据
INSERT INTO dim_event_type (event_type_code, event_type_name, category, avg_ticket_price_range, description)
VALUES
    ('CONCERT', '演唱会', '文化', '680-2200元', '大型音乐演出活动'),
    ('SPORTS', '体育赛事', '体育', '280-880元', '体育竞技比赛活动'),
    ('CULTURE', '文化活动', '文化', '180-680元', '文化演艺和节庆活动'),
    ('EXHIBITION', '展览', '文化', '80-380元', '展览展示类活动'),
    ('BUSINESS', '商业活动', '商业', '500-3000元', '商业发布和会议活动')
ON CONFLICT (event_type_code) DO NOTHING;


-- 维度表: 区域维度（含3D坐标，用于数字孪生3D模型映射）
-- ETL: 从设备巡检表提取唯一区域，补充3D坐标和容量信息
CREATE TABLE IF NOT EXISTS dim_zone (
    zone_key        SERIAL      PRIMARY KEY,    -- 区域代理键
    zone_code       VARCHAR(20) NOT NULL UNIQUE,-- 区域编码
    zone_name       VARCHAR(50) NOT NULL,       -- 区域名称
    floor_level     INTEGER,                    -- 楼层
    coord_x         NUMERIC(8,2),               -- 3D模型X坐标
    coord_y         NUMERIC(8,2),               -- 3D模型Y坐标
    coord_z         NUMERIC(8,2),               -- 3D模型Z坐标
    max_capacity    INTEGER,                    -- 最大容量
    area_sqm        NUMERIC(10,2),              -- 面积(平方米)
    zone_type       VARCHAR(30)                 -- 区域类型(观众区/功能区/设备区)
);
COMMENT ON TABLE dim_zone IS 'DWD层-区域维度表(含3D坐标)';
COMMENT ON COLUMN dim_zone.zone_key IS '区域代理键';
COMMENT ON COLUMN dim_zone.zone_code IS '区域编码';
COMMENT ON COLUMN dim_zone.zone_name IS '区域名称';
COMMENT ON COLUMN dim_zone.floor_level IS '楼层';
COMMENT ON COLUMN dim_zone.coord_x IS '3D模型X坐标';
COMMENT ON COLUMN dim_zone.coord_y IS '3D模型Y坐标';
COMMENT ON COLUMN dim_zone.coord_z IS '3D模型Z坐标';
COMMENT ON COLUMN dim_zone.max_capacity IS '最大容量(人)';
COMMENT ON COLUMN dim_zone.area_sqm IS '面积(平方米)';
COMMENT ON COLUMN dim_zone.zone_type IS '区域类型(观众区/功能区/设备区)';

-- 初始化区域数据（含3D坐标，基于鸟巢实际布局）
INSERT INTO dim_zone (zone_code, zone_name, floor_level, coord_x, coord_y, coord_z, max_capacity, area_sqm, zone_type)
VALUES
    ('ZONE_A', 'A区', 1, -50.0, 0.0, 0.0, 20000, 8000.0, '观众区'),
    ('ZONE_B', 'B区', 1, 50.0, 0.0, 0.0, 20000, 8000.0, '观众区'),
    ('ZONE_C', 'C区', 1, 0.0, 60.0, 0.0, 20000, 8000.0, '观众区'),
    ('ZONE_VIP', 'VIP区', 2, 0.0, 0.0, 15.0, 5000, 3000.0, '观众区'),
    ('ZONE_STAGE', '舞台区', 1, 0.0, -40.0, 0.0, 2000, 2500.0, '功能区'),
    ('ZONE_LIGHT', '灯光区', 2, 0.0, -40.0, 25.0, 500, 800.0, '设备区'),
    ('ZONE_AUDIO', '音响区', 2, 0.0, -40.0, 20.0, 500, 800.0, '设备区'),
    ('ZONE_SECURITY', '安防区', 1, 0.0, 0.0, 5.0, 1000, 1500.0, '功能区'),
    ('ZONE_FIRE', '消防区', -1, 0.0, 0.0, -5.0, 500, 2000.0, '设备区'),
    ('ZONE_POWER', '电力区', -1, 60.0, 0.0, -5.0, 500, 1500.0, '设备区')
ON CONFLICT (zone_code) DO NOTHING;


-- 维度表: 城市维度（含经纬度，用于飞线可视化）
-- ETL: 从客源流向表提取唯一城市，补充省份和经纬度
CREATE TABLE IF NOT EXISTS dim_city (
    city_key        SERIAL      PRIMARY KEY,    -- 城市代理键
    city_name       VARCHAR(50) NOT NULL,       -- 城市名称
    province_name   VARCHAR(50),                -- 省份名称
    latitude        NUMERIC(9,4),               -- 纬度
    longitude       NUMERIC(10,4),              -- 经度
    gdp_rank        NUMERIC(4,2),               -- GDP排名系数
    is_municipality BOOLEAN DEFAULT FALSE,      -- 是否直辖市
    region          VARCHAR(20),                -- 所属区域(华北/华东/华南/华中/西南/西北/东北)
    UNIQUE(city_name, province_name)
);
COMMENT ON TABLE dim_city IS 'DWD层-城市维度表(含经纬度)';
COMMENT ON COLUMN dim_city.city_key IS '城市代理键';
COMMENT ON COLUMN dim_city.city_name IS '城市名称';
COMMENT ON COLUMN dim_city.province_name IS '省份名称';
COMMENT ON COLUMN dim_city.latitude IS '纬度';
COMMENT ON COLUMN dim_city.longitude IS '经度';
COMMENT ON COLUMN dim_city.gdp_rank IS 'GDP排名系数';
COMMENT ON COLUMN dim_city.is_municipality IS '是否直辖市';
COMMENT ON COLUMN dim_city.region IS '所属区域';

CREATE INDEX IF NOT EXISTS idx_dim_city_name ON dim_city(city_name);
CREATE INDEX IF NOT EXISTS idx_dim_city_province ON dim_city(province_name);


-- 维度表: 设备维度
-- ETL: 从设备巡检表提取唯一设备(区域+设备名称)，补充设备属性
CREATE TABLE IF NOT EXISTS dim_equipment (
    equipment_key       SERIAL      PRIMARY KEY,    -- 设备代理键
    equipment_code      VARCHAR(30) NOT NULL UNIQUE,-- 设备编码
    equipment_name      VARCHAR(100) NOT NULL,      -- 设备名称
    equipment_type      VARCHAR(30),                -- 设备类型
    zone_code           VARCHAR(20),                -- 所属区域编码
    install_date        DATE,                       -- 安装日期
    manufacturer        VARCHAR(100),               -- 制造商
    expected_lifespan_days INTEGER,                 -- 预期寿命(天)
    criticality         VARCHAR(10) DEFAULT '中',   -- 关键程度(高/中/低)
    FOREIGN KEY (zone_code) REFERENCES dim_zone(zone_code)
);
COMMENT ON TABLE dim_equipment IS 'DWD层-设备维度表';
COMMENT ON COLUMN dim_equipment.equipment_key IS '设备代理键';
COMMENT ON COLUMN dim_equipment.equipment_code IS '设备编码';
COMMENT ON COLUMN dim_equipment.equipment_name IS '设备名称';
COMMENT ON COLUMN dim_equipment.equipment_type IS '设备类型(结构/暖通/电气/消防/安防/机械/控制/通信/特效/运输)';
COMMENT ON COLUMN dim_equipment.zone_code IS '所属区域编码';
COMMENT ON COLUMN dim_equipment.install_date IS '安装日期';
COMMENT ON COLUMN dim_equipment.manufacturer IS '制造商';
COMMENT ON COLUMN dim_equipment.expected_lifespan_days IS '预期寿命(天)';
COMMENT ON COLUMN dim_equipment.criticality IS '关键程度(高/中/低)';

CREATE INDEX IF NOT EXISTS idx_dim_equip_type ON dim_equipment(equipment_type);
CREATE INDEX IF NOT EXISTS idx_dim_equip_zone ON dim_equipment(zone_code);


-- ---- 事实表 ----

-- DWD: 票务收入事实表
-- ETL转换逻辑:
--   从ods_ticket_revenue清洗: 去重 -> 日期转datetime -> 数值校验(非负) -> 标准化活动类型
--   关联dim_date生成date_key, 关联dim_event_type生成event_type_key
--   派生: sell_rate = sold_tickets/total_tickets, revenue_per_ticket = total_revenue/sold_tickets
CREATE TABLE IF NOT EXISTS dwd_ticket_revenue_fact (
    id                  BIGSERIAL       PRIMARY KEY,    -- 事实代理键
    date_key            INTEGER         NOT NULL,       -- 日期维度键
    event_type_key      INTEGER,                        -- 活动类型维度键
    date                DATE            NOT NULL,       -- 活动日期(冗余，便于查询)
    event_type          VARCHAR(50),                    -- 活动类型(冗余)
    event_name          VARCHAR(200),                   -- 活动名称
    total_tickets       INTEGER         NOT NULL,       -- 总票数
    sold_tickets        INTEGER         NOT NULL,       -- 售出票数
    avg_ticket_price    NUMERIC(12,2)   NOT NULL,       -- 平均票价
    total_revenue       NUMERIC(15,2)   NOT NULL,       -- 总收入
    vip_revenue         NUMERIC(15,2),                  -- VIP收入
    merchandise_revenue NUMERIC(15,2),                  -- 周边商品收入
    sponsor_revenue     NUMERIC(15,2),                  -- 赞助收入
    sell_rate           NUMERIC(6,4),                   -- 售票率
    revenue_per_ticket  NUMERIC(12,2),                  -- 人均收入
    vip_revenue_ratio   NUMERIC(6,4),                   -- VIP收入占比
    sponsor_revenue_ratio NUMERIC(6,4),                 -- 赞助收入占比
    is_weekend          BOOLEAN,                        -- 是否周末
    etl_load_time       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (date_key) REFERENCES dim_date(date_key),
    FOREIGN KEY (event_type_key) REFERENCES dim_event_type(event_type_key)
);
COMMENT ON TABLE dwd_ticket_revenue_fact IS 'DWD层-票务收入事实表(清洗后)';
COMMENT ON COLUMN dwd_ticket_revenue_fact.date_key IS '日期维度键';
COMMENT ON COLUMN dwd_ticket_revenue_fact.event_type_key IS '活动类型维度键';
COMMENT ON COLUMN dwd_ticket_revenue_fact.sell_rate IS '售票率';
COMMENT ON COLUMN dwd_ticket_revenue_fact.revenue_per_ticket IS '人均收入(元)';
COMMENT ON COLUMN dwd_ticket_revenue_fact.vip_revenue_ratio IS 'VIP收入占比';
COMMENT ON COLUMN dwd_ticket_revenue_fact.sponsor_revenue_ratio IS '赞助收入占比';

CREATE INDEX IF NOT EXISTS idx_dwd_ticket_date ON dwd_ticket_revenue_fact(date_key);
CREATE INDEX IF NOT EXISTS idx_dwd_ticket_event ON dwd_ticket_revenue_fact(event_type_key);
CREATE INDEX IF NOT EXISTS idx_dwd_ticket_date_col ON dwd_ticket_revenue_fact(date);


-- DWD: 客流事实表
-- ETL转换逻辑:
--   从ods_daily_foot_traffic清洗: 去重 -> 日期转datetime -> 数值校验(客流非负, 占用率0-1)
--   关联dim_date生成date_key, 标准化天气和活动类型
--   派生: public_transport_ratio, time_period, gate_ratio
CREATE TABLE IF NOT EXISTS dwd_traffic_fact (
    id                          BIGSERIAL   PRIMARY KEY,    -- 事实代理键
    date_key                    INTEGER     NOT NULL,       -- 日期维度键
    date                        DATE        NOT NULL,       -- 日期(冗余)
    hour                        INTEGER     NOT NULL,       -- 小时
    total_visitors              INTEGER     NOT NULL,       -- 总客流量
    north_gate                  INTEGER,                    -- 北门客流
    south_gate                  INTEGER,                    -- 南门客流
    east_gate                   INTEGER,                    -- 东门客流
    west_gate                   INTEGER,                    -- 西门客流
    metro_ridership             INTEGER,                    -- 地铁客流
    bus_ridership               INTEGER,                    -- 公交客流
    taxi_count                  INTEGER,                    -- 出租车数
    private_car_count           INTEGER,                    -- 私家车数
    parking_occupancy_rate      NUMERIC(5,4),               -- 停车场占用率(0-1)
    nearby_hotel_avg_price      NUMERIC(10,2),              -- 周边酒店均价
    nearby_restaurant_revenue_index NUMERIC(8,2),           -- 周边餐饮收入指数
    weather_condition           VARCHAR(20),                -- 天气状况
    temperature                 NUMERIC(5,1),               -- 温度
    is_event_day                BOOLEAN,                    -- 是否活动日
    event_type                  VARCHAR(50),                -- 活动类型
    public_transport_ratio      NUMERIC(6,4),               -- 公共交通占比
    time_period                 VARCHAR(10),                -- 时间段(早高峰/上午/午间/下午/晚高峰/晚间/深夜)
    is_weekend                  BOOLEAN,                    -- 是否周末
    etl_load_time               TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (date_key) REFERENCES dim_date(date_key)
);
COMMENT ON TABLE dwd_traffic_fact IS 'DWD层-客流事实表(清洗后)';
COMMENT ON COLUMN dwd_traffic_fact.parking_occupancy_rate IS '停车场占用率(0-1)';
COMMENT ON COLUMN dwd_traffic_fact.public_transport_ratio IS '公共交通占比';
COMMENT ON COLUMN dwd_traffic_fact.time_period IS '时间段分类';

CREATE INDEX IF NOT EXISTS idx_dwd_traffic_date ON dwd_traffic_fact(date_key);
CREATE INDEX IF NOT EXISTS idx_dwd_traffic_date_hour ON dwd_traffic_fact(date, hour);
CREATE INDEX IF NOT EXISTS idx_dwd_traffic_event ON dwd_traffic_fact(is_event_day);


-- DWD: 设备事实表
-- ETL转换逻辑:
--   从ods_equipment_inspection清洗: 去重 -> 日期转datetime -> health_score校验(0-100)
--   关联dim_date生成date_key, 关联dim_zone生成zone_key, 关联dim_equipment生成equipment_key
--   派生: days_since_last_maintenance, health_grade, has_anomaly
--   逻辑校验: next_maintenance_date > date
CREATE TABLE IF NOT EXISTS dwd_equipment_fact (
    id                          BIGSERIAL       PRIMARY KEY,    -- 事实代理键
    date_key                    INTEGER         NOT NULL,       -- 日期维度键
    equipment_key               INTEGER,                        -- 设备维度键
    zone_key                    INTEGER,                        -- 区域维度键
    inspection_id               VARCHAR(20)     NOT NULL,       -- 巡检编号
    date                        DATE            NOT NULL,       -- 巡检日期(冗余)
    zone                        VARCHAR(20),                    -- 区域(冗余)
    equipment_name              VARCHAR(100),                   -- 设备名称(冗余)
    equipment_type              VARCHAR(30),                    -- 设备类型(冗余)
    health_score                INTEGER         NOT NULL,       -- 健康分数(0-100)
    status                      VARCHAR(20),                    -- 状态
    last_maintenance_date       DATE,                           -- 上次维护日期
    next_maintenance_date       DATE,                           -- 下次维护日期
    anomaly_type                VARCHAR(50),                    -- 异常类型
    risk_level                  VARCHAR(10),                    -- 风险等级
    temperature_reading         NUMERIC(6,1),                   -- 温度读数
    vibration_reading           NUMERIC(5,2),                   -- 振动读数
    power_consumption           NUMERIC(8,1),                   -- 功耗
    estimated_lifespan_days     INTEGER,                        -- 预估剩余寿命
    days_since_last_maintenance INTEGER,                        -- 距上次维护天数
    health_grade                VARCHAR(10),                    -- 健康等级(优秀/良好/一般/较差/危险)
    has_anomaly                 BOOLEAN,                        -- 是否有异常
    etl_load_time               TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (date_key) REFERENCES dim_date(date_key),
    FOREIGN KEY (equipment_key) REFERENCES dim_equipment(equipment_key),
    FOREIGN KEY (zone_key) REFERENCES dim_zone(zone_key)
);
COMMENT ON TABLE dwd_equipment_fact IS 'DWD层-设备事实表(清洗后)';
COMMENT ON COLUMN dwd_equipment_fact.health_score IS '健康分数(0-100, 已校验)';
COMMENT ON COLUMN dwd_equipment_fact.days_since_last_maintenance IS '距上次维护天数';
COMMENT ON COLUMN dwd_equipment_fact.health_grade IS '健康等级(优秀/良好/一般/较差/危险)';
COMMENT ON COLUMN dwd_equipment_fact.has_anomaly IS '是否有异常';

CREATE INDEX IF NOT EXISTS idx_dwd_equip_date ON dwd_equipment_fact(date_key);
CREATE INDEX IF NOT EXISTS idx_dwd_equip_zone ON dwd_equipment_fact(zone_key);
CREATE INDEX IF NOT EXISTS idx_dwd_equip_health ON dwd_equipment_fact(health_score);
CREATE INDEX IF NOT EXISTS idx_dwd_equip_risk ON dwd_equipment_fact(risk_level);


-- DWD: 经济事实表
-- ETL转换逻辑:
--   从ods_macro_economic清洗: 去重 -> 解析季度日期 -> 数值校验
--   关联dim_date生成date_key
--   派生: composite_economic_index, is_covid_period
CREATE TABLE IF NOT EXISTS dwd_economic_fact (
    id                          BIGSERIAL   PRIMARY KEY,    -- 事实代理键
    date_key                    INTEGER     NOT NULL,       -- 日期维度键
    date                        DATE        NOT NULL,       -- 季度起始日期(冗余)
    quarter                     INTEGER     NOT NULL,       -- 季度
    gdp_growth_rate             NUMERIC(6,2),               -- GDP增长率
    cpi_index                   NUMERIC(8,1),               -- CPI指数
    tourism_index               NUMERIC(8,1),               -- 旅游指数
    hotel_price_index           NUMERIC(8,1),               -- 酒店价格指数
    restaurant_revenue_index    NUMERIC(8,1),               -- 餐饮收入指数
    transport_demand_index      NUMERIC(8,1),               -- 交通需求指数
    event_count                 INTEGER,                    -- 活动数量
    total_revenue               NUMERIC(15,2),              -- 总收入
    employment_index            NUMERIC(8,1),               -- 就业指数
    real_estate_nearby_index    NUMERIC(8,1),               -- 周边房地产指数
    consumer_confidence_index   NUMERIC(8,1),               -- 消费者信心指数
    composite_economic_index    NUMERIC(8,2),               -- 综合经济指数
    is_covid_period             BOOLEAN,                    -- 是否COVID影响期
    etl_load_time               TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (date_key) REFERENCES dim_date(date_key)
);
COMMENT ON TABLE dwd_economic_fact IS 'DWD层-经济事实表(清洗后, 季度)';
COMMENT ON COLUMN dwd_economic_fact.composite_economic_index IS '综合经济指数(加权平均)';
COMMENT ON COLUMN dwd_economic_fact.is_covid_period IS '是否COVID影响期(2020-2022)';

CREATE INDEX IF NOT EXISTS idx_dwd_economic_date ON dwd_economic_fact(date_key);
CREATE INDEX IF NOT EXISTS idx_dwd_economic_quarter ON dwd_economic_fact(date, quarter);


-- DWD: 客源流向事实表
-- ETL转换逻辑:
--   从ods_event_source_flow清洗: 去重 -> 日期转datetime -> 数值校验(客流非负, 经纬度范围)
--   关联dim_date生成date_key, 关联dim_city生成source_city_key
--   派生: distance_km(Haversine), total_spending, visitor_level
CREATE TABLE IF NOT EXISTS dwd_flow_fact (
    id                  BIGSERIAL       PRIMARY KEY,    -- 事实代理键
    date_key            INTEGER         NOT NULL,       -- 日期维度键
    source_city_key     INTEGER,                        -- 来源城市维度键
    date                DATE            NOT NULL,       -- 日期(冗余)
    source_city         VARCHAR(50),                    -- 来源城市(冗余)
    source_province     VARCHAR(50),                    -- 来源省份(冗余)
    source_lat          NUMERIC(9,4),                   -- 来源纬度
    source_lng          NUMERIC(10,4),                  -- 来源经度
    visitor_count       INTEGER         NOT NULL,       -- 客流量
    avg_stay_days       NUMERIC(4,1),                   -- 平均停留天数
    avg_spending        NUMERIC(10,2),                  -- 人均消费
    transport_mode      VARCHAR(20),                    -- 交通方式
    dest_lat            NUMERIC(9,4),                   -- 目的地纬度
    dest_lng            NUMERIC(10,4),                  -- 目的地经度
    distance_km         NUMERIC(8,1),                   -- 距离(km, Haversine计算)
    total_spending      NUMERIC(15,2),                  -- 总消费贡献
    visitor_level       VARCHAR(10),                    -- 客流等级(高/中/低/极少)
    etl_load_time       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (date_key) REFERENCES dim_date(date_key),
    FOREIGN KEY (source_city_key) REFERENCES dim_city(city_key)
);
COMMENT ON TABLE dwd_flow_fact IS 'DWD层-客源流向事实表(清洗后)';
COMMENT ON COLUMN dwd_flow_fact.distance_km IS '到鸟巢距离(km, Haversine公式计算)';
COMMENT ON COLUMN dwd_flow_fact.total_spending IS '总消费贡献(客流量×人均消费)';
COMMENT ON COLUMN dwd_flow_fact.visitor_level IS '客流等级(高/中/低/极少)';

CREATE INDEX IF NOT EXISTS idx_dwd_flow_date ON dwd_flow_fact(date_key);
CREATE INDEX IF NOT EXISTS idx_dwd_flow_city ON dwd_flow_fact(source_city_key);
CREATE INDEX IF NOT EXISTS idx_dwd_flow_province ON dwd_flow_fact(source_province);


-- ============================================================
-- DWS层 (Data Warehouse Summary) - 汇总层
-- 说明: 按业务主题对DWD事实表进行轻度汇总
-- ETL转换逻辑: 按维度分组聚合，计算汇总指标
-- ============================================================

-- DWS: 季度收入汇总
-- ETL: 从dwd_ticket_revenue_fact按year+quarter聚合
--   SUM(total_revenue), SUM(vip_revenue), SUM(merchandise_revenue), SUM(sponsor_revenue)
--   AVG(sell_rate), AVG(avg_ticket_price), COUNT活动场次
CREATE TABLE IF NOT EXISTS dws_revenue_by_quarter (
    id                  BIGSERIAL       PRIMARY KEY,
    year                INTEGER         NOT NULL,       -- 年
    quarter             INTEGER         NOT NULL,       -- 季度
    quarter_label       VARCHAR(7)      NOT NULL,       -- 季度标签
    event_count         INTEGER,                        -- 活动场次
    total_tickets       BIGINT,                         -- 总票数
    sold_tickets        BIGINT,                         -- 售出票数
    avg_sell_rate       NUMERIC(6,4),                   -- 平均售票率
    avg_ticket_price    NUMERIC(12,2),                  -- 平均票价
    total_revenue       NUMERIC(18,2),                  -- 总收入
    vip_revenue         NUMERIC(18,2),                  -- VIP收入
    merchandise_revenue NUMERIC(18,2),                  -- 周边商品收入
    sponsor_revenue     NUMERIC(18,2),                  -- 赞助收入
    revenue_yoy_growth  NUMERIC(8,4),                   -- 收入同比增长率
    etl_load_time       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(year, quarter)
);
COMMENT ON TABLE dws_revenue_by_quarter IS 'DWS层-季度收入汇总';
COMMENT ON COLUMN dws_revenue_by_quarter.event_count IS '活动场次';
COMMENT ON COLUMN dws_revenue_by_quarter.avg_sell_rate IS '平均售票率';
COMMENT ON COLUMN dws_revenue_by_quarter.revenue_yoy_growth IS '收入同比增长率';

CREATE INDEX IF NOT EXISTS idx_dws_rev_quarter ON dws_revenue_by_quarter(year, quarter);


-- DWS: 按活动类型收入汇总
-- ETL: 从dwd_ticket_revenue_fact按event_type聚合
--   可选时间范围过滤(年/季度)
CREATE TABLE IF NOT EXISTS dws_revenue_by_event_type (
    id                  BIGSERIAL       PRIMARY KEY,
    year                INTEGER         NOT NULL,       -- 年
    quarter             INTEGER,                        -- 季度(NULL表示全年)
    event_type          VARCHAR(50)     NOT NULL,       -- 活动类型
    event_count         INTEGER,                        -- 活动场次
    total_tickets       BIGINT,                         -- 总票数
    sold_tickets        BIGINT,                         -- 售出票数
    avg_sell_rate       NUMERIC(6,4),                   -- 平均售票率
    avg_ticket_price    NUMERIC(12,2),                  -- 平均票价
    total_revenue       NUMERIC(18,2),                  -- 总收入
    vip_revenue         NUMERIC(18,2),                  -- VIP收入
    merchandise_revenue NUMERIC(18,2),                  -- 周边商品收入
    sponsor_revenue     NUMERIC(18,2),                  -- 赞助收入
    revenue_share       NUMERIC(6,4),                   -- 收入占比
    etl_load_time       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(year, quarter, event_type)
);
COMMENT ON TABLE dws_revenue_by_event_type IS 'DWS层-按活动类型收入汇总';
COMMENT ON COLUMN dws_revenue_by_event_type.revenue_share IS '该类型收入占全部收入比例';

CREATE INDEX IF NOT EXISTS idx_dws_rev_event ON dws_revenue_by_event_type(year, event_type);


-- DWS: 日客流汇总
-- ETL: 从dwd_traffic_fact按date聚合, SUM(total_visitors), AVG(parking_occupancy_rate)等
CREATE TABLE IF NOT EXISTS dws_traffic_daily_summary (
    id                          BIGSERIAL   PRIMARY KEY,
    date                        DATE        NOT NULL UNIQUE, -- 日期
    year                        INTEGER     NOT NULL,        -- 年
    month                       INTEGER,                     -- 月
    quarter                     INTEGER,                     -- 季度
    is_weekend                  BOOLEAN,                     -- 是否周末
    is_event_day                BOOLEAN,                     -- 是否活动日
    total_visitors              INTEGER,                     -- 日总客流
    peak_hour                   INTEGER,                     -- 峰值小时
    peak_hour_visitors          INTEGER,                     -- 峰值小时客流
    avg_hourly_visitors         INTEGER,                     -- 平均小时客流
    north_gate_total            INTEGER,                     -- 北门日客流
    south_gate_total            INTEGER,                     -- 南门日客流
    east_gate_total             INTEGER,                     -- 东门日客流
    west_gate_total             INTEGER,                     -- 西门日客流
    metro_ridership_total       INTEGER,                     -- 地铁日客流
    bus_ridership_total         INTEGER,                     -- 公交日客流
    avg_parking_occupancy       NUMERIC(5,4),                -- 平均停车场占用率
    avg_hotel_price             NUMERIC(10,2),               -- 平均酒店价格
    avg_restaurant_index        NUMERIC(8,2),                -- 平均餐饮指数
    visitors_yoy_growth         NUMERIC(8,4),                -- 客流同比增长率
    etl_load_time               TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON TABLE dws_traffic_daily_summary IS 'DWS层-日客流汇总';
COMMENT ON COLUMN dws_traffic_daily_summary.peak_hour IS '当日峰值小时';
COMMENT ON COLUMN dws_traffic_daily_summary.peak_hour_visitors IS '峰值小时客流';
COMMENT ON COLUMN dws_traffic_daily_summary.visitors_yoy_growth IS '客流同比增长率';

CREATE INDEX IF NOT EXISTS idx_dws_traffic_date ON dws_traffic_daily_summary(date);
CREATE INDEX IF NOT EXISTS idx_dws_traffic_year ON dws_traffic_daily_summary(year, month);


-- DWS: 小时客流模式
-- ETL: 从dwd_traffic_fact按hour聚合(可跨日期范围), 计算各小时平均客流
CREATE TABLE IF NOT EXISTS dws_traffic_hourly_pattern (
    id                      BIGSERIAL   PRIMARY KEY,
    hour                    INTEGER     NOT NULL,       -- 小时(0-23)
    time_period             VARCHAR(10),                -- 时间段
    avg_visitors            NUMERIC(10,1),              -- 平均客流
    avg_visitors_weekday    NUMERIC(10,1),              -- 工作日平均客流
    avg_visitors_weekend    NUMERIC(10,1),              -- 周末平均客流
    avg_visitors_event      NUMERIC(10,1),              -- 活动日平均客流
    avg_north_gate          NUMERIC(10,1),              -- 北门平均客流
    avg_south_gate          NUMERIC(10,1),              -- 南门平均客流
    avg_east_gate           NUMERIC(10,1),              -- 东门平均客流
    avg_west_gate           NUMERIC(10,1),              -- 西门平均客流
    avg_metro_ridership     NUMERIC(10,1),              -- 平均地铁客流
    avg_bus_ridership       NUMERIC(10,1),              -- 平均公交客流
    avg_parking_occupancy   NUMERIC(5,4),               -- 平均停车场占用率
    visitor_ratio           NUMERIC(6,4),               -- 该小时客流占全天比例
    etl_load_time           TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(hour)
);
COMMENT ON TABLE dws_traffic_hourly_pattern IS 'DWS层-小时客流模式';
COMMENT ON COLUMN dws_traffic_hourly_pattern.time_period IS '时间段分类';
COMMENT ON COLUMN dws_traffic_hourly_pattern.visitor_ratio IS '该小时客流占全天比例';

CREATE INDEX IF NOT EXISTS idx_dws_hourly_hour ON dws_traffic_hourly_pattern(hour);


-- DWS: 设备健康汇总（按区域）
-- ETL: 从dwd_equipment_fact按zone+date聚合
--   AVG(health_score), 各状态设备数, 异常设备数
CREATE TABLE IF NOT EXISTS dws_equipment_health_summary (
    id                          BIGSERIAL   PRIMARY KEY,
    date                        DATE        NOT NULL,       -- 汇总日期
    zone                        VARCHAR(20) NOT NULL,       -- 区域
    equipment_count             INTEGER,                    -- 设备总数
    avg_health_score            NUMERIC(6,2),               -- 平均健康分数
    min_health_score            INTEGER,                    -- 最低健康分数
    normal_count                INTEGER,                    -- 正常设备数
    warning_count               INTEGER,                    -- 预警设备数
    fault_count                 INTEGER,                    -- 故障设备数
    maintenance_count           INTEGER,                    -- 维修中设备数
    anomaly_count               INTEGER,                    -- 异常设备数
    high_risk_count             INTEGER,                    -- 高风险设备数
    critical_risk_count         INTEGER,                    -- 严重风险设备数
    avg_temperature             NUMERIC(6,1),               -- 平均温度读数
    avg_vibration               NUMERIC(5,2),               -- 平均振动读数
    avg_power_consumption       NUMERIC(8,1),               -- 平均功耗
    avg_lifespan_days           INTEGER,                    -- 平均剩余寿命
    etl_load_time               TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(date, zone)
);
COMMENT ON TABLE dws_equipment_health_summary IS 'DWS层-设备健康汇总(按区域+日期)';
COMMENT ON COLUMN dws_equipment_health_summary.avg_health_score IS '平均健康分数';
COMMENT ON COLUMN dws_equipment_health_summary.anomaly_count IS '异常设备数';
COMMENT ON COLUMN dws_equipment_health_summary.high_risk_count IS '高风险设备数';

CREATE INDEX IF NOT EXISTS idx_dws_equip_date ON dws_equipment_health_summary(date);
CREATE INDEX IF NOT EXISTS idx_dws_equip_zone ON dws_equipment_health_summary(zone);


-- DWS: 按城市客源汇总
-- ETL: 从dwd_flow_fact按source_city+时间范围聚合
--   SUM(visitor_count), AVG(avg_spending), 主交通方式
CREATE TABLE IF NOT EXISTS dws_flow_by_city (
    id                      BIGSERIAL       PRIMARY KEY,
    year                    INTEGER         NOT NULL,       -- 年
    month                   INTEGER,                        -- 月(NULL表示全年)
    source_city             VARCHAR(50)     NOT NULL,       -- 来源城市
    source_province         VARCHAR(50),                    -- 来源省份
    source_lat              NUMERIC(9,4),                   -- 纬度
    source_lng              NUMERIC(10,4),                  -- 经度
    total_visitor_count     BIGINT,                         -- 总客流量
    avg_stay_days           NUMERIC(4,1),                   -- 平均停留天数
    avg_spending            NUMERIC(10,2),                  -- 人均消费
    total_spending          NUMERIC(18,2),                  -- 总消费贡献
    primary_transport       VARCHAR(20),                    -- 主要交通方式
    distance_km             NUMERIC(8,1),                   -- 距离(km)
    visitor_share           NUMERIC(6,4),                   -- 客流占比
    etl_load_time           TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(year, month, source_city)
);
COMMENT ON TABLE dws_flow_by_city IS 'DWS层-按城市客源汇总';
COMMENT ON COLUMN dws_flow_by_city.total_visitor_count IS '总客流量';
COMMENT ON COLUMN dws_flow_by_city.primary_transport IS '主要交通方式(客流最多)';
COMMENT ON COLUMN dws_flow_by_city.visitor_share IS '该城市客流占全部客流比例';

CREATE INDEX IF NOT EXISTS idx_dws_flow_city ON dws_flow_by_city(source_city);
CREATE INDEX IF NOT EXISTS idx_dws_flow_year ON dws_flow_by_city(year, month);


-- DWS: 季度经济指标汇总
-- ETL: 从dwd_economic_fact直接映射(已是季度粒度), 补充同比计算
CREATE TABLE IF NOT EXISTS dws_economic_quarterly (
    id                          BIGSERIAL   PRIMARY KEY,
    year                        INTEGER     NOT NULL,       -- 年
    quarter                     INTEGER     NOT NULL,       -- 季度
    quarter_label               VARCHAR(7)  NOT NULL,       -- 季度标签
    gdp_growth_rate             NUMERIC(6,2),               -- GDP增长率
    cpi_index                   NUMERIC(8,1),               -- CPI指数
    tourism_index               NUMERIC(8,1),               -- 旅游指数
    hotel_price_index           NUMERIC(8,1),               -- 酒店价格指数
    restaurant_revenue_index    NUMERIC(8,1),               -- 餐饮收入指数
    transport_demand_index      NUMERIC(8,1),               -- 交通需求指数
    event_count                 INTEGER,                    -- 活动数量
    total_revenue               NUMERIC(15,2),              -- 总收入
    employment_index            NUMERIC(8,1),               -- 就业指数
    real_estate_nearby_index    NUMERIC(8,1),               -- 周边房地产指数
    consumer_confidence_index   NUMERIC(8,1),               -- 消费者信心指数
    composite_economic_index    NUMERIC(8,2),               -- 综合经济指数
    is_covid_period             BOOLEAN,                    -- 是否COVID影响期
    gdp_yoy_change              NUMERIC(6,2),               -- GDP同比变化
    tourism_yoy_change          NUMERIC(6,2),               -- 旅游指数同比变化
    etl_load_time               TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(year, quarter)
);
COMMENT ON TABLE dws_economic_quarterly IS 'DWS层-季度经济指标汇总';
COMMENT ON COLUMN dws_economic_quarterly.composite_economic_index IS '综合经济指数(加权平均)';
COMMENT ON COLUMN dws_economic_quarterly.gdp_yoy_change IS 'GDP增长率同比变化(百分点)';
COMMENT ON COLUMN dws_economic_quarterly.tourism_yoy_change IS '旅游指数同比变化';

CREATE INDEX IF NOT EXISTS idx_dws_econ_quarter ON dws_economic_quarterly(year, quarter);


-- ============================================================
-- ADS层 (Application Data Store) - 应用层
-- 说明: 面向具体应用场景的高度聚合数据，直接服务前端可视化
-- ETL转换逻辑: 从DWS层进一步聚合计算，面向特定展示需求
-- ============================================================

-- ADS: 总览KPI看板
-- ETL: 从dws_revenue_by_quarter和dws_traffic_daily_summary聚合最新周期数据
--   计算同比、环比、目标完成率等KPI
CREATE TABLE IF NOT EXISTS ads_overview_kpi (
    id                          BIGSERIAL   PRIMARY KEY,
    kpi_date                    DATE        NOT NULL,       -- KPI统计日期
    period_type                 VARCHAR(10) NOT NULL,       -- 统计周期类型(日/周/月/季/年)
    total_revenue               NUMERIC(18,2),              -- 总收入
    revenue_yoy_growth          NUMERIC(8,4),               -- 收入同比增长率
    revenue_mom_growth          NUMERIC(8,4),               -- 收入环比增长率
    total_visitors              BIGINT,                     -- 总客流量
    visitors_yoy_growth         NUMERIC(8,4),               -- 客流同比增长率
    event_count                 INTEGER,                    -- 活动场次
    avg_sell_rate               NUMERIC(6,4),               -- 平均售票率
    avg_ticket_price            NUMERIC(12,2),              -- 平均票价
    avg_health_score            NUMERIC(6,2),               -- 平均设备健康分数
    fault_equipment_count       INTEGER,                    -- 故障设备数
    avg_parking_occupancy       NUMERIC(5,4),               -- 平均停车场占用率
    gdp_growth_rate             NUMERIC(6,2),               -- GDP增长率
    consumer_confidence_index   NUMERIC(8,1),               -- 消费者信心指数
    etl_load_time               TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(kpi_date, period_type)
);
COMMENT ON TABLE ads_overview_kpi IS 'ADS层-总览KPI看板数据';
COMMENT ON COLUMN ads_overview_kpi.period_type IS '统计周期类型(日/周/月/季/年)';
COMMENT ON COLUMN ads_overview_kpi.revenue_yoy_growth IS '收入同比增长率';
COMMENT ON COLUMN ads_overview_kpi.revenue_mom_growth IS '收入环比增长率';
COMMENT ON COLUMN ads_overview_kpi.visitors_yoy_growth IS '客流同比增长率';

CREATE INDEX IF NOT EXISTS idx_ads_kpi_date ON ads_overview_kpi(kpi_date);
CREATE INDEX IF NOT EXISTS idx_ads_kpi_period ON ads_overview_kpi(period_type);


-- ADS: 收入趋势（折线图数据）
-- ETL: 从dws_revenue_by_quarter提取时间序列，支持多维度下钻
CREATE TABLE IF NOT EXISTS ads_revenue_trend (
    id                  BIGSERIAL       PRIMARY KEY,
    year                INTEGER         NOT NULL,       -- 年
    quarter             INTEGER         NOT NULL,       -- 季度
    quarter_label       VARCHAR(7)      NOT NULL,       -- 季度标签
    event_type          VARCHAR(50),                    -- 活动类型(NULL=全部)
    total_revenue       NUMERIC(18,2),                  -- 总收入
    vip_revenue         NUMERIC(18,2),                  -- VIP收入
    merchandise_revenue NUMERIC(18,2),                  -- 周边商品收入
    sponsor_revenue     NUMERIC(18,2),                  -- 赞助收入
    event_count         INTEGER,                        -- 活动场次
    avg_ticket_price    NUMERIC(12,2),                  -- 平均票价
    sell_rate           NUMERIC(6,4),                   -- 售票率
    revenue_yoy_growth  NUMERIC(8,4),                   -- 同比增长率
    etl_load_time       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(year, quarter, event_type)
);
COMMENT ON TABLE ads_revenue_trend IS 'ADS层-收入趋势(折线图)';
COMMENT ON COLUMN ads_revenue_trend.event_type IS '活动类型(NULL=全部汇总)';

CREATE INDEX IF NOT EXISTS idx_ads_rev_trend ON ads_revenue_trend(year, quarter);
CREATE INDEX IF NOT EXISTS idx_ads_rev_event ON ads_revenue_trend(event_type);


-- ADS: 客流热力图数据
-- ETL: 从dwd_traffic_fact按date+hour聚合，生成热力图矩阵
--   X轴=小时, Y轴=日期/星期, 值=客流量
CREATE TABLE IF NOT EXISTS ads_traffic_heatmap (
    id                  BIGSERIAL   PRIMARY KEY,
    year                INTEGER     NOT NULL,       -- 年
    month               INTEGER     NOT NULL,       -- 月
    weekday             INTEGER     NOT NULL,       -- 星期(1=周一,7=周日)
    hour                INTEGER     NOT NULL,       -- 小时(0-23)
    avg_visitors        NUMERIC(10,1),              -- 平均客流量
    max_visitors        INTEGER,                    -- 最大客流量
    min_visitors        INTEGER,                    -- 最小客流量
    is_event_day_ratio  NUMERIC(5,2),               -- 活动日占比(%)
    etl_load_time       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(year, month, weekday, hour)
);
COMMENT ON TABLE ads_traffic_heatmap IS 'ADS层-客流热力图数据';
COMMENT ON COLUMN ads_traffic_heatmap.weekday IS '星期(1=周一,7=周日)';
COMMENT ON COLUMN ads_traffic_heatmap.is_event_day_ratio IS '活动日占比(%)';

CREATE INDEX IF NOT EXISTS idx_ads_heatmap_time ON ads_traffic_heatmap(year, month);
CREATE INDEX IF NOT EXISTS idx_ads_heatmap_weekday ON ads_traffic_heatmap(weekday, hour);


-- ADS: 设备3D状态数据（数字孪生3D模型叠加层）
-- ETL: 从dws_equipment_health_summary关联dim_zone获取3D坐标
--   用于3D模型中各区域颜色映射和告警标注
CREATE TABLE IF NOT EXISTS ads_equipment_3d_status (
    id                      BIGSERIAL   PRIMARY KEY,
    date                    DATE        NOT NULL,       -- 日期
    zone_code               VARCHAR(20) NOT NULL,       -- 区域编码
    zone_name               VARCHAR(50),                -- 区域名称
    coord_x                 NUMERIC(8,2),               -- 3D X坐标
    coord_y                 NUMERIC(8,2),               -- 3D Y坐标
    coord_z                 NUMERIC(8,2),               -- 3D Z坐标
    avg_health_score        NUMERIC(6,2),               -- 平均健康分数
    health_status           VARCHAR(10),                -- 健康状态(优秀/良好/一般/较差/危险)
    equipment_count         INTEGER,                    -- 设备总数
    normal_count            INTEGER,                    -- 正常设备数
    warning_count           INTEGER,                    -- 预警设备数
    fault_count             INTEGER,                    -- 故障设备数
    maintenance_count       INTEGER,                    -- 维修中设备数
    anomaly_count           INTEGER,                    -- 异常设备数
    high_risk_count         INTEGER,                    -- 高风险设备数
    avg_temperature         NUMERIC(6,1),               -- 平均温度
    avg_vibration           NUMERIC(5,2),               -- 平均振动
    avg_power_consumption   NUMERIC(8,1),               -- 平均功耗
    color_code              VARCHAR(7),                 -- 3D模型颜色(#RRGGBB, 根据健康分数映射)
    alert_level             INTEGER,                    -- 告警等级(0=正常,1=预警,2=故障,3=严重)
    etl_load_time           TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(date, zone_code)
);
COMMENT ON TABLE ads_equipment_3d_status IS 'ADS层-设备3D状态数据(数字孪生3D模型叠加)';
COMMENT ON COLUMN ads_equipment_3d_status.coord_x IS '3D模型X坐标';
COMMENT ON COLUMN ads_equipment_3d_status.coord_y IS '3D模型Y坐标';
COMMENT ON COLUMN ads_equipment_3d_status.coord_z IS '3D模型Z坐标';
COMMENT ON COLUMN ads_equipment_3d_status.color_code IS '3D模型颜色(#RRGGBB, 根据健康分数映射)';
COMMENT ON COLUMN ads_equipment_3d_status.alert_level IS '告警等级(0=正常,1=预警,2=故障,3=严重)';

CREATE INDEX IF NOT EXISTS idx_ads_3d_date ON ads_equipment_3d_status(date);
CREATE INDEX IF NOT EXISTS idx_ads_3d_zone ON ads_equipment_3d_status(zone_code);


-- ADS: 飞线可视化数据
-- ETL: 从dws_flow_by_city关联dim_city获取经纬度
--   聚合为城市->鸟巢的飞线数据，含客流量、消费、交通方式
CREATE TABLE IF NOT EXISTS ads_flow_fly_lines (
    id                      BIGSERIAL       PRIMARY KEY,
    year                    INTEGER         NOT NULL,       -- 年
    month                   INTEGER,                        -- 月(NULL=全年)
    source_city             VARCHAR(50)     NOT NULL,       -- 来源城市
    source_province         VARCHAR(50),                    -- 来源省份
    source_lat              NUMERIC(9,4),                   -- 来源纬度
    source_lng              NUMERIC(10,4),                  -- 来源经度
    dest_lat                NUMERIC(9,4)    DEFAULT 39.9929,-- 目的地纬度(鸟巢)
    dest_lng                NUMERIC(10,4)   DEFAULT 116.3966,-- 目的地经度(鸟巢)
    visitor_count           BIGINT,                         -- 客流量
    avg_stay_days           NUMERIC(4,1),                   -- 平均停留天数
    avg_spending            NUMERIC(10,2),                  -- 人均消费
    total_spending          NUMERIC(18,2),                  -- 总消费贡献
    primary_transport       VARCHAR(20),                    -- 主要交通方式
    distance_km             NUMERIC(8,1),                   -- 距离(km)
    line_width              INTEGER,                        -- 飞线宽度(根据客流量映射)
    line_color              VARCHAR(7),                     -- 飞线颜色(#RRGGBB, 根据消费映射)
    etl_load_time           TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(year, month, source_city)
);
COMMENT ON TABLE ads_flow_fly_lines IS 'ADS层-飞线可视化数据(城市->鸟巢)';
COMMENT ON COLUMN ads_flow_fly_lines.dest_lat IS '目的地纬度(鸟巢: 39.9929)';
COMMENT ON COLUMN ads_flow_fly_lines.dest_lng IS '目的地经度(鸟巢: 116.3966)';
COMMENT ON COLUMN ads_flow_fly_lines.line_width IS '飞线宽度(根据客流量映射)';
COMMENT ON COLUMN ads_flow_fly_lines.line_color IS '飞线颜色(#RRGGBB, 根据消费映射)';

CREATE INDEX IF NOT EXISTS idx_ads_fly_year ON ads_flow_fly_lines(year, month);
CREATE INDEX IF NOT EXISTS idx_ads_fly_city ON ads_flow_fly_lines(source_city);


-- ADS: 经济关联分析数据
-- ETL: 从dws_economic_quarterly和dws_revenue_by_quarter关联
--   计算收入与各经济指标的相关系数，用于散点图和关联分析
CREATE TABLE IF NOT EXISTS ads_economic_correlation (
    id                          BIGSERIAL   PRIMARY KEY,
    year                        INTEGER     NOT NULL,       -- 年
    quarter                     INTEGER     NOT NULL,       -- 季度
    quarter_label               VARCHAR(7)  NOT NULL,       -- 季度标签
    venue_revenue               NUMERIC(18,2),              -- 场馆收入
    gdp_growth_rate             NUMERIC(6,2),               -- GDP增长率
    cpi_index                   NUMERIC(8,1),               -- CPI指数
    tourism_index               NUMERIC(8,1),               -- 旅游指数
    hotel_price_index           NUMERIC(8,1),               -- 酒店价格指数
    restaurant_revenue_index    NUMERIC(8,1),               -- 餐饮收入指数
    transport_demand_index      NUMERIC(8,1),               -- 交通需求指数
    employment_index            NUMERIC(8,1),               -- 就业指数
    consumer_confidence_index   NUMERIC(8,1),               -- 消费者信心指数
    composite_economic_index    NUMERIC(8,2),               -- 综合经济指数
    is_covid_period             BOOLEAN,                    -- 是否COVID影响期
    revenue_to_tourism_ratio    NUMERIC(8,4),               -- 收入/旅游指数比
    revenue_to_confidence_ratio NUMERIC(8,4),               -- 收入/信心指数比
    etl_load_time               TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(year, quarter)
);
COMMENT ON TABLE ads_economic_correlation IS 'ADS层-经济关联分析数据';
COMMENT ON COLUMN ads_economic_correlation.venue_revenue IS '场馆季度收入';
COMMENT ON COLUMN ads_economic_correlation.revenue_to_tourism_ratio IS '收入/旅游指数比(衡量旅游对收入拉动)';
COMMENT ON COLUMN ads_economic_correlation.revenue_to_confidence_ratio IS '收入/信心指数比(衡量消费信心对收入影响)';

CREATE INDEX IF NOT EXISTS idx_ads_econ_year ON ads_economic_correlation(year, quarter);
CREATE INDEX IF NOT EXISTS idx_ads_econ_covid ON ads_economic_correlation(is_covid_period);


-- ============================================================
-- ETL 层间转换逻辑汇总
-- ============================================================
--
-- ODS -> DWD 转换规则:
--   1. 数据清洗: 去重、空值处理(数值列中位数填充, 分类列众数填充)
--   2. 类型标准化: 日期列转DATE/TIMESTAMP, 数值列转NUMERIC/INTEGER
--   3. 分类标准化: trim空白, 统一命名映射(event_type/status/risk_level)
--   4. 范围校验: health_score 0-100, parking_occupancy_rate 0-1, 客流/票数非负
--   5. 逻辑校验: sold_tickets <= total_tickets, next_maintenance_date > date
--   6. 维度关联: 生成date_key, event_type_key, zone_key, city_key, equipment_key
--   7. 派生列: sell_rate, revenue_per_ticket, distance_km, health_grade等
--
-- DWD -> DWS 转换规则:
--   1. 按业务维度分组聚合(年/季度/区域/城市/活动类型)
--   2. 计算汇总指标: SUM/COUNT/AVG/MIN/MAX
--   3. 同比/环比计算: 与上年同季度/上季度对比
--   4. 占比计算: revenue_share, visitor_share
--
-- DWS -> ADS 转换规则:
--   1. 面向应用场景高度聚合
--   2. 关联维度表补充可视化属性(3D坐标、颜色编码)
--   3. 计算可视化映射值: line_width, line_color, color_code, alert_level
--   4. 跨主题关联: 场馆收入与宏观经济指标关联分析
--
-- ============================================================
