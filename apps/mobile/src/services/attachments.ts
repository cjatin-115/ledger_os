import type { Attachment } from '../types/api';
import { apiRequest } from './apiClient';

type EntityType = 'bill' | 'payment' | 'supplier';

export const attachmentsService = {
  list(entityType: EntityType, entityId: string) {
    return apiRequest<Attachment[]>(`/attachments/${entityType}/${entityId}`);
  },

  upload(entityType: EntityType, entityId: string, file: { uri: string; name: string; type: string }) {
    const formData = new FormData();
    formData.append('file', {
      uri: file.uri,
      name: file.name,
      type: file.type,
    } as unknown as Blob);

    return apiRequest<Attachment>(`/attachments/${entityType}/${entityId}`, {
      method: 'POST',
      formData,
    });
  },
};
