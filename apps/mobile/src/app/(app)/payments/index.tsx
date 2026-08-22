import { useQuery } from '@tanstack/react-query';
import { useRouter } from 'expo-router';
import React from 'react';
import { StyleSheet, View } from 'react-native';

import { EmptyState } from '../../../components/EmptyState';
import { Fab } from '../../../components/Fab';
import { ListRow } from '../../../components/ListRow';
import { LoadingScreen, Screen } from '../../../components/Screen';
import { ScreenHeader } from '../../../components/ScreenHeader';
import { StatusBadge } from '../../../components/StatusBadge';
import type { Payment } from '../../../types/api';
import { paymentsService } from '../../../services/payments';
import { formatDate } from '../../../utils/format';

export default function PaymentsScreen() {
  const router = useRouter();

  const { data: payments = [], isLoading, refetch, isRefetching } = useQuery({
    queryKey: ['payments'],
    queryFn: () => paymentsService.list(),
  });

  if (isLoading) return <LoadingScreen />;

  return (
    <View style={styles.wrap}>
      <Screen refreshing={isRefetching} onRefresh={refetch}>
        <ScreenHeader title="Payments" subtitle={`${payments.length} recorded`} />

        {payments.length === 0 ? (
          <EmptyState
            icon="wallet-outline"
            title="No payments yet"
            message="Record a payment to settle supplier bills."
            actionLabel="Record payment"
            onAction={() => router.push('/(app)/payments/new')}
          />
        ) : (
          payments.map((payment: Payment) => (
            <ListRow
              key={payment.id}
              title={payment.payment_method.toUpperCase()}
              subtitle={`${formatDate(payment.payment_date)}${payment.reference_number ? ` · ${payment.reference_number}` : ''}`}
              meta={`₹${parseFloat(payment.amount).toLocaleString('en-IN')}`}
              badge={<StatusBadge status={payment.status} />}
              icon="cash-outline"
              onPress={() => router.push(`/(app)/payments/${payment.id}`)}
            />
          ))
        )}
      </Screen>

      <Fab onPress={() => router.push('/(app)/payments/scan')} icon="scan" />
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: { flex: 1 },
});
