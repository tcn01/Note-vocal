import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { authApi, saveToken, clearToken } from "../api/auth"

export function useAuth() {
  const queryClient = useQueryClient()

  const { data: user, isLoading } = useQuery({
    queryKey: ["auth", "me"],
    queryFn: async () => {
      const res = await authApi.me()
      return res.data
    },
    retry: false,
    enabled: !!localStorage.getItem("access_token"),
  })

  const login = useMutation({
    mutationFn: authApi.login,
    onSuccess: (res) => {
      saveToken(res.data.access_token)
      queryClient.invalidateQueries({ queryKey: ["auth", "me"] })
    },
  })

  const register = useMutation({
    mutationFn: authApi.register,
  })

  const logout = () => {
    clearToken()
    queryClient.setQueryData(["auth", "me"], null)
    queryClient.invalidateQueries({ queryKey: ["auth", "me"] })
  }

  return { user, isLoading, login, register, logout, isAuthenticated: !!user }
}
