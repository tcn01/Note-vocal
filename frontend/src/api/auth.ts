import apiClient from "./client"
import type { LoginRequest, Token, User, UserCreate } from "../types"

export const authApi = {
  login: (data: LoginRequest) =>
    apiClient.post<Token>("/auth/login", data),

  register: (data: UserCreate) =>
    apiClient.post<User>("/users/", data),

  me: () =>
    apiClient.get<User>("/users/me"),
}

export const saveToken = (token: string) =>
  localStorage.setItem("access_token", token)

export const getToken = () =>
  localStorage.getItem("access_token")

export const clearToken = () =>
  localStorage.removeItem("access_token")
