import { defineStore } from 'pinia';
import { createTestCase, deleteTestCase, fetchTestCases, updateTestCase } from '@/api/test_cases';
import type { TestCase } from '@/types';

export const useTestCaseStore = defineStore('testCase', {
  state: () => ({
    testCases: [] as TestCase[],
    loading: false,
    error: '',
  }),
  actions: {
    async getTestCases(projectId: number) {
      this.loading = true;
      this.error = '';
      try {
        const response = await fetchTestCases(projectId);
        this.testCases = response.results.sort((a: { id: number; }, b: { id: number; }) => a.id - b.id);
      } catch (err) {
        this.error = '获取用例列表失败，请稍后重试';
        console.error(err);
      } finally {
        this.loading = false;
      }
    },

    async createTestCase(testCaseData: { name: string; description: string; project: number }) {
      try {
        await createTestCase(testCaseData);
        await this.getTestCases(testCaseData.project);
        return true;
      } catch (err) {
        this.error = '创建用例失败，请稍后重试';
        console.error(err);
        throw err;
      }
    },

    async updateTestCase(id: number, testCaseData: { name: string; description: string; project: number }) {
      try {
        await updateTestCase(id, testCaseData);
        await this.getTestCases(testCaseData.project);
        return true;
      } catch (err) {
        this.error = '更新用例失败，请稍后重试';
        console.error(err);
        throw err;
      }
    },

    async deleteTestCase(id: number, projectId: number) {
      try {
        await deleteTestCase(id);
        await this.getTestCases(projectId);
        return true;
      } catch (err) {
        this.error = '删除用例失败，请稍后重试';
        console.error(err);
        throw err;
      }
    }
  }
});
