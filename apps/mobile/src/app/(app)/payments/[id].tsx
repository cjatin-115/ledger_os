import { useQuery } from '@tanstack/react-query';
import { useLocalSearchParams } from 'expo-router';
import React from 'react';
import { StyleSheet, Text, View } from 'react-native';

import { Card } from '../../../components/Card';
import { LoadingScreen, Screen } from '../../../components/Screen';
import { ScreenHeader } from '../../../components/ScreenHeader';
import { StatusBadge } from '../../../components/StatusBadge';
import { MoneyAmount } from '../../../components/MoneyAmount';
import { paymentsService } from '../../../services/payments';
import { formatDate } from '../../../utils/format';
import { colors, spacing, typography } from '../../../constants/theme';

export default function PaymentDetailScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();

  const { data: payment, isLoading } = useQuery({
    queryKey: ['payment', id],
    queryFn: () => paymentsService.get(id!),
    enabled: !!id,
  });

  if (isLoading || !payment) return <LoadingScreen />;

  return (
    <Screen>
      <ScreenHeader title="Payment" subtitle={formatDate(payment.payment_date)} showBack />

      <Card style={styles.hero}>
        <StatusBadge status={payment.status} />
        <MoneyAmount value={payment.amount} size="lg" style={styles.amount} />
        <Text style={styles.method}>{payment.payment_method.replace(/_/g, ' ').toUpperCase()}</Text>
      </Card>

      <Card style={styles.section}>
        {[
          ['Reference', payment.reference_number],
          ['Cheque number', payment.cheque_number],
          ['Cheque date', payment.cheque_date ? formatDate(payment.cheque_date) : null],
          ['Bank', payment.bank_name],
        ]
          .filter(([, value]) => value)
          .map(([label, value]) => (
            <View key={label} style={styles.row}>
              <Text style={styles.label}>{label}</Text>
              <Text style={styles.value}>{value}</Text>
            </View>
          ))}
      </Card>

      {payment.notes ? (
        <Card>
          <Text style={styles.label}>Notes</Text>
          <Text style={styles.notes}>{payment.notes}</Text>
        </Card>
      ) : null}
    </Screen>
  );
}

const styles = StyleSheet.create({
  hero: { marginBottom: spacing.lg, gap: spacing.sm },
  amount: { marginTop: spacing.sm },
  method: { ...typography.caption, color: colors.textSecondary },
  section: { gap: spacing.md },
  row: { flexDirection: 'row', justifyContent: 'space-between' },
  label: { ...typography.body, color: colors.textSecondary },
  value: { ...typography.bodyBold, color: colors.text },
  notes: { ...typography.body, color: colors.textSecondary, marginTop: spacing.sm },
});
