import type { Bill, BillCreate, ExtractedBill, ScanConfirmResponse } from '../types/api';
import { apiRequest } from './apiClient';

export const billsService = {
  list(params?: { search?: string; status?: string }) {
    const query = new URLSearchParams();
    if (params?.search) query.set('search', params.search);
    if (params?.status) query.set('status', params.status);
    const qs = query.toString();
    return apiRequest<Bill[]>(`/bills${qs ? `?${qs}` : ''}`);
  },

  get(id: string) {
    return apiRequest<Bill>(`/bills/${id}`);
  },

  create(payload: BillCreate) {
    return apiRequest<Bill>('/bills', { method: 'POST', body: payload });
  },

  post(id: string) {
    return apiRequest<Bill>(`/bills/${id}/post`, { method: 'POST' });
  },

  scan(rawText: string) {
    return apiRequest<ExtractedBill>('/bills/scan', {
      method: 'POST',
      body: { raw_text: rawText },
    });
  },

  async scanImage(fileUri: string) {
    const formData = new FormData();
    const fileName = fileUri.split('/').pop() || 'bill.jpg';
    formData.append('file', {
      uri: fileUri,
      name: fileName,
      type: 'image/jpeg',
    } as any);

    return apiRequest<ExtractedBill>('/bills/scan-image', {
      method: 'POST',
      formData,
    });
  },

  confirmScan(payload: ExtractedBill) {
    return apiRequest<ScanConfirmResponse>('/bills/scan/confirm', {
      method: 'POST',
      body: payload,
    });
  },
};
