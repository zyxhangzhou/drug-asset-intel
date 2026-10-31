// Display labels for the controlled vocabularies of src/intel/enums.py and the scoring rules.

export const STAGE: Record<string, string> = {
  preclinical: '临床前',
  phase1: '1 期',
  phase1_2: '1/2 期',
  phase2: '2 期',
  phase2_3: '2/3 期',
  phase3: '3 期',
  filed: '已申报',
  approved: '已上市',
  unknown: '未知',
}

export const STAGE_ORDER = Object.keys(STAGE)

export const TA: Record<string, string> = {
  oncology: '肿瘤',
  heme_malignancy: '血液肿瘤',
  hematology: '血液（非肿瘤）',
  immunology: '免疫',
  neuroscience: '神经',
  infectious: '感染',
  rare_genetic: '罕见遗传病',
  obesity_metabolic: '肥胖与代谢',
  cardiovascular: '心血管',
  respiratory: '呼吸',
  ophthalmology: '眼科',
  liver: '肝病',
  renal: '肾病',
  attr: 'ATTR 淀粉样变',
}

export const taLabel = (codes: string | null) =>
  codes ? codes.split(';').map((c) => TA[c] ?? c).join('、') : '未归类'

// Order and weights follow docs/scoring-rules.md §3.
export const DIMENSIONS: { key: string; label: string; short: string }[] = [
  { key: 'buyer_fit', label: '买方契合度', short: '契合' },
  { key: 'stage_match', label: '研发阶段匹配度', short: '阶段' },
  { key: 'clinical', label: '临床证据与差异化', short: '临床' },
  { key: 'catalyst', label: '近期催化', short: '催化' },
  { key: 'dealability', label: '可交易性', short: '交易' },
]

export const RESEARCH_STATUS: Record<string, string> = {
  auto: '自动初筛',
  reviewed: '已复核',
  deep: '深度研究',
}

export const RIGHTS: Record<string, string> = {
  full: '全部权益',
  partial: '部分地区已授出',
  restricted: '受限（期权 / 优先权 / 共同开发）',
}

export const PRODUCED_BY: Record<string, string> = {
  api: '官方接口',
  manual: '人工',
  llm: 'LLM 抽取',
}

export const KIND: Record<string, string> = { fact: '事实', inference: '推断' }

export const CONFIDENCE: Record<string, string> = {
  high: '高',
  medium_high: '中高',
  medium: '中',
  low: '低',
}

export const SOURCE_TYPE: Record<string, string> = {
  mnc_material: '对方材料',
  sec_filing: 'SEC 申报',
  sec_xbrl: 'SEC XBRL',
  ctgov: 'ClinicalTrials.gov',
  openfda: 'openFDA',
  fda_web: 'FDA 官网',
  company_ir: '公司投资者关系',
  press_release: '新闻稿',
  publication: '文献',
  market_data: '行情数据',
  other: '其他',
}

export const CATALYST_TYPE: Record<string, string> = {
  data_readout: '数据读出',
  regulatory_filing: '监管申报',
  regulatory_decision: '监管决定',
  trial_start: '试验启动',
  other: '其他',
}

export const DATE_TYPE: Record<string, string> = { ESTIMATED: '预计', ACTUAL: '实际' }

export const PREFERENCE_DIMENSION: Record<string, string> = {
  therapeutic_area: '治疗领域',
  modality: '技术类型',
}

export const label = (map: Record<string, string>, key: string | null | undefined) =>
  key == null ? '—' : (map[key] ?? key)

// Amounts in the snapshot are in units of currency; show them in billions or millions.
export function money(v: number | null | undefined, currency = 'USD'): string {
  if (v == null) return '—'
  const sign = v < 0 ? '-' : ''
  const a = Math.abs(v)
  const unit = currency === 'USD' ? '$' : `${currency} `
  if (a >= 1e9) return `${sign}${unit}${(a / 1e9).toFixed(2)}B`
  if (a >= 1e6) return `${sign}${unit}${(a / 1e6).toFixed(1)}M`
  return `${sign}${unit}${a.toLocaleString()}`
}

// Buyer workbook amounts are already in billions of the stated currency.
export const billions = (v: number | null | undefined, currency: string) =>
  v == null ? '—' : `${v.toLocaleString()} ${currency === 'USD' ? '十亿美元' : `十亿 ${currency}`}`

// CT.gov-derived asset names often carry every alias in brackets; show the part before the first bracket
// and keep the full name on hover. Display only: the stored name is unchanged.
export function shortAsset(name: string | null | undefined): string {
  if (!name) return '—'
  const cut = name.search(/\s*[(（]/)
  return cut > 0 && name.length > 24 ? name.slice(0, cut) : name
}
