export const colors = {
  background: '#F7F8FA',
  surface: '#FFFFFF',
  surfaceMuted: '#F8FAFC',
  primary: '#3157D5',
  primaryLight: '#EBF0FF',
  primaryDark: '#1E3BB3',
  accent: '#F59E0B',
  accentLight: '#FEF3C7',
  text: '#151821',
  textSecondary: '#6B7280',
  textMuted: '#9CA3AF',
  border: '#E5E7EB',
  borderStrong: '#D1D5DB',
  success: '#18A673',
  successLight: '#E6F7F0',
  warning: '#E6A21A',
  warningLight: '#FFF8EB',
  danger: '#D64545',
  dangerLight: '#FDF2F2',
  error: '#D64545',
  sage: '#E2E8F0',
  sageDark: '#334155',
  heroLabel: '#60A5FA',
  heroText: '#FFFFFF',
  iconTile: '#F1F5F9',
  tabInactive: '#94A3B8',
  overlay: 'rgba(15, 23, 42, 0.45)',
} as const;

export const spacing = {
  xs: 4,
  sm: 8,
  md: 12,
  lg: 16,
  xl: 24,
  xxl: 32,
} as const;

export const radii = {
  sm: 12,
  md: 16,
  lg: 20,
  full: 9999,
} as const;

export const typography = {
  eyebrow: { fontSize: 11, fontWeight: '800' as const, letterSpacing: 1.2 },
  display: { fontSize: 32, fontWeight: '800' as const, letterSpacing: -0.5 },
  titleLarge: { fontSize: 26, fontWeight: '800' as const, letterSpacing: -0.3 },
  title: { fontSize: 20, fontWeight: '700' as const },
  heading: { fontSize: 16, fontWeight: '700' as const },
  body: { fontSize: 14, fontWeight: '500' as const },
  bodyBold: { fontSize: 14, fontWeight: '700' as const },
  caption: { fontSize: 12, fontWeight: '600' as const },
  label: { fontSize: 13, fontWeight: '700' as const },
} as const;

export const shadows = {
  card: {
    shadowColor: '#0F172A',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.04,
    shadowRadius: 8,
    elevation: 2,
  },
  modal: {
    shadowColor: '#0F172A',
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.12,
    shadowRadius: 24,
    elevation: 10,
  },
} as const;
