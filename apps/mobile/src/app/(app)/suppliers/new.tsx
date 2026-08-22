import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useRouter } from 'expo-router';
import React, { useState } from 'react';
import { Alert, ScrollView, StyleSheet } from 'react-native';

import { Button } from '../../../components/Button';
import { Card } from '../../../components/Card';
import { Input } from '../../../components/Input';
import { ScreenHeader } from '../../../components/ScreenHeader';
import { suppliersService } from '../../../services/suppliers';
import { ApiClientError } from '../../../services/apiClient';
import { colors, spacing } from '../../../constants/theme';

export default function NewSupplierScreen() {
  const router = useRouter();
  const queryClient = useQueryClient();

  const [name, setName] = useState('');
  const [phone, setPhone] = useState('');
  const [gstin, setGstin] = useState('');
  const [contact, setContact] = useState('');
  const [address, setAddress] = useState('');

  const mutation = useMutation({
    mutationFn: () =>
      suppliersService.create({
        name: name.trim(),
        phone: phone.trim() || null,
        gstin: gstin.trim().toUpperCase() || null,
        contact_person: contact.trim() || null,
        address: address.trim() || null,
        payment_terms_days: 30,
      }),
    onSuccess: (supplier) => {
      queryClient.invalidateQueries({ queryKey: ['suppliers'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
      Alert.alert('Supplier added', `${supplier.name} is now in your directory.`, [
        { text: 'OK', onPress: () => router.back() },
      ]);
    },
    onError: (error) => {
      Alert.alert(
        'Could not save',
        error instanceof ApiClientError ? error.message : 'Check the fields and try again.',
      );
    },
  });

  return (
    <ScrollView style={styles.safe} contentContainerStyle={styles.content} keyboardShouldPersistTaps="handled">
      <ScreenHeader title="Add supplier" subtitle="Build your vendor directory" showBack />

      <Card style={styles.form}>
        <Input label="Business name *" value={name} onChangeText={setName} />
        <Input label="Contact person" value={contact} onChangeText={setContact} />
        <Input label="Phone" value={phone} onChangeText={setPhone} keyboardType="phone-pad" />
        <Input label="GSTIN" value={gstin} onChangeText={setGstin} autoCapitalize="characters" />
        <Input label="Address" value={address} onChangeText={setAddress} multiline />
      </Card>

      <Button
        label="Save supplier"
        onPress={() => mutation.mutate()}
        loading={mutation.isPending}
        disabled={!name.trim()}
      />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: colors.background },
  content: { padding: spacing.xl, paddingBottom: 40, maxWidth: 720, alignSelf: 'center', width: '100%' },
  form: { marginBottom: spacing.xl, gap: spacing.lg },
});
