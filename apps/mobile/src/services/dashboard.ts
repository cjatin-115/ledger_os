import type { DashboardSummary, DueReminder } from '../types/api';
import { apiRequest } from './apiClient';

export const dashboardService = {
  getSummary() {
    return apiRequest<DashboardSummary>('/dashboard');
  },

  getDueReminders(days = 7) {
    return apiRequest<DueReminder[]>(`/reminders/due?days=${days}`);
  },
};
