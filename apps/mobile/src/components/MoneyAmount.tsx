import React from 'react';
import { StyleSheet, Text, type StyleProp, type TextStyle } from 'react-native';

import { colors, typography } from '../constants/theme';
import { formatMoney } from '../utils/format';

type MoneyAmountProps = {
  value: string | number;
  compact?: boolean;
  size?: 'sm' | 'md' | 'lg' | 'hero';
  style?: StyleProp<TextStyle>;
};

export function MoneyAmount({ value, compact, size = 'md', style }: MoneyAmountProps) {
  return (
    <Text style={[styles.base, styles[size], style]}>{formatMoney(value, compact)}</Text>
  );
}

const styles = StyleSheet.create({
  base: { color: colors.text, fontWeight: '800' },
  sm: { fontSize: 14 },
  md: { fontSize: 18 },
  lg: { fontSize: 24 },
  hero: { ...typography.titleLarge, color: colors.heroText },
});
