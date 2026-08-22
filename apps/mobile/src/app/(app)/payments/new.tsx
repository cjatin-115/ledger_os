import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useRouter } from 'expo-router';
import React, { useState } from 'react';
import { Alert, Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

import { Button } from '../../../components/Button';
import { Card } from '../../../components/Card';
import { Input } from '../../../components/Input';
import { ScreenHeader } from '../../../components/ScreenHeader';
import { paymentsService } from '../../../services/payments';
import { suppliersService } from '../../../services/suppliers';
import { billsService } from '../../../services/bills';
import type { Bill, Supplier } from '../../../types/api';
import { ApiClientError } from '../../../services/apiClient';
import { colors, radii, shadows, spacing, typography } from '../../../constants/theme';
import { formatMoney } from '../../../utils/format';

const METHODS = [
  { id: 'upi', label: '⚡ UPI' },
  { id: 'cash', label: '💵 Cash' },
  { id: 'bank_transfer', label: '🏦 Bank Transfer' },
  { id: 'cheque', label: '📄 Cheque' },
] as const;

export default function NewPaymentScreen() {
  const router = useRouter();
  const queryClient = useQueryClient();

  const [supplierId, setSupplierId] = useState('');
  const [amount, setAmount] = useState('5000');
  const [method, setMethod] = useState<'upi' | 'cash' | 'bank_transfer' | 'cheque'>('upi');
  const [reference, setReference] = useState('');
  const [notes, setNotes] = useState('');
  const [allocatedBills, setAllocatedBills] = useState<{ [billId: string]: string }>({});

  const { data: suppliers = [] } = useQuery({
    queryKey: ['suppliers'],
    queryFn: () => suppliersService.list(),
  });

  const { data: unpaidBills = [] } = useQuery({
    queryKey: ['bills', supplierId],
    queryFn: () => billsService.list({ status: 'posted' }),
    enabled: !!supplierId,
  });

  const supplierBills = unpaidBills.filter((b: Bill) => !supplierId || b.supplier_id === supplierId);

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
      queryClient.invalidateQueries({ queryKey: ['bills'] });
      Alert.alert('Payment Recorded!', `Recorded ${formatMoney(amount)} successfully.`, [
        { text: 'Done', onPress: () => router.replace('/(app)/payments/index') },
      ]);
    },
    onError: (error) => {
      Alert.alert(
        'Could not save',
        error instanceof ApiClientError ? error.message : 'Check fields and try again.',
      );
    },
  });

  const handleQuickAllocate = (billId: string, outstanding: string) => {
    setAllocatedBills((prev) => ({
      ...prev,
      [billId]: prev[billId] ? '' : outstanding,
    }));
  };

  return (
    <ScrollView style={styles.safe} contentContainerStyle={styles.content} keyboardShouldPersistTaps="handled">
      <ScreenHeader title="Record Payment" subtitle="Step 1: Details · Step 2: Allocation" showBack />

      {/* Step 1: Payment Details Card */}
      <Card style={styles.cardSection}>
        <Text style={styles.sectionHeaderTitle}>Step 1: Select Supplier & Amount</Text>

        <Text style={styles.fieldLabel}>Select Supplier</Text>
        <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.horizontalChips}>
          {suppliers.map((supplier: Supplier) => {
            const active = supplierId === supplier.id;
            return (
              <Pressable
                key={supplier.id}
                style={[styles.supplierChip, active && styles.supplierChipActive]}
                onPress={() => setSupplierId(supplier.id)}
              >
                <Text style={[styles.supplierChipText, active && styles.supplierChipTextActive]}>
                  {supplier.name}
                </Text>
              </Pressable>
            );
          })}
        </ScrollView>
        {suppliers.length === 0 ? (
          <Text style={styles.emptyHint}>No suppliers found. Please add a supplier first.</Text>
        ) : null}

        {/* Large Amount Input */}
        <View style={styles.amountBox}>
          <Text style={styles.currencySymbol}>₹</Text>
          <Input
            label="Payment Amount (₹)"
            value={amount}
            onChangeText={setAmount}
            keyboardType="decimal-pad"
          />
        </View>

        {/* Payment Method Selector Pills */}
        <Text style={styles.fieldLabel}>Payment Method</Text>
        <View style={styles.methodsRow}>
          {METHODS.map((item) => {
            const active = method === item.id;
            return (
              <Pressable
                key={item.id}
                style={[styles.methodPill, active && styles.methodPillActive]}
                onPress={() => setMethod(item.id)}
              >
                <Text style={[styles.methodPillText, active && styles.methodPillTextActive]}>
                  {item.label}
                </Text>
              </Pressable>
            );
          })}
        </View>

        <Input label="Reference / UTR / Transaction ID" value={reference} onChangeText={setReference} />
        <Input label="Notes (optional)" value={notes} onChangeText={setNotes} multiline />
      </Card>

      {/* Step 2: Instant Bill Allocation Interface */}
      {supplierId ? (
        <Card style={styles.cardSection}>
          <Text style={styles.sectionHeaderTitle}>Step 2: Instant Bill Allocation</Text>
          <Text style={styles.subtitleText}>Tap unpaid bills to allocate payment amount</Text>

          {supplierBills.length === 0 ? (
            <Text style={styles.emptyBillsHint}>No unpaid bills found for this supplier.</Text>
          ) : (
            supplierBills.map((bill: Bill) => {
              const allocated = allocatedBills[bill.id];
              return (
                <View key={bill.id} style={styles.allocationRow}>
                  <View style={{ flex: 1 }}>
                    <Text style={styles.billRefText}>{bill.bill_number}</Text>
                    <Text style={styles.billDateText}>
                      Date: {bill.bill_date} · Total: {formatMoney(bill.total_amount)}
                    </Text>
                  </View>
                  <Pressable
                    style={[styles.allocateBtn, Boolean(allocated) && styles.allocateBtnActive]}
                    onPress={() => handleQuickAllocate(bill.id, bill.total_amount)}
                  >
                    <Ionicons
                      name={allocated ? 'checkmark-circle' : 'add-circle-outline'}
                      size={18}
                      color={allocated ? '#FFFFFF' : colors.primary}
                    />
                    <Text style={[styles.allocateText, Boolean(allocated) && styles.allocateTextActive]}>
                      {allocated ? 'Allocated' : 'Allocate'}
                    </Text>
                  </Pressable>
                </View>
              );
            })
          )}
        </Card>
      ) : null}

      <Button
        label={`Record Payment (${formatMoney(amount || 0)})`}
        onPress={() => mutation.mutate()}
        loading={mutation.isPending}
        disabled={!supplierId || !amount}
      />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: colors.background },
  content: { padding: spacing.lg, paddingBottom: 40, maxWidth: 720, alignSelf: 'center', width: '100%' },

  cardSection: { marginBottom: spacing.lg, gap: spacing.md },
  sectionHeaderTitle: { ...typography.heading, color: colors.text, fontSize: 16 },
  subtitleText: { ...typography.caption, color: colors.textSecondary, marginBottom: spacing.xs },
  fieldLabel: { ...typography.caption, color: colors.textSecondary, marginTop: 4 },

  horizontalChips: { flexDirection: 'row', marginBottom: spacing.xs },
  supplierChip: {
    paddingHorizontal: 14,
    paddingVertical: 8,
    borderRadius: radii.full,
    backgroundColor: colors.surfaceMuted,
    borderWidth: 1,
    borderColor: colors.border,
    marginRight: spacing.xs,
  },
  supplierChipActive: { backgroundColor: colors.primary, borderColor: colors.primary },
  supplierChipText: { fontSize: 13, fontWeight: '700', color: colors.textSecondary },
  supplierChipTextActive: { color: '#FFFFFF' },

  amountBox: { marginVertical: spacing.xs },
  currencySymbol: { fontSize: 24, fontWeight: '800', color: colors.primary, marginBottom: -10 },

  methodsRow: { flexDirection: 'row', flexWrap: 'wrap', gap: spacing.xs, marginBottom: spacing.xs },
  methodPill: {
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: radii.sm,
    backgroundColor: colors.surfaceMuted,
    borderWidth: 1,
    borderColor: colors.border,
  },
  methodPillActive: { backgroundColor: colors.primaryLight, borderColor: colors.primary },
  methodPillText: { fontSize: 12, fontWeight: '700', color: colors.textSecondary },
  methodPillTextActive: { color: colors.primary },

  allocationRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingVertical: spacing.sm,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  billRefText: { ...typography.bodyBold, color: colors.text },
  billDateText: { ...typography.caption, color: colors.textSecondary, marginTop: 2 },

  allocateBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: radii.full,
    borderWidth: 1,
    borderColor: colors.primary,
  },
  allocateBtnActive: { backgroundColor: colors.success, borderColor: colors.success },
  allocateText: { fontSize: 12, fontWeight: '700', color: colors.primary },
  allocateTextActive: { color: '#FFFFFF' },

  emptyHint: { ...typography.caption, color: colors.warning },
  emptyBillsHint: { ...typography.caption, color: colors.textMuted, fontStyle: 'italic' },
});
