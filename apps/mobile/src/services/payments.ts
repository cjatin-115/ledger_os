import type { Payment, PaymentCreate, ExtractedPayment, PaymentScanConfirmResponse } from '../types/api';
import { apiRequest } from './apiClient';

export const paymentsService = {
  list() {
    return apiRequest<Payment[]>('/payments');
  },

  get(id: string) {
    return apiRequest<Payment>(`/payments/${id}`);
  },

  create(payload: PaymentCreate) {
    return apiRequest<Payment>('/payments', { method: 'POST', body: payload });
  },

  allocate(paymentId: string, billId: string, amount: string) {
    return apiRequest(`/payments/${paymentId}/allocate`, {
      method: 'POST',
      body: { bill_id: billId, amount },
    });
  },

  scan(rawText: string) {
    return apiRequest<ExtractedPayment>('/payments/scan', {
      method: 'POST',
      body: { raw_text: rawText },
    });
  },

  async scanImage(fileUri: string) {
    const formData = new FormData();
    const fileName = fileUri.split('/').pop() || 'upi_payment.jpg';
    formData.append('file', {
      uri: fileUri,
      name: fileName,
      type: 'image/jpeg',
    } as any);

    return apiRequest<ExtractedPayment>('/payments/scan-image', {
      method: 'POST',
      formData,
    });
  },

  confirmScan(payload: ExtractedPayment) {
    return apiRequest<PaymentScanConfirmResponse>('/payments/scan/confirm', {
      method: 'POST',
      body: payload,
    });
  },
};
