import React from 'react';
import { Modal, Pressable, StyleSheet, Text, View } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { colors, radii, shadows, spacing, typography } from '../constants/theme';

interface ActionSheetModalProps {
  visible: boolean;
  onClose: () => void;
  onSelectAction: (action: 'scan_bill' | 'manual_bill' | 'record_payment' | 'add_supplier') => void;
}

export function ActionSheetModal({ visible, onClose, onSelectAction }: ActionSheetModalProps) {
  const handleSelect = (action: 'scan_bill' | 'manual_bill' | 'record_payment' | 'add_supplier') => {
    onClose();
    setTimeout(() => onSelectAction(action), 150);
  };

  return (
    <Modal visible={visible} transparent animationType="slide" onRequestClose={onClose}>
      <Pressable style={styles.backdrop} onPress={onClose}>
        <Pressable style={styles.sheet} onPress={(e) => e.stopPropagation()}>
          <View style={styles.handle} />

          <Text style={styles.title}>Quick Actions</Text>
          <Text style={styles.subtitle}>Select an action to continue</Text>

          <View style={styles.actionsList}>
            {/* Primary Action Card: Scan Bill */}
            <Pressable
              style={({ pressed }) => [styles.primaryCard, pressed && styles.pressed]}
              onPress={() => handleSelect('scan_bill')}
            >
              <View style={styles.primaryIconContainer}>
                <Ionicons name="camera" size={24} color="#FFFFFF" />
              </View>
              <View style={styles.textContainer}>
                <Text style={styles.primaryTitle}>📷 Scan Supplier Bill</Text>
                <Text style={styles.primarySubtitle}>AI extracts GSTIN, items, tax & total automatically</Text>
              </View>
              <Ionicons name="chevron-forward" size={20} color="#FFFFFF" />
            </Pressable>

            {/* Action 2: Manual Bill Entry */}
            <Pressable
              style={({ pressed }) => [styles.actionCard, pressed && styles.pressed]}
              onPress={() => handleSelect('manual_bill')}
            >
              <View style={[styles.iconContainer, { backgroundColor: '#F1F5F9' }]}>
                <Ionicons name="create-outline" size={22} color={colors.primary} />
              </View>
              <View style={styles.textContainer}>
                <Text style={styles.cardTitle}>✍️ Manual Bill Entry</Text>
                <Text style={styles.cardSubtitle}>Key in bill details manually</Text>
              </View>
              <Ionicons name="chevron-forward" size={18} color={colors.textMuted} />
            </Pressable>

            {/* Action 3: Record Payment */}
            <Pressable
              style={({ pressed }) => [styles.actionCard, pressed && styles.pressed]}
              onPress={() => handleSelect('record_payment')}
            >
              <View style={[styles.iconContainer, { backgroundColor: '#E6F7F0' }]}>
                <Ionicons name="cash-outline" size={22} color={colors.success} />
              </View>
              <View style={styles.textContainer}>
                <Text style={styles.cardTitle}>💰 Record Payment</Text>
                <Text style={styles.cardSubtitle}>Scan UPI screenshot or enter payment</Text>
              </View>
              <Ionicons name="chevron-forward" size={18} color={colors.textMuted} />
            </Pressable>

            {/* Action 4: Add New Supplier */}
            <Pressable
              style={({ pressed }) => [styles.actionCard, pressed && styles.pressed]}
              onPress={() => handleSelect('add_supplier')}
            >
              <View style={[styles.iconContainer, { backgroundColor: '#FEF3C7' }]}>
                <Ionicons name="person-add-outline" size={22} color={colors.accent} />
              </View>
              <View style={styles.textContainer}>
                <Text style={styles.cardTitle}>👤 Add New Supplier</Text>
                <Text style={styles.cardSubtitle}>Register vendor profile & GSTIN</Text>
              </View>
              <Ionicons name="chevron-forward" size={18} color={colors.textMuted} />
            </Pressable>
          </View>
        </Pressable>
      </Pressable>
    </Modal>
  );
}

const styles = StyleSheet.create({
  backdrop: {
    flex: 1,
    backgroundColor: colors.overlay,
    justifyContent: 'flex-end',
  },
  sheet: {
    backgroundColor: colors.surface,
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
    paddingHorizontal: spacing.lg,
    paddingTop: spacing.md,
    paddingBottom: spacing.xxl,
    ...shadows.modal,
  },
  handle: {
    width: 40,
    height: 4,
    borderRadius: 2,
    backgroundColor: colors.borderStrong,
    alignSelf: 'center',
    marginBottom: spacing.md,
  },
  title: {
    ...typography.heading,
    color: colors.text,
  },
  subtitle: {
    ...typography.caption,
    color: colors.textSecondary,
    marginBottom: spacing.lg,
  },
  actionsList: {
    gap: spacing.md,
  },
  primaryCard: {
    backgroundColor: colors.primary,
    borderRadius: radii.md,
    padding: spacing.md,
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.md,
    ...shadows.card,
  },
  primaryIconContainer: {
    width: 44,
    height: 44,
    borderRadius: radii.sm,
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  primaryTitle: {
    ...typography.heading,
    color: '#FFFFFF',
    fontSize: 15,
  },
  primarySubtitle: {
    ...typography.caption,
    color: 'rgba(255, 255, 255, 0.8)',
    fontSize: 11,
    marginTop: 2,
  },
  actionCard: {
    backgroundColor: colors.surfaceMuted,
    borderRadius: radii.md,
    padding: spacing.md,
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.md,
    borderWidth: 1,
    borderColor: colors.border,
  },
  iconContainer: {
    width: 40,
    height: 40,
    borderRadius: radii.sm,
    justifyContent: 'center',
    alignItems: 'center',
  },
  textContainer: {
    flex: 1,
  },
  cardTitle: {
    ...typography.bodyBold,
    color: colors.text,
  },
  cardSubtitle: {
    ...typography.caption,
    color: colors.textSecondary,
    marginTop: 1,
  },
  pressed: {
    opacity: 0.85,
    transform: [{ scale: 0.98 }],
  },
});
