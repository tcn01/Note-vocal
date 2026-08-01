import apiClient from './client';
import type { Token, User, UserGrammarSettings } from '../types';

export const authAPI = {
  login: async (email: string, password: string): Promise<Token> => {
    const response = await apiClient.post<Token>('/auth/login', { email, password });
    return response.data;
  },

  register: async (data: { email: string; name: string; password: string; preferred_language?: string }): Promise<User> => {
    const response = await apiClient.post<User>('/users/', data);
    return response.data;
  },

  getCurrentUser: async (): Promise<User> => {
    const response = await apiClient.get<User>('/users/me');
    return response.data;
  },

  setGrammarLevel: async (level: string): Promise<UserGrammarSettings> => {
    const response = await apiClient.patch<UserGrammarSettings>('/users/me/grammar-level', {
      grammar_level: level,
    });
    return response.data;
  },
};