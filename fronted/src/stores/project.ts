import { defineStore } from 'pinia';
import { fetchProjects, createProject, updateProject, deleteProject } from '@/api/projects';
import type { Project } from '@/views/project/ProjectsView.vue';

export const useProjectStore = defineStore('project', {
  state: () => ({
    projects: [] as Project[],
    loading: false,
    error: '',
  }),
  actions: {
    async getProjects() {
      this.loading = true;
      this.error = '';
      try {
        const response = await fetchProjects();
        this.projects = response.results.sort((a, b) => a.id - b.id);
      } catch (err) {
        this.error = '获取项目列表失败，请稍后重试';
        console.error(err);
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
