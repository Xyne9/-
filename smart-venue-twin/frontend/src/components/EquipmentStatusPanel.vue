<script setup>
/**
 * EquipmentStatusPanel - 设备健康状态面板
 * 展示各类设备的运行状态、告警信息
 */
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { EQUIPMENT_STATUS, EQUIPMENT_TYPES } from '../utils/constants'
import { fetchEquipmentStatus } from '../api/index'

const props = defineProps({
  // 设备数据（可选，不传则使用默认数据）
  data: {
    type: Array,
    default: null,
  },
})

// 设备列表数据
const equipmentList = ref([])

// 默认示例数据
const defaultEquipment = [
  { type: 'hvac', name: '空调系统-1号机组', status: 'normal', health: 95, lastCheck: '10分钟前' },
  { type: 'lighting', name: '照明系统-主场馆', status: 'normal', health: 92, lastCheck: '5分钟前' },
  { type: 'security', name: '安防系统-东区', status: 'warning', health: 72, lastCheck: '2分钟前' },
  { type: 'fire', name: '消防系统-全场馆', status: 'normal', health: 98, lastCheck: '1分钟前' },
  { type: 'elevator', name: '电梯系统-1号梯', status: 'error', health: 15, lastCheck: '刚刚' },
  { type: 'network', name: '网络设备-核心交换', status: 'normal', health: 88, lastCheck: '3分钟前' },
  { type: 'power', name: '供电系统-主配电', status: 'normal', health: 96, lastCheck: '8分钟前' },
  { type: 'water', name: '给排水系统-泵房', status: 'maintenance', health: 45, lastCheck: '30分钟前' },
]

// 初始化数据
onMounted(async () => {
  if (props.data) {
    equipmentList.value = props.data
  } else {
    // 尝试从API获取，失败则使用默认数据
    try {
      const data = await fetchEquipmentStatus()
      equipmentList.value = data
    } catch {
      equipmentList.value = defaultEquipment
    }
  }
})

/**
 * 获取设备类型信息
 */
function getTypeInfo(type) {
  return EQUIPMENT_TYPES.find((t) => t.type === type) || { label: type, icon: '📋' }
}

/**
 * 获取状态信息
 */
function getStatusInfo(status) {
  return EQUIPMENT_STATUS[status] || EQUIPMENT_STATUS.offline
}

/**
 * 健康度颜色
 */
function healthColor(health) {
  if (health >= 80) return 'var(--accent-teal)'
  if (health >= 60) return 'var(--accent-yellow)'
  if (health >= 30) return 'var(--accent-orange)'
  return 'var(--accent-red)'
}

/**
 * 健康度条宽度
 */
function healthWidth(health) {
  return `${Math.max(health, 2)}%`
}
</script>

<template>
  <div class="equipment-status-panel">
    <div
      v-for="(item, index) in equipmentList"
      :key="index"
      class="equipment-item"
    >
      <!-- 设备图标和名称 -->
      <div class="equipment-item__header">
        <span class="equipment-item__icon">{{ getTypeInfo(item.type).icon }}</span>
        <span class="equipment-item__name">{{ item.name }}</span>
        <span
          class="equipment-item__status"
          :style="{ color: getStatusInfo(item.status).color }"
        >
          ● {{ getStatusInfo(item.status).label }}
        </span>
      </div>

      <!-- 健康度进度条 -->
      <div class="equipment-item__health">
        <div class="health-bar">
          <div
            class="health-bar__fill"
            :style="{
              width: healthWidth(item.health),
              backgroundColor: healthColor(item.health),
            }"
          />
        </div>
        <span class="health-value" :style="{ color: healthColor(item.health) }">
          {{ item.health }}%
        </span>
      </div>

      <!-- 最后检查时间 -->
      <div class="equipment-item__meta">
        检查于 {{ item.lastCheck }}
      </div>
    </div>
  </div>
</template>

<style scoped>
.equipment-status-panel {
  display: flex;
  flex-direction: column;
  gap: 8px;
  overflow-y: auto;
  max-height: 100%;
  padding-right: 4px;
}

.equipment-item {
  padding: 8px 10px;
  background: rgba(13, 17, 53, 0.4);
  border: 1px solid rgba(0, 240, 255, 0.06);
  border-radius: var(--radius-md);
  transition: border-color 0.3s ease;
}

.equipment-item:hover {
  border-color: rgba(0, 240, 255, 0.15);
}

.equipment-item__header {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 6px;
}

.equipment-item__icon {
  font-size: 14px;
  flex-shrink: 0;
}

.equipment-item__name {
  font-size: 12px;
  color: var(--text-primary);
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.equipment-item__status {
  font-size: 11px;
  font-family: var(--font-mono);
  flex-shrink: 0;
}

.equipment-item__health {
  display: flex;
  align-items: center;
  gap: 8px;
}

.health-bar {
  flex: 1;
  height: 4px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 2px;
  overflow: hidden;
}

.health-bar__fill {
  height: 100%;
  border-radius: 2px;
  transition: width 0.6s ease, background-color 0.3s ease;
  box-shadow: 0 0 6px currentColor;
}

.health-value {
  font-size: 11px;
  font-family: var(--font-mono);
  min-width: 32px;
  text-align: right;
}

.equipment-item__meta {
  font-size: 10px;
  color: var(--text-muted);
  margin-top: 4px;
}
</style>
