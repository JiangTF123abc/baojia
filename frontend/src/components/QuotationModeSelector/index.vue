<template>
  <div class="quotation-mode-selector">
    <el-form-item label="报价模式" required>
      <el-radio-group v-model="localValue" @change="handleChange">
        <el-radio label="detailed">
          <div class="mode-option">
            <div class="mode-title">详细逐项报价</div>
            <div class="mode-description">手动选择所有元器件，适用于复杂或非标项目</div>
          </div>
        </el-radio>
        <el-radio label="quick">
          <div class="mode-option">
            <div class="mode-title">快速报价</div>
            <div class="mode-description">自动匹配标准元器件，人工微调关键项，适用于标准或常规项目</div>
          </div>
        </el-radio>
      </el-radio-group>
    </el-form-item>

    <el-alert
      v-if="localValue === 'quick'"
      title="快速报价模式将根据柜体类型自动匹配标准元器件，您可以在创建后进行微调"
      type="info"
      :closable="false"
      style="margin-top: 10px"
    />

    <el-alert
      v-if="localValue === 'detailed'"
      title="详细报价模式需要您手动添加所有元器件，适合非标或特殊需求项目"
      type="info"
      :closable="false"
      style="margin-top: 10px"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { ElFormItem, ElRadioGroup, ElRadio, ElAlert } from 'element-plus'

type QuotationMode = 'detailed' | 'quick'

const props = defineProps<{
  modelValue: QuotationMode
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: QuotationMode): void
  (e: 'change', value: QuotationMode): void
}>()

const localValue = ref<QuotationMode>(props.modelValue || 'detailed')

const handleChange = () => {
  emit('update:modelValue', localValue.value)
  emit('change', localValue.value)
}

watch(
  () => props.modelValue,
  (newValue) => {
    if (newValue) {
      localValue.value = newValue
    }
  }
)
</script>

<style scoped>
.quotation-mode-selector {
  width: 100%;
}

.mode-option {
  display: inline-block;
  margin-left: 8px;
}

.mode-title {
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.mode-description {
  font-size: 12px;
  color: #909399;
  line-height: 1.4;
}

:deep(.el-radio) {
  display: flex;
  align-items: flex-start;
  margin-bottom: 16px;
  white-space: normal;
}

:deep(.el-radio__label) {
  white-space: normal;
  line-height: 1.5;
}
</style>
