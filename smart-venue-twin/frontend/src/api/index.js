/**
 * API请求层 - 智慧场馆数字孪生
 * 基于axios封装，统一管理所有后端接口
 */
import axios from 'axios'
import { API_PATHS } from '../utils/constants'

// 创建axios实例
const request = axios.create({
  baseURL: '/api',
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器 - 可添加token等认证信息
request.interceptors.request.use(
  (config) => {
    // 可在此添加token
    // const token = localStorage.getItem('token')
    // if (token) config.headers.Authorization = `Bearer ${token}`
    return config
  },
  (error) => {
    console.error('[API] 请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器 - 统一处理错误
request.interceptors.response.use(
  (response) => {
    const { data } = response
    // 如果后端返回统一格式 { code, data, message }
    if (data.code !== undefined && data.code !== 0 && data.code !== 200) {
      console.error('[API] 业务错误:', data.message)
      return Promise.reject(new Error(data.message || '请求失败'))
    }
    return data.data !== undefined ? data.data : data
  },
  (error) => {
    const msg = error.response?.data?.message || error.message || '网络异常'
    console.error('[API] 响应错误:', msg)
    return Promise.reject(error)
  }
)

// ========================================
// API接口函数
// ========================================

/**
 * 获取总览数据
 * @returns {Promise} 总览KPI数据
 */
export function fetchOverview() {
  return request.get(API_PATHS.OVERVIEW)
}

/**
 * 获取营收趋势数据
 * @param {object} params - 查询参数 { start_date, end_date, granularity }
 * @returns {Promise} 营收趋势时序数据
 */
export function fetchRevenueTrend(params) {
  return request.get(API_PATHS.REVENUE_TREND, { params })
}

/**
 * 获取营收分类数据
 * @returns {Promise} 各类型营收占比数据
 */
export function fetchRevenueByType() {
  return request.get(API_PATHS.REVENUE_BY_TYPE)
}

/**
 * 获取客流热力图数据
 * @returns {Promise} 场馆各区域客流密度数据
 */
export function fetchTrafficHeatmap() {
  return request.get(API_PATHS.TRAFFIC_HEATMAP)
}

/**
 * 获取客流流向线数据
 * @returns {Promise} 客流流动路径数据（用于飞线图）
 */
export function fetchTrafficFlowLines() {
  return request.get(API_PATHS.TRAFFIC_FLOW_LINES)
}

/**
 * 获取设备健康状态数据
 * @returns {Promise} 设备状态列表
 */
export function fetchEquipmentStatus() {
  return request.get(API_PATHS.EQUIPMENT_STATUS)
}

/**
 * 获取设备3D模型数据
 * @returns {Promise} 设备3D模型配置和位置数据
 */
export function fetchEquipment3DModel() {
  return request.get(API_PATHS.EQUIPMENT_3D_MODEL)
}

/**
 * 获取经济关联分析数据
 * @returns {Promise} 场馆经济影响关联数据
 */
export function fetchEconomicCorrelation() {
  return request.get(API_PATHS.ECONOMIC_CORRELATION)
}

/**
 * 获取周边酒店价格数据
 * @returns {Promise} 酒店价格时序数据
 */
export function fetchHotelPrice() {
  return request.get(API_PATHS.HOTEL_PRICE)
}

// 默认导出request实例，方便自定义请求
export default request
