import axios from 'axios';

// 创建 axios 实例
const api = axios.create({
  baseURL: 'http://127.0.0.1:8000/api',
  timeout: 10000
});

// 获取测试用例列表（支持按项目过滤）
export const fetchTestCases = async (projectId?: number) => {
  try {
    const params = projectId ? { project: projectId } : {};
    const response = await api.get('/test-cases/', { params });
    return response.data;
  } catch (error) {
    console.error('获取测试用例列表失败:', error);
    throw error;
  }
};

// 创建测试用例
export const createTestCase = async (testCaseData: {
  name: string;
  description?: string;
  project: number;
  environment?: number;
  setup_script?: string;
  teardown_script?: string;
}) => {
  try {
    const response = await api.post('/test-cases/', testCaseData);
    return response.data;
  } catch (error) {
    console.error('创建测试用例失败:', error);
    throw error;
  }
};

// 更新测试用例
export const updateTestCase = async (testCaseId: number, testCaseData: {
  name?: string;
  description?: string;
  environment?: number;
  setup_script?: string;
  teardown_script?: string;
}) => {
  try {
    const response = await api.put(`/test-cases/${testCaseId}/`, testCaseData);
    return response.data;
  } catch (error) {
    console.error('更新测试用例失败:', error);
    throw error;
  }
};

// 删除测试用例
export const deleteTestCase = async (testCaseId: number) => {
  try {
    const response = await api.delete(`/test-cases/${testCaseId}/`);
    return response.data;
  } catch (error) {
    console.error('删除测试用例失败:', error);
    throw error;
  }
};
