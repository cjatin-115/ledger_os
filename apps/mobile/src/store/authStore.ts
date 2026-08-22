import { create } from 'zustand';

import type { UserProfile } from '../types/api';
import { authService } from '../services/auth';
import { getAccessToken } from '../services/tokenStorage';

type AuthState = {
  user: UserProfile | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  hydrate: () => Promise<void>;
  setUser: (user: UserProfile | null) => void;
  login: (identifier: string, password: string) => Promise<void>;
  register: (payload: {
    organization_name: string;
    full_name: string;
    email?: string;
    phone_number: string;
    password: string;
  }) => Promise<void>;
  logout: () => Promise<void>;
};

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isAuthenticated: false,
  isLoading: true,

  setUser: (user) => set({ user, isAuthenticated: !!user }),

  hydrate: async () => {
    try {
      const token = await getAccessToken();
      if (!token) {
        set({ user: null, isAuthenticated: false, isLoading: false });
        return;
      }
      const user = await authService.getProfile();
      set({ user, isAuthenticated: true, isLoading: false });
    } catch {
      set({ user: null, isAuthenticated: false, isLoading: false });
    }
  },

  login: async (identifier, password) => {
    const isEmail = identifier.includes('@');
    await authService.login(
      isEmail
        ? { email: identifier, password }
        : { phone_number: identifier, password },
    );
    const user = await authService.getProfile();
    set({ user, isAuthenticated: true });
  },

  register: async (payload) => {
    await authService.register(payload);
    await authService.login({ phone_number: payload.phone_number, password: payload.password });
    const user = await authService.getProfile();
    set({ user, isAuthenticated: true });
  },

  logout: async () => {
    await authService.logout();
    set({ user: null, isAuthenticated: false });
  },
}));
