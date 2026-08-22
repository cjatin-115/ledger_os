export const colors = {
  background: '#F6F4EF',
  surface: '#FFFFFF',
  surfaceMuted: '#FFFDF8',
  primary: '#1D3327',
  primaryLight: '#2A4A3A',
  accent: '#9A6B36',
  accentLight: '#D6A15D',
  text: '#17211B',
  textSecondary: '#6F786F',
  textMuted: '#A0A79F',
  border: '#EEECE7',
  borderStrong: '#E6E1D8',
  success: '#4C8B62',
  warning: '#C38B55',
  error: '#B84A3A',
  heroLabel: '#AFC8A6',
  heroText: '#FFFDF7',
  sage: '#DDE8D7',
  sageDark: '#375A3F',
  iconTile: '#F3E5D3',
  tabInactive: '#9AA198',
  overlay: 'rgba(23, 33, 27, 0.45)',
} as const;

export const spacing = {
  xs: 4,
  sm: 8,
  md: 12,
  lg: 16,
  xl: 22,
  xxl: 32,
} as const;

export const radii = {
  sm: 10,
  md: 14,
  lg: 18,
  full: 999,
} as const;

export const typography = {
  eyebrow: { fontSize: 11, fontWeight: '800' as const, letterSpacing: 1.4 },
  title: { fontSize: 28, fontWeight: '800' as const },
  titleLarge: { fontSize: 34, fontWeight: '800' as const },
  heading: { fontSize: 18, fontWeight: '800' as const },
  body: { fontSize: 14, fontWeight: '500' as const },
  bodyBold: { fontSize: 14, fontWeight: '700' as const },
  caption: { fontSize: 12, fontWeight: '600' as const },
  label: { fontSize: 13, fontWeight: '700' as const },
} as const;

export const shadows = {
  card: {
    shadowColor: '#1D3327',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.06,
    shadowRadius: 12,
    elevation: 3,
  },
} as const;
