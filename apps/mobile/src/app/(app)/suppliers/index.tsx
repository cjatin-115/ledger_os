import { useQuery } from '@tanstack/react-query';
import { useRouter } from 'expo-router';
import React from 'react';
import { StyleSheet, View } from 'react-native';

import { EmptyState } from '../../../components/EmptyState';
import { Fab } from '../../../components/Fab';
import { ListRow } from '../../../components/ListRow';
import { LoadingScreen, Screen } from '../../../components/Screen';
import { ScreenHeader } from '../../../components/ScreenHeader';
import type { Supplier } from '../../../types/api';
import { suppliersService } from '../../../services/suppliers';

export default function SuppliersScreen() {
  const router = useRouter();

  const { data: suppliers = [], isLoading, refetch, isRefetching } = useQuery({
    queryKey: ['suppliers'],
    queryFn: () => suppliersService.list(),
  });

  if (isLoading) return <LoadingScreen />;

  return (
    <View style={styles.wrap}>
      <Screen refreshing={isRefetching} onRefresh={refetch}>
        <ScreenHeader title="Suppliers" subtitle={`${suppliers.length} vendors`} />

        {suppliers.length === 0 ? (
          <EmptyState
            icon="people-outline"
            title="No suppliers yet"
            message="Add your first supplier to start recording bills."
            actionLabel="Add supplier"
            onAction={() => router.push('/(app)/suppliers/new')}
          />
        ) : (
          suppliers.map((supplier: Supplier) => (
            <ListRow
              key={supplier.id}
              title={supplier.name}
              subtitle={[supplier.phone, supplier.gstin].filter(Boolean).join(' · ') || 'No contact info'}
              icon="storefront-outline"
              onPress={() => router.push(`/(app)/suppliers/${supplier.id}`)}
            />
          ))
        )}
      </Screen>

      <Fab onPress={() => router.push('/(app)/suppliers/new')} />
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: { flex: 1 },
});
