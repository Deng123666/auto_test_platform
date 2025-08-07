import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import AppLayout from '@/components/layout/AppLayout.vue'
import Home from '@/views/Home.vue'
import ProjectsView from '@/views/project/ProjectsView.vue'
import TestCaseView from '@/views/test-case/TestCaseView.vue'
// import CaseDetailView from '@/views/test-case/CaseDetailView.vue'
import HistoryTasksView from '@/views/task/HistoryTasksView.vue'
import ReportsView from '@/views/report/ReportsView.vue'

const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    component: AppLayout,
    children: [
      { path: '/', redirect: '/home' },
      { path: '/home', name: 'Home', component: Home },
      { path: '/projects/', name: 'projects', component: ProjectsView },
      { path: '/project/:projectId/', name: 'ProjectDetailCases', component: TestCaseView, props: true },
      { path: '/test-cases/', name: 'Cases', component: TestCaseView },
      { path: '/test-executions/', name: 'Executions', component: HistoryTasksView },
      { path: '/reports/', name: 'Reports', component: ReportsView}
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
