import { Alert, Card, Collapse, Descriptions, Table, Tabs, Tag } from 'antd'
import { Link, useParams } from 'react-router'
import { fetchTarget, type Recommendation, type TargetDetail as Detail, type TrialResult } from '../api/client'
import { useApi } from '../api/useApi'
import { Loaded } from '../components/Loaded'
import { PageHead, Score } from '../components/Page'
import { Legend, Sourced, SourcedText } from '../components/Sourced'
import { CATALYST_TYPE, DATE_TYPE, DIMENSIONS, label, money, RESEARCH_STATUS, RIGHTS, STAGE, taLabel } from '../labels'

const REVIEW_FIELDS: [keyof Recommendation, string][] = [
  ['need_item', '对应买方需求'],
  ['match_note', '匹配说明'],
  ['design', '研究设计'],
  ['result', '结果'],
  ['comparability', '可比性'],
  ['limitation', '局限'],
  ['next_event', '下一事件'],
  ['funding_flag', '资金状况'],
]

// One recommendation direction: asset × indication × buyer.
const direction = (r: Recommendation) => `${r.asset ?? '—'} × ${r.indication ?? '—'} × ${r.buyer ?? '—'}`

// Key facts beside the thesis: the numbers a reader checks first.
function Facts({ r }: { r: Recommendation }) {
  const s = r.sources
  return (
    <aside className="facts">
      <div style={{ display: 'grid', gap: 8 }}>
        <div className="sub">保守分 / 乐观分（0–100）</div>
        <div>
          <span className="big">{r.conservative}</span>
          <span className="sub" style={{ fontSize: 14 }}> / {r.optimistic}</span>
          <span className="sub" style={{ marginLeft: 10 }}>覆盖率 {Math.round(r.coverage * 100)}% · {label(RESEARCH_STATUS, r.research_status)}</span>
        </div>
        <div className="range" aria-hidden>
          <i style={{ left: 0, width: `${r.optimistic}%` }} />
          <span style={{ left: 0, width: `${r.conservative}%` }} />
        </div>
      </div>
      <div className="strip">
        {DIMENSIONS.map((d) => (
          <div key={d.key} title={d.label}>
            <Sourced sources={s} field={d.key}><Score value={r.scores[d.key]} /></Sourced>
            {d.short}
          </div>
        ))}
      </div>
      <dl>
        <dt>资产</dt>
        <dd>{r.asset ?? '—'}</dd>
        <dt>适应症</dt>
        <dd>{r.indication ?? '—'}（{label(STAGE, r.stage)}，{taLabel(r.therapeutic_area)}）</dd>
        <dt>买方 · 偏好</dt>
        <dd>{r.buyer_ticker ? <Link to={`/buyers/${r.buyer_ticker}`}>{r.buyer}</Link> : '—'} · {r.preference ?? '—'}</dd>
        <dt>下一事件时间</dt>
        <dd><Sourced sources={s} field="event_timing"><b>{r.event_timing ?? '—'}</b></Sourced></dd>
        <dt>交易形式</dt>
        <dd><Sourced sources={s} field="deal_form">{r.deal_form ?? '—'}</Sourced></dd>
        <dt>企业价值</dt>
        <dd><Sourced sources={s} field="enterprise_value"><span className="figure">{money(r.enterprise_value)}</span></Sourced></dd>
        <dt>资产权益</dt>
        <dd><Sourced sources={s} field="rights_status">{r.rights_status ? label(RIGHTS, r.rights_status) : '待核实'}</Sourced></dd>
      </dl>
    </aside>
  )
}

function RecommendationView({ r }: { r: Recommendation }) {
  return (
    <>
      <div className="review-top">
        <div style={{ display: 'grid', gap: 8 }}>
          <div>
            <b style={{ fontSize: 15 }}>推荐逻辑</b>
            <span className="sub" style={{ marginLeft: 10 }}>两句话：买方需求与资产的对应；证据、下一事件与主要障碍</span>
          </div>
          {r.thesis ? (
            <p className="thesis">
              <Sourced sources={r.sources} field="thesis">{r.thesis}</Sourced>
            </p>
          ) : (
            <p className="note">仅经自动初筛，尚未撰写推荐逻辑。</p>
          )}
        </div>
        <Facts r={r} />
      </div>
      <dl className="fields">
        {REVIEW_FIELDS.filter(([key]) => r[key]).map(([key, text]) => (
          <div className="field" key={key}>
            <dt>{text}</dt>
            <dd><SourcedText sources={r.sources} field={key} text={r[key] as string} /></dd>
          </div>
        ))}
      </dl>
    </>
  )
}

export function ResultsTable({ results, showTrial = true }: { results: TrialResult[]; showTrial?: boolean }) {
  return (
    <Table
      rowKey={(r, i) => `${r.nct_id}-${i}`}
      size="small"
      dataSource={results}
      pagination={results.length > 20 ? { pageSize: 20 } : false}
      scroll={{ x: 1000 }}
      columns={[
        ...(showTrial
          ? [{ title: '试验', width: 130, render: (_: unknown, r: TrialResult) => <Link className="mono" to={`/trials/${r.nct_id}`}>{r.nct_id}</Link> }]
          : []),
        { title: '终点', width: 240, render: (_, r) => <Sourced sources={r.sources} field="endpoint">{r.endpoint ?? '—'}</Sourced> },
        { title: '结果', render: (_, r) => <SourcedText sources={r.sources} field="result" text={r.result} /> },
        { title: '统计分析', width: 220, render: (_, r) => <SourcedText sources={r.sources} field="analysis" text={r.analysis} /> },
        { title: '对照', width: 140, render: (_, r) => <Sourced sources={r.sources} field="comparator">{r.comparator ?? '—'}</Sourced> },
        { title: '相对标准治疗', width: 160, render: (_, r) => <Sourced sources={r.sources} field="advantage_vs_soc">{r.advantage_vs_soc ?? '—'}</Sourced> },
      ]}
    />
  )
}

function View({ d }: { d: Detail }) {
  const t = d.target
  const [primary, ...others] = d.recommendations
  const f = d.financial
  return (
    <>
      <PageHead
        title={t.name}
        ticker={t.ticker}
        meta={
          <>
            {t.shortlisted && <Tag color="gold">入选</Tag>}
            {t.deep_dive && <Tag color="purple">深度研究</Tag>}
            {t.excluded && <Tag color="red">已排除</Tag>}
            {primary && (
              <span>
                主推荐方向：保守分 <b className="figure" style={{ color: 'var(--ink)' }}>{primary.conservative}</b> / 乐观分 {primary.optimistic} ·
                覆盖率 {Math.round(primary.coverage * 100)}% · {label(RESEARCH_STATUS, primary.research_status)}
              </span>
            )}
          </>
        }
      />
      <Legend />
      {t.selection_rationale && t.selection_rationale !== primary?.thesis && (
        <Alert style={{ marginTop: 12 }} type="success" title="入选理由"
          description={<SourcedText sources={t.sources} field="selection_rationale" text={t.selection_rationale} />} />
      )}
      {t.excluded && (
        <Alert style={{ marginTop: 12 }} type="warning" title="排除原因"
          description={<SourcedText sources={t.sources} field="exclusion_reason" text={t.exclusion_reason} />} />
      )}

      {primary && (
        <Card size="small" title={`${primary.is_primary ? '主推荐方向' : '推荐方向'}：${direction(primary)}`}>
          <p className="note">推荐方向 = 资产 × 适应症 × 买方。公司的分数与排名按主推荐方向计算。</p>
          <RecommendationView r={primary} />
          {others.length > 0 && (
            <div style={{ marginTop: 24 }}>
              <b style={{ fontSize: 15 }}>其他可能方向</b>
              <span className="sub" style={{ marginLeft: 10 }}>不计入公司分数；点开查看各自的评分与依据</span>
              <Collapse style={{ marginTop: 10 }} size="small"
                items={others.map((r, i) => ({
                  key: i,
                  label: direction(r),
                  extra: <span className="sub">保守分 <b className="figure" style={{ color: 'var(--ink)' }}>{r.conservative}</b></span>,
                  children: <RecommendationView r={r} />,
                }))} />
            </div>
          )}
        </Card>
      )}

      {f && (
        <Card size="small" title={`财务快照（截至 ${f.as_of}）`}>
          <Descriptions column={{ xs: 1, md: 3 }} size="small" bordered>
            <Descriptions.Item label="现金及投资"><Sourced sources={f.sources} field="cash_and_investments">{money(f.cash_and_investments)}</Sourced></Descriptions.Item>
            <Descriptions.Item label="总债务"><Sourced sources={f.sources} field="total_debt">{money(f.total_debt)}</Sourced></Descriptions.Item>
            <Descriptions.Item label={`经营现金流（${f.operating_cash_flow_months ?? '?'} 个月）`}>
              <Sourced sources={f.sources} field="operating_cash_flow_ytd">{money(f.operating_cash_flow_ytd)}</Sourced>
            </Descriptions.Item>
            <Descriptions.Item label="可支撑月数"><Sourced sources={f.sources} field="runway_months">{f.runway_months == null ? '—' : f.runway_months.toFixed(0)}</Sourced></Descriptions.Item>
            <Descriptions.Item label="市值"><Sourced sources={f.sources} field="market_cap">{money(f.market_cap)}</Sourced></Descriptions.Item>
            <Descriptions.Item label="收购成本区间">
              <Sourced sources={f.sources} field={['acquisition_cost_low', 'acquisition_cost_high']}>
                {f.acquisition_cost_low == null && f.acquisition_cost_high == null ? '—' : `${money(f.acquisition_cost_low)} – ${money(f.acquisition_cost_high)}`}
              </Sourced>
            </Descriptions.Item>
          </Descriptions>
        </Card>
      )}

      <Tabs
        style={{ marginTop: 32 }}
        items={[
          {
            key: 'pipeline',
            label: `管线（${d.programs.length}）`,
            children: (
              <>
                <p className="note">
                  管线、适应症与阶段由 ClinicalTrials.gov 登记推导（推断）；作用机制与技术类型来自签字的文档抽取或人工核实。
                </p>
                <Table
                  rowKey="name"
                  size="small"
                  pagination={d.programs.length > 20 ? { pageSize: 20 } : false}
                  dataSource={d.programs}
                  scroll={{ x: 900 }}
                  columns={[
                    { title: '药物', dataIndex: 'name', width: 180, render: (v) => <b style={{ wordBreak: 'break-word' }}>{v}</b> },
                    { title: '作用机制', render: (_, p) => <Sourced sources={p.sources} field="mechanism">{p.mechanism ?? '—'}</Sourced> },
                    { title: '技术类型', width: 140, render: (_, p) => <Sourced sources={p.sources} field="modality">{p.modality ?? '—'}</Sourced> },
                    {
                      title: '适应症 · 领域 · 阶段',
                      render: (_, p) => (
                        <div style={{ display: 'grid', gap: 2 }}>
                          {p.indications.map((i) => (
                            <span key={i.id}>
                              <Sourced sources={i.sources} field="indication">{i.indication ?? '—'}</Sourced>
                              {' · '}
                              <Sourced sources={i.sources} field="therapeutic_area">{taLabel(i.therapeutic_area)}</Sourced>
                              {' · '}
                              <Sourced sources={i.sources} field="stage"><Tag>{label(STAGE, i.stage)}</Tag></Sourced>
                            </span>
                          ))}
                        </div>
                      ),
                    },
                  ]}
                />
              </>
            ),
          },
          {
            key: 'trials',
            label: `试验（${d.trials.length}）`,
            children: (
              <Table
                rowKey="nct_id"
                size="small"
                dataSource={d.trials}
                pagination={d.trials.length > 20 ? { pageSize: 20 } : false}
                scroll={{ x: 1180 }}
                columns={[
                  { title: 'NCT', width: 130, render: (_, r) => <Link className="mono" to={`/trials/${r.nct_id}`}>{r.nct_id}</Link> },
                  { title: '标题', dataIndex: 'title', ellipsis: { showTitle: true } },
                  { title: '阶段', width: 70, render: (_, r) => label(STAGE, r.phase) },
                  { title: '状态', dataIndex: 'status', width: 150 },
                  { title: '入组', width: 100, render: (_, r) => (r.enrollment == null ? '—' : `${r.enrollment}（${label(DATE_TYPE, r.enrollment_type)}）`) },
                  { title: '开始', dataIndex: 'start_date', width: 90 },
                  { title: '主要完成', width: 130, render: (_, r) => (r.primary_completion_date ? `${r.primary_completion_date}（${label(DATE_TYPE, r.primary_completion_type)}）` : '—') },
                  { title: '预计读出', dataIndex: 'expected_readout', width: 90, render: (v) => v ?? '—' },
                  { title: '结果', dataIndex: 'results', width: 60, align: 'right' },
                  { title: '来源', width: 170, render: (_, r) => r.source_ids.map((s) => <Link key={s} className="src-chip" to={`/sources/${s}`}>{s}</Link>) },
                ]}
              />
            ),
          },
          { key: 'results', label: `结果（${d.results.length}）`, children: <ResultsTable results={d.results} /> },
          {
            key: 'approvals',
            label: `获批产品（${d.approvals.length}）`,
            children: (
              <Table
                rowKey={(a, i) => `${a.application_number}-${i}`}
                size="small"
                pagination={false}
                dataSource={d.approvals}
                columns={[
                  { title: '申请号', render: (_, a) => <Sourced sources={a.sources} field="application_number">{a.application_number ?? '—'}</Sourced> },
                  { title: '商品名', render: (_, a) => <Sourced sources={a.sources} field="brand_name">{a.brand_name ?? '—'}</Sourced> },
                  { title: '活性成分', render: (_, a) => <Sourced sources={a.sources} field="active_ingredients">{a.active_ingredients ?? '—'}</Sourced> },
                  { title: '首次批准', render: (_, a) => <Sourced sources={a.sources} field="first_approval_date">{a.first_approval_date ?? '—'}</Sourced> },
                ]}
              />
            ),
          },
          {
            key: 'catalysts',
            label: `催化事件（${d.catalysts.length}）`,
            children: (
              <Table
                rowKey={(c, i) => `${c.event}-${i}`}
                size="small"
                pagination={false}
                dataSource={d.catalysts}
                columns={[
                  { title: '事件', render: (_, c) => <Sourced sources={c.sources} field="event">{c.event ?? '—'}</Sourced> },
                  { title: '药物', dataIndex: 'program', width: 120, render: (v) => v ?? '—' },
                  { title: '类型', width: 100, render: (_, c) => label(CATALYST_TYPE, c.event_type) },
                  {
                    title: '时间窗',
                    width: 200,
                    render: (_, c) => (
                      <Sourced sources={c.sources} field={['window_start', 'window_end']}>
                        {c.window_start ?? '?'} – {c.window_end ?? '?'}
                      </Sourced>
                    ),
                  },
                ]}
              />
            ),
          },
        ]}
      />
    </>
  )
}

export default function TargetDetail() {
  const { ticker = '' } = useParams()
  const state = useApi(() => fetchTarget(ticker), [ticker])
  return <Loaded state={state}>{(d) => <View d={d} />}</Loaded>
}
