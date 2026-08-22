import { Platform } from 'react-native';

export const APP_NAME = 'LedgerOS';

/** Android emulator maps host machine localhost to 10.0.2.2 */
export const API_BASE_URL =
  Platform.OS === 'android' ? 'http://10.0.2.2:8000' : 'http://localhost:8000';

export * from './theme';
export * from './layout';
