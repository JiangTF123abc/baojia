<template>
  <div class="material-search" ref="containerRef">
    <el-input
      v-model="inputValue"
      size="small"
      placeholder="输入型号搜索..."
      :loading="loading"
      @input="onInput"
      @focus="showDropdown = true"
      @blur="handleBlur"
      @keydown.down.prevent="moveSelection(1)"
      @keydown.up.prevent="moveSelection(-1)"
      @keydown.enter.prevent="confirmSelection"
      @keydown.esc="showDropdown = false"
    />
    <div v-if="showDropdown && results.length > 0" class="dropdown">
      <div
        v-for="(item, idx) in results"
        :key="item.id"
        class="dropdown-item"
        :class="{ active: idx === activeIdx }"
        @mousedown.prevent="selectItem(item)"
      >
        <span class="model">{{ item.model_number }}</span>
        <span class="name">{{ item.name }}</span>
        <span class="spec">{{ item.specification }}</span>
        <span class="price">¥{{ item.unit_price }}</span>
      </div>
    </div>
    <div v-if="showDropdown && !loading && results.length === 0 && inputValue" class="dropdown no-result">
      未找到匹配项
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { materialApi } from '@/api'
import { useDebounceSearch } from '@/composables/useDebounceSearch'

const props = defineProps<{ modelValue?: string }>()
const emit = defineEmits<{
  (e: 'update:modelValue', v: string): void
  (e: 'select', material: any): void
  (e: 'blur'): void
}>()

const inputValue = ref(props.modelValue || '')
const showDropdown = ref(false)
const activeIdx = ref(-1)
const containerRef = ref()

watch(() => props.modelValue, (v) => { inputValue.value = v || '' })

async function fetchMaterials(query: string) {
  const res = await materialApi.search(query)
  return res.data.data || []
}

const { results, loading, search } = useDebounceSearch(fetchMaterials, 300)

function onInput(val: string) {
  emit('update:modelValue', val)
  activeIdx.value = -1
  search(val)
  showDropdown.value = true
}

function selectItem(item: any) {
  inputValue.value = item.model_number
  emit('update:modelValue', item.model_number)
  emit('select', item)
  showDropdown.value = false
}

function moveSelection(dir: number) {
  if (!results.value.length) return
  activeIdx.value = Math.max(0, Math.min(results.value.length - 1, activeIdx.value + dir))
}

function confirmSelection() {
  if (activeIdx.value >= 0 && results.value[activeIdx.value]) {
    selectItem(results.value[activeIdx.value])
  }
}

function handleBlur() {
  setTimeout(() => {
    showDropdown.value = false
    emit('blur')
  }, 150)
}
</script>

<style scoped>
.material-search { position: relative; }
.dropdown {
  position: absolute; top: 100%; left: 0; right: 0;
  background: white; border: 1px solid #e4e7ed;
  border-radius: 4px; box-shadow: 0 2px 8px rgba(0,0,0,0.15);
  z-index: 9999; max-height: 280px; overflow-y: auto;
}
.dropdown-item {
  display: flex; gap: 8px; align-items: center;
  padding: 6px 12px; cursor: pointer; font-size: 12px;
}
.dropdown-item:hover, .dropdown-item.active { background: #f0f7ff; }
.model { font-weight: 600; min-width: 80px; }
.name { color: #606266; flex: 1; }
.spec { color: #909399; font-size: 11px; }
.price { color: #e6a23c; min-width: 60px; text-align: right; }
.no-result { padding: 12px; color: #909399; text-align: center; font-size: 13px; }
</style>
