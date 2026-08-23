import { Ionicons } from '@expo/vector-icons';
import React, { useState } from 'react';
import {
  Alert,
  KeyboardAvoidingView,
  Platform,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { Button } from '../../components/Button';
import { Input } from '../../components/Input';
import { checkBackendHealth } from '../../services/api';
import { ApiClientError } from '../../services/apiClient';
import { useAuthStore } from '../../store/authStore';
import { colors, radii, spacing, typography } from '../../constants/theme';

type Mode = 'login' | 'register';

export default function LoginScreen() {
  const { login, register } = useAuthStore();
  const [mode, setMode] = useState<Mode>('login');
  const [loading, setLoading] = useState(false);
  const [connected, setConnected] = useState<boolean | null>(null);
  const [checking, setChecking] = useState(false);

  const [identifier, setIdentifier] = useState('');
  const [password, setPassword] = useState('');
  const [orgName, setOrgName] = useState('');
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');

  const performHealthCheck = React.useCallback(async () => {
    setChecking(true);
    try {
      const ok = await checkBackendHealth();
      setConnected(ok);
    } catch {
      setConnected(false);
    } finally {
      setChecking(false);
    }
  }, []);

  React.useEffect(() => {
    performHealthCheck();
    // Auto-retry checking health every 5s if not connected (helpful for cloud cold starts)
    const interval = setInterval(() => {
      if (!connected) {
        performHealthCheck();
      }
    }, 5000);
    return () => clearInterval(interval);
  }, [connected, performHealthCheck]);

  const handleSubmit = async () => {
    setLoading(true);
    try {
      if (mode === 'login') {
        await login(identifier.trim(), password);
      } else {
        if (!orgName.trim() || !fullName.trim() || !phone.trim()) {
          Alert.alert('Missing fields', 'Shop name, your name, and phone are required.');
          return;
        }
        await register({
          organization_name: orgName.trim(),
          full_name: fullName.trim(),
          phone_number: phone.trim(),
          email: email.trim() || undefined,
          password,
        });
      }
    } catch (error) {
      const message =
        error instanceof ApiClientError ? error.message : 'Something went wrong. Try again.';
      Alert.alert('Unable to sign in', message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <SafeAreaView style={styles.safe}>
      <KeyboardAvoidingView
        style={styles.flex}
        behavior={Platform.OS === 'ios' ? 'padding' : undefined}
      >
        <ScrollView
          contentContainerStyle={styles.scroll}
          keyboardShouldPersistTaps="handled"
          showsVerticalScrollIndicator={false}
        >
          <View style={styles.hero}>
            <View style={styles.logoWrap}>
              <Text style={styles.logoText}>₹</Text>
            </View>
            <Text style={styles.brand}>LedgerOS</Text>
            <Text style={styles.tagline}>Smart payables for your shop</Text>
            <Pressable
              style={styles.statusRow}
              onPress={performHealthCheck}
              disabled={checking}
            >
              <View
                style={[
                  styles.dot,
                  connected
                    ? styles.dotOnline
                    : checking
                      ? styles.dotChecking
                      : styles.dotOffline,
                ]}
              />
              <Text style={styles.statusText}>
                {checking
                  ? 'Connecting to backend…'
                  : connected === null
                    ? 'Checking server status…'
                    : connected
                      ? 'Server connected'
                      : 'Server offline — tap to retry'}
              </Text>
              {!connected && !checking && (
                <Ionicons name="reload" size={12} color={colors.textMuted} style={{ marginLeft: 2 }} />
              )}
            </Pressable>
          </View>

          <View style={styles.tabs}>
            <Pressable
              style={[styles.tab, mode === 'login' && styles.tabActive]}
              onPress={() => setMode('login')}
            >
              <Text style={[styles.tabText, mode === 'login' && styles.tabTextActive]}>Sign in</Text>
            </Pressable>
            <Pressable
              style={[styles.tab, mode === 'register' && styles.tabActive]}
              onPress={() => setMode('register')}
            >
              <Text style={[styles.tabText, mode === 'register' && styles.tabTextActive]}>
                Create shop
              </Text>
            </Pressable>
          </View>

          <View style={styles.form}>
            {mode === 'register' ? (
              <>
                <Input label="Shop / business name" value={orgName} onChangeText={setOrgName} />
                <Input label="Your full name" value={fullName} onChangeText={setFullName} />
                <Input
                  label="Phone number"
                  value={phone}
                  onChangeText={setPhone}
                  keyboardType="phone-pad"
                />
                <Input
                  label="Email (optional)"
                  value={email}
                  onChangeText={setEmail}
                  keyboardType="email-address"
                  autoCapitalize="none"
                />
              </>
            ) : (
              <Input
                label="Phone or email"
                value={identifier}
                onChangeText={setIdentifier}
                autoCapitalize="none"
                keyboardType="email-address"
              />
            )}

            <Input
              label="Password"
              value={password}
              onChangeText={setPassword}
              secureTextEntry
            />

            <Button
              label={mode === 'login' ? 'Sign in' : 'Create account & sign in'}
              onPress={handleSubmit}
              loading={loading}
              style={styles.submit}
            />

            {mode === 'login' ? (
              <Button
                label="⚡ Fill Test Account (9876543210)"
                variant="secondary"
                onPress={() => {
                  setIdentifier('9876543210');
                  setPassword('Demo@1234');
                }}
              />
            ) : null}

            {mode === 'register' ? (
              <Text style={styles.hint}>
                Includes a 14-day free trial. You can scan bills, track suppliers, and record
                payments right away.
              </Text>
            ) : null}
          </View>

          <View style={styles.features}>
            {[
              { icon: 'scan-outline' as const, text: 'Scan & upload bills' },
              { icon: 'people-outline' as const, text: 'Supplier ledger' },
              { icon: 'wallet-outline' as const, text: 'Track payments' },
            ].map((item) => (
              <View key={item.text} style={styles.feature}>
                <Ionicons name={item.icon} size={18} color={colors.accent} />
                <Text style={styles.featureText}>{item.text}</Text>
              </View>
            ))}
          </View>
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: colors.background },
  flex: { flex: 1 },
  scroll: { padding: spacing.xl, paddingBottom: 40, maxWidth: 480, alignSelf: 'center', width: '100%' },
  hero: { alignItems: 'center', marginBottom: spacing.xxl },
  logoWrap: {
    width: 72,
    height: 72,
    borderRadius: 20,
    backgroundColor: colors.primary,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: spacing.lg,
  },
  logoText: { fontSize: 32, fontWeight: '800', color: colors.heroText },
  brand: { ...typography.title, color: colors.text },
  tagline: { ...typography.body, color: colors.textSecondary, marginTop: 6 },
  statusRow: { flexDirection: 'row', alignItems: 'center', marginTop: spacing.md, gap: 6 },
  dot: { width: 8, height: 8, borderRadius: 4, backgroundColor: colors.warning },
  dotOnline: { backgroundColor: colors.success },
  dotChecking: { backgroundColor: colors.primary },
  dotOffline: { backgroundColor: colors.danger },
  statusText: { ...typography.caption, color: colors.textSecondary },
  tabs: {
    flexDirection: 'row',
    backgroundColor: colors.surface,
    borderRadius: radii.sm,
    padding: 4,
    marginBottom: spacing.xl,
    borderWidth: 1,
    borderColor: colors.border,
  },
  tab: { flex: 1, paddingVertical: 12, alignItems: 'center', borderRadius: 8 },
  tabActive: { backgroundColor: colors.primary },
  tabText: { ...typography.bodyBold, color: colors.textSecondary },
  tabTextActive: { color: colors.surfaceMuted },
  form: { gap: spacing.lg },
  submit: { marginTop: spacing.sm },
  hint: { ...typography.caption, color: colors.textMuted, textAlign: 'center', lineHeight: 18 },
  features: { marginTop: spacing.xxl, gap: spacing.md },
  feature: { flexDirection: 'row', alignItems: 'center', gap: spacing.md },
  featureText: { ...typography.body, color: colors.textSecondary },
});
