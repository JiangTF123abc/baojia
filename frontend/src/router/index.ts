import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'Login',
      component: () => import('@/views/LoginView.vue'),
      meta: { requiresAuth: false }
    },
    {
      path: '/register',
      name: 'Register',
      component: () => import('@/views/RegisterView.vue'),
      meta: { requiresAuth: false }
    },
    {
      path: '/',
      component: () => import('@/views/MainLayout.vue'),
      meta: { requiresAuth: true },
      children: [
        { path: '', redirect: '/projects' },
        { path: 'projects', component: () => import('@/views/ProjectList.vue'), children: [
          { path: ':id', name: 'ProjectDetail', component: () => import('@/views/ProjectDetail.vue') },
        ]},
        { path: 'templates', name: 'Templates', component: () => import('@/views/TemplateLibrary.vue') },
        { path: 'admin', name: 'Admin', component: () => import('@/views/AdminPanel.vue'), meta: { requiresRole: 'admin' } }
      ]
    },
    { path: '/:pathMatch(.*)*', redirect: '/' }
  ]
})

router.beforeEach((to) => {
  const auth = useAuthStore()
  if (to.meta.requiresAuth !== false && !auth.isLoggedIn) {
    return { name: 'Login' }
  }
  if (to.meta.requiresRole && auth.user?.role !== to.meta.requiresRole) {
    return { path: '/' }
  }
})

export default router
