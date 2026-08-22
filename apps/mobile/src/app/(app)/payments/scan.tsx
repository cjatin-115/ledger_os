import { Ionicons } from '@expo/vector-icons';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import * as ImagePicker from 'expo-image-picker';
import { useRouter } from 'expo-router';
import React, { useState } from 'react';
import {
  Alert,
  Image,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View,
} from 'react-native';

import { Button } from '../../../components/Button';
import { Card } from '../../../components/Card';
import { Input } from '../../../components/Input';
import { ScreenHeader } from '../../../components/ScreenHeader';
import { attachmentsService } from '../../../services/attachments';
import { paymentsService } from '../../../services/payments';
import { suppliersService } from '../../../services/suppliers';
import { ApiClientError } from '../../../services/apiClient';
import type { ExtractedPayment, Supplier } from '../../../types/api';
import { colors, radii, spacing, typography } from '../../../constants/theme';

type Step = 'capture' | 'review' | 'done';

const SAMPLE_UPI_RECEIPT = `Paid to Metro Electricals
₹10,000.00
UPI Ref: 523456789012
Date: 22/08/2026, 2:30 PM
Payment successful`;

export default function PaymentScanScreen() {
  const router = useRouter();
  const queryClient = useQueryClient();

  const [step, setStep] = useState<Step>('capture');
  const [rawText, setRawText] = useState('');
  const [imageUri, setImageUri] = useState<string | null>(null);
  const [extracted, setExtracted] = useState<ExtractedPayment | null>(null);
  const [resultSummary, setResultSummary] = useState<string>('');

  const { data: suppliers = [] } = useQuery({
    queryKey: ['suppliers'],
    queryFn: () => suppliersService.list(),
  });

  const scanMutation = useMutation({
    mutationFn: () => {
      if (imageUri) {
        return paymentsService.scanImage(imageUri);
      }
      return paymentsService.scan(rawText.trim());
    },
    onSuccess: (data) => {
      setExtracted(data);
      setStep('review');
    },
    onError: (error) => {
      Alert.alert(
        'Scan failed',
        error instanceof ApiClientError ? error.message : 'Could not parse payment receipt.',
      );
    },
  });

  const confirmMutation = useMutation({
    mutationFn: async () => {
      if (!extracted) throw new Error('No extracted data');
      const result = await paymentsService.confirmScan(extracted);

      if (imageUri) {
        await attachmentsService.upload('payment', result.payment_id, {
          uri: imageUri,
          name: `payment-scan-${Date.now()}.jpg`,
          type: 'image/jpeg',
        });
      }

      return result;
    },
    onSuccess: (result) => {
      const allocText =
        result.allocations.length > 0
          ? result.allocations
              .map((a) => `${a.bill_number}: ₹${a.amount} (${a.bill_status})`)
              .join('\n')
          : 'No open bills matched — payment recorded as unallocated.';

      setResultSummary(
        `Paid ₹${result.amount} to ${result.supplier_name}\n\nAllocated:\n${allocText}\n\nRemaining unallocated: ₹${result.unallocated_amount}`,
      );
      setStep('done');
      queryClient.invalidateQueries({ queryKey: ['payments'] });
      queryClient.invalidateQueries({ queryKey: ['bills'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    },
    onError: (error) => {
      Alert.alert(
        'Could not record payment',
        error instanceof ApiClientError ? error.message : 'Check fields and try again.',
      );
    },
  });

  const pickImage = async (useCamera: boolean) => {
    const permission = useCamera
      ? await ImagePicker.requestCameraPermissionsAsync()
      : await ImagePicker.requestMediaLibraryPermissionsAsync();

    if (!permission.granted) {
      Alert.alert('Permission needed', 'Allow camera or photo access.');
      return;
    }

    const result = useCamera
      ? await ImagePicker.launchCameraAsync({ quality: 0.85 })
      : await ImagePicker.launchImageLibraryAsync({
          mediaTypes: ImagePicker.MediaTypeOptions.Images,
          quality: 0.85,
        });

    if (!result.canceled && result.assets[0]) {
      setImageUri(result.assets[0].uri);
    }
  };

  const updateField = (field: keyof ExtractedPayment, value: string) => {
    setExtracted((prev) => (prev ? { ...prev, [field]: value } : prev));
  };

  if (step === 'done') {
    return (
      <ScrollView style={styles.safe} contentContainerStyle={styles.doneContent}>
        <Ionicons name="checkmark-circle" size={64} color={colors.success} />
        <Text style={styles.doneTitle}>Payment recorded!</Text>
        <Text style={styles.doneMessage}>{resultSummary}</Text>
        <Button label="View payments" onPress={() => router.replace('/(app)/payments')} />
        <Button
          label="Scan another"
          variant="secondary"
          onPress={() => router.replace('/(app)/payments/scan')}
          style={styles.doneBtn}
        />
      </ScrollView>
    );
  }

  return (
    <ScrollView style={styles.safe} contentContainerStyle={styles.content} keyboardShouldPersistTaps="handled">
      <ScreenHeader
        title={step === 'capture' ? 'Scan payment' : 'Review payment'}
        subtitle="UPI screenshot → AI Vision extract & auto-allocate"
        showBack
      />

      {step === 'capture' ? (
        <>
          <Card style={styles.section}>
            <Text style={styles.sectionTitle}>1. Payment screenshot</Text>
            <Text style={styles.hint}>Upload your Google Pay, PhonePe, Paytm or BHIM payment confirmation screen.</Text>
            <View style={styles.photoActions}>
              <Button label="Camera" variant="secondary" onPress={() => pickImage(true)} style={styles.photoBtn} />
              <Button label="Gallery" variant="secondary" onPress={() => pickImage(false)} style={styles.photoBtn} />
            </View>
            {imageUri ? (
              <Image source={{ uri: imageUri }} style={styles.preview} resizeMode="contain" />
            ) : (
              <View style={styles.previewPlaceholder}>
                <Ionicons name="image-outline" size={40} color={colors.textMuted} />
                <Text style={styles.placeholderText}>No screenshot selected</Text>
              </View>
            )}
          </Card>

          <Card style={styles.section}>
            <Text style={styles.sectionTitle}>2. Or receipt text (Optional)</Text>
            <Text style={styles.hint}>
              If you don't have an image, paste the text below.
            </Text>
            <TextInput
              style={styles.textArea}
              multiline
              value={rawText}
              onChangeText={setRawText}
              placeholder="Paste UPI receipt text…"
              placeholderTextColor={colors.textMuted}
              textAlignVertical="top"
            />
            <Button label="Use sample UPI receipt" variant="ghost" onPress={() => setRawText(SAMPLE_UPI_RECEIPT)} />
          </Card>

          <Button
            label="AI Vision Extract"
            onPress={() => scanMutation.mutate()}
            loading={scanMutation.isPending}
            disabled={!imageUri && !rawText.trim()}
          />
        </>
      ) : extracted ? (
        <>
          {extracted.warnings?.map((w) => (
            <Text key={w} style={styles.warning}>
              ⚠ {w}
            </Text>
          ))}

          <Card style={styles.section}>
            <Text style={styles.label}>Supplier</Text>
            <View style={styles.chips}>
              {suppliers.map((supplier: Supplier) => (
                <Text
                  key={supplier.id}
                  style={[styles.chip, extracted.supplier_id === supplier.id && styles.chipActive]}
                  onPress={() => {
                    updateField('supplier_id', supplier.id);
                    updateField('supplier_name', supplier.name);
                  }}
                >
                  {supplier.name}
                </Text>
              ))}
            </View>
            <Input
              label="Detected supplier name"
              value={extracted.supplier_name ?? ''}
              onChangeText={(v) => updateField('supplier_name', v)}
            />
            <Input
              label="Amount (₹)"
              value={extracted.amount ?? ''}
              onChangeText={(v) => updateField('amount', v)}
              keyboardType="decimal-pad"
            />
            <Input
              label="UPI / Reference"
              value={extracted.reference_number ?? ''}
              onChangeText={(v) => updateField('reference_number', v)}
            />
            <Input
              label="Payment date (YYYY-MM-DD)"
              value={extracted.payment_date ?? ''}
              onChangeText={(v) => updateField('payment_date', v)}
            />
          </Card>

          <Text style={styles.autoHint}>
            On save, this payment will automatically allocate to open bills for this supplier (oldest
            due first) and update outstanding balances.
          </Text>

          <View style={styles.reviewActions}>
            <Button label="Back" variant="ghost" onPress={() => setStep('capture')} style={styles.flexBtn} />
            <Button
              label="Record & settle bills"
              onPress={() => confirmMutation.mutate()}
              loading={confirmMutation.isPending}
              style={styles.flexBtn}
            />
          </View>
        </>
      ) : null}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: colors.background },
  content: { padding: spacing.xl, paddingBottom: 40, maxWidth: 720, alignSelf: 'center', width: '100%' },
  section: { marginBottom: spacing.lg, gap: spacing.md },
  sectionTitle: { ...typography.bodyBold, color: colors.text },
  hint: { ...typography.caption, color: colors.textSecondary, lineHeight: 18 },
  photoActions: { flexDirection: 'row', gap: spacing.md },
  photoBtn: { flex: 1 },
  preview: { width: '100%', height: 220, borderRadius: radii.md, backgroundColor: colors.border },
  previewPlaceholder: {
    height: 160,
    borderRadius: radii.md,
    borderWidth: 1,
    borderColor: colors.border,
    borderStyle: 'dashed',
    alignItems: 'center',
    justifyContent: 'center',
    gap: spacing.sm,
  },
  placeholderText: { ...typography.caption, color: colors.textMuted },
  textArea: {
    minHeight: 140,
    borderWidth: 1,
    borderColor: colors.borderStrong,
    borderRadius: radii.sm,
    padding: spacing.lg,
    fontSize: 14,
    color: colors.text,
    backgroundColor: colors.surface,
  },
  warning: { ...typography.caption, color: colors.warning, marginBottom: 4 },
  label: { ...typography.caption, color: colors.textSecondary },
  chips: { flexDirection: 'row', flexWrap: 'wrap', gap: spacing.sm },
  chip: {
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 999,
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.border,
    color: colors.textSecondary,
    fontSize: 12,
    fontWeight: '700',
    overflow: 'hidden',
  },
  chipActive: { backgroundColor: colors.primary, color: colors.surfaceMuted, borderColor: colors.primary },
  autoHint: { ...typography.caption, color: colors.textSecondary, marginBottom: spacing.lg, lineHeight: 18 },
  reviewActions: { flexDirection: 'row', gap: spacing.md },
  flexBtn: { flex: 1 },
  doneContent: {
    flexGrow: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: spacing.xxl,
    maxWidth: 480,
    alignSelf: 'center',
    width: '100%',
    gap: spacing.md,
  },
  doneTitle: { ...typography.title, color: colors.text },
  doneMessage: { ...typography.body, color: colors.textSecondary, textAlign: 'center', lineHeight: 22 },
  doneBtn: { marginTop: spacing.sm, width: '100%' },
});
