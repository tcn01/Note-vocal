import apiClient from './client';
import type {
  GrammarTopicProgress,
  TodayPlan,
  GrammarLesson,
  GrammarLessonUpdate,
  GrammarGenerateRequest,
} from '../types';

export const grammarAPI = {
  getCurriculum: async (level?: string): Promise<GrammarTopicProgress[]> => {
    const params = level ? { level } : {};
    const response = await apiClient.get<GrammarTopicProgress[]>('/ai/grammar/curriculum', { params });
    return response.data;
  },

  getTodayPlan: async (): Promise<TodayPlan> => {
    const response = await apiClient.get<TodayPlan>('/ai/grammar/today');
    return response.data;
  },

  getNextTopic: async (): Promise<GrammarTopicProgress> => {
    const response = await apiClient.get<GrammarTopicProgress>('/ai/grammar/next');
    return response.data;
  },

  generateLesson: async (data: GrammarGenerateRequest): Promise<GrammarLesson> => {
    const response = await apiClient.post<GrammarLesson>('/ai/grammar/generate', data);
    return response.data;
  },

  updateLesson: async (lessonId: number, data: GrammarLessonUpdate): Promise<GrammarLesson> => {
    const response = await apiClient.patch<GrammarLesson>(`/ai/grammar/lessons/${lessonId}`, data);
    return response.data;
  },

  getLessons: async (): Promise<GrammarLesson[]> => {
    const response = await apiClient.get<GrammarLesson[]>('/ai/grammar/lessons');
    return response.data;
  },
};