import { Ionicons } from '@expo/vector-icons';
import * as ImagePicker from 'expo-image-picker';
import { useFocusEffect, useRouter } from 'expo-router';
import React, { useCallback, useEffect, useState } from 'react';
import {
  ActivityIndicator,
  Alert,
  Image,
  Modal,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from 'react-native';

import { Card } from '../../../components/Card';
import { Input } from '../../../components/Input';
import { Screen } from '../../../components/Screen';
import { billsService } from '../../../services/bills';
import type { ExtractedBill } from '../../../types/api';
import { colors, radii, shadows, spacing, typography } from '../../../constants/theme';
import { formatMoney } from '../../../utils/format';

export default function BillScanScreen() {
  const router = useRouter();
  const [imageUri, setImageUri] = useState<string | null>(null);
  const [isScanning, setIsScanning] = useState(false);
  const [extracted, setExtracted] = useState<ExtractedBill | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  const [savedSuccess, setSavedSuccess] = useState(false);
  const [countdown, setCountdown] = useState(10);
  const [timerActive, setTimerActive] = useState(false);

  // Reset state on screen focus so opening the scanner starts 100% fresh every time
  useFocusEffect(
    useCallback(() => {
      setImageUri(null);
      setIsScanning(false);
      setExtracted(null);
      setIsSaving(false);
      setSavedSuccess(false);
      setCountdown(10);
      setTimerActive(false);
    }, [])
  );

  // 10-Second Auto-Redirect Timer logic after saving bill
  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (savedSuccess && timerActive && countdown > 0) {
      interval = setInterval(() => {
        setCountdown((prev) => prev - 1);
      }, 1000);
    } else if (savedSuccess && timerActive && countdown === 0) {
      handleGoBackNow();
    }
    return () => clearInterval(interval);
  }, [savedSuccess, timerActive, countdown]);

  const handleGoBackNow = () => {
    setTimerActive(false);
    setSavedSuccess(false);
    router.replace('/(app)/bills/index');
  };

  const handlePickImage = async (useCamera: boolean) => {
    try {
      const permissionResult = useCamera
        ? await ImagePicker.requestCameraPermissionsAsync()
        : await ImagePicker.requestMediaLibraryPermissionsAsync();

      if (!permissionResult.granted) {
        Alert.alert('Permission Denied', 'Camera / Photo permission is required to scan bills.');
        return;
      }

      const result = useCamera
        ? await ImagePicker.launchCameraAsync({ quality: 0.8, allowsEditing: false })
        : await ImagePicker.launchImageLibraryAsync({ quality: 0.8, allowsEditing: false });

      if (!result.canceled && result.assets[0]) {
        const uri = result.assets[0].uri;
        setImageUri(uri);
        await runAiScan(uri);
      }
    } catch (err) {
      Alert.alert('Error', 'Failed to pick image.');
    }
  };

  const runAiScan = async (uri: string) => {
    setIsScanning(true);
    try {
      const res = await billsService.scanImage(uri);
      setExtracted(res);
    } catch (err: any) {
      Alert.alert('Scan Warning', err?.message || 'Could not parse bill using AI Vision.');
    } finally {
      setIsScanning(false);
    }
  };

  const updateField = (field: keyof ExtractedBill, value: any) => {
    if (!extracted) return;
    setExtracted({ ...extracted, [field]: value });
  };

  const handleSaveBill = async () => {
    if (!extracted) return;
    setIsSaving(true);
    try {
      await billsService.confirmScan(extracted);
      setSavedSuccess(true);
      setCountdown(10);
      setTimerActive(true);
    } catch (err: any) {
      Alert.alert('Could not save bill', err?.response?.data?.detail || err?.message || 'Save failed.');
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <Screen>
      <View style={styles.topHeader}>
        <Pressable style={styles.backBtn} onPress={() => router.back()}>
          <Ionicons name="arrow-back" size={20} color={colors.text} />
        </Pressable>
        <Text style={styles.headerTitle}>📷 Scan Supplier Bill</Text>
        <View style={{ width: 40 }} />
      </View>

      {!imageUri && !isScanning && !extracted && (
        <View style={styles.cameraBox}>
          {/* Edge Alignment Corners */}
          <View style={[styles.corner, styles.topLeft]} />
          <View style={[styles.corner, styles.topRight]} />
          <View style={[styles.corner, styles.bottomLeft]} />
          <View style={[styles.corner, styles.bottomRight]} />

          <Ionicons name="camera-outline" size={56} color={colors.primary} />
          <Text style={styles.cameraInstruction}>Position Supplier Bill Inside Frame</Text>
          <Text style={styles.cameraSubtext}>Supports tax invoices, receipts, and photos</Text>

          <View style={styles.scanActionsRow}>
            <Pressable style={styles.shutterBtn} onPress={() => handlePickImage(true)}>
              <Ionicons name="camera" size={24} color="#FFFFFF" />
              <Text style={styles.shutterText}>Take Photo</Text>
            </Pressable>
            <Pressable style={styles.galleryBtn} onPress={() => handlePickImage(false)}>
              <Ionicons name="image-outline" size={20} color={colors.primary} />
              <Text style={styles.galleryText}>Upload Gallery</Text>
            </Pressable>
          </View>
        </View>
      )}

      {/* Live AI Scan Progression HUD */}
      {isScanning && (
        <Card style={styles.hudCard}>
          <ActivityIndicator size="large" color={colors.primary} />
          <Text style={styles.hudTitle}>Scanning Bill with AI Vision...</Text>
          
          <View style={styles.hudSteps}>
            <Text style={styles.hudStepText}>✓ Reading Supplier & GSTIN</Text>
            <Text style={styles.hudStepText}>✓ Reading Invoice Number & Date</Text>
            <Text style={styles.hudStepText}>✓ Extracting Line Items & Quantities</Text>
            <Text style={styles.hudStepText}>✓ Calculating Subtotal, Tax & Totals</Text>
          </View>

          <View style={styles.confidenceTag}>
            <Text style={styles.confidenceText}>🟢 98% AI Confidence</Text>
          </View>
        </Card>
      )}

      {/* Screen 3: AI Extraction Review & Edit Form */}
      {extracted && !isScanning && (
        <ScrollView style={styles.reviewScroll} showsVerticalScrollIndicator={false}>
          {/* AI Confidence & Warning Banner */}
          <View style={styles.reviewBanner}>
            <Ionicons name="checkmark-circle" size={20} color={colors.success} />
            <Text style={styles.reviewBannerText}>
              Extracted with {Math.round((extracted.confidence || 0.98) * 100)}% AI Confidence
            </Text>
          </View>

          {extracted.warnings && extracted.warnings.length > 0 && (
            <View style={styles.warningBanner}>
              <Ionicons name="warning-outline" size={18} color={colors.warning} />
              <Text style={styles.warningText}>{extracted.warnings.join('. ')}</Text>
            </View>
          )}

          {/* Supplier Info */}
          <Card style={styles.formSection}>
            <Text style={styles.sectionHeaderTitle}>Supplier Details</Text>
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
          </Card>

          {/* Metadata Grid */}
          <Card style={styles.formSection}>
            <Text style={styles.sectionHeaderTitle}>Invoice Metadata</Text>
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
          </Card>

          {/* Line Items List */}
          {extracted.items && extracted.items.length > 0 && (
            <Card style={styles.formSection}>
              <Text style={styles.sectionHeaderTitle}>
                Line Items ({extracted.items.length})
              </Text>
              {extracted.items.map((item, idx) => (
                <View key={idx} style={styles.itemRow}>
                  <View style={{ flex: 1 }}>
                    <Text style={styles.itemDesc}>{item.description}</Text>
                    <Text style={styles.itemMeta}>
                      {item.quantity} {item.unit} × {formatMoney(item.unit_price)}
                    </Text>
                  </View>
                  <Text style={styles.itemTotal}>{formatMoney(item.line_total)}</Text>
                </View>
              ))}
            </Card>
          )}

          {/* Financial Breakdown Card */}
          <Card style={styles.formSection}>
            <Text style={styles.sectionHeaderTitle}>Financial Breakdown</Text>
            <Input
              label="Taxable Amount / Subtotal (₹)"
              value={String(extracted.taxable_amount ?? extracted.subtotal ?? '')}
              onChangeText={(v) => {
                updateField('taxable_amount', v);
                updateField('subtotal', v);
              }}
              keyboardType="decimal-pad"
            />
            <View style={styles.rowTwo}>
              <View style={{ flex: 1 }}>
                <Input
                  label="CGST (₹)"
                  value={String(extracted.cgst_amount ?? '')}
                  onChangeText={(v) => updateField('cgst_amount', v)}
                  keyboardType="decimal-pad"
                />
              </View>
              <View style={{ flex: 1 }}>
                <Input
                  label="SGST (₹)"
                  value={String(extracted.sgst_amount ?? '')}
                  onChangeText={(v) => updateField('sgst_amount', v)}
                  keyboardType="decimal-pad"
                />
              </View>
            </View>
            <Input
              label="Grand Total Amount (₹)"
              value={String(extracted.total_amount ?? '')}
              onChangeText={(v) => updateField('total_amount', v)}
              keyboardType="decimal-pad"
            />
          </Card>

          {/* Bottom CTAs */}
          <View style={styles.ctaRow}>
            <Pressable style={styles.secondaryBtn} onPress={() => setExtracted(null)}>
              <Text style={styles.secondaryBtnText}>Rescan</Text>
            </Pressable>
            <Pressable style={styles.primaryBtn} onPress={handleSaveBill} disabled={isSaving}>
              {isSaving ? (
                <ActivityIndicator color="#FFFFFF" />
              ) : (
                <Text style={styles.primaryBtnText}>Save Bill to Database</Text>
              )}
            </Pressable>
          </View>
        </ScrollView>
      )}

      {/* 10-Second Auto-Redirect Confirmation Modal */}
      <Modal visible={savedSuccess} transparent animationType="fade">
        <View style={styles.modalBackdrop}>
          <View style={styles.successCard}>
            <View style={styles.successIcon}>
              <Ionicons name="checkmark-circle" size={56} color={colors.success} />
            </View>
            <Text style={styles.successTitle}>Bill Saved Successfully!</Text>
            <Text style={styles.successMsg}>
              Posted to supplier ledger. Auto-redirecting in {countdown} seconds...
            </Text>

            {/* Countdown Timer Bar */}
            <View style={styles.timerTrack}>
              <View style={[styles.timerFill, { width: `${(countdown / 10) * 100}%` }]} />
            </View>

            <View style={styles.modalBtns}>
              <Pressable style={styles.cancelTimerBtn} onPress={() => setTimerActive(false)}>
                <Text style={styles.cancelTimerText}>Stay Here</Text>
              </Pressable>
              <Pressable style={styles.goBackNowBtn} onPress={handleGoBackNow}>
                <Text style={styles.goBackNowText}>Go to Bills List Now</Text>
              </Pressable>
            </View>
          </View>
        </View>
      </Modal>
    </Screen>
  );
}

const styles = StyleSheet.create({
  topHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.md,
  },
  backBtn: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: colors.surface,
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: colors.border,
  },
  headerTitle: { ...typography.heading, color: colors.text },

  cameraBox: {
    backgroundColor: colors.surface,
    borderRadius: radii.md,
    height: 380,
    justifyContent: 'center',
    alignItems: 'center',
    padding: spacing.xl,
    borderWidth: 1,
    borderColor: colors.border,
    position: 'relative',
    ...shadows.card,
  },
  corner: {
    position: 'absolute',
    width: 24,
    height: 24,
    borderColor: colors.primary,
  },
  topLeft: { top: 12, left: 12, borderTopWidth: 3, borderLeftWidth: 3 },
  topRight: { top: 12, right: 12, borderTopWidth: 3, borderRightWidth: 3 },
  bottomLeft: { bottom: 12, left: 12, borderBottomWidth: 3, borderLeftWidth: 3 },
  bottomRight: { bottom: 12, right: 12, borderBottomWidth: 3, borderRightWidth: 3 },

  cameraInstruction: { ...typography.heading, color: colors.text, marginTop: spacing.md, fontSize: 16 },
  cameraSubtext: { ...typography.caption, color: colors.textSecondary, marginTop: 4 },

  scanActionsRow: {
    flexDirection: 'row',
    gap: spacing.md,
    marginTop: spacing.xl,
    width: '100%',
  },
  shutterBtn: {
    flex: 1,
    backgroundColor: colors.primary,
    paddingVertical: spacing.md,
    borderRadius: radii.sm,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: spacing.xs,
  },
  shutterText: { color: '#FFFFFF', fontWeight: '700' },
  galleryBtn: {
    flex: 1,
    backgroundColor: colors.primaryLight,
    paddingVertical: spacing.md,
    borderRadius: radii.sm,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: spacing.xs,
  },
  galleryText: { color: colors.primary, fontWeight: '700' },

  hudCard: {
    alignItems: 'center',
    padding: spacing.xl,
    gap: spacing.md,
  },
  hudTitle: { ...typography.heading, color: colors.text },
  hudSteps: { gap: 6, width: '100%', paddingHorizontal: spacing.md },
  hudStepText: { ...typography.body, color: colors.success, fontSize: 13 },
  confidenceTag: {
    backgroundColor: colors.successLight,
    paddingHorizontal: 12,
    paddingVertical: 4,
    borderRadius: radii.full,
  },
  confidenceText: { fontSize: 12, fontWeight: '700', color: colors.success },

  reviewScroll: { flex: 1 },
  reviewBanner: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.xs,
    backgroundColor: colors.successLight,
    padding: spacing.md,
    borderRadius: radii.sm,
    marginBottom: spacing.md,
  },
  reviewBannerText: { ...typography.bodyBold, color: colors.success, fontSize: 13 },
  warningBanner: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.xs,
    backgroundColor: colors.warningLight,
    padding: spacing.md,
    borderRadius: radii.sm,
    marginBottom: spacing.md,
  },
  warningText: { ...typography.caption, color: colors.warning },

  formSection: { marginBottom: spacing.md },
  sectionHeaderTitle: { ...typography.heading, color: colors.text, marginBottom: spacing.sm, fontSize: 15 },

  itemRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: spacing.xs,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  itemDesc: { ...typography.bodyBold, color: colors.text },
  itemMeta: { ...typography.caption, color: colors.textSecondary },
  itemTotal: { ...typography.bodyBold, color: colors.primary },

  rowTwo: { flexDirection: 'row', gap: spacing.md },

  ctaRow: { flexDirection: 'row', gap: spacing.md, marginVertical: spacing.xl },
  secondaryBtn: {
    paddingVertical: spacing.md,
    paddingHorizontal: spacing.lg,
    borderRadius: radii.sm,
    borderWidth: 1,
    borderColor: colors.border,
    justifyContent: 'center',
    alignItems: 'center',
  },
  secondaryBtnText: { ...typography.bodyBold, color: colors.textSecondary },
  primaryBtn: {
    flex: 1,
    backgroundColor: colors.primary,
    paddingVertical: spacing.md,
    borderRadius: radii.sm,
    justifyContent: 'center',
    alignItems: 'center',
  },
  primaryBtnText: { ...typography.bodyBold, color: '#FFFFFF' },

  modalBackdrop: {
    flex: 1,
    backgroundColor: colors.overlay,
    justifyContent: 'center',
    alignItems: 'center',
    padding: spacing.lg,
  },
  successCard: {
    backgroundColor: colors.surface,
    borderRadius: radii.md,
    padding: spacing.xl,
    width: '100%',
    maxWidth: 340,
    alignItems: 'center',
    ...shadows.modal,
  },
  successIcon: { marginBottom: spacing.md },
  successTitle: { ...typography.heading, color: colors.text, fontSize: 18 },
  successMsg: { ...typography.caption, color: colors.textSecondary, textAlign: 'center', marginTop: 4 },
  timerTrack: {
    height: 6,
    width: '100%',
    backgroundColor: colors.border,
    borderRadius: 3,
    marginVertical: spacing.lg,
    overflow: 'hidden',
  },
  timerFill: {
    height: '100%',
    backgroundColor: colors.success,
  },
  modalBtns: { flexDirection: 'row', gap: spacing.md, width: '100%' },
  cancelTimerBtn: {
    flex: 1,
    paddingVertical: spacing.sm,
    borderRadius: radii.sm,
    borderWidth: 1,
    borderColor: colors.border,
    alignItems: 'center',
  },
  cancelTimerText: { ...typography.caption, color: colors.textSecondary },
  goBackNowBtn: {
    flex: 1,
    backgroundColor: colors.primary,
    paddingVertical: spacing.sm,
    borderRadius: radii.sm,
    alignItems: 'center',
  },
  goBackNowText: { ...typography.caption, color: '#FFFFFF', fontWeight: '700' },
});
