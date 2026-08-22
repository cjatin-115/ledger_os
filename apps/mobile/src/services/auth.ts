import { Platform } from 'react-native';

import type {
  LoginRequest,
  RegisterRequest,
  TokenResponse,
  UserProfile,
} from '../types/api';
import { apiRequest } from './apiClient';
import { clearTokens, getOrCreateDeviceId, setTokens } from './tokenStorage';

export const authService = {
  async login(payload: Omit<LoginRequest, 'device_id' | 'device_name'>): Promise<TokenResponse> {
    const deviceId = await getOrCreateDeviceId();
    const tokens = await apiRequest<TokenResponse>('/auth/login', {
      method: 'POST',
      auth: false,
      body: {
        ...payload,
        device_id: deviceId,
        device_name: Platform.OS === 'ios' ? 'iOS Device' : 'Android Device',
      },
    });
    await setTokens(tokens.access_token, tokens.refresh_token);
    return tokens;
  },

  async register(payload: RegisterRequest): Promise<UserProfile> {
    return apiRequest<UserProfile>('/auth/register', {
      method: 'POST',
      auth: false,
      body: payload,
    });
  },

  async getProfile(): Promise<UserProfile> {
    return apiRequest<UserProfile>('/auth/me');
  },

  async logout(): Promise<void> {
    await clearTokens();
  },
};
