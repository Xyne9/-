/**
 * 格式化工具函数
 * 提供数字、货币、百分比、日期等格式化方法
 */

/**
 * 格式化数字 - 添加千分位分隔符
 * @param {number} num - 要格式化的数字
 * @param {number} decimals - 保留小数位数，默认0
 * @returns {string} 格式化后的字符串
 */
export function formatNumber(num, decimals = 0) {
  if (num === null || num === undefined || isNaN(num)) return '--'
  const n = Number(num)
  return n.toLocaleString('zh-CN', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  })
}

/**
 * 格式化货币 - 添加人民币符号和千分位
 * @param {number} num - 金额
 * @param {number} decimals - 保留小数位数，默认2
 * @param {string} unit - 单位（万、亿等），默认空
 * @returns {string} 格式化后的货币字符串
 */
export function formatCurrency(num, decimals = 2, unit = '') {
  if (num === null || num === undefined || isNaN(num)) return '¥--'
  const n = Number(num)
  const formatted = n.toLocaleString('zh-CN', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  })
  return `¥${formatted}${unit}`
}

/**
 * 格式化货币 - 自动转换单位（万/亿）
 * @param {number} num - 金额
 * @returns {string} 格式化后的货币字符串
 */
export function formatCurrencyAuto(num) {
  if (num === null || num === undefined || isNaN(num)) return '¥--'
  const n = Number(num)
  if (n >= 100000000) {
    return `¥${(n / 100000000).toFixed(2)}亿`
  } else if (n >= 10000) {
    return `¥${(n / 10000).toFixed(2)}万`
  }
  return `¥${n.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
}

/**
 * 格式化百分比
 * @param {number} num - 数值（0-100 或 0-1）
 * @param {number} decimals - 保留小数位数，默认1
 * @param {boolean} isRatio - 是否为0-1的比率值，默认false
 * @returns {string} 格式化后的百分比字符串
 */
export function formatPercent(num, decimals = 1, isRatio = false) {
  if (num === null || num === undefined || isNaN(num)) return '--%'
  const n = isRatio ? Number(num) * 100 : Number(num)
  return `${n.toFixed(decimals)}%`
}

/**
 * 格式化日期
 * @param {Date|string|number} date - 日期
 * @param {string} format - 格式类型: 'full'|'date'|'time'|'datetime'|'short'
 * @returns {string} 格式化后的日期字符串
 */
export function formatDate(date, format = 'datetime') {
  if (!date) return '--'
  const d = date instanceof Date ? date : new Date(date)
  if (isNaN(d.getTime())) return '--'

  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  const hours = String(d.getHours()).padStart(2, '0')
  const minutes = String(d.getMinutes()).padStart(2, '0')
  const seconds = String(d.getSeconds()).padStart(2, '0')

  switch (format) {
    case 'full':
      return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
    case 'date':
      return `${year}-${month}-${day}`
    case 'time':
      return `${hours}:${minutes}:${seconds}`
    case 'short':
      return `${month}-${day} ${hours}:${minutes}`
    case 'datetime':
    default:
      return `${year}-${month}-${day} ${hours}:${minutes}`
  }
}

/**
 * 格式化文件大小
 * @param {number} bytes - 字节数
 * @returns {string} 格式化后的大小字符串
 */
export function formatFileSize(bytes) {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return `${(bytes / Math.pow(k, i)).toFixed(2)} ${sizes[i]}`
}

/**
 * 格式化持续时间（秒 -> 可读时间）
 * @param {number} seconds - 秒数
 * @returns {string} 格式化后的时间字符串
 */
export function formatDuration(seconds) {
  if (!seconds || seconds < 0) return '0秒'
  const h = Math.floor(seconds / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  const s = Math.floor(seconds % 60)
  if (h > 0) return `${h}小时${m}分${s}秒`
  if (m > 0) return `${m}分${s}秒`
  return `${s}秒`
}

/**
 * 格式化紧凑数字（如 1.2K, 3.5M）
 * @param {number} num - 数字
 * @returns {string} 紧凑格式字符串
 */
export function formatCompact(num) {
  if (num === null || num === undefined || isNaN(num)) return '--'
  const n = Number(num)
  if (n >= 100000000) return `${(n / 100000000).toFixed(1)}亿`
  if (n >= 10000) return `${(n / 10000).toFixed(1)}万`
  if (n >= 1000) return `${(n / 1000).toFixed(1)}K`
  return String(Math.round(n))
}
