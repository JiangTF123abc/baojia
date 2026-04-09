<template>
  <div class="template-library">
    <div class="page-header">
      <h3>模板库</h3>
      <el-input
        v-model="searchQuery"
        placeholder="搜索模板..."
        style="width: 240px"
        clearable
        @input="filterTemplates"
      />
    </div>

    <el-table :data="filteredTemplates" border v-loading="loading">
      <el-table-column label="模板名称" prop="name" min-width="160" />
      <el-table-column label="描述" prop="description" min-width="200" />
      <el-table-column label="类型" prop="node_type" width="90">
        <template #default="{ row }">
          <el-tag size="small">{{ typeLabel(row.node_type) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="创建时间" prop="created_at" width="160">
        <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
      </el-table-column>
      <el-table-column label="操作" width="160">
        <template #default="{ row }">
          <el-button size="small" type="primary" link @click="applyTemplate(row)">应用</el-button>
          <el-button size="small" link @click="editTemplate(row)">编辑</el-button>
          <el-button size="small" type="danger" link @click="deleteTemplate(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 应用模板对话框 -->
    <el-dialog v-model="showApply" title="应用模板到项目" width="360px">
      <el-select v-model="targetProjectId" placeholder="选择目标项目" style="width: 100%">
        <el-option
          v-for="p in projectStore.projects"
          :key="p.id"
          :label="p.name"
          :value="p.id"
        />
      </el-select>
      <template #footer>
        <el-button @click="showApply = false">取消</el-button>
        <el-button type="primary" :loading="applying" @click="confirmApply">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { templateApi } from '@/api'
import { useProjectStore } from '@/stores/project'

const projectStore = useProjectStore()
const loading = ref(false)
const templates = ref<any[]>([])
const searchQuery = ref('')
const showApply = ref(false)
const applying = ref(false)
const targetProjectId = ref<number | null>(null)
const selectedTemplate = ref<any>(null)

const filteredTemplates = computed(() =>
  templates.value.filter((t) =>
    !searchQuery.value ||
    t.name.includes(searchQuery.value) ||
    (t.description || '').includes(searchQuery.value)
  )
)

onMounted(async () => {
  loading.value = true
  try {
    const res = await templateApi.list()
    templates.value = res.data.data || []
  } finally {
    loading.value = false
  }
  if (!projectStore.projects.length) await projectStore.loadProjects()
})

function filterTemplates() { /* computed 自动过滤 */ }

function typeLabel(type: string) {
  return { project: '项目', cabinet: '配电柜', structure: '结构组件' }[type] || type
}

function formatDate(iso: string) {
  return iso ? iso.slice(0, 16).replace('T', ' ') : '-'
}

function applyTemplate(tpl: any) {
  selectedTemplate.value = tpl
  targetProjectId.value = null
  showApply.value = true
}

async function confirmApply() {
  if (!targetProjectId.value) { ElMessage.warning('请选择目标项目'); return }
  applying.value = true
  try {
    await templateApi.apply(selectedTemplate.value.id, targetProjectId.value)
    ElMessage.success('模板已应用')
    showApply.value = false
    await projectStore.loadProjects()
  } catch {
    ElMessage.error('应用失败')
  } finally {
    applying.value = false
  }
}

function editTemplate(tpl: any) {
  ElMessage.info('编辑功能开发中')
}

async function deleteTemplate(tpl: any) {
  await ElMessageBox.confirm(`确认删除模板"${tpl.name}"？`, '警告', { type: 'warning' })
  try {
    await templateApi.delete(tpl.id)
    templates.value = templates.value.filter((t) => t.id !== tpl.id)
    ElMessage.success('已删除')
  } catch {
    ElMessage.error('删除失败')
  }
}
</script>

<style scoped>
.template-library { padding: 16px; }
.page-header {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 16px;
}
.page-header h3 { margin: 0; }
</style>
