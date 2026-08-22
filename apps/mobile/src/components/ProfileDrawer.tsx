import React from 'react';
import { Modal, Pressable, StyleSheet, Text, View } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useRouter } from 'expo-router';
import { useAuthStore } from '../store/authStore';
import { colors, radii, shadows, spacing, typography } from '../constants/theme';

interface ProfileDrawerProps {
  visible: boolean;
  onClose: () => void;
}

export function ProfileDrawer({ visible, onClose }: ProfileDrawerProps) {
  const router = useRouter();
  const { user, organization, logout } = useAuthStore();

  const handleSignOut = async () => {
    onClose();
    await logout();
    router.replace('/(auth)/login');
  };

  const initials = user?.full_name
    ? user.full_name
        .split(' ')
        .map((n: string) => n[0])
        .join('')
        .toUpperCase()
        .slice(0, 2)
    : 'J';

  return (
    <Modal visible={visible} transparent animationType="fade" onRequestClose={onClose}>
      <Pressable style={styles.backdrop} onPress={onClose}>
        <Pressable style={styles.drawer} onPress={(e) => e.stopPropagation()}>
          {/* Header User Card */}
          <View style={styles.userHeader}>
            <View style={styles.avatar}>
              <Text style={styles.avatarText}>{initials}</Text>
            </View>
            <View style={styles.userInfo}>
              <Text style={styles.userName}>{user?.full_name || 'Jatin'}</Text>
              <Text style={styles.shopName}>{organization?.name || 'ABC Hardware'}</Text>
              <View style={styles.planBadge}>
                <Text style={styles.planText}>Pro Account</Text>
              </View>
            </View>
          </View>

          <View style={styles.divider} />

          {/* Menu Items */}
          <View style={styles.menuList}>
            <Pressable
              style={styles.menuItem}
              onPress={() => {
                onClose();
                router.push({ pathname: '/(app)/work-in-progress', params: { feature: 'Organization Profile' } });
              }}
            >
              <Ionicons name="business-outline" size={20} color={colors.primary} />
              <Text style={styles.menuText}>Organization Profile</Text>
              <Ionicons name="chevron-forward" size={18} color={colors.textMuted} />
            </Pressable>

            <Pressable
              style={styles.menuItem}
              onPress={() => {
                onClose();
                router.push({ pathname: '/(app)/work-in-progress', params: { feature: 'GSTIN & Tax Settings' } });
              }}
            >
              <Ionicons name="card-outline" size={20} color={colors.primary} />
              <Text style={styles.menuText}>GSTIN & Tax Settings</Text>
              <Ionicons name="chevron-forward" size={18} color={colors.textMuted} />
            </Pressable>

            <Pressable
              style={styles.menuItem}
              onPress={() => {
                onClose();
                router.push({ pathname: '/(app)/work-in-progress', params: { feature: 'Payment Reminders' } });
              }}
            >
              <Ionicons name="notifications-outline" size={20} color={colors.primary} />
              <Text style={styles.menuText}>Payment Reminders</Text>
              <Ionicons name="chevron-forward" size={18} color={colors.textMuted} />
            </Pressable>

            <Pressable
              style={styles.menuItem}
              onPress={() => {
                onClose();
                router.push({ pathname: '/(app)/work-in-progress', params: { feature: 'Theme Switcher' } });
              }}
            >
              <Ionicons name="moon-outline" size={20} color={colors.primary} />
              <Text style={styles.menuText}>Appearance & Theme</Text>
              <Text style={styles.tagText}>Light Mode</Text>
            </Pressable>

            <Pressable
              style={styles.menuItem}
              onPress={() => {
                onClose();
                router.push({ pathname: '/(app)/work-in-progress', params: { feature: 'Help & Support' } });
              }}
            >
              <Ionicons name="help-circle-outline" size={20} color={colors.primary} />
              <Text style={styles.menuText}>Help & Support</Text>
              <Ionicons name="chevron-forward" size={18} color={colors.textMuted} />
            </Pressable>
          </View>

          {/* Sign Out Button */}
          <View style={styles.footer}>
            <Pressable style={styles.logoutButton} onPress={handleSignOut}>
              <Ionicons name="log-out-outline" size={20} color={colors.danger} />
              <Text style={styles.logoutText}>Sign Out</Text>
            </Pressable>
          </View>
        </Pressable>
      </Pressable>
    </Modal>
  );
}

const styles = StyleSheet.create({
  backdrop: {
    flex: 1,
    backgroundColor: colors.overlay,
    flexDirection: 'row',
    justifyContent: 'flex-start',
  },
  drawer: {
    width: '80%',
    maxWidth: 320,
    backgroundColor: colors.surface,
    height: '100%',
    paddingTop: spacing.xxl,
    paddingHorizontal: spacing.lg,
    paddingBottom: spacing.xl,
    justifyContent: 'space-between',
    ...shadows.modal,
  },
  userHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.md,
    marginBottom: spacing.md,
  },
  avatar: {
    width: 52,
    height: 52,
    borderRadius: 26,
    backgroundColor: colors.primary,
    justifyContent: 'center',
    alignItems: 'center',
  },
  avatarText: {
    ...typography.heading,
    color: '#FFFFFF',
    fontSize: 18,
  },
  userInfo: {
    flex: 1,
  },
  userName: {
    ...typography.heading,
    color: colors.text,
    fontSize: 17,
  },
  shopName: {
    ...typography.caption,
    color: colors.textSecondary,
    marginTop: 2,
  },
  planBadge: {
    alignSelf: 'flex-start',
    backgroundColor: colors.primaryLight,
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: radii.full,
    marginTop: 4,
  },
  planText: {
    fontSize: 10,
    fontWeight: '700',
    color: colors.primary,
  },
  divider: {
    height: 1,
    backgroundColor: colors.border,
    marginVertical: spacing.md,
  },
  menuList: {
    flex: 1,
    gap: spacing.xs,
    marginTop: spacing.md,
  },
  menuItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 12,
    paddingHorizontal: 8,
    borderRadius: radii.sm,
    gap: spacing.md,
  },
  menuText: {
    flex: 1,
    ...typography.bodyBold,
    color: colors.text,
    fontSize: 14,
  },
  tagText: {
    ...typography.caption,
    color: colors.textMuted,
  },
  footer: {
    borderTopWidth: 1,
    borderTopColor: colors.border,
    paddingTop: spacing.md,
  },
  logoutButton: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.sm,
    paddingVertical: spacing.sm,
    paddingHorizontal: spacing.xs,
  },
  logoutText: {
    ...typography.bodyBold,
    color: colors.danger,
  },
});
