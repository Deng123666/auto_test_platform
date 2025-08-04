<template>
  <div class="sidebar-container">
    <el-menu
      router
      :default-active="$route.path"
      class="custom-menu"
      background-color="#ffffff"
      text-color="#333333"
      active-text-color="#409eff"
    >
      <!-- 模块导航区域 -->
      <el-menu-item
        v-for="item in topLevelMenus"
        :key="item.index"
        :index="item.index"
        class="menu-item"
      >
        <el-icon v-if="item.icon">
          <component :is="item.icon" />
        </el-icon>
        <span>{{ item.title }}</span>
      </el-menu-item>

      <!-- 带子菜单的导航项 -->
      <el-sub-menu
        v-for="menu in subMenus"
        :key="menu.index"
        :index="menu.index"
        class="sub-menu"
      >
        <template #title>
          <el-icon v-if="menu.icon">
            <component :is="menu.icon" />
          </el-icon>
          <span>{{ menu.title }}</span>
        </template>
        <el-menu-item
          v-for="child in menu.children"
          :key="child.index"
          :index="child.index"
          class="sub-menu-item"
        >
          {{ child.title }}
        </el-menu-item>
      </el-sub-menu>
    </el-menu>

    <!-- 登录状态 -->
    <div class="fixed-footer">
      <div class="user-info">
        <el-icon :color="userStore.isLoggedIn ? '#67c23a' : '#f56c6c'"><User /></el-icon>
        <span class="username">{{ userStore.username || '未登录' }}</span>
      </div>
      <el-button
        v-if="!userStore.isLoggedIn"
        type="primary"
        size="small"
        plain
        @click="userStore.login()"
      >登录</el-button>
      <el-button
        v-else
        type="danger"
        size="small"
        plain
        @click="userStore.logout()"
      >登出</el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import {
  HomeFilled,
  Folder,
  CircleCheckFilled,
  User,
  List,
  Calendar
} from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import type { MenuItem } from '@/types'

const route = useRoute()
const userStore = useUserStore()

// 定义菜单结构
const menus: MenuItem[] = [
  {
    index: '/home',
    title: '仪表板',
    icon: HomeFilled
  },
  {
    index: '/projects',
    title: '项目管理',
    icon: Folder,
  },
  {
    index: '/test-cases',
    title: '用例管理',
    icon: CircleCheckFilled,
  },
  {
    index: '/test-execution',
    title: '自动化测试',
    icon: Calendar,
  },
  {
    index: '/reports',
    title: '测试结果',
    icon: List,
  }
]

// 分类菜单项
const topLevelMenus = computed(() => menus.filter(menu => !menu.children))
const subMenus = computed(() => menus.filter(menu => menu.children))
</script>

<style scoped>
.sidebar-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  width: 100%;
  border-right: 1px solid #e6e6e6;
  background-color: #ffffff;
}

.custom-menu {
  border-right: none;
  flex-grow: 1;
}

.menu-item, .sub-menu-item {
  height: 48px;
  line-height: 48px;
  margin: 4px 0;
  border-radius: 4px;
}

.menu-item:hover, .sub-menu-item:hover {
  background-color: #f5f7fa !important;
}

.sub-menu :deep(.el-sub-menu__title) {
  height: 48px;
  line-height: 48px;
  margin: 4px 0;
  border-radius: 4px;
}

.sub-menu :deep(.el-sub-menu__title:hover) {
  background-color: #f5f7fa !important;
}

.fixed-footer {
  padding: 16px;
  border-top: 1px solid #e6e6e6;
  background-color: #ffffff;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.user-info {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
  color: #333;
}

.username {
  margin-left: 8px;
  font-size: 14px;
}

.el-button {
  width: 100%;
  margin: 4px 0;
}
</style>
