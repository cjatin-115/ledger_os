import { Platform } from 'react-native';
import Constants from 'expo-constants';

const debuggerHost = Constants.expoConfig?.hostUri;
const hostIp = debuggerHost ? debuggerHost.split(':')[0] : (Platform.OS === 'android' ? '10.0.2.2' : 'localhost');

export const APP_NAME = 'LedgerOS';

export const API_BASE_URL =
  process.env.EXPO_PUBLIC_API_URL || `http://${hostIp}:8000`;

export * from './theme';
export * from './layout';
