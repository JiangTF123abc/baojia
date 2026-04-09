import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

const api = axios.create({ baseURL: '/api' })

// 请求拦截器：注入 JWT
api.interceptors.request.use((config) => {
  const auth = useAuthStore()
  if (auth.token) {
    config.headers.Authorization = `Bearer ${auth.token}`
  }
  return config
})

// 响应拦截器：处理 401 自动跳转
api.interceptors.response.use(
  (res) => res,
  async (error) => {
    if (error.response?.status === 401) {
      const auth = useAuthStore()
      // 尝试刷新令牌
      if (auth.refreshToken && !error.config._retry) {
        error.config._retry = true
        try {
          await auth.refresh()
          error.config.headers.Authorization = `Bearer ${auth.token}`
          return api(error.config)
        } catch {
          auth.logout()
          window.location.href = '/login'
        }
      } else {
        auth.logout()
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

export default api

// ── 认证 API ──
export const authApi = {
  login: (username: string, password: string) =>
    api.post('/auth/login', { username, password }),
  register: (username: string, password: string, displayName?: string) =>
    api.post('/auth/register', { username, password, display_name: displayName }),
  refresh: (refreshToken: string) =>
    api.post('/auth/refresh', { refresh_token: refreshToken }),
  logout: () => api.post('/auth/logout'),
}

// ── 项目 API ──
export const projectApi = {
  list: () => api.get('/projects'),
  get: (id: number) => api.get(`/projects/${id}`),
  getTree: (id: number) => api.get(`/projects/${id}/tree`),
  create: (data: object) => api.post('/projects', data),
  update: (id: number, data: object) => api.put(`/projects/${id}`, data),
  delete: (id: number) => api.delete(`/projects/${id}`),
}

// ── 配电柜 API ──
export const cabinetApi = {
  create: (data: object) => api.post('/cabinets', data),
  update: (id: number, data: object) => api.put(`/cabinets/${id}`, data),
  delete: (id: number) => api.delete(`/cabinets/${id}`),
  copy: (id: number) => api.post(`/cabinets/${id}/copy`),
  move: (id: number, targetProjectId: number) =>
    api.put(`/cabinets/${id}/move`, { target_project_id: targetProjectId }),
  autoMatch: (id: number) => api.post(`/cabinets/${id}/auto-match`),
  applyHideRules: (id: number) => api.post(`/cabinets/${id}/apply-hide-rules`),
  getAutoMatchPreview: (id: number) => api.get(`/cabinets/${id}/auto-match-preview`),
}

// ── 柜体配置 API ──
export const cabinetConfigApi = {
  list: (params?: object) => api.get('/cabinet-type-configs', { params }),
  get: (id: number) => api.get(`/cabinet-type-configs/${id}`),
  getAutoMatchRules: (id: number) => api.get(`/cabinet-type-configs/${id}/auto-match-rules`),
  create: (data: object) => api.post('/cabinet-type-configs', data),
  update: (id: number, data: object) => api.put(`/cabinet-type-configs/${id}`, data),
  delete: (id: number) => api.delete(`/cabinet-type-configs/${id}`),
  search: (params: object) => api.get('/cabinet-type-configs/search', { params }),
}

// ── 组件 API ──
export const componentApi = {
  createStructure: (data: object) => api.post('/structure-components', data),
  updateStructure: (id: number, data: object) => api.put(`/structure-components/${id}`, data),
  deleteStructure: (id: number) => api.delete(`/structure-components/${id}`),
  createBase: (data: object) => api.post('/base-components', data),
  updateBase: (id: number, data: object) => api.put(`/base-components/${id}`, data),
  deleteBase: (id: number) => api.delete(`/base-components/${id}`),
}

// ── 材料 API ──
export const materialApi = {
  search: (query: string) => api.get('/materials/search', { params: { q: query } }),
  getAccessories: (id: number) => api.get(`/materials/${id}/accessories`),
}

// ── 模板 API ──
export const templateApi = {
  list: () => api.get('/templates'),
  save: (data: object) => api.post('/templates', data),
  apply: (id: number, projectId: number) =>
    api.post(`/templates/${id}/apply`, { target_project_id: projectId }),
  delete: (id: number) => api.delete(`/templates/${id}`),
}

// ── BOM API ──
export const bomApi = {
  upload: (file: File) => {
    const form = new FormData()
    form.append('file', file)
    return api.post('/bom/upload', form, { headers: { 'Content-Type': 'multipart/form-data' } })
  },
  confirm: (data: object) => api.post('/bom/confirm', data),
}

// ── 报表 API ──
export const reportApi = {
  generateInternalPricing: (projectId: number, params?: object) =>
    api.post(`/reports/internal-pricing/${projectId}`, params || {}),
  generateCustomerQuotation: (projectId: number, params?: object) =>
    api.post(`/reports/customer-quotation/${projectId}`, params || {}),
  download: (token: string) => `/api/reports/download/${token}`,
}

// ── 价格引擎 API ──
export const priceApi = {
  calculate: (data: object) => api.post('/price-engine/calculate', data),
  calculateLabor: (cabinetId: number, baseCost: number) =>
    api.post('/price-engine/calculate-labor', { cabinet_id: cabinetId, base_cost: baseCost }),
  listFormulas: () => api.get('/price-formulas'),
}

// ── 审计日志 API ──
export const auditApi = {
  query: (params?: object) => api.get('/audit-logs', { params }),
  export: (params?: object) => api.get('/audit-logs/export', { params }),
}
