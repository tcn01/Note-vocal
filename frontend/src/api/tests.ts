import apiClient from './client';
import type { TestResult, TestResultOut, TestGenerateRequest, TestSubmitRequest } from '../types';

export const testsAPI = {
  generateTest: async (data: TestGenerateRequest): Promise<TestResultOut> => {
    const response = await apiClient.post<TestResultOut>('/tests/generate', data);
    return response.data;
  },

  submitTest: async (testId: number, data: TestSubmitRequest): Promise<TestResult> => {
    const response = await apiClient.post<TestResult>(`/tests/${testId}/submit`, data);
    return response.data;
  },

  getTests: async (): Promise<TestResult[]> => {
    const response = await apiClient.get<TestResult[]>('/tests/');
    return response.data;
  },
};