import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api'

interface User {
  id: number
  username: string
  role: string
}

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem('token'))
  const refreshToken = ref<string | null>(localStorage.getItem('refreshToken'))
  const user = ref<User | null>(JSON.parse(localStorage.getItem('user') || 'null'))

  const isLoggedIn = computed(() => !!token.value)

  async function login(username: string, password: string) {
    const res = await authApi.login(username, password)
    const { access_token, refresh_token, user: userData } = res.data.data
    token.value = access_token
    refreshToken.value = refresh_token
    user.value = userData
    localStorage.setItem('token', access_token)
    localStorage.setItem('refreshToken', refresh_token)
    localStorage.setItem('user', JSON.stringify(userData))
  }

  async function register(username: string, password: string, displayName?: string) {
    const res = await authApi.register(username, password, displayName)
    const { access_token, refresh_token, user: userData } = res.data.data
    token.value = access_token
    refreshToken.value = refresh_token
    user.value = userData
    localStorage.setItem('token', access_token)
    localStorage.setItem('refreshToken', refresh_token)
    localStorage.setItem('user', JSON.stringify(userData))
  }

  async function refresh() {
    if (!refreshToken.value) throw new Error('No refresh token')
    const res = await authApi.refresh(refreshToken.value)
    token.value = res.data.data.access_token
    localStorage.setItem('token', token.value!)
  }

  function logout() {
    token.value = null
    refreshToken.value = null
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('refreshToken')
    localStorage.removeItem('user')
  }

  return { token, refreshToken, user, isLoggedIn, login, register, refresh, logout }
})
