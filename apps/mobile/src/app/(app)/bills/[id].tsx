import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useLocalSearchParams, useRouter } from 'expo-router';
import React from 'react';
import { Alert, StyleSheet, Text, View } from 'react-native';

import { Button } from '../../../components/Button';
import { Card } from '../../../components/Card';
import { LoadingScreen, Screen } from '../../../components/Screen';
import { ScreenHeader } from '../../../components/ScreenHeader';
import { StatusBadge } from '../../../components/StatusBadge';
import { MoneyAmount } from '../../../components/MoneyAmount';
import type { BillItem } from '../../../types/api';
import { billsService } from '../../../services/bills';
import { ApiClientError } from '../../../services/apiClient';
import { formatDate } from '../../../utils/format';
import { colors, spacing, typography } from '../../../constants/theme';

export default function BillDetailScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const router = useRouter();
  const queryClient = useQueryClient();

  const { data: bill, isLoading } = useQuery({
    queryKey: ['bill', id],
    queryFn: () => billsService.get(id!),
    enabled: !!id,
  });

  const postMutation = useMutation({
    mutationFn: () => billsService.post(id!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['bill', id] });
      queryClient.invalidateQueries({ queryKey: ['bills'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
      Alert.alert('Bill posted', 'This bill is now on your ledger.');
    },
    onError: (error) => {
      Alert.alert('Could not post bill', error instanceof ApiClientError ? error.message : 'Try again.');
    },
  });

  if (isLoading || !bill) return <LoadingScreen />;

  return (
    <Screen>
      <ScreenHeader title={bill.bill_number} subtitle="Bill details" showBack />

      <Card style={styles.hero}>
        <View style={styles.heroTop}>
          <StatusBadge status={bill.status} />
          <Text style={styles.source}>{bill.source_type}</Text>
        </View>
        <MoneyAmount value={bill.total_amount} size="lg" />
        <Text style={styles.date}>
          Bill date: {formatDate(bill.bill_date)}
          {bill.due_date ? ` · Due ${formatDate(bill.due_date)}` : ''}
        </Text>
      </Card>

      <Card style={styles.section}>
        <Text style={styles.sectionTitle}>Tax breakdown</Text>
        {[
          ['Subtotal', bill.subtotal],
          ['Taxable', bill.taxable_amount],
          ['CGST', bill.cgst_amount],
          ['SGST', bill.sgst_amount],
          ['IGST', bill.igst_amount],
          ['Discount', bill.discount_amount],
        ].map(([label, value]) => (
          <View key={label} style={styles.row}>
            <Text style={styles.rowLabel}>{label}</Text>
            <Text style={styles.rowValue}>₹{parseFloat(value).toLocaleString('en-IN')}</Text>
          </View>
        ))}
      </Card>

      {bill.items.length > 0 ? (
        <Card style={styles.section}>
          <Text style={styles.sectionTitle}>Line items ({bill.items.length})</Text>
          {bill.items.map((item: BillItem, index: number) => (
            <View key={index} style={[styles.itemRow, index > 0 && styles.itemBorder]}>
              <Text style={styles.itemTitle}>{item.description}</Text>
              <Text style={styles.itemMeta}>
                {item.quantity} {item.unit} × ₹{item.unit_price} = ₹{item.line_total}
              </Text>
            </View>
          ))}
        </Card>
      ) : null}

      {bill.notes ? (
        <Card style={styles.section}>
          <Text style={styles.sectionTitle}>Notes</Text>
          <Text style={styles.notes}>{bill.notes}</Text>
        </Card>
      ) : null}

      {bill.status === 'draft' ? (
        <Button
          label="Post to ledger"
          onPress={() => postMutation.mutate()}
          loading={postMutation.isPending}
          style={styles.action}
        />
      ) : null}

      <Button
        label="Record payment"
        variant="secondary"
        onPress={() => router.push('/(app)/payments/new')}
        style={styles.action}
      />
    </Screen>
  );
}

const styles = StyleSheet.create({
  hero: { marginBottom: spacing.lg, gap: spacing.sm },
  heroTop: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  source: { ...typography.caption, color: colors.textMuted, textTransform: 'capitalize' },
  date: { ...typography.caption, color: colors.textSecondary },
  section: { marginBottom: spacing.lg, gap: spacing.md },
  sectionTitle: { ...typography.bodyBold, color: colors.text },
  row: { flexDirection: 'row', justifyContent: 'space-between' },
  rowLabel: { ...typography.body, color: colors.textSecondary },
  rowValue: { ...typography.bodyBold, color: colors.text },
  itemRow: { paddingVertical: spacing.sm },
  itemBorder: { borderTopWidth: 1, borderTopColor: colors.border },
  itemTitle: { ...typography.bodyBold, color: colors.text },
  itemMeta: { ...typography.caption, color: colors.textSecondary, marginTop: 2 },
  notes: { ...typography.body, color: colors.textSecondary, lineHeight: 20 },
  action: { marginBottom: spacing.md },
});
