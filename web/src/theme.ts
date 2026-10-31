import type { ThemeConfig } from 'antd'

// Mirrors the variables in index.css; antd cannot read CSS variables for its derived colours.
const ink = '#1b2422'
const accent = '#0d5257'
const rule = '#d8d2c3'
const paper = '#f5f2ea'
const sheet = '#fffdf7'

export const theme: ThemeConfig = {
  token: {
    colorPrimary: accent,
    colorLink: accent,
    colorText: ink,
    colorTextSecondary: '#4c5652',
    colorTextTertiary: '#6a726e',
    colorBorder: '#c9c2b1',
    colorBorderSecondary: rule,
    colorBgLayout: paper,
    colorBgContainer: sheet,
    colorBgElevated: sheet,
    colorFillAlter: '#efebe0',
    colorSuccess: '#2e7d4f',
    colorWarning: '#b26b12',
    colorError: '#a23b2c',
    colorInfo: accent,
    borderRadius: 3,
    borderRadiusSM: 2,
    borderRadiusLG: 4,
    fontFamily: "'Inter Variable', 'PingFang SC', 'Microsoft YaHei', 'Noto Sans CJK SC', system-ui, sans-serif",
    fontSize: 14,
    boxShadowSecondary: '0 8px 24px -6px rgba(27, 36, 34, 0.18), 0 2px 6px rgba(27, 36, 34, 0.08)',
  },
  components: {
    Table: {
      headerBg: 'transparent',
      headerSplitColor: 'transparent',
      rowHoverBg: '#efebe0',
      rowSelectedBg: '#e2ecea',
      rowSelectedHoverBg: '#d6e5e2',
      borderColor: rule,
      cellPaddingBlockSM: 8,
      cellPaddingInlineSM: 8,
      headerSortActiveBg: '#efebe0',
      headerSortHoverBg: '#efebe0',
      bodySortBg: 'transparent',
      fixedHeaderSortActiveBg: '#efebe0',
    },
    Descriptions: { labelBg: '#efebe0', titleMarginBottom: 8 },
    Tabs: { itemColor: '#4c5652', inkBarColor: accent, titleFontSize: 15 },
    Tag: { defaultBg: '#efebe0', defaultColor: '#4c5652' },
    Popover: { titleMinWidth: 280 },
    Collapse: { headerBg: '#efebe0', contentBg: 'transparent' },
    Alert: { withDescriptionPadding: '12px 16px' },
  },
}
