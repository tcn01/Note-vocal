import apiClient from "./client"
import type { Vocabulary } from "../types"

export const vocabularyApi = {
  list: (params?: { skip?: number; limit?: number }) =>
    apiClient.get<Vocabulary[]>("/vocabularies/", { params }),

  get: (id: number) =>
    apiClient.get<Vocabulary>(`/vocabularies/${id}`),

  create: (data: Partial<Vocabulary>) =>
    apiClient.post<Vocabulary>("/vocabularies/", data),

  update: (id: number, data: Partial<Vocabulary>) =>
    apiClient.patch<Vocabulary>(`/vocabularies/${id}`, data),

  delete: (id: number) =>
    apiClient.delete<void>(`/vocabularies/${id}`),
}
