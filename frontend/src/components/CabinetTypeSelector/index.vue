<template>
  <div class="cabinet-type-selector">
    <el-form-item label="控制大类" required>
      <el-select
        v-model="localValue.control_category"
        placeholder="请选择控制大类"
        @change="handleControlCategoryChange"
        style="width: 100%"
      >
        <el-option
          v-for="category in controlCategories"
          :key="category.value"
          :label="category.label"
          :value="category.value"
        />
      </el-select>
    </el-form-item>

    <el-form-item label="柜体类型" required>
      <el-select
        v-model="localValue.cabinet_type"
        placeholder="请选择柜体类型"
        :disabled="!localValue.control_category"
        @change="handleCabinetTypeChange"
        style="width: 100%"
      >
        <el-option
          v-for="type in availableCabinetTypes"
          :key="type.value"
          :label="type.label"
          :value="type.value"
        />
      </el-select>
    </el-form-item>

    <el-form-item label="控制结构" required>
      <el-select
        v-model="localValue.control_structure"
        placeholder="请选择控制结构"
        :disabled="!localValue.cabinet_type"
        @change="handleControlStructureChange"
        style="width: 100%"
      >
        <el-option
          v-for="structure in availableControlStructures"
          :key="structure.value"
          :label="structure.label"
          :value="structure.value"
        />
      </el-select>
    </el-form-item>

    <el-alert
      v-if="selectionComplete"
      :title="`已选择：${selectionSummary}`"
      type="success"
      :closable="false"
      style="margin-top: 10px"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { ElFormItem, ElSelect, ElOption, ElAlert } from 'element-plus'

interface CabinetTypeSelection {
  control_category: string
  cabinet_type: string
  control_structure: string
}

const props = defineProps<{
  modelValue: CabinetTypeSelection
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: CabinetTypeSelection): void
  (e: 'change', value: CabinetTypeSelection): void
}>()

const localValue = ref<CabinetTypeSelection>({
  control_category: props.modelValue?.control_category || '',
  cabinet_type: props.modelValue?.cabinet_type || '',
  control_structure: props.modelValue?.control_structure || ''
})

// 控制大类选项
const controlCategories = [
  { value: '低压类', label: '低压类' },
  { value: '配电类', label: '配电类' },
  { value: '控制类', label: '控制类' },
  { value: '自控类', label: '自控类' }
]

// 柜体类型映射
const cabinetTypeMap: Record<string, Array<{ value: string; label: string }>> = {
  '低压类': [
    { value: '低压进线柜', label: '低压进线柜' },
    { value: '低压出线柜', label: '低压出线柜' },
    { value: '低压补偿柜', label: '低压补偿柜' },
    { value: '低压控制柜', label: '低压控制柜' },
    { value: 'MCC柜', label: 'MCC柜（GGD）' },
    { value: '抽屉柜', label: '抽屉柜（MNS/GCK）' }
  ],
  '配电类': [
    { value: '配电箱', label: '配电箱' },
    { value: '配电柜', label: '配电柜' }
  ],
  '控制类': [
    { value: '控制箱', label: '控制箱' },
    { value: '控制柜', label: '控制柜' }
  ],
  '自控类': [
    { value: '自控柜', label: '自控柜' },
    { value: 'PLC控制柜', label: 'PLC控制柜' }
  ]
}

// 控制结构映射
const controlStructureMap: Record<string, Array<{ value: string; label: string }>> = {
  '控制箱': [
    { value: '非标控制', label: '非标控制（不带PLC）' },
    { value: '自控型', label: '自控型（带PLC+控制回路）' },
    { value: '纯PLC型', label: '纯PLC型（带PLC，不含控制回路）' }
  ],
  '控制柜': [
    { value: '非标控制', label: '非标控制（不带PLC）' },
    { value: '自控型', label: '自控型（带PLC+控制回路）' },
    { value: '纯PLC型', label: '纯PLC型（带PLC，不含控制回路）' }
  ],
  'MCC柜': [
    { value: 'GGD标准柜', label: 'GGD标准柜' }
  ],
  '抽屉柜': [
    { value: 'MNS标准柜', label: 'MNS标准柜' },
    { value: 'GCK标准柜', label: 'GCK标准柜' }
  ],
  '配电柜': [
    { value: '非标配电', label: '非标配电' }
  ],
  '配电箱': [
    { value: '非标配电', label: '非标配电' }
  ],
  '自控柜': [
    { value: '自控型', label: '自控型（带PLC+控制回路）' }
  ],
  'PLC控制柜': [
    { value: '纯PLC型', label: '纯PLC型（带PLC，不含控制回路）' }
  ]
}

// 可用的柜体类型
const availableCabinetTypes = computed(() => {
  if (!localValue.value.control_category) return []
  return cabinetTypeMap[localValue.value.control_category] || []
})

// 可用的控制结构
const availableControlStructures = computed(() => {
  if (!localValue.value.cabinet_type) return []
  return controlStructureMap[localValue.value.cabinet_type] || []
})

// 选择是否完整
const selectionComplete = computed(() => {
  return !!(
    localValue.value.control_category &&
    localValue.value.cabinet_type &&
    localValue.value.control_structure
  )
})

// 选择摘要
const selectionSummary = computed(() => {
  if (!selectionComplete.value) return ''
  return `${localValue.value.control_category} > ${localValue.value.cabinet_type} > ${localValue.value.control_structure}`
})

// 处理控制大类变化
const handleControlCategoryChange = () => {
  // 清空下级选择
  localValue.value.cabinet_type = ''
  localValue.value.control_structure = ''
  emitChange()
}

// 处理柜体类型变化
const handleCabinetTypeChange = () => {
  // 清空下级选择
  localValue.value.control_structure = ''
  emitChange()
}

// 处理控制结构变化
const handleControlStructureChange = () => {
  emitChange()
}

// 发出变化事件
const emitChange = () => {
  emit('update:modelValue', { ...localValue.value })
  emit('change', { ...localValue.value })
}

// 监听外部变化
watch(
  () => props.modelValue,
  (newValue) => {
    if (newValue) {
      localValue.value = { ...newValue }
    }
  },
  { deep: true }
)
</script>

<style scoped>
.cabinet-type-selector {
  width: 100%;
}
</style>
