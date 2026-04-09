<template>
  <div class="admin-panel">
    <el-tabs v-model="activeTab">
      <!-- 审计日志 -->
      <el-tab-pane label="审计日志" name="audit">
        <div class="tab-toolbar">
          <el-date-picker
            v-model="auditDateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            size="small"
          />
          <el-select v-model="auditAction" placeholder="操作类型" clearable size="small" style="width: 120px">
            <el-option label="CREATE" value="CREATE" />
            <el-option label="UPDATE" value="UPDATE" />
            <el-option label="DELETE" value="DELETE" />
            <el-option label="EXPORT" value="EXPORT" />
          </el-select>
          <el-button size="small" type="primary" @click="loadAuditLogs">查询</el-button>
          <el-button size="small" @click="exportAuditLogs">导出</el-button>
        </div>
        <el-table :data="auditLogs" border size="small" v-loading="auditLoading">
          <el-table-column label="时间" prop="created_at" width="160">
            <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
          </el-table-column>
          <el-table-column label="用户" prop="username" width="100" />
          <el-table-column label="操作" prop="action" width="80" />
          <el-table-column label="实体类型" prop="entity_type" width="100" />
          <el-table-column label="实体ID" prop="entity_id" width="80" />
          <el-table-column label="IP" prop="ip_address" width="120" />
          <el-table-column label="详情" prop="new_value" min-width="200" show-overflow-tooltip />
        </el-table>
        <el-pagination
          v-model:current-page="auditPage"
          :page-size="50"
          :total="auditTotal"
          layout="total, prev, pager, next"
          @current-change="loadAuditLogs"
          style="margin-top: 8px"
        />
      </el-tab-pane>

      <!-- 价格公式配置 -->
      <el-tab-pane label="价格公式" name="formulas">
        <div class="tab-toolbar">
          <el-button size="small" type="primary" @click="showAddFormula = true">新增公式</el-button>
        </div>
        <el-table :data="formulas" border size="small" v-loading="formulaLoading">
          <el-table-column label="名称" prop="name" min-width="120" />
          <el-table-column label="公式" prop="formula_str" min-width="240" show-overflow-tooltip />
          <el-table-column label="默认" prop="is_default" width="70">
            <template #default="{ row }">
              <el-tag v-if="row.is_default" type="success" size="small">是</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="状态" prop="is_active" width="70">
            <template #default="{ row }">
              <el-tag :type="row.is_active ? 'success' : 'info'" size="small">
                {{ row.is_active ? '启用' : '禁用' }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>

        <el-dialog v-model="showAddFormula" title="新增价格公式" width="480px">
          <el-form :model="newFormula" label-width="80px">
            <el-form-item label="名称">
              <el-input v-model="newFormula.name" />
            </el-form-item>
            <el-form-item label="公式">
              <el-input
                v-model="newFormula.formula_str"
                type="textarea"
                :rows="3"
                placeholder="例：base_cost * (1 + loss_rate) * (1 + tax_rate) + aux_material_fee + labor_fee"
              />
            </el-form-item>
            <el-form-item label="设为默认">
              <el-switch v-model="newFormula.is_default" />
            </el-form-item>
          </el-form>
          <template #footer>
            <el-button @click="showAddFormula = false">取消</el-button>
            <el-button type="primary" @click="saveFormula">保存</el-button>
          </template>
        </el-dialog>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { auditApi, priceApi } from '@/api'
import api from '@/api'

const activeTab = ref('audit')

// ── 审计日志 ──
const auditLogs = ref<any[]>([])
const auditLoading = ref(false)
const auditDateRange = ref<[Date, Date] | null>(null)
const auditAction = ref('')
const auditPage = ref(1)
const auditTotal = ref(0)

async function loadAuditLogs() {
  auditLoading.value = true
  try {
    const params: any = { page: auditPage.value, per_page: 50 }
    if (auditDateRange.value) {
      params.start = auditDateRange.value[0].toISOString()
      params.end = auditDateRange.value[1].toISOString()
    }
    if (auditAction.value) params.action = auditAction.value
    const res = await auditApi.query(params)
    auditLogs.value = res.data.data?.items || []
    auditTotal.value = res.data.data?.total || 0
  } finally {
    auditLoading.value = false
  }
}

async function exportAuditLogs() {
  const params: any = {}
  if (auditDateRange.value) {
    params.start = auditDateRange.value[0].toISOString()
    params.end = auditDateRange.value[1].toISOString()
  }
  const res = await auditApi.export(params)
  const logs = res.data.data || []
  const csv = [
    '时间,用户,操作,实体类型,实体ID,IP',
    ...logs.map((l: any) =>
      [l.created_at, l.username, l.action, l.entity_type, l.entity_id, l.ip_address].join(',')
    ),
  ].join('\n')
  const blob = new Blob(['\uFEFF' + csv], { type: 'text/csv;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `audit_logs_${new Date().toISOString().slice(0, 10)}.csv`
  a.click()
  URL.revokeObjectURL(url)
}

// ── 价格公式 ──
const formulas = ref<any[]>([])
const formulaLoading = ref(false)
const showAddFormula = ref(false)
const newFormula = reactive({ name: '', formula_str: '', is_default: false })

async function loadFormulas() {
  formulaLoading.value = true
  try {
    const res = await priceApi.listFormulas()
    formulas.value = res.data.data || []
  } finally {
    formulaLoading.value = false
  }
}

async function saveFormula() {
  if (!newFormula.name || !newFormula.formula_str) {
    ElMessage.warning('请填写名称和公式')
    return
  }
  try {
    await api.post('/price-formulas', { ...newFormula, is_active: true })
    ElMessage.success('公式已保存')
    showAddFormula.value = false
    newFormula.name = ''
    newFormula.formula_str = ''
    newFormula.is_default = false
    await loadFormulas()
  } catch {
    ElMessage.error('保存失败')
  }
}

function formatDate(iso: string) {
  return iso ? iso.slice(0, 16).replace('T', ' ') : '-'
}

onMounted(() => {
  loadAuditLogs()
  loadFormulas()
})
</script>

<style scoped>
.admin-panel { padding: 16px; }
.tab-toolbar {
  display: flex; gap: 8px; align-items: center;
  margin-bottom: 12px; flex-wrap: wrap;
}
</style>
