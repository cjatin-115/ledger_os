import { Ionicons } from '@expo/vector-icons';
import { useQuery } from '@tanstack/react-query';
import { useRouter } from 'expo-router';
import React, { useMemo, useState } from 'react';
import {
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View,
} from 'react-native';

import { Card } from '../../../components/Card';
import { EmptyState } from '../../../components/EmptyState';
import { LoadingScreen, Screen } from '../../../components/Screen';
import { billsService } from '../../../services/bills';
import type { Bill } from '../../../types/api';
import { colors, radii, shadows, spacing, typography } from '../../../constants/theme';
import { formatDate, formatMoney } from '../../../utils/format';

export default function BillsScreen() {
  const router = useRouter();
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<string | undefined>();
  const [selectedMonth, setSelectedMonth] = useState<string>('All');
  const [selectedSupplier, setSelectedSupplier] = useState<string>('All');

  const { data: bills = [], isLoading, refetch, isRefetching } = useQuery({
    queryKey: ['bills', statusFilter],
    queryFn: () => billsService.list(statusFilter ? { status: statusFilter } : undefined),
  });

  // Extract unique months (e.g. "August 2026") from available bills
  const availableMonths = useMemo(() => {
    const monthsSet = new Set<string>();
    bills.forEach((b: Bill) => {
      if (b.bill_date) {
        const d = new Date(b.bill_date);
        const monthYear = d.toLocaleDateString('en-IN', { month: 'long', year: 'numeric' });
        monthsSet.add(monthYear);
      }
    });
    return ['All', ...Array.from(monthsSet)];
  }, [bills]);

  // Extract unique supplier names from available bills
  const availableSuppliers = useMemo(() => {
    const suppSet = new Set<string>();
    bills.forEach((b: Bill) => {
      if (b.supplier_name) suppSet.add(b.supplier_name);
    });
    return ['All', ...Array.from(suppSet)];
  }, [bills]);

  // Filter bills by search query, month, supplier, and status
  const filteredBills = useMemo(() => {
    return bills.filter((b: Bill) => {
      // Search
      const query = searchQuery.toLowerCase().trim();
      const matchSearch =
        !query ||
        b.bill_number.toLowerCase().includes(query) ||
        (b.supplier_name && b.supplier_name.toLowerCase().includes(query));

      // Month
      const d = new Date(b.bill_date);
      const monthYear = d.toLocaleDateString('en-IN', { month: 'long', year: 'numeric' });
      const matchMonth = selectedMonth === 'All' || monthYear === selectedMonth;

      // Supplier
      const matchSupplier =
        selectedSupplier === 'All' || b.supplier_name === selectedSupplier;

      return matchSearch && matchMonth && matchSupplier;
    });
  }, [bills, searchQuery, selectedMonth, selectedSupplier]);

  // Group filtered bills by Month (skipping empty months!)
  const groupedByMonth = useMemo(() => {
    const groups: { [key: string]: { bills: Bill[]; total: number } } = {};
    filteredBills.forEach((b: Bill) => {
      const d = new Date(b.bill_date);
      const monthYear = d.toLocaleDateString('en-IN', { month: 'long', year: 'numeric' });
      if (!groups[monthYear]) {
        groups[monthYear] = { bills: [], total: 0 };
      }
      groups[monthYear].bills.push(b);
      groups[monthYear].total += parseFloat(b.total_amount);
    });

    // Sort months in reverse chronological order
    return Object.keys(groups)
      .sort((a, b) => new Date(b).getTime() - new Date(a).getTime())
      .map((month) => ({
        month,
        bills: groups[month].bills,
        total: groups[month].total,
      }));
  }, [filteredBills]);

  if (isLoading) return <LoadingScreen />;

  return (
    <Screen refreshing={isRefetching} onRefresh={refetch}>
      <View style={styles.headerRow}>
        <View>
          <Text style={styles.title}>Bills & Invoices</Text>
          <Text style={styles.subtitle}>{filteredBills.length} bills total</Text>
        </View>
        <Pressable
          style={styles.scanHeaderBtn}
          onPress={() => router.push('/(app)/bills/scan')}
        >
          <Ionicons name="camera" size={18} color="#FFFFFF" />
          <Text style={styles.scanBtnText}>Scan Bill</Text>
        </Pressable>
      </View>

      {/* Top Search Bar */}
      <View style={styles.searchBarContainer}>
        <Ionicons name="search-outline" size={20} color={colors.textSecondary} />
        <TextInput
          style={styles.searchInput}
          placeholder="Search bill number or supplier..."
          placeholderTextColor={colors.textMuted}
          value={searchQuery}
          onChangeText={setSearchQuery}
        />
        {searchQuery ? (
          <Pressable onPress={() => setSearchQuery('')}>
            <Ionicons name="close-circle" size={18} color={colors.textMuted} />
          </Pressable>
        ) : null}
      </View>

      {/* Horizontal Filter Controls */}
      <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.filterScroll}>
        {/* Status Pills */}
        {['All', 'unpaid', 'partially_paid', 'paid', 'overdue'].map((item) => {
          const active = (item === 'All' && !statusFilter) || statusFilter === item;
          return (
            <Pressable
              key={item}
              style={[styles.chip, active && styles.chipActive]}
              onPress={() => setStatusFilter(item === 'All' ? undefined : item)}
            >
              <Text style={[styles.chipText, active && styles.chipTextActive]}>
                {item === 'All' ? 'All Status' : item.replace(/_/g, ' ')}
              </Text>
            </Pressable>
          );
        })}
      </ScrollView>

      {/* Month & Supplier Filter Dropdown Chips */}
      <View style={styles.dropdownFiltersRow}>
        {/* Month Selector */}
        <ScrollView horizontal showsHorizontalScrollIndicator={false}>
          <Text style={styles.filterLabel}>Month:</Text>
          {availableMonths.map((m) => (
            <Pressable
              key={m}
              style={[styles.miniChip, selectedMonth === m && styles.miniChipActive]}
              onPress={() => setSelectedMonth(m)}
            >
              <Text style={[styles.miniChipText, selectedMonth === m && styles.miniChipTextActive]}>
                {m}
              </Text>
            </Pressable>
          ))}
        </ScrollView>
      </View>

      {/* Monthly Grouped Bills List (Skipping Empty Months!) */}
      {groupedByMonth.length === 0 ? (
        <EmptyState
          icon="document-text-outline"
          title="No bills found"
          message="Scan an invoice or add a bill manually to get started."
          actionLabel="📷 Scan Bill"
          onAction={() => router.push('/(app)/bills/scan')}
        />
      ) : (
        groupedByMonth.map((group) => (
          <View key={group.month} style={styles.monthGroup}>
            {/* Month Header Banner */}
            <View style={styles.monthHeader}>
              <Text style={styles.monthTitle}>{group.month}</Text>
              <Text style={styles.monthSubtotal}>
                {group.bills.length} bills · {formatMoney(group.total)}
              </Text>
            </View>

            <Card padding={0}>
              {group.bills.map((bill, index) => {
                const statusColor =
                  bill.status === 'paid'
                    ? colors.success
                    : bill.status === 'partially_paid'
                    ? colors.warning
                    : colors.danger;

                return (
                  <Pressable
                    key={bill.id}
                    style={[styles.billCardRow, index > 0 && styles.cardBorder]}
                    onPress={() => router.push(`/(app)/bills/${bill.id}`)}
                  >
                    <View style={[styles.statusDot, { backgroundColor: statusColor }]} />

                    <View style={styles.billMainInfo}>
                      <Text style={styles.supplierNameText}>
                        {bill.supplier_name || 'Metro Electricals'}
                      </Text>
                      <Text style={styles.billNumberMeta}>
                        Invoice: {bill.bill_number} · {formatDate(bill.bill_date)}
                      </Text>
                    </View>

                    <View style={styles.billRightInfo}>
                      <Text style={styles.billAmountText}>
                        {formatMoney(bill.total_amount)}
                      </Text>
                      <View style={[styles.statusPill, { backgroundColor: `${statusColor}15` }]}>
                        <Text style={[styles.statusPillText, { color: statusColor }]}>
                          {bill.status.replace(/_/g, ' ').toUpperCase()}
                        </Text>
                      </View>
                    </View>
                  </Pressable>
                );
              })}
            </Card>
          </View>
        ))
      )}
    </Screen>
  );
}

const styles = StyleSheet.create({
  headerRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.md,
  },
  title: { ...typography.title, color: colors.text },
  subtitle: { ...typography.caption, color: colors.textSecondary, marginTop: 2 },
  scanHeaderBtn: {
    backgroundColor: colors.primary,
    paddingHorizontal: 14,
    paddingVertical: 8,
    borderRadius: radii.full,
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
  },
  scanBtnText: { color: '#FFFFFF', fontSize: 12, fontWeight: '700' },

  searchBarContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.surface,
    borderRadius: radii.sm,
    paddingHorizontal: spacing.md,
    height: 44,
    borderWidth: 1,
    borderColor: colors.border,
    marginBottom: spacing.sm,
    gap: spacing.xs,
  },
  searchInput: {
    flex: 1,
    fontSize: 14,
    color: colors.text,
  },

  filterScroll: { marginBottom: spacing.xs },
  chip: {
    paddingHorizontal: 14,
    paddingVertical: 6,
    borderRadius: radii.full,
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.border,
    marginRight: spacing.xs,
  },
  chipActive: { backgroundColor: colors.primary, borderColor: colors.primary },
  chipText: { color: colors.textSecondary, fontSize: 12, fontWeight: '700', textTransform: 'capitalize' },
  chipTextActive: { color: '#FFFFFF' },

  dropdownFiltersRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: spacing.lg,
  },
  filterLabel: { ...typography.caption, color: colors.textSecondary, marginRight: 6, alignSelf: 'center' },
  miniChip: {
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: radii.sm,
    backgroundColor: colors.surfaceMuted,
    borderWidth: 1,
    borderColor: colors.border,
    marginRight: 6,
  },
  miniChipActive: { backgroundColor: colors.primaryLight, borderColor: colors.primary },
  miniChipText: { fontSize: 11, fontWeight: '600', color: colors.textSecondary },
  miniChipTextActive: { color: colors.primary, fontWeight: '700' },

  monthGroup: { marginBottom: spacing.lg },
  monthHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.xs,
    paddingHorizontal: 4,
  },
  monthTitle: { ...typography.heading, color: colors.text, fontSize: 15 },
  monthSubtotal: { ...typography.caption, color: colors.textSecondary, fontWeight: '600' },

  billCardRow: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: spacing.md,
    gap: spacing.md,
  },
  cardBorder: { borderTopWidth: 1, borderTopColor: colors.border },
  statusDot: {
    width: 10,
    height: 10,
    borderRadius: 5,
  },
  billMainInfo: { flex: 1 },
  supplierNameText: { ...typography.bodyBold, color: colors.text, fontSize: 15 },
  billNumberMeta: { ...typography.caption, color: colors.textSecondary, marginTop: 2 },

  billRightInfo: { alignItems: 'flex-end' },
  billAmountText: { ...typography.bodyBold, color: colors.text, fontSize: 15 },
  statusPill: {
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: radii.full,
    marginTop: 4,
  },
  statusPillText: { fontSize: 10, fontWeight: '800' },
});
