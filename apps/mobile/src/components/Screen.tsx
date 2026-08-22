import React from 'react';
import {
  ActivityIndicator,
  RefreshControl,
  ScrollView,
  StyleSheet,
  View,
  type ScrollViewProps,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { colors } from '../constants/theme';
import { useResponsive } from '../hooks/useResponsive';

type ScreenProps = ScrollViewProps & {
  children: React.ReactNode;
  centered?: boolean;
  refreshing?: boolean;
  onRefresh?: () => void;
  safe?: boolean;
};

export function Screen({
  children,
  centered,
  refreshing,
  onRefresh,
  safe = true,
  contentContainerStyle,
  ...props
}: ScreenProps) {
  const { contentWidth, horizontalPadding } = useResponsive();
  const Wrapper = safe ? SafeAreaView : View;

  return (
    <Wrapper style={styles.safe} edges={['top', 'left', 'right']}>
      <ScrollView
        showsVerticalScrollIndicator={false}
        refreshControl={
          onRefresh ? (
            <RefreshControl refreshing={!!refreshing} onRefresh={onRefresh} tintColor={colors.primary} />
          ) : undefined
        }
        contentContainerStyle={[
          styles.content,
          { paddingHorizontal: horizontalPadding },
          centered && styles.centered,
          contentContainerStyle,
        ]}
        {...props}
      >
        <View style={[styles.inner, { maxWidth: contentWidth, width: '100%' }]}>{children}</View>
      </ScrollView>
    </Wrapper>
  );
}

export function LoadingScreen() {
  return (
    <SafeAreaView style={styles.loading}>
      <ActivityIndicator size="large" color={colors.primary} />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: colors.background },
  content: { paddingBottom: 40, flexGrow: 1 },
  inner: { alignSelf: 'center' },
  centered: { flexGrow: 1, justifyContent: 'center' },
  loading: {
    flex: 1,
    backgroundColor: colors.background,
    alignItems: 'center',
    justifyContent: 'center',
  },
});
