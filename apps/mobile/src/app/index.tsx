import { Redirect } from 'expo-router';
import React from 'react';
import { useAuthStore } from '../store/authStore';

export default function Index() {
  const { isAuthenticated } = useAuthStore();

  if (isAuthenticated) {
    return <Redirect href="/(app)" />;
  }

  return <Redirect href="/(auth)/login" />;
}
