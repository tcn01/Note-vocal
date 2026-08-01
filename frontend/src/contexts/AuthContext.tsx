import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { authAPI } from '../api/auth';
import type { User, Token } from '../types';

interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (email: string, password: string) => Promise<void>;
  register: (data: { email: string; name: string; password: string; preferred_language?: string }) => Promise<void>;
  logout: () => void;
  isLoading: boolean;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(localStorage.getItem('visionnest_token'));
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (token) {
      authAPI.getCurrentUser()
        .then(setUser)
        .catch(() => {
          localStorage.removeItem('visionnest_token');
          setToken(null);
        })
        .finally(() => setIsLoading(false));
    } else {
      setIsLoading(false);
    }
  }, []);

  const login = async (email: string, password: string) => {
    const data: Token = await authAPI.login(email, password);
    localStorage.setItem('visionnest_token', data.access_token);
    setToken(data.access_token);
    const userData = await authAPI.getCurrentUser();
    setUser(userData);
  };

  const register = async (data: { email: string; name: string; password: string; preferred_language?: string }) => {
    const user = await authAPI.register(data);
    const tokenData: Token = await authAPI.login(data.email, data.password);
    localStorage.setItem('visionnest_token', tokenData.access_token);
    setToken(tokenData.access_token);
    setUser(user);
  };

  const logout = () => {
    localStorage.removeItem('visionnest_token');
    setToken(null);
    setUser(null);
  };

  const value: AuthContextType = {
    user,
    token,
    login,
    register,
    logout,
    isLoading,
    isAuthenticated: !!token && !!user,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}