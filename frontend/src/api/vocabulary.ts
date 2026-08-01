import apiClient from './client';
import type { Vocabulary, LookupWordRequest } from '../types';

export const vocabularyAPI = {
  lookupWord: async (data: LookupWordRequest): Promise<Vocabulary> => {
    const response = await apiClient.post<Vocabulary>('/ai/lookup-word', data);
    return response.data;
  },

  getVocabulary: async (fromDate?: string, toDate?: string, skip = 0, limit = 100): Promise<Vocabulary[]> => {
    const params: Record<string, string | number> = { skip, limit };
    if (fromDate) params.from_date = fromDate;
    if (toDate) params.to_date = toDate;
    const response = await apiClient.get<Vocabulary[]>('/ai/vocabulary', { params });
    return response.data;
  },

  deleteWord: async (vocabId: number): Promise<void> => {
    await apiClient.delete(`/ai/vocabulary/${vocabId}`);
  },

  toggleImportant: async (vocabId: number): Promise<Vocabulary> => {
    const response = await apiClient.patch<Vocabulary>(`/ai/vocabulary/${vocabId}/toggle-important`);
    return response.data;
  },
};