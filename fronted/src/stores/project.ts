import { defineStore } from 'pinia';
import { fetchProjects, createProject, updateProject, deleteProject } from '@/api/projects';
import type { Project } from '@/types';
import { ElMessage } from 'element-plus';

export const useProjectStore = defineStore('project', {
  state: () => ({
    projects: [] as Project[],
    loading: false,
    error: '',
  }),
  persist: true,
  actions: {
     async getProjects() {
      this.loading = true;
      this.error = '';
      try {
        const response = await fetchProjects();
        this.projects = response.results.sort((a: { id: number; }, b: { id: number; }) => a.id - b.id);
        console.log('项目数据加载成功:', this.projects);
      } catch (err) {
        this.error = '获取项目列表失败，请稍后重试';
        console.error(err);
        ElMessage.error(this.error);
      } finally {
        this.loading = false;
      }
    },

    async createProject(projectData: { name: string; description: string }) {
      try {
        await createProject(projectData);
        await this.getProjects();
        return true;
      } catch (err) {
        this.error = '创建项目失败，请稍后重试';
        console.error(err);
        throw err;
      }
    },

    async updateProject(id: number, projectData: { name: string; description: string }) {
      try {
        await updateProject(id, projectData);
        await this.getProjects();
        return true;
      } catch (err) {
        this.error = '更新项目失败，请稍后重试';
        console.error(err);
        throw err;
      }
    },

    async deleteProject(id: number) {
      try {
        await deleteProject(id);
        await this.getProjects();
        return true;
      } catch (err) {
        this.error = '删除项目失败，请稍后重试';
        console.error(err);
        throw err;
      }
    }
  }
});



