import { Stack, useRouter, useSegments } from 'expo-router';
import React, { useEffect } from 'react';

import { AppProviders } from '../providers/AppProviders';
import { LoadingScreen } from '../components/Screen';
import { useAuthStore } from '../store/authStore';

function AuthGate({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading, hydrate } = useAuthStore();
  const segments = useSegments();
  const router = useRouter();

  useEffect(() => {
    hydrate();
  }, [hydrate]);

  useEffect(() => {
    if (isLoading) return;

    const inAuthGroup = segments[0] === '(auth)';

    if (!isAuthenticated && !inAuthGroup) {
      router.replace('/(auth)/login');
    } else if (isAuthenticated && inAuthGroup) {
      router.replace('/(app)');
    }
  }, [isAuthenticated, isLoading, segments, router]);

  if (isLoading) return <LoadingScreen />;

  return <>{children}</>;
}

export default function RootLayout() {
  return (
    <AppProviders>
      <AuthGate>
        <Stack screenOptions={{ headerShown: false }} />
      </AuthGate>
    </AppProviders>
  );
}
