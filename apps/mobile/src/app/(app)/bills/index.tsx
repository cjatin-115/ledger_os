import { useQuery } from '@tanstack/react-query';
import { useRouter } from 'expo-router';
import React, { useMemo, useState } from 'react';
import { Pressable, StyleSheet, Text, View } from 'react-native';

import { Card } from '../../../components/Card';
import { EmptyState } from '../../../components/EmptyState';
import { Fab } from '../../../components/Fab';
import { ListRow } from '../../../components/ListRow';
import { LoadingScreen, Screen } from '../../../components/Screen';
import { ScreenHeader } from '../../../components/ScreenHeader';
import { StatusBadge } from '../../../components/StatusBadge';
import { billsService } from '../../../services/bills';
import { formatDate } from '../../../utils/format';
import { colors, spacing } from '../../../constants/theme';

export default function BillsScreen() {
  const router = useRouter();
  const [statusFilter, setStatusFilter] = useState<string | undefined>();

  const { data: bills = [], isLoading, refetch, isRefetching } = useQuery({
    queryKey: ['bills', statusFilter],
    queryFn: () => billsService.list(statusFilter ? { status: statusFilter } : undefined),
  });

  const sorted = useMemo(
    () => [...bills].sort((a, b) => b.bill_date.localeCompare(a.bill_date)),
    [bills],
  );

  if (isLoading) return <LoadingScreen />;

  return (
    <View style={styles.wrap}>
      <Screen refreshing={isRefetching} onRefresh={refetch}>
        <ScreenHeader title="Bills" subtitle={`${bills.length} total`} />

        <View style={styles.filters}>
          {['All', 'draft', 'posted', 'partially_paid', 'paid'].map((item) => {
            const active = (item === 'All' && !statusFilter) || statusFilter === item;
            return (
              <Pressable
                key={item}
                style={[styles.chip, active && styles.chipActive]}
                onPress={() => setStatusFilter(item === 'All' ? undefined : item)}
              >
                <Text style={[styles.chipText, active && styles.chipTextActive]}>
                  {item === 'All' ? 'All' : item.replace(/_/g, ' ')}
                </Text>
              </Pressable>
            );
          })}
        </View>

        <Card padding={0}>
          {sorted.length === 0 ? (
            <EmptyState
              icon="document-text-outline"
              title="No bills yet"
              message="Scan an invoice or add a bill manually to get started."
              actionLabel="Scan bill"
              onAction={() => router.push('/(app)/bills/scan')}
            />
          ) : (
            sorted.map((bill) => (
              <ListRow
                key={bill.id}
                title={bill.bill_number}
                subtitle={`${formatDate(bill.bill_date)}${bill.due_date ? ` · Due ${formatDate(bill.due_date)}` : ''}`}
                meta={`₹${parseFloat(bill.total_amount).toLocaleString('en-IN')}`}
                badge={<StatusBadge status={bill.status} />}
                icon="receipt-outline"
                onPress={() => router.push(`/(app)/bills/${bill.id}`)}
              />
            ))
          )}
        </Card>
      </Screen>

      <Fab onPress={() => router.push('/(app)/bills/scan')} icon="scan" />
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: { flex: 1 },
  filters: { flexDirection: 'row', flexWrap: 'wrap', gap: spacing.sm, marginBottom: spacing.lg },
  chip: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 999,
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.border,
  },
  chipActive: { backgroundColor: colors.primary, borderColor: colors.primary },
  chipText: { color: colors.textSecondary, fontSize: 12, fontWeight: '700', textTransform: 'capitalize' },
  chipTextActive: { color: colors.surfaceMuted },
});
