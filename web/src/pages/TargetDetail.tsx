import { Alert, Card, Collapse, Descriptions, Table, Tabs, Tag, Typography } from 'antd'
import { Link, useParams } from 'react-router'
import { fetchTarget, type Recommendation, type TargetDetail as Detail, type TrialResult } from '../api/client'
import { useApi } from '../api/useApi'
import { Loaded } from '../components/Loaded'
import { Legend, Sourced } from '../components/Sourced'
import { CATALYST_TYPE, DATE_TYPE, DIMENSIONS, label, money, RESEARCH_STATUS, RIGHTS, STAGE, taLabel } from '../labels'

const REVIEW_FIELDS: [keyof Recommendation, string][] = [
  ['need_item', '对应买方需求'],
  ['match_note', '匹配说明'],
  ['deal_form', '可能的交易形式'],
  ['design', '研究设计'],
  ['comparability', '可比性'],
  ['result', '结果'],
  ['limitation', '局限'],
  ['next_event', '下一事件'],
  ['event_timing', '事件时间'],
  ['funding_flag', '资金状况'],
]

function RecommendationView({ r }: { r: Recommendation }) {
  return (
    <>
      <Descriptions column={{ xs: 1, md: 2 }} size="small" bordered>
        <Descriptions.Item label="资产 × 适应症">
          {r.asset ?? '—'} · {r.indication ?? '—'}（{label(STAGE, r.stage)}，{taLabel(r.therapeutic_area)}）
        </Descriptions.Item>
        <Descriptions.Item label="买方 · 偏好">
          {r.buyer_ticker ? <Link to={`/buyers/${r.buyer_ticker}`}>{r.buyer}</Link> : '—'} · {r.preference ?? '—'}
        </Descriptions.Item>
        {DIMENSIONS.map((d) => (
          <Descriptions.Item key={d.key} label={`${d.label}（0–4）`}>
            <Sourced sources={r.sources} field={d.key}>{r.scores[d.key] ?? '—'}</Sourced>
          </Descriptions.Item>
        ))}
        <Descriptions.Item label="保守分 / 乐观分 / 覆盖率">
          {r.conservative} / {r.optimistic} / {Math.round(r.coverage * 100)}%（{label(RESEARCH_STATUS, r.research_status)}）
        </Descriptions.Item>
        {REVIEW_FIELDS.map(([key, text]) => (
          <Descriptions.Item key={key} label={text} span={2}>
            <Sourced sources={r.sources} field={key}>
              <span style={{ whiteSpace: 'pre-wrap' }}>{(r[key] as string | null) ?? '—'}</span>
            </Sourced>
          </Descriptions.Item>
        ))}
        <Descriptions.Item label="企业价值">
          <Sourced sources={r.sources} field="enterprise_value">{money(r.enterprise_value)}</Sourced>
        </Descriptions.Item>
        <Descriptions.Item label="资产权益">
          <Sourced sources={r.sources} field="rights_status">{r.rights_status ? label(RIGHTS, r.rights_status) : '待核实'}</Sourced>
        </Descriptions.Item>
      </Descriptions>
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
          ? [{ title: '试验', width: 130, render: (_: unknown, r: TrialResult) => <Link to={`/trials/${r.nct_id}`}>{r.nct_id}</Link> }]
          : []),
        { title: '终点', width: 240, render: (_, r) => <Sourced sources={r.sources} field="endpoint">{r.endpoint ?? '—'}</Sourced> },
        { title: '结果', render: (_, r) => <Sourced sources={r.sources} field="result">{r.result ?? '—'}</Sourced> },
        { title: '统计分析', width: 200, render: (_, r) => <Sourced sources={r.sources} field="analysis">{r.analysis ?? '—'}</Sourced> },
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
      <Typography.Title level={3} style={{ marginBottom: 4 }}>
        {t.name} <Typography.Text type="secondary">{t.ticker}</Typography.Text>{' '}
        {t.shortlisted && <Tag color="gold">入选</Tag>}
        {t.deep_dive && <Tag color="purple">深度研究</Tag>}
        {t.excluded && <Tag color="red">已排除</Tag>}
      </Typography.Title>
      <Legend />
      {t.selection_rationale && t.selection_rationale !== primary?.thesis && (
        <Alert style={{ marginTop: 12 }} type="success" title="入选理由"
          description={<Sourced sources={t.sources} field="selection_rationale">{t.selection_rationale}</Sourced>} />
      )}
      {t.excluded && (
        <Alert style={{ marginTop: 12 }} type="warning" title="排除原因"
          description={<Sourced sources={t.sources} field="exclusion_reason">{t.exclusion_reason ?? '—'}</Sourced>} />
      )}

      {primary && (
        <Card size="small" style={{ marginTop: 16 }} title={primary.is_primary ? '主组合复核结论' : '组合'}>
          {primary.thesis && (
            <Typography.Paragraph strong>
              <Sourced sources={primary.sources} field="thesis">{primary.thesis}</Sourced>
            </Typography.Paragraph>
          )}
          <RecommendationView r={primary} />
          {others.length > 0 && (
            <Collapse style={{ marginTop: 12 }} size="small"
              items={others.map((r, i) => ({
                key: i,
                label: `其他组合：${r.asset ?? '—'} · ${r.indication ?? '—'} · ${r.buyer ?? '—'}（保守分 ${r.conservative}）`,
                children: <RecommendationView r={r} />,
              }))} />
          )}
        </Card>
      )}

      {f && (
        <Card size="small" style={{ marginTop: 16 }} title={`财务快照（截至 ${f.as_of}）`}>
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
        style={{ marginTop: 16 }}
        items={[
          {
            key: 'pipeline',
            label: `管线（${d.programs.length}）`,
            children: (
              <>
                <Typography.Paragraph type="secondary" style={{ fontSize: 12 }}>
                  管线、适应症与阶段由 ClinicalTrials.gov 登记推导（推断）；作用机制与技术类型来自签字的文档抽取或人工核实。
                </Typography.Paragraph>
                <Table
                  rowKey="name"
                  size="small"
                  pagination={d.programs.length > 20 ? { pageSize: 20 } : false}
                  dataSource={d.programs}
                  scroll={{ x: 900 }}
                  columns={[
                    { title: '药物', dataIndex: 'name', width: 160 },
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
                scroll={{ x: 1200 }}
                columns={[
                  { title: 'NCT', width: 120, render: (_, r) => <Link to={`/trials/${r.nct_id}`}>{r.nct_id}</Link> },
                  { title: '标题', dataIndex: 'title', ellipsis: true },
                  { title: '阶段', width: 70, render: (_, r) => label(STAGE, r.phase) },
                  { title: '状态', dataIndex: 'status', width: 150 },
                  { title: '入组', width: 100, render: (_, r) => (r.enrollment == null ? '—' : `${r.enrollment}（${label(DATE_TYPE, r.enrollment_type)}）`) },
                  { title: '开始', dataIndex: 'start_date', width: 90 },
                  { title: '主要完成', width: 130, render: (_, r) => (r.primary_completion_date ? `${r.primary_completion_date}（${label(DATE_TYPE, r.primary_completion_type)}）` : '—') },
                  { title: '预计读出', dataIndex: 'expected_readout', width: 90, render: (v) => v ?? '—' },
                  { title: '结果', dataIndex: 'results', width: 60, align: 'right' },
                  { title: '来源', width: 150, render: (_, r) => r.source_ids.map((s) => <Link key={s} to={`/sources/${s}`}>{s} </Link>) },
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
