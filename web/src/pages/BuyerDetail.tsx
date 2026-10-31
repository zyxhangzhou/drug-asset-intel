import { Card, Descriptions, Table, Tag } from 'antd'
import { Link, useParams } from 'react-router'
import { fetchBuyer, type BuyerDetail as Detail } from '../api/client'
import { useApi } from '../api/useApi'
import { Loaded } from '../components/Loaded'
import { PageHead } from '../components/Page'
import { Legend, Sourced, SourcedText } from '../components/Sourced'
import { billions, CONFIDENCE, label, PREFERENCE_DIMENSION } from '../labels'

const PROFILE: [keyof Detail['buyer'], string][] = [
  ['financial_signals', '财务信号'],
  ['therapeutic_priorities', '治疗领域偏好'],
  ['modality_priorities', '技术偏好'],
  ['deal_preference', '交易偏好'],
  ['buy_rationale', '收购逻辑'],
  ['key_evidence', '关键证据'],
]

function View({ d }: { d: Detail }) {
  const b = d.buyer
  return (
    <>
      <PageHead
        title={b.name_zh ?? b.name}
        ticker={b.ticker}
        meta={
          <>
            <span>{b.name}</span>
            <span>画像置信度 {label(CONFIDENCE, b.confidence)}</span>
            <Link to={`/targets?buyer=${b.ticker}`}>查看以其为主组合买方的候选公司 →</Link>
          </>
        }
      />
      <Legend />
      <Card title="画像" size="small">
        <Descriptions column={1} size="small" bordered>
          {PROFILE.map(([key, text]) => (
            <Descriptions.Item key={key} label={text}>
              <SourcedText sources={b.sources} field={key} text={b[key] as string | null} />
            </Descriptions.Item>
          ))}
        </Descriptions>
      </Card>

      <Card title="资产偏好" size="small">
        <Table
          rowKey="id"
          size="small"
          pagination={false}
          scroll={{ x: 900 }}
          dataSource={d.preferences}
          columns={[
            { title: '维度', render: (_, p) => `${label(PREFERENCE_DIMENSION, p.dimension)} #${p.rank}`, width: 110 },
            { title: '偏好', render: (_, p) => <Sourced sources={p.sources} field="label">{p.label}</Sourced>, width: 140 },
            { title: '需求类型', render: (_, p) => <Sourced sources={p.sources} field="need_type">{p.need_type}</Sourced> },
            { title: '目标资产画像', render: (_, p) => <Sourced sources={p.sources} field="target_profile">{p.target_profile}</Sourced> },
            { title: '理想阶段', render: (_, p) => <Sourced sources={p.sources} field="ideal_stage">{p.ideal_stage}</Sourced> },
            { title: '交易形式', render: (_, p) => <Sourced sources={p.sources} field="deal_form">{p.deal_form}</Sourced> },
            { title: '置信度', render: (_, p) => label(CONFIDENCE, p.confidence), width: 70 },
          ]}
          expandable={{
            expandedRowRender: (p) => (
              <Descriptions column={1} size="small">
                <Descriptions.Item label="证据">
                  <SourcedText sources={p.sources} field="evidence" text={p.evidence} />
                </Descriptions.Item>
                <Descriptions.Item label="分析">
                  <SourcedText sources={p.sources} field="analysis" text={p.analysis} />
                </Descriptions.Item>
              </Descriptions>
            ),
          }}
        />
      </Card>

      <Card title="财务" size="small">
        {d.financials.map((f) => (
          <Descriptions key={f.fiscal_year} title={`${f.fiscal_year} 财年`} column={{ xs: 1, md: 2 }} size="small" bordered>
            {(
              [
                ['revenue_total', '总收入'],
                ['revenue_us', '美国收入'],
                ['cash_and_short_term_investments', '现金及短期投资'],
                ['total_debt', '总债务'],
                ['net_debt', '净债务'],
                ['free_cash_flow', '自由现金流'],
              ] as const
            ).map(([key, text]) => (
              <Descriptions.Item key={key} label={text}>
                <Sourced sources={f.sources} field={key}>{billions(f[key], f.currency)}</Sourced>
              </Descriptions.Item>
            ))}
            <Descriptions.Item label="资本配置" span={2}>
              <SourcedText sources={f.sources} field="capital_allocation_note" text={f.capital_allocation_note} />
            </Descriptions.Item>
            <Descriptions.Item label="近期交易" span={2}>
              <SourcedText sources={f.sources} field="recent_deals" text={f.recent_deals} />
            </Descriptions.Item>
            <Descriptions.Item label="重点领域" span={2}>
              <SourcedText sources={f.sources} field="focus_areas" text={f.focus_areas} />
            </Descriptions.Item>
          </Descriptions>
        ))}
      </Card>

      <Card title="专利到期产品（美国）" size="small">
        <Table
          rowKey="product"
          size="small"
          pagination={false}
          scroll={{ x: 800 }}
          dataSource={d.products}
          columns={[
            { title: '产品', dataIndex: 'product' },
            { title: '全球收入', render: (_, p) => <Sourced sources={p.sources} field="revenue_global">{p.revenue_global ?? '—'}</Sourced> },
            { title: '美国收入', render: (_, p) => <Sourced sources={p.sources} field="revenue_us">{p.revenue_us ?? '—'}</Sourced> },
            { title: '美国 LOE', render: (_, p) => <Sourced sources={p.sources} field="us_loe">{p.us_loe ?? '—'}</Sourced> },
            { title: '仿制药状态', render: (_, p) => <Sourced sources={p.sources} field="generic_status">{p.generic_status ?? '—'}</Sourced> },
            { title: '防御策略', render: (_, p) => <Sourced sources={p.sources} field="defense">{p.defense ?? '—'}</Sourced> },
          ]}
        />
        <p className="note" style={{ marginTop: 8 }}>收入单位：十亿（本币）</p>
      </Card>

      <Card title={`匹配分最高的候选公司（前 ${d.matches.length}）`} size="small">
        <Table
          rowKey="ticker"
          size="small"
          pagination={false}
          dataSource={d.matches}
          columns={[
            {
              title: '公司',
              render: (_, m) => (
                <>
                  <Link to={`/targets/${m.ticker}`}>{m.name}</Link> <span className="sub">{m.ticker}</span>
                  {m.shortlisted && <Tag color="gold" style={{ marginLeft: 8 }}>入选</Tag>}
                </>
              ),
            },
            { title: '匹配分', render: (_, m) => <Sourced sources={m.sources} field="score"><span className="figure">{m.score}</span></Sourced>, width: 90, align: 'right' as const },
            { title: '匹配理由', render: (_, m) => <SourcedText sources={m.sources} field="rationale" text={m.rationale} /> },
          ]}
        />
      </Card>
    </>
  )
}

export default function BuyerDetail() {
  const { ticker = '' } = useParams()
  const state = useApi(() => fetchBuyer(ticker), [ticker])
  return <Loaded state={state}>{(d) => <View d={d} />}</Loaded>
}
