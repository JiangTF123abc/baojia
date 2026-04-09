<template>
  <div class="project-tree">
    <div class="tree-toolbar">
      <el-button size="small" type="primary" @click="showCreateProject = true">
        <el-icon><Plus /></el-icon> 新建项目
      </el-button>
    </div>
    <el-tree
      ref="treeRef"
      :data="projectStore.treeData"
      :props="treeProps"
      node-key="key"
      highlight-current
      :expand-on-click-node="false"
      @node-click="handleNodeClick"
      @node-contextmenu="handleContextMenu"
    >
      <template #default="{ node, data }">
        <span class="tree-node">
          <el-icon v-if="data.type === 'project'"><FolderOpened /></el-icon>
          <el-icon v-else-if="data.type === 'cabinet'"><Box /></el-icon>
          <el-icon v-else-if="data.type === 'structure'"><Grid /></el-icon>
          <el-icon v-else><Document /></el-icon>
          <span>{{ node.label }}</span>
        </span>
      </template>
    </el-tree>

    <!-- 右键菜单 -->
    <div
      v-if="contextMenu.visible"
      class="context-menu"
      :style="{ left: contextMenu.x + 'px', top: contextMenu.y + 'px' }"
      @mouseleave="contextMenu.visible = false"
    >
      <div v-if="contextMenu.node?.type === 'cabinet'">
        <div class="menu-item" @click="copyCabinet">复制配电柜</div>
        <div class="menu-item danger" @click="deleteNode">删除</div>
      </div>
      <div v-else>
        <div class="menu-item danger" @click="deleteNode">删除</div>
      </div>
    </div>

    <!-- 新建项目对话框 -->
    <el-dialog v-model="showCreateProject" title="新建项目" width="400px">
      <el-form :model="newProject" label-width="80px">
        <el-form-item label="项目名称">
          <el-input v-model="newProject.name" />
        </el-form-item>
        <el-form-item label="客户">
          <el-input v-model="newProject.customer" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateProject = false">取消</el-button>
        <el-button type="primary" @click="createProject">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useProjectStore } from '@/stores/project'
import { cabinetApi } from '@/api'

const router = useRouter()
const projectStore = useProjectStore()
const treeRef = ref()
const showCreateProject = ref(false)
const newProject = reactive({ name: '', customer: '' })

const treeProps = {
  label: 'label',
  children: 'children',
}

const contextMenu = reactive({
  visible: false,
  x: 0,
  y: 0,
  node: null as any,
})

onMounted(async () => {
  try {
    await projectStore.loadProjects()
  } catch (error) {
    console.error('加载项目列表失败:', error)
  }
})

function handleNodeClick(data: any) {
  projectStore.selectNode(data)
  // 点击项目节点时跳转到项目详情页
  if (data.type === 'project') {
    router.push(`/projects/${data.id}`)
  }
}

function handleContextMenu(event: MouseEvent, data: any, node: any) {
  event.preventDefault()
  contextMenu.visible = true
  contextMenu.x = event.clientX
  contextMenu.y = event.clientY
  contextMenu.node = data
}

async function copyCabinet() {
  contextMenu.visible = false
  try {
    await cabinetApi.copy(contextMenu.node.id)
    ElMessage.success('配电柜已复制')
    await projectStore.loadProjects()
  } catch {
    ElMessage.error('复制失败')
  }
}

async function deleteNode() {
  contextMenu.visible = false
  try {
    await ElMessageBox.confirm('确认删除？此操作不可撤销。', '警告', { type: 'warning' })
    console.log('开始删除节点:', contextMenu.node)
    await projectStore.deleteNode(contextMenu.node)
    console.log('删除成功')
    ElMessage.success('已删除')
  } catch (error) {
    console.error('删除失败:', error)
    if (error !== 'cancel') {
      ElMessage.error('删除失败: ' + (error as any).message)
    }
  }
}

async function createProject() {
  if (!newProject.name) { ElMessage.warning('请输入项目名称'); return }
  try {
    console.log('开始创建项目:', newProject)
    await projectStore.createProject({ ...newProject })
    showCreateProject.value = false
    newProject.name = ''
    newProject.customer = ''
    ElMessage.success('项目已创建')
  } catch (error: any) {
    console.error('创建项目失败:', error)
    const msg = error.response?.data?.message || error.message || '创建失败'
    ElMessage.error('创建项目失败: ' + msg)
  }
}
</script>

<style scoped>
.project-tree { height: 100%; display: flex; flex-direction: column; }
.tree-toolbar { padding: 8px; border-bottom: 1px solid #e4e7ed; }
.tree-node { display: flex; align-items: center; gap: 4px; }
.context-menu {
  position: fixed; background: white; border: 1px solid #e4e7ed;
  border-radius: 4px; box-shadow: 0 2px 8px rgba(0,0,0,0.15);
  z-index: 9999; min-width: 120px;
}
.menu-item {
  padding: 8px 16px; cursor: pointer; font-size: 13px;
}
.menu-item:hover { background: #f5f7fa; }
.menu-item.danger { color: #f56c6c; }
</style>
