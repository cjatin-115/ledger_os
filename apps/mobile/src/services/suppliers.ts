import type { Supplier, SupplierCreate } from '../types/api';
import { apiRequest } from './apiClient';

export const suppliersService = {
  list() {
    return apiRequest<Supplier[]>('/suppliers');
  },

  get(id: string) {
    return apiRequest<Supplier>(`/suppliers/${id}`);
  },

  create(payload: SupplierCreate) {
    return apiRequest<Supplier>('/suppliers', { method: 'POST', body: payload });
  },

  update(id: string, payload: Partial<SupplierCreate & { is_active?: boolean }>) {
    return apiRequest<Supplier>(`/suppliers/${id}`, { method: 'PATCH', body: payload });
  },
};
