import { useWindowDimensions } from 'react-native';

import { CONTENT_MAX_WIDTH, getColumns, getDeviceSize, type DeviceSize } from '../constants/layout';

export function useResponsive() {
  const { width, height } = useWindowDimensions();
  const deviceSize = getDeviceSize(width);
  const isTablet = deviceSize !== 'phone';
  const isDesktop = deviceSize === 'desktop';
  const contentWidth = Math.min(width, CONTENT_MAX_WIDTH);
  const horizontalPadding = isTablet ? 28 : 20;

  return {
    width,
    height,
    deviceSize,
    isTablet,
    isDesktop,
    contentWidth,
    horizontalPadding,
    columns: (phone = 1, tablet = 2, desktop = 3) => getColumns(deviceSize, phone, tablet, desktop),
  };
}

export type { DeviceSize };
