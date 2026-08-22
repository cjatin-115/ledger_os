import { useQuery } from '@tanstack/react-query';
import { useLocalSearchParams } from 'expo-router';
import React from 'react';
import { StyleSheet, Text, View } from 'react-native';

import { Card } from '../../../components/Card';
import { LoadingScreen, Screen } from '../../../components/Screen';
import { ScreenHeader } from '../../../components/ScreenHeader';
import { suppliersService } from '../../../services/suppliers';
import { formatDate } from '../../../utils/format';
import { colors, spacing, typography } from '../../../constants/theme';

export default function SupplierDetailScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();

  const { data: supplier, isLoading } = useQuery({
    queryKey: ['supplier', id],
    queryFn: () => suppliersService.get(id!),
    enabled: !!id,
  });

  if (isLoading || !supplier) return <LoadingScreen />;

  return (
    <Screen>
      <ScreenHeader title={supplier.name} subtitle="Supplier profile" showBack />

      <Card style={styles.section}>
        {[
          ['Contact', supplier.contact_person],
          ['Phone', supplier.phone],
          ['Email', supplier.email],
          ['GSTIN', supplier.gstin],
          ['Address', supplier.address],
          ['Payment terms', supplier.payment_terms_days ? `${supplier.payment_terms_days} days` : null],
          ['Added', formatDate(supplier.created_at)],
        ]
          .filter(([, value]) => value)
          .map(([label, value]) => (
            <View key={label} style={styles.row}>
              <Text style={styles.label}>{label}</Text>
              <Text style={styles.value}>{value}</Text>
            </View>
          ))}
      </Card>
    </Screen>
  );
}

const styles = StyleSheet.create({
  section: { gap: spacing.lg },
  row: { gap: 4 },
  label: { ...typography.caption, color: colors.textSecondary },
  value: { ...typography.bodyBold, color: colors.text },
});
