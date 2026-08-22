export const BREAKPOINTS = {
  tablet: 768,
  desktop: 1024,
} as const;

export const CONTENT_MAX_WIDTH = 960;

export type DeviceSize = 'phone' | 'tablet' | 'desktop';

export function getDeviceSize(width: number): DeviceSize {
  if (width >= BREAKPOINTS.desktop) return 'desktop';
  if (width >= BREAKPOINTS.tablet) return 'tablet';
  return 'phone';
}

export function getColumns(deviceSize: DeviceSize, phone = 1, tablet = 2, desktop = 3): number {
  if (deviceSize === 'desktop') return desktop;
  if (deviceSize === 'tablet') return tablet;
  return phone;
}
