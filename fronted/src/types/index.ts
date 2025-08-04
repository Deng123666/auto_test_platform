import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import AppLayout from '@/components/layout/AppLayout.vue'
import Home from '@/views/Home.vue'
import Module1 from '@/views/Module1.vue'
import Module2 from '@/views/Module2.vue'

const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    component: AppLayout,
    children: [
      { path: '/home', name: 'Home', component: Home },
      { path: '/module1', name: 'Module1', component: Module1 },
      { path: '/module2', name: 'Module2', component: Module2 },

      // 更新为命名的重定向，更安全可靠
      { path: '/', redirect: { name: 'Home' } }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

export default router

export interface MenuItem {
  index: string;             // 路由地址或唯一标识
  title: string;             // 菜单显示名称
  icon?: any;                // 图标组件 (类型为 Vue 组件)
  children?: MenuItem[];     // 子菜单项
  routeName?: string;        // 路由名称
}

// 项目类型
export interface Project {
  id: number;
  name: string;
  description: string | null;
  created_at: string;
  updated_at: string;
}

// 测试用例类型
export interface TestCase {
  id: number;
  name: string;
  description: string | null;
  created_at: string;
  updated_at: string;
  project?: number; // 关联的项目ID
}

// API响应类型
export interface ApiResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}
