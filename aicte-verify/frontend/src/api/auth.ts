import apiClient from './client';
import { User, UserRole } from '../types';
import { mockUsers } from './mockData';

export interface LoginCredentials {
  username: string;
  password?: string;
}

export interface AuthResponse {
  token: string;
  user: User;
}
export const authApi = {
  login: async (credentials: LoginCredentials): Promise<AuthResponse> => {
    try {
      const response = await apiClient.post<any>('/auth/login', credentials);
      const token = response.data.access_token || response.data.token;
      const user = response.data.user;
      if (!token) {
        throw new Error('No token returned');
      }
      localStorage.setItem('aicte_token', token);
      localStorage.setItem('aicte_user', JSON.stringify(user));
      return { token, user };
    } catch {
      // Fallback for demonstration / local testing
      const foundUser = mockUsers.find(
        (u) =>
          u.username.toLowerCase() === credentials.username.toLowerCase() ||
          u.email.toLowerCase() === credentials.username.toLowerCase()
      ) || mockUsers[0];

      const mockResponse: AuthResponse = {
        token: `mock_jwt_token_${foundUser.role}_${Date.now()}`,
        user: foundUser,
      };

      localStorage.setItem('aicte_token', mockResponse.token);
      localStorage.setItem('aicte_user', JSON.stringify(mockResponse.user));
      return mockResponse;
    }
  },

  register: async (userData: Partial<User>): Promise<User> => {
    try {
      const response = await apiClient.post<User>('/auth/register', userData);
      return response.data;
    } catch {
      const newUser: User = {
        id: `u-${Date.now()}`,
        username: userData.username || 'new_user',
        email: userData.email || 'user@example.com',
        full_name: userData.full_name || 'New AICTE User',
        role: userData.role || 'college_user',
        institution_name: userData.institution_name,
        created_at: new Date().toISOString(),
      };
      mockUsers.push(newUser);
      return newUser;
    }
  },

  getMe: async (): Promise<User> => {
    try {
      const response = await apiClient.get<User>('/auth/me');
      return response.data;
    } catch {
      const saved = localStorage.getItem('aicte_user');
      if (saved && saved !== 'undefined' && saved !== 'null') {
        try {
          return JSON.parse(saved);
        } catch {
          return mockUsers[0];
        }
      }
      return mockUsers[0];
    }
  },

  getUsers: async (): Promise<User[]> => {
    try {
      const response = await apiClient.get<User[]>('/users');
      return response.data;
    } catch {
      return [...mockUsers];
    }
  },

  updateUserRole: async (userId: string, role: UserRole): Promise<User> => {
    try {
      const response = await apiClient.patch<User>(`/users/${userId}/role`, { role });
      return response.data;
    } catch {
      const user = mockUsers.find((u) => u.id === userId);
      if (user) {
        user.role = role;
        return { ...user };
      }
      throw new Error('User not found');
    }
  },

  logout: () => {
    localStorage.removeItem('aicte_token');
    localStorage.removeItem('aicte_user');
  },
};
