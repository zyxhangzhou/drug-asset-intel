// Types mirror the pydantic response models in src/intel/api.py and src/intel/views.py.

export interface SnapshotMeta {
  generated_at: string | null
  generator: string | null
  snapshot_date: string | null
  counts: Record<string, number>
}

export interface SourceRef {
  source_id: string
  title: string | null
  source_type: string
  publisher: string | null
  published_date: string | null
  published_date_text: string | null
  url: string | null
}

export interface Claim {
  value: string | null
  kind: 'fact' | 'inference'
  confidence: string | null
  produced_by: 'api' | 'manual' | 'llm'
  model: string | null
  quote: string | null
  as_of: string | null
  note: string | null
  source: SourceRef
}

export type Sources = Record<string, Claim[]>

export interface Sourced {
  sources: Sources
}

export type Scores = Record<string, number | null>

export interface ShortlistItem {
  rank: number
  ticker: string
  name: string
  asset: string | null
  indication: string | null
  therapeutic_area: string | null
  stage: string | null
  buyer_ticker: string | null
  buyer: string | null
  preference: string | null
  scores: Scores
  conservative: number
  optimistic: number
  coverage: number
  research_status: string
  shortlisted: boolean
  next_event: string | null
  event_timing: string | null
  enterprise_value: number | null
  rights_status: string | null
  funding_flag: string | null
  thesis: string | null
}

export interface Shortlist {
  weights: Record<string, number>
  items: ShortlistItem[]
}

export interface BuyerSummary {
  ticker: string
  name: string
  name_zh: string | null
  preferences: number
  primary_targets: number
  therapeutic_areas: string[]
  loe: { product: string; us_loe: string }[]
}

export interface Buyer extends Sourced {
  ticker: string
  name: string
  name_zh: string | null
  financial_signals: string | null
  therapeutic_priorities: string | null
  modality_priorities: string | null
  deal_preference: string | null
  buy_rationale: string | null
  key_evidence: string | null
  confidence: string | null
}

export interface Preference extends Sourced {
  id: number
  dimension: string
  rank: number
  label: string | null
  need_type: string | null
  target_profile: string | null
  evidence: string | null
  analysis: string | null
  ideal_stage: string | null
  deal_form: string | null
  confidence: string | null
}

export interface BuyerFinancial extends Sourced {
  fiscal_year: string
  currency: string
  revenue_total: number | null
  revenue_us: number | null
  cash_and_short_term_investments: number | null
  total_debt: number | null
  net_debt: number | null
  free_cash_flow: number | null
  capital_allocation_note: string | null
  recent_deals: string | null
  focus_areas: string | null
}

export interface LoeProduct extends Sourced {
  product: string
  revenue_global: number | null
  revenue_us: number | null
  us_loe: string | null
  generic_status: string | null
  defense: string | null
  basis_note: string | null
}

export interface BuyerMatch extends Sourced {
  ticker: string
  name: string
  shortlisted: boolean
  score: number | null
  rationale: string | null
  confidence: string | null
}

export interface BuyerDetail {
  buyer: Buyer
  preferences: Preference[]
  financials: BuyerFinancial[]
  products: LoeProduct[]
  matches: BuyerMatch[]
}

export interface Target extends Sourced {
  ticker: string
  name: string
  cik: string | null
  excluded: boolean
  exclusion_category: string | null
  exclusion_reason: string | null
  shortlisted: boolean
  deep_dive: boolean
  selection_rationale: string | null
}

export interface Recommendation extends Sourced {
  is_primary: boolean
  asset: string | null
  indication: string | null
  therapeutic_area: string | null
  stage: string | null
  buyer_ticker: string | null
  buyer: string | null
  preference: string | null
  scores: Scores
  need_item: string | null
  match_note: string | null
  deal_form: string | null
  design: string | null
  comparability: string | null
  result: string | null
  limitation: string | null
  next_event: string | null
  event_timing: string | null
  event_importance: string | null
  event_certainty: string | null
  enterprise_value: number | null
  rights_status: string | null
  funding_flag: string | null
  thesis: string | null
  conservative: number
  optimistic: number
  coverage: number
  research_status: string
}

export interface Indication extends Sourced {
  id: number
  indication: string | null
  therapeutic_area: string | null
  stage: string
}

export interface Program extends Sourced {
  name: string
  mechanism: string | null
  modality: string | null
  indications: Indication[]
}

export interface Approval extends Sourced {
  application_number: string | null
  brand_name: string | null
  active_ingredients: string | null
  first_approval_date: string | null
}

export interface Catalyst extends Sourced {
  program: string | null
  event: string | null
  event_type: string
  window_start: string | null
  window_end: string | null
}

export interface Financial extends Sourced {
  as_of: string
  currency: string
  cash_and_investments: number | null
  total_debt: number | null
  operating_cash_flow_ytd: number | null
  operating_cash_flow_months: number | null
  runway_months: number | null
  shares_outstanding: number | null
  share_price: number | null
  market_cap: number | null
  acquisition_cost_low: number | null
  acquisition_cost_high: number | null
}

export interface TrialSummary {
  nct_id: string
  title: string | null
  phase: string | null
  status: string | null
  enrollment: number | null
  enrollment_type: string | null
  start_date: string | null
  primary_completion_date: string | null
  primary_completion_type: string | null
  expected_readout: string | null
  indication: string | null
  results: number
  source_ids: string[]
}

export interface TrialResult extends Sourced {
  nct_id: string
  trial_title: string | null
  endpoint: string | null
  result: string | null
  analysis: string | null
  comparator: string | null
  advantage_vs_soc: string | null
}

export interface TargetDetail {
  target: Target
  recommendations: Recommendation[]
  programs: Program[]
  approvals: Approval[]
  catalysts: Catalyst[]
  financial: Financial | null
  trials: TrialSummary[]
  results: TrialResult[]
}

export interface Trial extends Sourced {
  nct_id: string
  title: string | null
  phase: string | null
  status: string | null
  design: string | null
  conditions: string | null
  interventions: string | null
  enrollment: number | null
  enrollment_type: string | null
  start_date: string | null
  primary_completion_date: string | null
  primary_completion_type: string | null
  completion_date: string | null
  expected_readout: string | null
}

export interface TrialDetail {
  trial: Trial
  ticker: string
  company: string
  asset: string | null
  indication: Indication | null
  results: TrialResult[]
}

export interface SourceDetail {
  source_id: string
  url: string | null
  source_type: string
  title: string | null
  publisher: string | null
  doc_kind: string | null
  note: string | null
  published_date: string | null
  published_date_text: string | null
  fetched_at: string
  content_hash: string | null
  link_status: string
  has_text: boolean
  claims: number
}

async function get(path: string): Promise<Response> {
  const resp = await fetch(path)
  if (!resp.ok) throw new Error(resp.status === 404 ? '未找到' : `${path} → HTTP ${resp.status}`)
  return resp
}

const getJson = async <T,>(path: string): Promise<T> => (await get(path)).json() as Promise<T>
const enc = encodeURIComponent

export const fetchMeta = () => getJson<SnapshotMeta>('/api/meta')
export const fetchShortlist = (weights?: number[]) =>
  getJson<Shortlist>(weights ? `/api/shortlist?weights=${weights.join(',')}` : '/api/shortlist')
export const fetchBuyers = () => getJson<BuyerSummary[]>('/api/buyers')
export const fetchBuyer = (ticker: string) => getJson<BuyerDetail>(`/api/buyers/${enc(ticker)}`)
export const fetchTarget = (ticker: string) => getJson<TargetDetail>(`/api/targets/${enc(ticker)}`)
export const fetchTrial = (nct: string) => getJson<TrialDetail>(`/api/trials/${enc(nct)}`)
export const fetchSource = (id: string) => getJson<SourceDetail>(`/api/sources/${enc(id)}`)
export const fetchSourceText = async (id: string) => (await get(`/api/sources/${enc(id)}/text`)).text()
