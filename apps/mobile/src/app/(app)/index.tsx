import { Ionicons } from '@expo/vector-icons';
import { useQuery } from '@tanstack/react-query';
import { LinearGradient } from 'expo-linear-gradient';
import { useRouter } from 'expo-router';
import React, { useState } from 'react';
import { Pressable, StyleSheet, Text, View } from 'react-native';

import { Card } from '../../components/Card';
import { LoadingScreen, Screen } from '../../components/Screen';
import { ProfileDrawer } from '../../components/ProfileDrawer';
import { checkBackendHealth } from '../../services/api';
import { dashboardService } from '../../services/dashboard';
import { useAuthStore } from '../../store/authStore';
import type { DueReminder } from '../../types/api';
import { formatMoney } from '../../utils/format';
import { colors, radii, shadows, spacing, typography } from '../../constants/theme';

export default function HomeScreen() {
  const router = useRouter();
  const { user, organization } = useAuthStore();
  const [profileDrawerOpen, setProfileDrawerOpen] = useState(false);

  const { data: connected } = useQuery({
    queryKey: ['health'],
    queryFn: checkBackendHealth,
    refetchInterval: 30_000,
  });

  const {
    data: summary,
    isLoading,
    refetch,
    isRefetching,
  } = useQuery({
    queryKey: ['dashboard'],
    queryFn: () => dashboardService.getSummary(),
  });

  const { data: dueSoon = [] } = useQuery({
    queryKey: ['reminders'],
    queryFn: () => dashboardService.getDueReminders(7),
  });

  if (isLoading && !summary) return <LoadingScreen />;

  const outstandingVal = parseFloat(summary?.outstanding_amount ?? '124500');
  const overdueVal = parseFloat(summary?.overdue_amount ?? '42800');
  const paidVal = parseFloat(summary?.paid_amount ?? '18500');
  const suppliersCount = summary?.suppliers_count ?? 12;
  const openBillsCount = summary?.open_bills_count ?? 7;

  const initials = user?.full_name
    ? user.full_name
        .split(' ')
        .map((n) => n[0])
        .join('')
        .toUpperCase()
        .slice(0, 2)
    : 'J';

  return (
    <Screen refreshing={isRefetching} onRefresh={refetch}>
      {/* Top Bar Header */}
      <View style={styles.topBar}>
        <View style={styles.topBarCopy}>
          <Text style={styles.greeting}>Good morning, {user?.full_name?.split(' ')[0] ?? 'Jatin'}</Text>
          <Text style={styles.businessName}>{organization?.name ?? 'ABC Hardware'}</Text>
        </View>
        <View style={styles.topBarIcons}>
          <Pressable
            style={styles.iconCircle}
            onPress={() => router.push({ pathname: '/(app)/work-in-progress', params: { feature: 'Notifications Center' } })}
          >
            <Ionicons name="notifications-outline" size={20} color={colors.text} />
          </Pressable>
          <Pressable style={styles.avatarCircle} onPress={() => setProfileDrawerOpen(true)}>
            <Text style={styles.avatarText}>{initials}</Text>
          </Pressable>
        </View>
      </View>

      {/* Connection Status Indicator */}
      <View style={styles.statusRow}>
        <View style={[styles.dot, connected && styles.dotOnline]} />
        <Text style={styles.statusText}>
          {connected ? 'All systems operational' : 'Offline mode'}
        </Text>
      </View>

      {/* Hero Financial Widget */}
      <LinearGradient colors={['#1E3BB3', colors.primary]} style={styles.heroWidget}>
        <Text style={styles.heroLabel}>OUTSTANDING PAYABLES</Text>
        <Text style={styles.heroAmount}>{formatMoney(outstandingVal)}</Text>

        <View style={styles.heroPill}>
          <Ionicons name="alert-circle" size={14} color="#FEF3C7" />
          <Text style={styles.heroPillText}>
            {suppliersCount} suppliers · {openBillsCount} overdue
          </Text>
        </View>

        <View style={styles.heroSplitRow}>
          <View style={styles.heroSplitItem}>
            <Text style={styles.heroSplitLabel}>This Month</Text>
            <Text style={styles.heroSplitValue}>{formatMoney(overdueVal)}</Text>
          </View>
          <View style={styles.heroSplitDivider} />
          <View style={styles.heroSplitItem}>
            <Text style={styles.heroSplitLabel}>Paid</Text>
            <Text style={styles.heroSplitValue}>{formatMoney(paidVal)}</Text>
          </View>
        </View>
      </LinearGradient>

      {/* Quick Actions (Without Add Bill Card) */}
      <View style={styles.sectionHeader}>
        <Text style={styles.sectionTitle}>Quick actions</Text>
      </View>
      <View style={styles.actionGrid}>
        <Pressable
          style={({ pressed }) => [styles.actionCard, pressed && styles.pressed]}
          onPress={() => router.push('/(app)/bills/scan')}
        >
          <View style={[styles.actionIcon, { backgroundColor: colors.primaryLight }]}>
            <Ionicons name="camera" size={22} color={colors.primary} />
          </View>
          <Text style={styles.actionLabel}>📷 Scan Bill</Text>
          <Text style={styles.actionDetail}>AI Vision upload</Text>
        </Pressable>

        <Pressable
          style={({ pressed }) => [styles.actionCard, pressed && styles.pressed]}
          onPress={() => router.push('/(app)/payments/new')}
        >
          <View style={[styles.actionIcon, { backgroundColor: colors.successLight }]}>
            <Ionicons name="cash" size={22} color={colors.success} />
          </View>
          <Text style={styles.actionLabel}>💰 Record Payment</Text>
          <Text style={styles.actionDetail}>Settle balance</Text>
        </Pressable>

        <Pressable
          style={({ pressed }) => [styles.actionCard, pressed && styles.pressed]}
          onPress={() => router.push('/(app)/suppliers/new')}
        >
          <View style={[styles.actionIcon, { backgroundColor: colors.accentLight }]}>
            <Ionicons name="person-add" size={22} color={colors.accent} />
          </View>
          <Text style={styles.actionLabel}>👤 Add Supplier</Text>
          <Text style={styles.actionDetail}>Register vendor</Text>
        </Pressable>
      </View>

      {/* Recent Bills Feed */}
      <View style={styles.sectionHeader}>
        <Text style={styles.sectionTitle}>Recent Bills</Text>
        <Pressable onPress={() => router.push('/(app)/bills/index')}>
          <Text style={styles.link}>View all</Text>
        </Pressable>
      </View>

      <Card padding={0}>
        {dueSoon.length === 0 ? (
          <View style={styles.emptyFeed}>
            <Ionicons name="receipt-outline" size={32} color={colors.textMuted} />
            <Text style={styles.emptyText}>No recent bills found</Text>
          </View>
        ) : (
          dueSoon.slice(0, 5).map((item: DueReminder, index: number) => (
            <Pressable
              key={item.bill_id || index}
              style={[styles.feedRow, index > 0 && styles.feedBorder]}
              onPress={() => router.push(`/(app)/bills/${item.bill_id}`)}
            >
              <View style={styles.feedIcon}>
                <Ionicons name="document-text" size={20} color={colors.primary} />
              </View>
              <View style={styles.feedCopy}>
                <Text style={styles.feedSupplier}>Metro Electricals</Text>
                <Text style={styles.feedMeta}>
                  {item.bill_number} · Due in {item.days_until_due} days
                </Text>
              </View>
              <View style={styles.feedRight}>
                <Text style={styles.feedAmount}>{formatMoney(item.outstanding_amount)}</Text>
                <View style={[styles.statusBadge, { backgroundColor: colors.warningLight }]}>
                  <Text style={[styles.statusBadgeText, { color: colors.warning }]}>UNPAID</Text>
                </View>
              </View>
            </Pressable>
          ))
        )}
      </Card>

      {/* Profile Sidebar Drawer */}
      <ProfileDrawer
        visible={profileDrawerOpen}
        onClose={() => setProfileDrawerOpen(false)}
      />
    </Screen>
  );
}

const styles = StyleSheet.create({
  topBar: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.sm,
    paddingTop: spacing.xs,
  },
  topBarCopy: { flex: 1 },
  greeting: { ...typography.title, color: colors.text },
  businessName: { ...typography.caption, color: colors.textSecondary, marginTop: 2 },
  topBarIcons: { flexDirection: 'row', alignItems: 'center', gap: spacing.sm },
  iconCircle: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: colors.surface,
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: colors.border,
  },
  avatarCircle: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: colors.primary,
    justifyContent: 'center',
    alignItems: 'center',
  },
  avatarText: { color: '#FFFFFF', fontSize: 15, fontWeight: '800' },
  statusRow: { flexDirection: 'row', alignItems: 'center', marginBottom: spacing.md, gap: 6 },
  dot: { width: 8, height: 8, borderRadius: 4, backgroundColor: colors.warning },
  dotOnline: { backgroundColor: colors.success },
  statusText: { ...typography.caption, color: colors.textSecondary },

  heroWidget: {
    borderRadius: radii.md,
    padding: spacing.lg,
    marginBottom: spacing.xl,
    ...shadows.card,
  },
  heroLabel: { ...typography.eyebrow, color: 'rgba(255, 255, 255, 0.7)' },
  heroAmount: {
    ...typography.display,
    color: '#FFFFFF',
    marginVertical: spacing.xs,
  },
  heroPill: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    backgroundColor: 'rgba(255, 255, 255, 0.15)',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: radii.full,
    alignSelf: 'flex-start',
    marginBottom: spacing.lg,
  },
  heroPillText: { fontSize: 12, fontWeight: '700', color: '#FFFFFF' },
  heroSplitRow: {
    flexDirection: 'row',
    borderTopWidth: 1,
    borderTopColor: 'rgba(255, 255, 255, 0.2)',
    paddingTop: spacing.md,
  },
  heroSplitItem: { flex: 1 },
  heroSplitLabel: { fontSize: 11, fontWeight: '600', color: 'rgba(255, 255, 255, 0.7)' },
  heroSplitValue: { fontSize: 16, fontWeight: '800', color: '#FFFFFF', marginTop: 2 },
  heroSplitDivider: { width: 1, backgroundColor: 'rgba(255, 255, 255, 0.2)', marginHorizontal: spacing.md },

  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.md,
  },
  sectionTitle: { ...typography.heading, color: colors.text },
  link: { color: colors.primary, fontSize: 13, fontWeight: '700' },

  actionGrid: { flexDirection: 'row', gap: spacing.md, marginBottom: spacing.xl },
  actionCard: {
    flex: 1,
    backgroundColor: colors.surface,
    borderRadius: radii.sm,
    padding: spacing.md,
    borderWidth: 1,
    borderColor: colors.border,
    alignItems: 'flex-start',
    ...shadows.card,
  },
  actionIcon: {
    width: 36,
    height: 36,
    borderRadius: radii.sm,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: spacing.xs,
  },
  actionLabel: { ...typography.bodyBold, color: colors.text, fontSize: 13 },
  actionDetail: { ...typography.caption, color: colors.textSecondary, fontSize: 11, marginTop: 1 },

  emptyFeed: { padding: spacing.xl, alignItems: 'center', gap: spacing.sm },
  emptyText: { ...typography.caption, color: colors.textMuted },
  feedRow: { flexDirection: 'row', alignItems: 'center', padding: spacing.md, gap: spacing.md },
  feedBorder: { borderTopWidth: 1, borderTopColor: colors.border },
  feedIcon: {
    width: 38,
    height: 38,
    borderRadius: radii.sm,
    backgroundColor: colors.primaryLight,
    justifyContent: 'center',
    alignItems: 'center',
  },
  feedCopy: { flex: 1 },
  feedSupplier: { ...typography.bodyBold, color: colors.text },
  feedMeta: { ...typography.caption, color: colors.textSecondary, marginTop: 2 },
  feedRight: { alignItems: 'flex-end' },
  feedAmount: { ...typography.bodyBold, color: colors.text },
  statusBadge: { paddingHorizontal: 6, paddingVertical: 2, borderRadius: radii.full, marginTop: 2 },
  statusBadgeText: { fontSize: 10, fontWeight: '800' },
  pressed: { opacity: 0.85, transform: [{ scale: 0.98 }] },
});
