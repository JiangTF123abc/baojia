<template>
  <div class="quotation-table" @keydown="handleKeyDown" tabindex="0">
    <!-- 工具栏 -->
    <div class="table-toolbar">
      <el-button size="small" type="primary" @click="addRow">
        <el-icon><Plus /></el-icon> 添加元器件
      </el-button>
      <el-checkbox v-model="showHidden" @change="emit('change')" style="margin-left: 12px">
        显示隐藏元器件
      </el-checkbox>
      <template v-if="selectedRows.length > 0">
        <el-button size="small" @click="showBatchDiscount = true">
          批量修改折扣率 ({{ selectedRows.length }})
        </el-button>
        <el-button size="small" type="danger" @click="batchDelete">
          批量删除
        </el-button>
      </template>
      <span class="total-price">合计：¥ {{ totalPrice }}</span>
    </div>

    <!-- 表格 -->
    <el-table
      :data="visibleRows"
      @selection-change="selectedRows = $event"
      border
      size="small"
      style="width: 100%"
      :row-class-name="getRowClassName"
    >
      <el-table-column type="selection" width="40" />
      <el-table-column label="分类" prop="component_category" width="100">
        <template #default="{ row }">
          <el-tag v-if="row.component_category" size="small" type="info">
            {{ row.component_category }}
          </el-tag>
          <span v-else class="text-muted">-</span>
        </template>
      </el-table-column>
      <el-table-column label="型号" prop="model_number" min-width="140">
        <template #default="{ row, $index }">
          <div class="cell-with-badge">
            <MaterialSearch
              v-if="editingCell?.row === $index && editingCell?.col === 'model_number'"
              v-model="row.model_number"
              @select="(m) => fillFromMaterial(row, m)"
              @blur="saveCell(row)"
            />
            <span v-else class="cell-text" @click="startEdit($index, 'model_number')">
              {{ row.model_number || '点击编辑' }}
            </span>
            <el-tag v-if="row.is_auto_matched" size="small" type="success" class="auto-badge">
              自动
            </el-tag>
          </div>
        </template>
      </el-table-column>
      <el-table-column label="名称" prop="name" min-width="120">
        <template #default="{ row, $index }">
          <el-input
            v-if="editingCell?.row === $index && editingCell?.col === 'name'"
            v-model="row.name"
            size="small"
            @blur="saveCell(row)"
            @keydown.enter="moveDown($index, 'name')"
            @keydown.tab.prevent="moveRight($index, 'name')"
          />
          <span v-else class="cell-text" @click="startEdit($index, 'name')">{{ row.name || '-' }}</span>
        </template>
      </el-table-column>
      <el-table-column label="规格" prop="specification" min-width="120">
        <template #default="{ row, $index }">
          <el-input
            v-if="editingCell?.row === $index && editingCell?.col === 'specification'"
            v-model="row.specification"
            size="small"
            @blur="saveCell(row)"
            @keydown.enter="moveDown($index, 'specification')"
            @keydown.tab.prevent="moveRight($index, 'specification')"
          />
          <span v-else class="cell-text" @click="startEdit($index, 'specification')">{{ row.specification || '-' }}</span>
        </template>
      </el-table-column>
      <el-table-column label="数量" prop="quantity" width="90">
        <template #default="{ row, $index }">
          <el-input-number
            v-if="editingCell?.row === $index && editingCell?.col === 'quantity'"
            v-model="row.quantity"
            :min="0.0001"
            :precision="4"
            size="small"
            style="width: 80px"
            @blur="saveCell(row)"
            @keydown.enter="moveDown($index, 'quantity')"
          />
          <span v-else class="cell-text" @click="startEdit($index, 'quantity')">{{ row.quantity }}</span>
        </template>
      </el-table-column>
      <el-table-column label="单价" prop="unit_price" width="110">
        <template #default="{ row, $index }">
          <el-input-number
            v-if="editingCell?.row === $index && editingCell?.col === 'unit_price'"
            v-model="row.unit_price"
            :min="0"
            :precision="4"
            size="small"
            style="width: 100px"
            @blur="saveCell(row)"
            @keydown.enter="moveDown($index, 'unit_price')"
          />
          <span v-else class="cell-text" @click="startEdit($index, 'unit_price')">{{ row.unit_price }}</span>
        </template>
      </el-table-column>
      <el-table-column label="折扣率" prop="discount_rate" width="90">
        <template #default="{ row, $index }">
          <el-input-number
            v-if="editingCell?.row === $index && editingCell?.col === 'discount_rate'"
            v-model="row.discount_rate"
            :min="0"
            :max="1"
            :step="0.01"
            :precision="4"
            size="small"
            style="width: 80px"
            @blur="saveCell(row)"
            @keydown.enter="moveDown($index, 'discount_rate')"
          />
          <span v-else class="cell-text" @click="startEdit($index, 'discount_rate')">{{ row.discount_rate }}</span>
        </template>
      </el-table-column>
      <el-table-column label="总价" width="110">
        <template #default="{ row }">
          <span class="total-cell">
            {{ calcRowTotal(row) }}
          </span>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="60">
        <template #default="{ row }">
          <el-button link type="danger" size="small" @click="deleteRow(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 批量修改折扣率对话框 -->
    <el-dialog v-model="showBatchDiscount" title="批量修改折扣率" width="300px">
      <el-input-number v-model="batchDiscountValue" :min="0" :max="1" :step="0.01" :precision="4" />
      <template #footer>
        <el-button @click="showBatchDiscount = false">取消</el-button>
        <el-button type="primary" @click="applyBatchDiscount">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import MaterialSearch from '@/components/MaterialSearch/index.vue'
import { useQuotationTable } from './useQuotationTable'

const props = defineProps<{
  structureComponentId: number
  initialRows?: any[]
}>()

const emit = defineEmits<{
  (e: 'change'): void
}>()

const {
  rows,
  selectedRows,
  editingCell,
  showBatchDiscount,
  batchDiscountValue,
  showHidden,
  visibleRows,
  totalPrice,
  getRowClassName,
  calcRowTotal,
  startEdit,
  moveDown,
  moveRight,
  handleKeyDown,
  saveCell,
  fillFromMaterial,
  addRow,
  deleteRow,
  batchDelete,
  applyBatchDiscount
} = useQuotationTable(props, emit)

</script>

<style scoped>
.quotation-table { outline: none; }
.table-toolbar {
  display: flex; align-items: center; gap: 8px;
  padding: 8px 0; margin-bottom: 8px;
}
.total-price { margin-left: auto; font-weight: bold; color: #e6a23c; }
.cell-text {
  display: block; min-height: 22px; cursor: pointer;
  padding: 2px 4px; border-radius: 2px;
}
.cell-text:hover { background: #f0f2f5; }
.total-cell { font-weight: 500; color: #409eff; }
.cell-with-badge {
  display: flex;
  align-items: center;
  gap: 6px;
}
.auto-badge {
  flex-shrink: 0;
}
.text-muted {
  color: #909399;
  font-size: 12px;
}
:deep(.hidden-row) {
  background-color: #f5f7fa;
  opacity: 0.6;
}
:deep(.hidden-row td) {
  color: #909399;
}
</style>
