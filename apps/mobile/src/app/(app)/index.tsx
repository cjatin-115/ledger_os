import { Ionicons } from '@expo/vector-icons';
import { useQuery } from '@tanstack/react-query';
import { LinearGradient } from 'expo-linear-gradient';
import { useRouter } from 'expo-router';
import React from 'react';
import { Pressable, StyleSheet, Text, View } from 'react-native';

import { Card } from '../../components/Card';
import { LoadingScreen, Screen } from '../../components/Screen';
import { MoneyAmount } from '../../components/MoneyAmount';
import type { DueReminder } from '../../types/api';
import { checkBackendHealth } from '../../services/api';
import { dashboardService } from '../../services/dashboard';
import { useAuthStore } from '../../store/authStore';
import { useResponsive } from '../../hooks/useResponsive';
import { dueLabel, formatMoney } from '../../utils/format';
import { colors, radii, spacing, typography } from '../../constants/theme';

export default function HomeScreen() {
  const router = useRouter();
  const { user, logout } = useAuthStore();
  const { columns, isTablet } = useResponsive();

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

  const metricCols = columns(2, 2, 4);

  return (
    <Screen refreshing={isRefetching} onRefresh={refetch}>
      <View style={styles.header}>
        <View style={styles.headerCopy}>
          <Text style={styles.eyebrow}>LEDGEROS / TODAY</Text>
          <Text style={styles.greeting}>Hi, {user?.full_name?.split(' ')[0] ?? 'there'}</Text>
          <Text style={styles.subtitle}>Here is your shop at a glance.</Text>
        </View>
        <Pressable style={styles.avatar} onPress={() => logout()}>
          <Text style={styles.avatarText}>{user?.full_name?.[0]?.toUpperCase() ?? 'L'}</Text>
        </Pressable>
      </View>

      <View style={styles.statusRow}>
        <View style={[styles.dot, connected && styles.dotOnline]} />
        <Text style={styles.statusText}>
          {connected ? 'All systems operational' : 'Offline — showing cached data'}
        </Text>
      </View>

      <LinearGradient colors={[colors.primary, colors.primaryLight]} style={styles.hero}>
        <Text style={styles.heroLabel}>OUTSTANDING PAYABLES</Text>
        <MoneyAmount value={summary?.outstanding_amount ?? '0'} size="hero" />
        <View style={styles.heroFooter}>
          <Text style={styles.heroMeta}>{summary?.open_bills_count ?? 0} open bills</Text>
          {parseFloat(summary?.overdue_amount ?? '0') > 0 ? (
            <Text style={styles.heroTrend}>
              {formatMoney(summary?.overdue_amount ?? '0', true)} overdue
            </Text>
          ) : (
            <Text style={styles.heroTrend}>On track</Text>
          )}
        </View>
      </LinearGradient>

      <View style={[styles.metricGrid, { flexWrap: isTablet ? 'wrap' : 'nowrap' }]}>
        {[
          { label: 'Due this week', value: summary?.due_soon_amount ?? '0', detail: 'Next 7 days' },
          { label: 'Paid total', value: summary?.paid_amount ?? '0', detail: `${summary?.payments_count ?? 0} payments` },
          { label: 'Suppliers', value: String(summary?.suppliers_count ?? 0), detail: 'Active vendors', isCount: true },
          { label: 'Billed', value: summary?.billed_amount ?? '0', detail: `${summary?.bills_count ?? 0} bills` },
        ].map((metric) => (
          <View
            key={metric.label}
            style={[styles.metricCard, { width: isTablet ? `${100 / metricCols - 2}%` : '48%' }]}
          >
            <Text style={styles.metricLabel}>{metric.label}</Text>
            <Text style={styles.metricValue}>
              {metric.isCount ? metric.value : formatMoney(metric.value, true)}
            </Text>
            <Text style={styles.metricDetail}>{metric.detail}</Text>
          </View>
        ))}
      </View>

      <View style={styles.sectionHeader}>
        <Text style={styles.sectionTitle}>Quick actions</Text>
      </View>
      <View style={styles.actionGrid}>
        <Action
          label="Scan bill"
          detail="Photo + OCR upload"
          icon="scan-outline"
          onPress={() => router.push('/(app)/bills/scan')}
        />
        <Action
          label="Add bill"
          detail="Manual entry"
          icon="add-circle-outline"
          onPress={() => router.push('/(app)/bills')}
        />
        <Action
          label="Scan payment"
          detail="UPI screenshot → settle"
          icon="qr-code-outline"
          onPress={() => router.push('/(app)/payments/scan')}
        />
        <Action
          label="Record payment"
          detail="Manual entry"
          icon="wallet-outline"
          onPress={() => router.push('/(app)/payments/new')}
        />
        <Action
          label="Add supplier"
          detail="Build directory"
          icon="person-add-outline"
          onPress={() => router.push('/(app)/suppliers/new')}
        />
      </View>

      <View style={styles.sectionHeader}>
        <Text style={styles.sectionTitle}>Due soon</Text>
        <Pressable onPress={() => router.push('/(app)/bills')}>
          <Text style={styles.link}>View all</Text>
        </Pressable>
      </View>

      <Card padding={0}>
        {dueSoon.length === 0 ? (
          <Text style={styles.emptyDue}>No bills due in the next 7 days.</Text>
        ) : (
          dueSoon.slice(0, 5).map((item: DueReminder, index: number) => (
            <Pressable
              key={item.bill_id}
              style={[styles.dueRow, index > 0 && styles.dueBorder]}
              onPress={() => router.push(`/(app)/bills/${item.bill_id}`)}
            >
              <View style={styles.dueIcon}>
                <Text style={styles.dueIconText}>₹</Text>
              </View>
              <View style={styles.dueCopy}>
                <Text style={styles.dueBill}>{item.bill_number}</Text>
                <Text style={styles.dueMeta}>{dueLabel(item.days_until_due)}</Text>
              </View>
              <MoneyAmount value={item.outstanding_amount} size="sm" />
            </Pressable>
          ))
        )}
      </Card>
    </Screen>
  );
}

function Action({
  label,
  detail,
  icon,
  onPress,
}: {
  label: string;
  detail: string;
  icon: keyof typeof Ionicons.glyphMap;
  onPress: () => void;
}) {
  return (
    <Pressable style={styles.actionCard} onPress={onPress}>
      <Ionicons name={icon} size={20} color={colors.accent} />
      <Text style={styles.actionLabel}>{label}</Text>
      <Text style={styles.actionDetail}>{detail}</Text>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.lg,
    paddingTop: spacing.sm,
  },
  headerCopy: { flex: 1 },
  eyebrow: { ...typography.eyebrow, color: colors.accent },
  greeting: { ...typography.title, color: colors.text, marginTop: 6 },
  subtitle: { ...typography.body, color: colors.textSecondary, marginTop: 4 },
  avatar: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: colors.sage,
    alignItems: 'center',
    justifyContent: 'center',
  },
  avatarText: { color: colors.sageDark, fontSize: 17, fontWeight: '800' },
  statusRow: { flexDirection: 'row', alignItems: 'center', marginBottom: spacing.lg, gap: 8 },
  dot: { width: 8, height: 8, borderRadius: 4, backgroundColor: colors.warning },
  dotOnline: { backgroundColor: colors.success },
  statusText: { ...typography.caption, color: colors.textSecondary },
  hero: { borderRadius: radii.lg, padding: spacing.xl, marginBottom: spacing.lg },
  heroLabel: { ...typography.eyebrow, color: colors.heroLabel },
  heroFooter: { flexDirection: 'row', justifyContent: 'space-between', marginTop: spacing.xl },
  heroMeta: { color: '#D5E0D1', fontSize: 13 },
  heroTrend: { color: '#D6B27B', fontSize: 13, fontWeight: '700' },
  metricGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: spacing.md, marginBottom: spacing.xl },
  metricCard: {
    backgroundColor: colors.surface,
    borderRadius: radii.md,
    padding: spacing.lg,
    borderWidth: 1,
    borderColor: colors.border,
    minWidth: '46%',
  },
  metricLabel: { ...typography.caption, color: colors.textSecondary },
  metricValue: { fontSize: 19, fontWeight: '800', color: colors.text, marginTop: 8 },
  metricDetail: { ...typography.caption, color: colors.textMuted, marginTop: 4 },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.md,
  },
  sectionTitle: { ...typography.heading, color: colors.text },
  link: { color: colors.accent, fontSize: 13, fontWeight: '800' },
  actionGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: spacing.md, marginBottom: spacing.xl },
  actionCard: {
    width: '48%',
    minHeight: 104,
    backgroundColor: colors.surface,
    borderRadius: radii.md,
    padding: spacing.lg,
    borderWidth: 1,
    borderColor: colors.border,
    gap: 6,
  },
  actionLabel: { ...typography.bodyBold, color: colors.text },
  actionDetail: { fontSize: 11, color: colors.textMuted },
  emptyDue: { padding: spacing.xl, textAlign: 'center', color: colors.textSecondary },
  dueRow: { flexDirection: 'row', alignItems: 'center', padding: spacing.lg, gap: spacing.md },
  dueBorder: { borderTopWidth: 1, borderTopColor: colors.border },
  dueIcon: {
    width: 36,
    height: 36,
    borderRadius: radii.sm,
    backgroundColor: colors.iconTile,
    alignItems: 'center',
    justifyContent: 'center',
  },
  dueIconText: { color: colors.accent, fontSize: 16, fontWeight: '800' },
  dueCopy: { flex: 1 },
  dueBill: { ...typography.bodyBold, color: colors.text },
  dueMeta: { ...typography.caption, color: colors.textSecondary, marginTop: 2 },
});
