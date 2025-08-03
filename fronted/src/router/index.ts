import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import AppLayout from '@/components/layout/AppLayout.vue'
import Home from '@/views/Home.vue'
import ProjectsView from '@/views/project/ProjectsView.vue'
import TestCaseView from '@/views/project/TestCaseView.vue'

const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    component: AppLayout,
    children: [
      { path: '/', redirect: '/home' },
      { path: '/home', name: 'Home', component: Home },
      { path: '/projects/', name: 'projects', component: ProjectsView },
      { path: '/test-cases/', name: 'Cases', component: TestCaseView },
      { path: '/test-steps/', name: 'Steps', component: ProjectsView },
      { path: '/test-executions/', name: 'Executions', component: ProjectsView },
      { path: '/apis/', name: 'Apis', component: ProjectsView },
      { path: '/environments/', name: 'Environments', component: ProjectsView },
    ]
  },
  {
    path: '/projects',
    name: 'Projects',
    component: () => import('@/views/project/ProjectsView.vue')
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

export default router
