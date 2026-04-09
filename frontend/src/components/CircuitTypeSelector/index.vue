<template>
  <div class="circuit-type-selector">
    <el-form-item label="回路类型" required>
      <el-select
        v-model="localValue"
        placeholder="请选择回路类型"
        @change="handleChange"
        style="width: 100%"
      >
        <el-option
          v-for="type in circuitTypes"
          :key="type.value"
          :label="type.label"
          :value="type.value"
        >
          <div class="circuit-option">
            <span class="circuit-label">{{ type.label }}</span>
            <span class="circuit-description">{{ type.description }}</span>
          </div>
        </el-option>
      </el-select>
    </el-form-item>

    <el-alert
      v-if="localValue"
      :title="`已选择：${selectedCircuitType?.label}`"
      type="success"
      :closable="false"
      style="margin-top: 10px"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { ElFormItem, ElSelect, ElOption, ElAlert } from 'element-plus'

const props = defineProps<{
  modelValue: string
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
  (e: 'change', value: string): void
}>()

const localValue = ref<string>(props.modelValue || '')

// 回路类型选项
const circuitTypes = [
  {
    value: '电机回路',
    label: '电机回路',
    description: '直接启动电机控制回路'
  },
  {
    value: '变频回路',
    label: '变频回路',
    description: '变频器控制电机回路'
  },
  {
    value: '三角降压回路',
    label: '三角降压回路',
    description: '星三角降压启动回路'
  },
  {
    value: '软启动回路',
    label: '软启动回路',
    description: '软启动器控制回路'
  },
  {
    value: '照明回路',
    label: '照明回路',
    description: '照明配电回路'
  },
  {
    value: '插座回路',
    label: '插座回路',
    description: '插座配电回路'
  },
  {
    value: '加热回路',
    label: '加热回路',
    description: '加热设备控制回路'
  },
  {
    value: '制冷回路',
    label: '制冷回路',
    description: '制冷设备控制回路'
  },
  {
    value: '通用控制回路',
    label: '通用控制回路',
    description: '其他通用控制回路'
  }
]

// 当前选中的回路类型
const selectedCircuitType = computed(() => {
  return circuitTypes.find(type => type.value === localValue.value)
})

const handleChange = () => {
  emit('update:modelValue', localValue.value)
  emit('change', localValue.value)
}

watch(
  () => props.modelValue,
  (newValue) => {
    if (newValue !== undefined) {
      localValue.value = newValue
    }
  }
)
</script>

<style scoped>
.circuit-type-selector {
  width: 100%;
}

.circuit-option {
  display: flex;
  flex-direction: column;
}

.circuit-label {
  font-weight: 500;
  color: #303133;
}

.circuit-description {
  font-size: 12px;
  color: #909399;
  margin-top: 2px;
}
</style>
