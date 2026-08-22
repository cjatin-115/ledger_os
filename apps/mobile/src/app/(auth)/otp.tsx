import { useRouter } from 'expo-router';
import React, { useState } from 'react';
import { Alert, ScrollView, StyleSheet, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { Button } from '../../components/Button';
import { Input } from '../../components/Input';
import { ScreenHeader } from '../../components/ScreenHeader';
import { apiRequest } from '../../services/apiClient';
import { colors, spacing, typography } from '../../constants/theme';

export default function OTPScreen() {
  const router = useRouter();
  const [target, setTarget] = useState('9876543210');
  const [otp, setOtp] = useState('123456');
  const [loading, setLoading] = useState(false);
  const [sentMsg, setSentMsg] = useState('');

  const handleSendOTP = async () => {
    setLoading(true);
    try {
      const res = await apiRequest<{ message: string; test_otp?: string }>('/auth/otp/send', {
        method: 'POST',
        body: { phone_number: target },
      });
      setSentMsg(res.message + (res.test_otp ? ` (Test OTP: ${res.test_otp})` : ''));
    } catch (err: any) {
      Alert.alert('Error sending OTP', err?.message || 'Failed to send verification code.');
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyOTP = async () => {
    setLoading(true);
    try {
      const res = await apiRequest<{ verified: boolean; message: string }>('/auth/otp/verify', {
        method: 'POST',
        body: { phone_number: target, otp },
      });
      if (res.verified) {
        Alert.alert('Success', 'Phone number verified!', [
          { text: 'OK', onPress: () => router.replace('/(auth)/login') },
        ]);
      }
    } catch (err: any) {
      Alert.alert('Verification Failed', err?.message || 'Invalid OTP code.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <SafeAreaView style={styles.safe}>
      <ScrollView contentContainerStyle={styles.content} keyboardShouldPersistTaps="handled">
        <ScreenHeader title="Verify Phone" subtitle="Enter 6-digit OTP code" showBack />

        <View style={styles.form}>
          <Input
            label="Phone number or email"
            value={target}
            onChangeText={setTarget}
            keyboardType="phone-pad"
          />

          <Button
            label="Send Verification Code"
            variant="secondary"
            onPress={handleSendOTP}
            loading={loading}
          />

          {sentMsg ? <Text style={styles.sentText}>✅ {sentMsg}</Text> : null}

          <Input
            label="6-Digit OTP Code"
            value={otp}
            onChangeText={setOtp}
            keyboardType="number-pad"
            maxLength={6}
          />

          <Button
            label="Verify & Continue"
            onPress={handleVerifyOTP}
            loading={loading}
            style={{ marginTop: spacing.md }}
          />
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: colors.background },
  content: { padding: spacing.xl, maxWidth: 480, alignSelf: 'center', width: '100%' },
  form: { gap: spacing.lg, marginTop: spacing.xl },
  sentText: { ...typography.caption, color: colors.success, textAlign: 'center' },
});
