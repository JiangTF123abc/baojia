<template>
  <div v-if="accessories.length > 0 && !dismissed" class="accessory-panel">
    <div class="panel-header">
      <el-icon><InfoFilled /></el-icon>
      <span>已自动补充标准附件</span>
      <el-button link size="small" @click="dismissed = true">忽略</el-button>
    </div>
    <div class="accessory-list">
      <div v-for="acc in accessories" :key="acc.id" class="accessory-item">
        <span class="acc-model">{{ acc.model_number }}</span>
        <span class="acc-name">{{ acc.name }}</span>
        <el-button size="small" type="primary" link @click="addAccessory(acc)">添加</el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { materialApi, componentApi } from '@/api'

const props = defineProps<{
  materialId?: number | null
  structureComponentId: number
}>()

const emit = defineEmits<{ (e: 'added'): void }>()

const accessories = ref<any[]>([])
const dismissed = ref(false)

watch(() => props.materialId, async (id) => {
  dismissed.value = false
  accessories.value = []
  if (!id) return
  try {
    const res = await materialApi.getAccessories(id)
    accessories.value = res.data.data || []
  } catch {
    // 静默失败
  }
})

async function addAccessory(acc: any) {
  try {
    await componentApi.createBase({
      structure_component_id: props.structureComponentId,
      material_id: acc.id,
      model_number: acc.model_number,
      name: acc.name,
      specification: acc.specification,
      unit_price: acc.unit_price,
      quantity: 1,
      discount_rate: 1,
    })
    accessories.value = accessories.value.filter((a) => a.id !== acc.id)
    emit('added')
    ElMessage.success(`已添加附件：${acc.model_number}`)
  } catch {
    ElMessage.error('添加附件失败')
  }
}
</script>

<style scoped>
.accessory-panel {
  margin-top: 8px; border: 1px solid #e6a23c;
  border-radius: 4px; background: #fdf6ec;
}
.panel-header {
  display: flex; align-items: center; gap: 6px;
  padding: 6px 12px; color: #e6a23c; font-size: 13px;
}
.accessory-list { padding: 4px 12px 8px; }
.accessory-item {
  display: flex; align-items: center; gap: 8px;
  padding: 4px 0; font-size: 12px;
}
.acc-model { font-weight: 600; min-width: 80px; }
.acc-name { color: #606266; flex: 1; }
</style>
