import { Alert, Table, Typography } from 'antd'
import type { ReactNode } from 'react'
import { Link, useSearchParams } from 'react-router'
import { fetchShortlist, type ShortlistItem } from '../api/client'
import { useApi } from '../api/useApi'
import { Loaded } from '../components/Loaded'
import { DIMENSIONS, label, money, RESEARCH_STATUS, RIGHTS, STAGE, taLabel } from '../labels'

const ROWS: [string, (i: ShortlistItem) => ReactNode][] = [
  ['排名', (i) => i.rank],
  ['资产', (i) => i.asset ?? '—'],
  ['适应症', (i) => i.indication ?? '—'],
  ['治疗领域', (i) => taLabel(i.therapeutic_area)],
  ['阶段', (i) => label(STAGE, i.stage)],
  ['买方', (i) => i.buyer ?? '—'],
  ['对应偏好', (i) => i.preference ?? '—'],
  ...DIMENSIONS.map((d): [string, (i: ShortlistItem) => ReactNode] => [`${d.label}（0–4）`, (i) => i.scores[d.key] ?? '—']),
  ['保守分', (i) => i.conservative],
  ['乐观分', (i) => i.optimistic],
  ['覆盖率', (i) => `${Math.round(i.coverage * 100)}%`],
  ['研究状态', (i) => label(RESEARCH_STATUS, i.research_status)],
  ['下一事件', (i) => i.next_event ?? '—'],
  ['事件时间', (i) => i.event_timing ?? '—'],
  ['企业价值', (i) => money(i.enterprise_value)],
  ['资产权益', (i) => (i.rights_status ? label(RIGHTS, i.rights_status) : '待核实')],
  ['资金状况', (i) => i.funding_flag ?? '—'],
  ['两句话论点', (i) => i.thesis ?? '—'],
]

export default function Compare() {
  const [params] = useSearchParams()
  const tickers = (params.get('t') ?? '').split(',').map((t) => t.trim().toUpperCase()).filter(Boolean).slice(0, 4)
  const state = useApi(() => fetchShortlist(), [])
  return (
    <>
      <Typography.Title level={3}>公司对比</Typography.Title>
      <Typography.Paragraph type="secondary">按默认权重比较各公司的主组合。链接可直接分享。</Typography.Paragraph>
      <Loaded state={state}>
        {(s) => {
          const items = tickers.map((t) => s.items.find((i) => i.ticker === t))
          const missing = tickers.filter((_, k) => !items[k])
          const found = items.filter((i): i is ShortlistItem => !!i)
          if (found.length < 2)
            return <Alert type="info" title="请在候选列表勾选 2–4 家公司后对比" description={<Link to="/targets">返回候选列表</Link>} />
          return (
            <>
              {missing.length > 0 && <Alert type="warning" title={`未找到：${missing.join('、')}`} style={{ marginBottom: 12 }} />}
              <Table
                rowKey="0"
                size="small"
                bordered
                pagination={false}
                scroll={{ x: 300 + found.length * 260 }}
                dataSource={ROWS}
                columns={[
                  { title: '', render: (_, r) => <b>{r[0]}</b>, width: 140, fixed: 'left' },
                  ...found.map((i) => ({
                    title: <Link to={`/targets/${i.ticker}`}>{i.name}（{i.ticker}）</Link>,
                    width: 260,
                    render: (_: unknown, r: (typeof ROWS)[number]) => r[1](i),
                  })),
                ]}
              />
            </>
          )
        }}
      </Loaded>
    </>
  )
}
