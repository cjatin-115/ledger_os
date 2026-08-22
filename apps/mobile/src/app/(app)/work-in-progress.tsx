import React from 'react';
import { Pressable, StyleSheet, Text, View } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useLocalSearchParams, useRouter } from 'expo-router';

import { Screen } from '../../components/Screen';
import { Card } from '../../components/Card';
import { colors, radii, shadows, spacing, typography } from '../../constants/theme';

export default function WorkInProgressScreen() {
  const router = useRouter();
  const { feature = 'This Feature' } = useLocalSearchParams<{ feature?: string }>();

  return (
    <Screen style={styles.container}>
      {/* Top Header */}
      <View style={styles.topHeader}>
        <Pressable style={styles.backBtn} onPress={() => router.back()}>
          <Ionicons name="arrow-back" size={20} color={colors.text} />
        </Pressable>
        <Text style={styles.headerTitle}>Feature Status</Text>
        <View style={{ width: 40 }} />
      </View>

      {/* Main Linear Style Card */}
      <Card style={styles.mainCard}>
        <View style={styles.statusBadge}>
          <Ionicons name="hardware-chip-outline" size={16} color={colors.primary} />
          <Text style={styles.statusBadgeText}>UNDER ACTIVE DEVELOPMENT</Text>
        </View>

        <Text style={styles.featureTitle}>{feature}</Text>
        <Text style={styles.featureSub}>
          Our engineering team is actively building this module with Revolut-grade precision.
        </Text>

        {/* Progress Bar */}
        <View style={styles.progressContainer}>
          <View style={styles.progressHeader}>
            <Text style={styles.progressLabel}>Module Completion</Text>
            <Text style={styles.progressPercent}>85%</Text>
          </View>
          <View style={styles.progressTrack}>
            <View style={styles.progressFill} />
          </View>
        </View>

        {/* Feature Highlights */}
        <View style={styles.highlightsList}>
          <View style={styles.highlightItem}>
            <Ionicons name="checkmark-circle" size={18} color={colors.success} />
            <Text style={styles.highlightText}>Subsecond response times & cloud sync</Text>
          </View>
          <View style={styles.highlightItem}>
            <Ionicons name="checkmark-circle" size={18} color={colors.success} />
            <Text style={styles.highlightText}>Automated GST compliance validation</Text>
          </View>
          <View style={styles.highlightItem}>
            <Ionicons name="time-outline" size={18} color={colors.warning} />
            <Text style={styles.highlightText}>Scheduled for upcoming LedgerOS patch update</Text>
          </View>
        </View>

        {/* Action Buttons */}
        <View style={styles.actionsBox}>
          <Pressable
            style={({ pressed }) => [styles.notifyBtn, pressed && styles.pressed]}
            onPress={() => router.back()}
          >
            <Ionicons name="notifications" size={18} color="#FFFFFF" />
            <Text style={styles.notifyBtnText}>Notify Me On Release</Text>
          </Pressable>

          <Pressable
            style={({ pressed }) => [styles.backHomeBtn, pressed && styles.pressed]}
            onPress={() => router.replace('/(app)')}
          >
            <Text style={styles.backHomeText}>← Return to Home Dashboard</Text>
          </Pressable>
        </View>
      </Card>
    </Screen>
  );
}

const styles = StyleSheet.create({
  container: {
    paddingHorizontal: spacing.lg,
  },
  topHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.lg,
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

  mainCard: {
    padding: spacing.xl,
    alignItems: 'flex-start',
    gap: spacing.md,
    ...shadows.card,
  },
  statusBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    backgroundColor: colors.primaryLight,
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: radii.full,
  },
  statusBadgeText: {
    fontSize: 11,
    fontWeight: '800',
    color: colors.primary,
    letterSpacing: 0.5,
  },
  featureTitle: {
    ...typography.titleLarge,
    color: colors.text,
    fontSize: 24,
    marginTop: spacing.xs,
  },
  featureSub: {
    ...typography.body,
    color: colors.textSecondary,
    fontSize: 14,
    lineHeight: 20,
  },

  progressContainer: {
    width: '100%',
    marginVertical: spacing.md,
  },
  progressHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 6,
  },
  progressLabel: { ...typography.caption, color: colors.textSecondary },
  progressPercent: { ...typography.caption, color: colors.primary, fontWeight: '800' },
  progressTrack: {
    height: 8,
    backgroundColor: colors.border,
    borderRadius: 4,
    overflow: 'hidden',
  },
  progressFill: {
    width: '85%',
    height: '100%',
    backgroundColor: colors.primary,
    borderRadius: 4,
  },

  highlightsList: {
    gap: spacing.xs,
    width: '100%',
    marginBottom: spacing.md,
  },
  highlightItem: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.sm,
  },
  highlightText: { ...typography.caption, color: colors.text, fontSize: 13 },

  actionsBox: {
    width: '100%',
    gap: spacing.sm,
    marginTop: spacing.sm,
  },
  notifyBtn: {
    backgroundColor: colors.primary,
    paddingVertical: spacing.md,
    borderRadius: radii.sm,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: spacing.xs,
  },
  notifyBtnText: { color: '#FFFFFF', fontWeight: '700', fontSize: 14 },
  backHomeBtn: {
    paddingVertical: spacing.md,
    borderRadius: radii.sm,
    borderWidth: 1,
    borderColor: colors.border,
    alignItems: 'center',
  },
  backHomeText: { color: colors.textSecondary, fontWeight: '700', fontSize: 13 },
  pressed: { opacity: 0.85, transform: [{ scale: 0.98 }] },
});
