import { Ionicons } from '@expo/vector-icons';
import { Tabs, useRouter } from 'expo-router';
import React, { useState } from 'react';
import { Platform, Pressable, StyleSheet, View } from 'react-native';

import { ActionSheetModal } from '../../components/ActionSheetModal';
import { colors } from '../../constants/theme';

export default function AppLayout() {
  const router = useRouter();
  const [actionSheetVisible, setActionSheetVisible] = useState(false);

  const handleActionSelect = (action: 'scan_bill' | 'manual_bill' | 'record_payment' | 'add_supplier') => {
    switch (action) {
      case 'scan_bill':
        router.push('/(app)/bills/scan');
        break;
      case 'manual_bill':
        router.push('/(app)/bills/scan');
        break;
      case 'record_payment':
        router.push('/(app)/payments/new');
        break;
      case 'add_supplier':
        router.push('/(app)/suppliers/new');
        break;
    }
  };

  return (
    <>
      <Tabs
        screenOptions={{
          headerShown: false,
          tabBarActiveTintColor: colors.primary,
          tabBarInactiveTintColor: colors.tabInactive,
          tabBarLabelStyle: { fontSize: 11, fontWeight: '700' },
          tabBarStyle: {
            height: Platform.OS === 'ios' ? 86 : 66,
            paddingTop: 8,
            paddingBottom: Platform.OS === 'ios' ? 24 : 10,
            borderTopWidth: 1,
            borderTopColor: colors.border,
            backgroundColor: colors.surface,
          },
        }}
      >
        <Tabs.Screen
          name="index"
          options={{
            title: 'Home',
            tabBarIcon: ({ color, size }) => <Ionicons name="home-outline" size={size} color={color} />,
          }}
        />
        <Tabs.Screen
          name="bills/index"
          options={{
            title: 'Bills',
            tabBarIcon: ({ color, size }) => (
              <Ionicons name="receipt-outline" size={size} color={color} />
            ),
          }}
        />
        <Tabs.Screen
          name="action_dummy"
          options={{
            title: '',
            tabBarButton: () => (
              <Pressable
                style={styles.fabCenterContainer}
                onPress={() => setActionSheetVisible(true)}
              >
                <View style={styles.fabCenter}>
                  <Ionicons name="add" size={28} color="#FFFFFF" />
                </View>
              </Pressable>
            ),
          }}
        />
        <Tabs.Screen
          name="suppliers/index"
          options={{
            title: 'Suppliers',
            tabBarIcon: ({ color, size }) => <Ionicons name="people-outline" size={size} color={color} />,
          }}
        />
        <Tabs.Screen
          name="payments/index"
          options={{
            title: 'Payments',
            tabBarIcon: ({ color, size }) => <Ionicons name="wallet-outline" size={size} color={color} />,
          }}
        />
        <Tabs.Screen name="bills/[id]" options={{ href: null }} />
        <Tabs.Screen name="bills/scan" options={{ href: null }} />
        <Tabs.Screen name="payments/[id]" options={{ href: null }} />
        <Tabs.Screen name="payments/scan" options={{ href: null }} />
        <Tabs.Screen name="payments/new" options={{ href: null }} />
        <Tabs.Screen name="suppliers/[id]" options={{ href: null }} />
        <Tabs.Screen name="suppliers/new" options={{ href: null }} />
        <Tabs.Screen name="work-in-progress" options={{ href: null }} />
      </Tabs>

      <ActionSheetModal
        visible={actionSheetVisible}
        onClose={() => setActionSheetVisible(false)}
        onSelectAction={handleActionSelect}
      />
    </>
  );
}

const styles = StyleSheet.create({
  fabCenterContainer: {
    top: -14,
    justifyContent: 'center',
    alignItems: 'center',
    width: 60,
  },
  fabCenter: {
    width: 52,
    height: 52,
    borderRadius: 26,
    backgroundColor: colors.primary,
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: colors.primary,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 6,
  },
});
