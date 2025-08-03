import { defineStore } from 'pinia'
import type { User } from '@/types'

export const useUserStore = defineStore('user', {
  state: (): User => ({
    isLoggedIn: false,       // 登录状态
    username: '未登录',      // 用户名
  }),
  actions: {
    // 登录方法
    login(username: string = '测试用户') {
      this.isLoggedIn = true;
      this.username = username;
    },
    // 登出方法
    logout() {
      this.isLoggedIn = false;
      this.username = '未登录';
    }
  }
})
