import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useRouter } from 'expo-router';
import React, { useState } from 'react';
import { Alert, ScrollView, StyleSheet, Text, View } from 'react-native';

import { Button } from '../../../components/Button';
import { Card } from '../../../components/Card';
import { Input } from '../../../components/Input';
import { ScreenHeader } from '../../../components/ScreenHeader';
import { paymentsService } from '../../../services/payments';
import { suppliersService } from '../../../services/suppliers';
import type { Supplier } from '../../../types/api';
import { ApiClientError } from '../../../services/apiClient';
import { colors, spacing, typography } from '../../../constants/theme';

const METHODS = ['cash', 'upi', 'cheque', 'bank_transfer'] as const;

export default function NewPaymentScreen() {
  const router = useRouter();
  const queryClient = useQueryClient();

  const [supplierId, setSupplierId] = useState('');
  const [amount, setAmount] = useState('');
  const [method, setMethod] = useState<(typeof METHODS)[number]>('upi');
  const [reference, setReference] = useState('');
  const [notes, setNotes] = useState('');

  const { data: suppliers = [] } = useQuery({
    queryKey: ['suppliers'],
    queryFn: () => suppliersService.list(),
  });

  const mutation = useMutation({
    mutationFn: () =>
      paymentsService.create({
        supplier_id: supplierId,
        amount,
        payment_method: method,
        payment_date: new Date().toISOString().slice(0, 10),
        reference_number: reference || null,
        notes: notes || null,
      }),
    onSuccess: (payment) => {
      queryClient.invalidateQueries({ queryKey: ['payments'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
      Alert.alert('Payment recorded', 'Payment saved successfully.', [
        { text: 'View', onPress: () => router.replace(`/(app)/payments/${payment.id}`) },
        { text: 'Done', onPress: () => router.back() },
      ]);
    },
    onError: (error) => {
      Alert.alert(
        'Could not save',
        error instanceof ApiClientError ? error.message : 'Check the fields and try again.',
      );
    },
  });

  return (
    <ScrollView style={styles.safe} contentContainerStyle={styles.content} keyboardShouldPersistTaps="handled">
      <ScreenHeader title="Record payment" subtitle="Settle a supplier" showBack />

      <Card style={styles.section}>
        <Text style={styles.label}>Supplier</Text>
        <View style={styles.chips}>
          {suppliers.map((supplier: Supplier) => (
            <Text
              key={supplier.id}
              style={[styles.chip, supplierId === supplier.id && styles.chipActive]}
              onPress={() => setSupplierId(supplier.id)}
            >
              {supplier.name}
            </Text>
          ))}
        </View>
        {suppliers.length === 0 ? (
          <Text style={styles.emptyHint}>Add a supplier first from the Suppliers tab.</Text>
        ) : null}

        <Input label="Amount (₹)" value={amount} onChangeText={setAmount} keyboardType="decimal-pad" />
        <Input label="Reference / UTR" value={reference} onChangeText={setReference} />

        <Text style={styles.label}>Payment method</Text>
        <View style={styles.chips}>
          {METHODS.map((item) => (
            <Text
              key={item}
              style={[styles.chip, method === item && styles.chipActive]}
              onPress={() => setMethod(item)}
            >
              {item.replace(/_/g, ' ')}
            </Text>
          ))}
        </View>

        <Input label="Notes (optional)" value={notes} onChangeText={setNotes} multiline />
      </Card>

      <Button
        label="Save payment"
        onPress={() => mutation.mutate()}
        loading={mutation.isPending}
        disabled={!supplierId || !amount}
      />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: colors.background },
  content: { padding: spacing.xl, paddingBottom: 40, maxWidth: 720, alignSelf: 'center', width: '100%' },
  section: { marginBottom: spacing.xl, gap: spacing.lg },
  label: { ...typography.caption, color: colors.textSecondary },
  chips: { flexDirection: 'row', flexWrap: 'wrap', gap: spacing.sm },
  chip: {
    paddingHorizontal: 14,
    paddingVertical: 8,
    borderRadius: 999,
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.border,
    color: colors.textSecondary,
    fontSize: 13,
    fontWeight: '700',
    textTransform: 'capitalize',
    overflow: 'hidden',
  },
  chipActive: { backgroundColor: colors.primary, color: colors.surfaceMuted, borderColor: colors.primary },
  emptyHint: { ...typography.caption, color: colors.warning },
});
