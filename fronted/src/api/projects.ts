import axios from 'axios';
import Project from '@/views/project/ProjectsView.vue';

// 创建 axios 实例
const api = axios.create({
  baseURL: 'http://127.0.0.1:8000/api', // 替换为你的API基础URL
  timeout: 10000
});

// 获取项目列表
export const fetchProjects = async () => {
  try {
    const response = await api.get('/projects');
    return response.data;
  } catch (error) {
    console.error('获取项目列表失败:', error);
    throw error;
  }
};

// 添加获取单个项目详情的API方法
export const fetchProjectDetail = async (projectId: number) => {
  try {
    const response = await api.get('/projects/${projectId}/');
    return response.data;
  } catch (error) {
    console.error('获取项目详情失败:', error);
    throw error;
  }
};

// 其他项目相关API可以继续在这里添加
export const createProject = async (projectData: { name: string; description: string; }) => {
  try {
    const response = await api.post('/projects/', projectData);
    return response.data;
  } catch (error) {
    console.error('创建项目失败:', error);
    throw error;
  }
};

export const updateProject = async (projectId: number, projectData: { name: string; description: string; }) => {
  try {
    const response = await api.put(`/projects/${projectId}/`, projectData);
    return response.data;
  } catch (error) {
    console.error('更新项目失败:', error);
    throw error;
  }
};

export const deleteProject = async (projectId: number) => {
  try {
    const response = await api.delete(`/projects/${projectId}/`);
    return response.data;
  } catch (error) {
    console.error('删除项目失败:', error);
    throw error;
  }
};
