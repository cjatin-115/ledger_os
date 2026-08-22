import { Ionicons } from '@expo/vector-icons';
import { useMutation, useQueryClient } from '@tanstack/react-query';
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
import { billsService } from '../../../services/bills';
import { ApiClientError } from '../../../services/apiClient';
import type { ExtractedBill } from '../../../types/api';
import { colors, radii, spacing, typography } from '../../../constants/theme';

type Step = 'capture' | 'review' | 'done';

const SAMPLE_INVOICE = `ABC HARDWARE
GSTIN: 27AABCU9603R1ZM
Invoice No: INV-1045
Date: 20/08/2026
1 PVC Pipe 10 PCS 120.00 1200
2 Elbow 20 PCS 25.00 500
Subtotal: 1700
CGST: 153
SGST: 153
TOTAL: 2006`;

export default function BillScanScreen() {
  const router = useRouter();
  const queryClient = useQueryClient();

  const [step, setStep] = useState<Step>('capture');
  const [rawText, setRawText] = useState('');
  const [imageUri, setImageUri] = useState<string | null>(null);
  const [extracted, setExtracted] = useState<ExtractedBill | null>(null);
  const [createdBillId, setCreatedBillId] = useState<string | null>(null);

  const scanMutation = useMutation({
    mutationFn: () => {
      if (imageUri) {
        return billsService.scanImage(imageUri);
      }
      return billsService.scan(rawText.trim());
    },
    onSuccess: (data) => {
      setExtracted(data);
      setStep('review');
    },
    onError: (error) => {
      Alert.alert(
        'Scan failed',
        error instanceof ApiClientError ? error.message : 'Could not extract bill data.',
      );
    },
  });

  const confirmMutation = useMutation({
    mutationFn: async () => {
      if (!extracted) throw new Error('No extracted data');
      const result = await billsService.confirmScan(extracted);

      if (imageUri) {
        const fileName = `bill-scan-${Date.now()}.jpg`;
        await attachmentsService.upload('bill', result.bill.id, {
          uri: imageUri,
          name: fileName,
          type: 'image/jpeg',
        });
      }

      return result;
    },
    onSuccess: (result) => {
      setCreatedBillId(result.bill.id);
      setStep('done');
      queryClient.invalidateQueries({ queryKey: ['bills'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
      queryClient.invalidateQueries({ queryKey: ['suppliers'] });
    },
    onError: (error) => {
      Alert.alert(
        'Could not save bill',
        error instanceof ApiClientError ? error.message : 'Please check the fields and try again.',
      );
    },
  });

  const pickImage = async (useCamera: boolean) => {
    const permission = useCamera
      ? await ImagePicker.requestCameraPermissionsAsync()
      : await ImagePicker.requestMediaLibraryPermissionsAsync();

    if (!permission.granted) {
      Alert.alert('Permission needed', 'Allow camera or photo access to scan bills.');
      return;
    }

    const result = useCamera
      ? await ImagePicker.launchCameraAsync({ quality: 0.85, allowsEditing: false })
      : await ImagePicker.launchImageLibraryAsync({
          mediaTypes: ImagePicker.MediaTypeOptions.Images,
          quality: 0.85,
        });

    if (!result.canceled && result.assets[0]) {
      setImageUri(result.assets[0].uri);
    }
  };

  const updateField = (field: keyof ExtractedBill, value: string) => {
    setExtracted((prev) => (prev ? { ...prev, [field]: value } : prev));
  };

  if (step === 'done') {
    return (
      <ScrollView style={styles.safe} contentContainerStyle={styles.doneContent}>
        <View style={styles.successIcon}>
          <Ionicons name="checkmark-circle" size={64} color={colors.success} />
        </View>
        <Text style={styles.doneTitle}>Bill saved!</Text>
        <Text style={styles.doneMessage}>
          Invoice uploaded to your database as a draft. Post it when you are ready.
        </Text>
        <Button
          label="View bill"
          onPress={() => router.replace(`/(app)/bills/${createdBillId}`)}
          style={styles.doneBtn}
        />
        <Button label="Scan another" variant="secondary" onPress={() => router.replace('/(app)/bills/scan')} />
      </ScrollView>
    );
  }

  return (
    <ScrollView style={styles.safe} contentContainerStyle={styles.content} keyboardShouldPersistTaps="handled">
      <ScreenHeader
        title={step === 'capture' ? 'Scan bill' : 'Review invoice'}
        subtitle={step === 'capture' ? 'Photo + AI vision extraction' : 'Edit before saving'}
        showBack
      />

      {step === 'capture' ? (
        <>
          <Card style={styles.section}>
            <Text style={styles.sectionTitle}>1. Capture invoice photo</Text>
            <Text style={styles.hint}>
              Take a photo or upload an image. AI Vision will automatically read all bill details.
            </Text>
            <View style={styles.photoActions}>
              <Button label="Camera" variant="secondary" onPress={() => pickImage(true)} style={styles.photoBtn} />
              <Button label="Gallery" variant="secondary" onPress={() => pickImage(false)} style={styles.photoBtn} />
            </View>
            {imageUri ? (
              <Image source={{ uri: imageUri }} style={styles.preview} resizeMode="contain" />
            ) : (
              <View style={styles.previewPlaceholder}>
                <Ionicons name="image-outline" size={40} color={colors.textMuted} />
                <Text style={styles.placeholderText}>No photo selected</Text>
              </View>
            )}
          </Card>

          <Card style={styles.section}>
            <Text style={styles.sectionTitle}>2. Or paste invoice text (Optional)</Text>
            <Text style={styles.hint}>
              If you don't have an image, paste text below.
            </Text>
            <TextInput
              style={styles.textArea}
              multiline
              numberOfLines={10}
              value={rawText}
              onChangeText={setRawText}
              placeholder="Paste invoice text here…"
              placeholderTextColor={colors.textMuted}
              textAlignVertical="top"
            />
            <Button
              label="Use sample invoice"
              variant="ghost"
              onPress={() => setRawText(SAMPLE_INVOICE)}
            />
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
          {extracted.confidence != null ? (
            <View style={styles.confidenceBar}>
              <Text style={styles.confidenceText}>
                Confidence: {Math.round(extracted.confidence * 100)}%
              </Text>
              {extracted.warnings?.map((warning) => (
                <Text key={warning} style={styles.warning}>
                  ⚠ {warning}
                </Text>
              ))}
            </View>
          ) : null}

          {imageUri ? (
            <Image source={{ uri: imageUri }} style={styles.previewSmall} resizeMode="cover" />
          ) : null}

          <Card style={styles.section}>
            <Input
              label="Supplier name"
              value={extracted.supplier_name ?? ''}
              onChangeText={(v) => updateField('supplier_name', v)}
            />
            <Input
              label="Supplier GSTIN"
              value={extracted.supplier_gstin ?? ''}
              onChangeText={(v) => updateField('supplier_gstin', v)}
              autoCapitalize="characters"
            />
            <Input
              label="Bill number"
              value={extracted.bill_number ?? ''}
              onChangeText={(v) => updateField('bill_number', v)}
            />
            <Input
              label="Bill date (YYYY-MM-DD)"
              value={extracted.bill_date ?? ''}
              onChangeText={(v) => updateField('bill_date', v)}
            />
            <Input
              label="Taxable Amount / Subtotal (₹)"
              value={extracted.taxable_amount ?? extracted.subtotal ?? ''}
              onChangeText={(v) => {
                updateField('taxable_amount', v);
                updateField('subtotal', v);
              }}
              keyboardType="decimal-pad"
            />
            <Input
              label="CGST (₹)"
              value={extracted.cgst_amount ?? ''}
              onChangeText={(v) => updateField('cgst_amount', v)}
              keyboardType="decimal-pad"
            />
            <Input
              label="SGST (₹)"
              value={extracted.sgst_amount ?? ''}
              onChangeText={(v) => updateField('sgst_amount', v)}
              keyboardType="decimal-pad"
            />
            <Input
              label="Total amount (₹)"
              value={extracted.total_amount ?? ''}
              onChangeText={(v) => updateField('total_amount', v)}
              keyboardType="decimal-pad"
            />
          </Card>

          {extracted.items && extracted.items.length > 0 ? (
            <Card style={styles.section}>
              <Text style={styles.sectionTitle}>{extracted.items.length} line items detected</Text>
              {extracted.items.map((item, index) => (
                <Text key={index} style={styles.itemLine}>
                  {item.description} — {item.quantity} × ₹{item.unit_price}
                </Text>
              ))}
            </Card>
          ) : null}

          <View style={styles.reviewActions}>
            <Button label="Back" variant="ghost" onPress={() => setStep('capture')} style={styles.flexBtn} />
            <Button
              label="Save to database"
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
  previewSmall: { width: '100%', height: 120, borderRadius: radii.md, marginBottom: spacing.lg },
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
    minHeight: 160,
    borderWidth: 1,
    borderColor: colors.borderStrong,
    borderRadius: radii.sm,
    padding: spacing.lg,
    fontSize: 14,
    color: colors.text,
    backgroundColor: colors.surface,
  },
  confidenceBar: {
    backgroundColor: colors.iconTile,
    padding: spacing.lg,
    borderRadius: radii.md,
    marginBottom: spacing.lg,
    gap: 4,
  },
  confidenceText: { ...typography.bodyBold, color: colors.accent },
  warning: { ...typography.caption, color: colors.warning },
  itemLine: { ...typography.body, color: colors.textSecondary },
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
  },
  successIcon: { marginBottom: spacing.lg },
  doneTitle: { ...typography.title, color: colors.text, marginBottom: spacing.sm },
  doneMessage: { ...typography.body, color: colors.textSecondary, textAlign: 'center', marginBottom: spacing.xl },
  doneBtn: { width: '100%', marginBottom: spacing.md },
});
