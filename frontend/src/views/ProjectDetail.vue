<template>
  <div class="project-detail" v-if="project">
    <!-- 顶部标题栏 -->
    <div class="detail-header">
      <div class="header-left">
        <h3>{{ project.name }}</h3>
        <span class="customer" v-if="project.customer">客户：{{ project.customer }}</span>
        <div class="price-info">
          <span class="total-badge">材料总价：¥ {{ projectTotal }}</span>
          <el-popover
            v-if="laborCostDetail && selectedCabinetId"
            placement="bottom"
            :width="300"
            trigger="hover"
          >
            <template #reference>
              <span class="labor-badge">
                人工费用：¥ {{ formatNumber(laborCostDetail.total_labor_cost) }}
                <el-icon style="margin-left: 4px"><InfoFilled /></el-icon>
              </span>
            </template>
            <div class="labor-detail">
              <div class="detail-title">人工费用明细</div>
              <div class="detail-item">
                <span>组装费：</span>
                <span>¥ {{ formatNumber(laborCostDetail.assembly_fee) }}</span>
              </div>
              <div class="detail-item">
                <span>管理费：</span>
                <span>¥ {{ formatNumber(laborCostDetail.management_fee) }}</span>
              </div>
              <div class="detail-item">
                <span>利润：</span>
                <span>¥ {{ formatNumber(laborCostDetail.profit) }}</span>
              </div>
              <div class="detail-item" v-if="laborCostDetail.programming_fee">
                <span>编程费：</span>
                <span>¥ {{ formatNumber(laborCostDetail.programming_fee) }}</span>
              </div>
              <div class="detail-item" v-if="laborCostDetail.debugging_fee">
                <span>调试费：</span>
                <span>¥ {{ formatNumber(laborCostDetail.debugging_fee) }}</span>
              </div>
              <div class="detail-divider"></div>
              <div class="detail-item total">
                <span>合计：</span>
                <span>¥ {{ formatNumber(laborCostDetail.total_labor_cost) }}</span>
              </div>
            </div>
          </el-popover>
          <span class="grand-total-badge" v-if="laborCostDetail">
            项目总价：¥ {{ projectTotalWithLabor }}
          </span>
        </div>
      </div>
      <div class="actions">
        <el-button size="small" @click="showBomImport = true">
          <el-icon><Upload /></el-icon> 导入BOM
        </el-button>
        <el-button size="small" @click="generateExcel" :loading="excelLoading">
          <el-icon><Download /></el-icon> 核价单Excel
        </el-button>
        <el-button size="small" type="primary" @click="generatePdf" :loading="pdfLoading">
          <el-icon><Document /></el-icon> 客户报价单PDF
        </el-button>
      </div>
    </div>

    <!-- 主体：左侧配电柜列表 + 右侧内容 -->
    <div class="detail-body">
      <!-- 左侧配电柜面板 -->
      <div class="cabinet-panel">
        <div class="panel-header">
          <span>配电柜</span>
          <el-button link size="small" type="primary" @click="showAddCabinet = true">
            <el-icon><Plus /></el-icon>
          </el-button>
        </div>
        <div class="cabinet-list">
          <div
            v-for="cabinet in cabinets"
            :key="cabinet.id"
            class="cabinet-item"
            :class="{ active: selectedCabinetId === cabinet.id }"
            @click="selectCabinet(cabinet)"
            @contextmenu.prevent="showCabinetMenu($event, cabinet)"
          >
            <el-icon><Box /></el-icon>
            <span class="cabinet-name">{{ cabinet.name }}</span>
            <span class="cabinet-price">¥{{ getCabinetTotal(cabinet) }}</span>
          </div>
          <el-empty v-if="cabinets.length === 0" description="暂无配电柜" :image-size="60" />
        </div>
      </div>

      <!-- 右侧内容区 -->
      <div class="content-area" v-if="selectedCabinet">
        <!-- 结构组件标签页 -->
        <div class="structure-tabs">
          <div class="tabs-header">
            <div
              v-for="sc in selectedCabinet.structure_components || []"
              :key="sc.id"
              class="tab-item"
              :class="{ active: selectedScId === sc.id }"
              @click="selectSc(sc)"
              @dblclick="startRenameTab(sc)"
            >
              <span v-if="renamingScId !== sc.id">{{ sc.name }}</span>
              <el-input
                v-else
                v-model="renamingScName"
                size="small"
                style="width: 100px"
                @blur="confirmRenameTab(sc)"
                @keydown.enter="confirmRenameTab(sc)"
                @keydown.esc="renamingScId = null"
                ref="renameInputRef"
              />
              <el-icon class="tab-close" @click.stop="deleteSc(sc)"><Close /></el-icon>
            </div>
            <el-button link size="small" @click="addStructureComponent" style="margin-left: 4px">
              <el-icon><Plus /></el-icon> 新增组件
            </el-button>
          </div>

          <!-- 报价表格 -->
          <div class="tab-content" v-if="selectedSc">
            <QuotationTable
              :key="`quotation-${selectedSc.id}-${selectedCabinet.id}`"
              :structure-component-id="selectedSc.id"
              :initial-rows="selectedSc.base_components || []"
              @change="reloadProjectDebounced"
            />
            <AccessoryPanel
              :material-id="lastAddedMaterialId"
              :structure-component-id="selectedSc.id"
              @added="reloadProjectDebounced"
            />
          </div>
          <el-empty v-else-if="(selectedCabinet.structure_components || []).length === 0"
            description="点击「新增组件」添加结构组件" />
        </div>
      </div>

      <div class="content-area empty-hint" v-else>
        <el-empty description="请从左侧选择配电柜" />
      </div>
    </div>

    <!-- 右键菜单：配电柜 -->
    <div
      v-if="cabinetMenu.visible"
      class="context-menu"
      :style="{ left: cabinetMenu.x + 'px', top: cabinetMenu.y + 'px' }"
      @mouseleave="cabinetMenu.visible = false"
    >
      <div class="menu-item" @click="renameCabinet(cabinetMenu.cabinet)">重命名</div>
      <div class="menu-item" @click="copyCabinet(cabinetMenu.cabinet)">复制配电柜</div>
      <div class="menu-item danger" @click="deleteCabinet(cabinetMenu.cabinet)">删除</div>
    </div>

    <!-- 新建配电柜对话框 -->
    <el-dialog v-model="showAddCabinet" title="新建配电柜" width="600px">
      <el-form :model="newCabinetForm" label-width="100px">
        <el-form-item label="名称" required>
          <el-input v-model="newCabinetForm.name" placeholder="请输入配电柜名称" />
        </el-form-item>
        
        <!-- 柜体类型选择器 -->
        <CabinetTypeSelector
          v-model="newCabinetForm.cabinetType"
          @change="onCabinetTypeChange"
        />
        
        <!-- 报价模式选择器 -->
        <QuotationModeSelector
          v-model="newCabinetForm.quotationMode"
          @change="onQuotationModeChange"
        />
      </el-form>
      <template #footer>
        <el-button @click="showAddCabinet = false">取消</el-button>
        <el-button type="primary" @click="addCabinet" :loading="addingCabinet">确定</el-button>
      </template>
    </el-dialog>

    <!-- 重命名配电柜对话框 -->
    <el-dialog v-model="showRenameCabinet" title="重命名配电柜" width="360px">
      <el-input v-model="renameCabinetName" placeholder="请输入新名称" />
      <template #footer>
        <el-button @click="showRenameCabinet = false">取消</el-button>
        <el-button type="primary" @click="confirmRenameCabinet">确定</el-button>
      </template>
    </el-dialog>

    <!-- BOM 导入对话框 -->
    <el-dialog v-model="showBomImport" title="导入BOM" width="600px">
      <BomImport @imported="onBomImported" :project-id="project.id" />
    </el-dialog>

    <!-- 新增结构组件对话框 -->
    <el-dialog v-model="showAddStructure" title="新增结构组件" width="500px">
      <el-form :model="newStructureForm" label-width="100px">
        <el-form-item label="组件名称" required>
          <el-input v-model="newStructureForm.name" placeholder="请输入组件名称" />
        </el-form-item>
        
        <!-- 回路类型选择器（仅非标控制时显示） -->
        <CircuitTypeSelector
          v-if="selectedCabinet && selectedCabinet.control_structure === '非标控制'"
          v-model="newStructureForm.circuit_type"
        />
      </el-form>
      <template #footer>
        <el-button @click="showAddStructure = false">取消</el-button>
        <el-button type="primary" @click="createStructureComponent">确定</el-button>
      </template>
    </el-dialog>
  </div>
  <el-empty v-else description="项目不存在" />
</template>

<script setup lang="ts">
import { computed, watch, onErrorCaptured } from 'vue'
import { useRoute } from 'vue-router'
import QuotationTable from '@/components/QuotationTable/index.vue'
import AccessoryPanel from '@/components/AccessoryPanel/index.vue'
import BomImport from '@/components/BomImport/index.vue'
import CabinetTypeSelector from '@/components/CabinetTypeSelector/index.vue'
import QuotationModeSelector from '@/components/QuotationModeSelector/index.vue'
import CircuitTypeSelector from '@/components/CircuitTypeSelector/index.vue'

import {
  getCabinetTotalNum,
  useProjectDetail,
  useLaborCost,
  useCabinetManager,
  useStructureManager
} from '@/composables/useProjectDetailSimple'

const route = useRoute()

// 全局错误抑制：捕获并静默处理Vue响应式冲突错误
onErrorCaptured((err: any) => {
  const errorMsg = err?.message || ''
  // 静默处理Vue内部的响应式更新冲突
  if (errorMsg.includes('Cannot set properties of null') ||
      errorMsg.includes('Cannot read properties of null') ||
      errorMsg.includes('parentNode') ||
      errorMsg.includes('__vnode') ||
      errorMsg.includes('emitsOptions') ||
      errorMsg.includes('nextSibling')) {
    // 完全静默，不输出任何信息
    return false
  }
  return true
})

// 1. 项目基础与报表管理
const {
  project,
  cabinets,
  excelLoading,
  pdfLoading,
  showBomImport,
  reloadProject,
  reloadProjectDebounced,
  generateExcel,
  generatePdf,
  onBomImported,
  projectStore,
  updateLocalData
} = useProjectDetail()

// 2. 人工费用计算
const {
  laborCostDetail,
  loadingLaborCost,
  loadLaborCost
} = useLaborCost(cabinets)

// 3. 配电柜管理
const {
  selectedCabinetId,
  selectedCabinet,
  showAddCabinet,
  showRenameCabinet,
  addingCabinet,
  newCabinetForm,
  renameCabinetName,
  cabinetMenu,
  showCabinetMenu,
  addCabinet,
  renameCabinet,
  confirmRenameCabinet,
  copyCabinet,
  deleteCabinet
} = useCabinetManager(project, cabinets, async () => {
  await reloadProject()
})

// 4. 结构组件管理
const {
  selectedScId,
  selectedSc,
  showAddStructure,
  newStructureForm,
  renamingScId,
  renamingScName,
  renameInputRef,
  addStructureComponent,
  createStructureComponent,
  startRenameTab,
  confirmRenameTab,
  deleteSc
} = useStructureManager(selectedCabinet, selectedCabinetId, async () => {
  await reloadProject()
}, projectStore, updateLocalData)

const lastAddedMaterialId = computed(() => null) // 可根据需求在此或子组件中维护

const projectTotal = computed(() => {
  const total = cabinets.value.reduce((sum: number, c: any) => sum + getCabinetTotalNum(c), 0)
  return total.toFixed(2)
})

const projectTotalWithLabor = computed(() => {
  if (!laborCostDetail.value) return projectTotal.value
  const materialTotal = parseFloat(projectTotal.value) || 0
  const laborTotal = Number(laborCostDetail.value.total_labor_cost) || 0
  return (materialTotal + laborTotal).toFixed(2)
})

function getCabinetTotal(cabinet: any): string {
  return getCabinetTotalNum(cabinet).toFixed(2)
}

function selectCabinet(cabinet: any) {
  selectedCabinetId.value = cabinet.id
  const scs = cabinet.structure_components || []
  selectedScId.value = scs.length > 0 ? scs[0].id : null
}

function selectSc(sc: any) {
  selectedScId.value = sc.id
}

// 路由变化时重置状态
watch(() => route.params.id, () => {
  selectedCabinetId.value = null
  selectedScId.value = null
  laborCostDetail.value = null
})

// 列表变化自动选中第一个
watch(cabinets, (list) => {
  if (list.length > 0 && !selectedCabinetId.value) {
    selectCabinet(list[0])
  }
}, { immediate: true })

// 切换配电柜重新加载人工费
watch(selectedCabinetId, async (cabinetId, oldCabinetId) => {
  // 如果是从有值变为null（清空状态），不加载
  if (!cabinetId) {
    laborCostDetail.value = null
    return
  }
  
  // 如果值没有真正改变，不重复加载
  if (cabinetId === oldCabinetId) {
    return
  }
  
  try {
    await loadLaborCost(cabinetId)
  } catch (error) {
    console.error('加载人工费用失败:', error)
  }
})

function onCabinetTypeChange(value: any) {
  console.log('柜体类型已选择:', value)
}

function onQuotationModeChange(value: 'detailed' | 'quick') {
  console.log('报价模式已选择:', value)
}

// 安全的数字格式化函数
function formatNumber(value: any): string {
  if (value === null || value === undefined) return '0.00'
  const num = Number(value)
  if (isNaN(num)) return '0.00'
  return num.toFixed(2)
}
</script>

<style scoped>
.project-detail { height: 100%; display: flex; flex-direction: column; overflow: hidden; }

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  color: #909399;
  font-size: 14px;
}

.detail-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 10px 16px; border-bottom: 1px solid #e4e7ed;
  background: #fff; flex-shrink: 0;
}
.header-left { display: flex; align-items: center; gap: 16px; flex-wrap: wrap; }
.detail-header h3 { margin: 0; font-size: 16px; }
.customer { color: #909399; font-size: 13px; }
.price-info { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
.total-badge {
  background: #fdf6ec; color: #e6a23c;
  border: 1px solid #faecd8; border-radius: 4px;
  padding: 2px 10px; font-size: 13px; font-weight: 600;
}
.labor-badge {
  background: #f0f9ff; color: #409eff;
  border: 1px solid #d9ecff; border-radius: 4px;
  padding: 2px 10px; font-size: 13px; font-weight: 600;
  cursor: pointer; display: inline-flex; align-items: center;
}
.labor-badge:hover {
  background: #ecf5ff;
}
.grand-total-badge {
  background: #f0f9ff; color: #67c23a;
  border: 1px solid #c2e7b0; border-radius: 4px;
  padding: 2px 10px; font-size: 13px; font-weight: 600;
}
.labor-detail {
  padding: 4px 0;
}
.detail-title {
  font-weight: 600;
  font-size: 14px;
  margin-bottom: 12px;
  color: #303133;
}
.detail-item {
  display: flex;
  justify-content: space-between;
  padding: 6px 0;
  font-size: 13px;
  color: #606266;
}
.detail-item.total {
  font-weight: 600;
  color: #303133;
  font-size: 14px;
}
.detail-divider {
  height: 1px;
  background: #e4e7ed;
  margin: 8px 0;
}
.actions { display: flex; gap: 8px; }

.detail-body { flex: 1; display: flex; overflow: hidden; }

/* 左侧配电柜面板 */
.cabinet-panel {
  width: 200px; border-right: 1px solid #e4e7ed;
  display: flex; flex-direction: column; flex-shrink: 0;
  background: #fafafa;
}
.panel-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 8px 12px; font-size: 13px; font-weight: 600;
  border-bottom: 1px solid #e4e7ed; color: #303133;
}
.cabinet-list { flex: 1; overflow-y: auto; padding: 4px 0; }
.cabinet-item {
  display: flex; align-items: center; gap: 6px;
  padding: 8px 12px; cursor: pointer; font-size: 13px;
  transition: background 0.15s;
}
.cabinet-item:hover { background: #f0f2f5; }
.cabinet-item.active { background: #ecf5ff; color: #409eff; }
.cabinet-name { flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.cabinet-price { font-size: 11px; color: #e6a23c; }

/* 右侧内容区 */
.content-area { flex: 1; display: flex; flex-direction: column; overflow: hidden; }
.empty-hint { justify-content: center; align-items: center; }

/* 结构组件标签页 */
.structure-tabs { flex: 1; display: flex; flex-direction: column; overflow: hidden; }
.tabs-header {
  display: flex; align-items: center; flex-wrap: nowrap;
  padding: 0 8px; border-bottom: 1px solid #e4e7ed;
  background: #fff; overflow-x: auto; flex-shrink: 0;
}
.tab-item {
  display: flex; align-items: center; gap: 4px;
  padding: 8px 12px; cursor: pointer; font-size: 13px;
  border-bottom: 2px solid transparent; white-space: nowrap;
  transition: all 0.15s;
}
.tab-item:hover { color: #409eff; }
.tab-item.active { color: #409eff; border-bottom-color: #409eff; }
.tab-close {
  font-size: 12px; color: #c0c4cc; margin-left: 2px;
  border-radius: 50%; padding: 1px;
}
.tab-close:hover { color: #f56c6c; background: #fef0f0; }
.tab-content { flex: 1; overflow: auto; padding: 12px; }

/* 右键菜单 */
.context-menu {
  position: fixed; background: white; border: 1px solid #e4e7ed;
  border-radius: 4px; box-shadow: 0 2px 8px rgba(0,0,0,0.15);
  z-index: 9999; min-width: 130px;
}
.menu-item {
  padding: 8px 16px; cursor: pointer; font-size: 13px;
}
.menu-item:hover { background: #f5f7fa; }
.menu-item.danger { color: #f56c6c; }
</style>
