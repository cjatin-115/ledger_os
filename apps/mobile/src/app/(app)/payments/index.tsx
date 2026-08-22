import { Ionicons } from '@expo/vector-icons';
import { useQuery } from '@tanstack/react-query';
import { useRouter } from 'expo-router';
import React, { useState } from 'react';
import { Modal, Pressable, StyleSheet, Text, View } from 'react-native';

import { Card } from '../../../components/Card';
import { EmptyState } from '../../../components/EmptyState';
import { LoadingScreen, Screen } from '../../../components/Screen';
import { ScreenHeader } from '../../../components/ScreenHeader';
import { paymentsService } from '../../../services/payments';
import type { Payment } from '../../../types/api';
import { colors, radii, shadows, spacing, typography } from '../../../constants/theme';
import { formatDate, formatMoney } from '../../../utils/format';

export default function PaymentsScreen() {
  const router = useRouter();
  const [modalVisible, setModalVisible] = useState(false);

  const { data: payments = [], isLoading, refetch, isRefetching } = useQuery({
    queryKey: ['payments'],
    queryFn: () => paymentsService.list(),
  });

  const handleOptionSelect = (option: 'scan' | 'manual') => {
    setModalVisible(false);
    if (option === 'scan') {
      router.push('/(app)/payments/scan');
    } else {
      router.push('/(app)/payments/new');
    }
  };

  if (isLoading) return <LoadingScreen />;

  return (
    <View style={styles.wrap}>
      <Screen refreshing={isRefetching} onRefresh={refetch}>
        <View style={styles.headerRow}>
          <ScreenHeader title="Payments" subtitle={`${payments.length} total payments recorded`} />
          <Pressable style={styles.addPaymentBtn} onPress={() => setModalVisible(true)}>
            <Ionicons name="add" size={22} color="#FFFFFF" />
            <Text style={styles.addBtnText}>Payment</Text>
          </Pressable>
        </View>

        {payments.length === 0 ? (
          <EmptyState
            icon="wallet-outline"
            title="No payments recorded yet"
            message="Record a payment to settle supplier invoices."
            actionLabel="＋ Record Payment"
            onAction={() => setModalVisible(true)}
          />
        ) : (
          <Card padding={0}>
            {payments.map((payment: Payment, idx: number) => (
              <Pressable
                key={payment.id}
                style={[styles.paymentRow, idx > 0 && styles.rowBorder]}
                onPress={() => router.push(`/(app)/payments/${payment.id}`)}
              >
                <View style={styles.paymentIcon}>
                  <Ionicons name="cash" size={20} color={colors.success} />
                </View>

                <View style={styles.paymentCopy}>
                  <Text style={styles.paymentTitle}>
                    {payment.payee_payer_name || 'Metro Electricals'}
                  </Text>
                  <Text style={styles.paymentMeta}>
                    {payment.payment_method.toUpperCase()} · {formatDate(payment.payment_date)}
                    {payment.reference_number ? ` · Ref: ${payment.reference_number}` : ''}
                  </Text>
                </View>

                <View style={styles.paymentRight}>
                  <Text style={styles.paymentAmount}>{formatMoney(payment.amount)}</Text>
                  <View style={styles.settledBadge}>
                    <Text style={styles.settledText}>SETTLED</Text>
                  </View>
                </View>
              </Pressable>
            ))}
          </Card>
        )}
      </Screen>

      {/* Floating Action Button (+) */}
      <Pressable style={styles.fabPlus} onPress={() => setModalVisible(true)}>
        <Ionicons name="add" size={32} color="#FFFFFF" />
      </Pressable>

      {/* Option Selection Modal */}
      <Modal visible={modalVisible} transparent animationType="slide" onRequestClose={() => setModalVisible(false)}>
        <Pressable style={styles.modalBackdrop} onPress={() => setModalVisible(false)}>
          <Pressable style={styles.modalSheet} onPress={(e) => e.stopPropagation()}>
            <View style={styles.sheetHandle} />
            <Text style={styles.sheetTitle}>Record Payment</Text>
            <Text style={styles.sheetSubtitle}>Choose how you want to add payment details</Text>

            <View style={styles.optionsList}>
              <Pressable
                style={({ pressed }) => [styles.optionCard, pressed && styles.pressed]}
                onPress={() => handleOptionSelect('scan')}
              >
                <View style={[styles.optionIcon, { backgroundColor: colors.primaryLight }]}>
                  <Ionicons name="qr-code-outline" size={24} color={colors.primary} />
                </View>
                <View style={styles.optionCopy}>
                  <Text style={styles.optionTitle}>📷 Scan UPI Screenshot</Text>
                  <Text style={styles.optionSub}>AI extracts UPI ID, UTR, Amount & Date automatically</Text>
                </View>
                <Ionicons name="chevron-forward" size={20} color={colors.textMuted} />
              </Pressable>

              <Pressable
                style={({ pressed }) => [styles.optionCard, pressed && styles.pressed]}
                onPress={() => handleOptionSelect('manual')}
              >
                <View style={[styles.optionIcon, { backgroundColor: colors.successLight }]}>
                  <Ionicons name="create-outline" size={24} color={colors.success} />
                </View>
                <View style={styles.optionCopy}>
                  <Text style={styles.optionTitle}>✏️ Manual Entry</Text>
                  <Text style={styles.optionSub}>Enter Cash, Bank Transfer, Cheque or UPI details manually</Text>
                </View>
                <Ionicons name="chevron-forward" size={20} color={colors.textMuted} />
              </Pressable>
            </View>
          </Pressable>
        </Pressable>
      </Modal>
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: { flex: 1 },
  headerRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.md,
  },
  addPaymentBtn: {
    backgroundColor: colors.primary,
    paddingHorizontal: 14,
    paddingVertical: 8,
    borderRadius: radii.full,
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
  },
  addBtnText: { color: '#FFFFFF', fontSize: 13, fontWeight: '700' },

  paymentRow: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: spacing.md,
    gap: spacing.md,
  },
  rowBorder: { borderTopWidth: 1, borderTopColor: colors.border },
  paymentIcon: {
    width: 40,
    height: 40,
    borderRadius: radii.sm,
    backgroundColor: colors.successLight,
    justifyContent: 'center',
    alignItems: 'center',
  },
  paymentCopy: { flex: 1 },
  paymentTitle: { ...typography.bodyBold, color: colors.text, fontSize: 15 },
  paymentMeta: { ...typography.caption, color: colors.textSecondary, marginTop: 2 },

  paymentRight: { alignItems: 'flex-end' },
  paymentAmount: { ...typography.bodyBold, color: colors.success, fontSize: 15 },
  settledBadge: {
    backgroundColor: colors.successLight,
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: radii.full,
    marginTop: 4,
  },
  settledText: { fontSize: 10, fontWeight: '800', color: colors.success },

  fabPlus: {
    position: 'absolute',
    bottom: 24,
    right: 24,
    width: 56,
    height: 56,
    borderRadius: 28,
    backgroundColor: colors.primary,
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: colors.primary,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.35,
    shadowRadius: 10,
    elevation: 6,
  },

  modalBackdrop: {
    flex: 1,
    backgroundColor: colors.overlay,
    justifyContent: 'flex-end',
  },
  modalSheet: {
    backgroundColor: colors.surface,
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
    paddingHorizontal: spacing.lg,
    paddingTop: spacing.md,
    paddingBottom: spacing.xxl,
    ...shadows.modal,
  },
  sheetHandle: {
    width: 40,
    height: 4,
    borderRadius: 2,
    backgroundColor: colors.borderStrong,
    alignSelf: 'center',
    marginBottom: spacing.md,
  },
  sheetTitle: { ...typography.heading, color: colors.text },
  sheetSubtitle: { ...typography.caption, color: colors.textSecondary, marginBottom: spacing.lg },

  optionsList: { gap: spacing.md },
  optionCard: {
    backgroundColor: colors.surfaceMuted,
    borderRadius: radii.md,
    padding: spacing.md,
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.md,
    borderWidth: 1,
    borderColor: colors.border,
  },
  optionIcon: {
    width: 44,
    height: 44,
    borderRadius: radii.sm,
    justifyContent: 'center',
    alignItems: 'center',
  },
  optionCopy: { flex: 1 },
  optionTitle: { ...typography.bodyBold, color: colors.text },
  optionSub: { ...typography.caption, color: colors.textSecondary, marginTop: 2 },
  pressed: { opacity: 0.85, transform: [{ scale: 0.98 }] },
});
