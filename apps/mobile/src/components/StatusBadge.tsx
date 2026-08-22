import React from 'react';
import { StyleSheet, Text, View } from 'react-native';

import { colors, radii, typography } from '../constants/theme';

const STATUS_COLORS: Record<string, { bg: string; text: string }> = {
  draft: { bg: '#F3E5D3', text: colors.accent },
  posted: { bg: '#E8F0EA', text: colors.success },
  partially_paid: { bg: '#FFF3E0', text: '#B8730A' },
  paid: { bg: '#E8F0EA', text: colors.success },
  cancelled: { bg: '#F5E8E6', text: colors.error },
  recorded: { bg: '#E8F0EA', text: colors.success },
};

export function StatusBadge({ status }: { status: string }) {
  const palette = STATUS_COLORS[status] ?? { bg: colors.sage, text: colors.primary };
  const label = status.replace(/_/g, ' ');

  return (
    <View style={[styles.badge, { backgroundColor: palette.bg }]}>
      <Text style={[styles.text, { color: palette.text }]}>{label}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  badge: {
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: radii.full,
    alignSelf: 'flex-start',
  },
  text: { ...typography.caption, textTransform: 'capitalize' },
});
