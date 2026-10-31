import type { ThemeConfig } from 'antd'

// Mirrors the variables in index.css; antd cannot read CSS variables for its derived colours.
const ink = '#111827'
const accent = '#2b50c8'
const line = '#e5e7eb'
const panel2 = '#f9fafb'

export const theme: ThemeConfig = {
  token: {
    colorPrimary: accent,
    colorLink: accent,
    colorText: ink,
    colorTextSecondary: '#374151',
    colorTextTertiary: '#6b7280',
    colorBorder: '#d1d5db',
    colorBorderSecondary: line,
    colorBgLayout: '#f5f6f8',
    colorBgContainer: '#ffffff',
    colorBgElevated: '#ffffff',
    colorFillAlter: panel2,
    colorSuccess: '#1f9254',
    colorWarning: '#c27215',
    colorError: '#c2362b',
    colorInfo: accent,
    borderRadius: 6,
    borderRadiusSM: 4,
    borderRadiusLG: 8,
    fontFamily: "'Inter Variable', 'Noto Sans SC', 'PingFang SC', 'Microsoft YaHei', system-ui, sans-serif",
    fontSize: 14,
    boxShadowSecondary: '0 12px 32px -8px rgba(17, 24, 39, 0.18), 0 2px 6px rgba(17, 24, 39, 0.06)',
  },
  components: {
    Table: {
      headerBg: panel2,
      rowHoverBg: panel2,
      rowSelectedBg: '#eef2fd',
      rowSelectedHoverBg: '#e3e9fb',
      borderColor: line,
      cellPaddingBlockSM: 9,
      cellPaddingInlineSM: 10,
      headerSortActiveBg: '#f1f3f6',
      headerSortHoverBg: '#f1f3f6',
      bodySortBg: 'transparent',
      fixedHeaderSortActiveBg: '#f1f3f6',
    },
    Descriptions: { labelBg: panel2, titleMarginBottom: 8 },
    Tabs: { itemColor: '#374151', inkBarColor: accent, titleFontSize: 14 },
    Tag: { defaultBg: '#f3f4f6', defaultColor: '#374151' },
    Popover: { titleMinWidth: 280 },
    Collapse: { headerBg: panel2, contentBg: '#ffffff' },
    Alert: { withDescriptionPadding: '12px 16px' },
  },
}
