import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { projectApi, cabinetApi, componentApi } from '@/api'

interface TreeNode {
  key: string
  label: string
  type: 'project' | 'cabinet' | 'structure' | 'base'
  id: number
  data: any
  children?: TreeNode[]
}

export const useProjectStore = defineStore('project', () => {
  const projects = ref<any[]>([])
  const selectedNode = ref<TreeNode | null>(null)
  const currentProject = ref<any | null>(null)

  const treeData = computed<TreeNode[]>(() =>
    projects.value.map((p) => ({
      key: `project-${p.id}`,
      label: p.name,
      type: 'project' as const,
      id: p.id,
      data: p,
      children: (p.cabinets || []).map((c: any) => ({
        key: `cabinet-${c.id}`,
        label: c.name,
        type: 'cabinet' as const,
        id: c.id,
        data: c,
        children: (c.structure_components || []).map((sc: any) => ({
          key: `structure-${sc.id}`,
          label: sc.name,
          type: 'structure' as const,
          id: sc.id,
          data: sc,
          children: (sc.base_components || []).map((bc: any) => ({
            key: `base-${bc.id}`,
            label: `${bc.model_number || ''} ${bc.name || ''}`.trim(),
            type: 'base' as const,
            id: bc.id,
            data: bc,
          })),
        })),
      })),
    }))
  )

  async function loadProjects() {
    try {
      const res = await projectApi.list()
      const list = res.data.data || []
      
      // 并发加载所有项目树
      const detailed = await Promise.all(
        list.map(async (p: any) => {
          try {
            const treeRes = await projectApi.getTree(p.id)
            return treeRes.data.data
          } catch (error) {
            console.error(`加载项目 ${p.id} 树失败:`, error)
            return p // 如果树加载失败，至少返回基本信息
          }
        })
      )
      
      projects.value = detailed
    } catch (error: any) {
      console.error('加载项目失败:', error)
      // 如果是401错误，axios拦截器会自动处理（跳转到登录页）
      // 其他错误则重置项目列表
      if (error.response?.status !== 401) {
        projects.value = []
        throw error
      }
    }
  }

  function selectNode(node: TreeNode) {
    selectedNode.value = node
    if (node.type === 'project') {
      currentProject.value = node.data
    }
  }

  async function createProject(data: object) {
    try {
      await projectApi.create(data)
      await loadProjects()
    } catch (error) {
      console.error('创建项目失败:', error)
      throw error
    }
  }

  async function reloadProject(projectId: number) {
    try {
      console.log('reloadProject: 开始加载项目', projectId)
      const treeRes = await projectApi.getTree(projectId)
      const updatedProject = treeRes.data.data
      console.log('reloadProject: 获取到项目数据', updatedProject)
      
      // 找到并更新对应的项目
      const index = projects.value.findIndex(p => p.id === projectId)
      console.log('reloadProject: 项目索引', index)
      
      if (index >= 0) {
        // 创建新数组以确保响应式更新
        projects.value = [
          ...projects.value.slice(0, index),
          updatedProject,
          ...projects.value.slice(index + 1)
        ]
        console.log('reloadProject: 项目已更新，新数组长度', projects.value.length)
      } else {
        // 如果找不到，添加到列表
        projects.value = [...projects.value, updatedProject]
        console.log('reloadProject: 项目已添加')
      }
    } catch (error) {
      console.error(`重新加载项目 ${projectId} 失败:`, error)
      // 如果reload失败，回退到加载所有项目
      await loadProjects()
    }
  }

  async function deleteNode(node: TreeNode) {
    if (node.type === 'project') {
      await projectApi.delete(node.id)
    } else if (node.type === 'cabinet') {
      await cabinetApi.delete(node.id)
    } else if (node.type === 'structure') {
      await componentApi.deleteStructure(node.id)
    } else if (node.type === 'base') {
      await componentApi.deleteBase(node.id)
    }
    await loadProjects()
  }

  return { projects, selectedNode, currentProject, treeData, loadProjects, selectNode, createProject, deleteNode, reloadProject }
})
