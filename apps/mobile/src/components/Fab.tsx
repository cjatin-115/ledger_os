import { Ionicons } from '@expo/vector-icons';
import React from 'react';
import { Pressable, StyleSheet } from 'react-native';

import { colors, shadows } from '../constants/theme';

type FabProps = {
  onPress: () => void;
  icon?: keyof typeof Ionicons.glyphMap;
};

export function Fab({ onPress, icon = 'add' }: FabProps) {
  return (
    <Pressable
      style={({ pressed }) => [styles.fab, shadows.card, pressed && styles.pressed]}
      onPress={onPress}
    >
      <Ionicons name={icon} size={26} color={colors.surfaceMuted} />
    </Pressable>
  );
}

const styles = StyleSheet.create({
  fab: {
    position: 'absolute',
    right: 22,
    bottom: 24,
    width: 56,
    height: 56,
    borderRadius: 28,
    backgroundColor: colors.primary,
    alignItems: 'center',
    justifyContent: 'center',
  },
  pressed: { transform: [{ scale: 0.95 }] },
});
