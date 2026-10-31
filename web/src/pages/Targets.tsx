import { Button, Card, Input, InputNumber, Select, Space, Switch, Table, Tag, Typography } from 'antd'
import { useMemo, useState } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router'
import { fetchShortlist, type ShortlistItem } from '../api/client'
import { useApi } from '../api/useApi'
import { Loaded } from '../components/Loaded'
import { DIMENSIONS, label, money, RESEARCH_STATUS, STAGE, STAGE_ORDER, TA, taLabel } from '../labels'

const DEFAULT_WEIGHTS = [30, 20, 20, 15, 15]
const MAX_COMPARE = 4

// Filters live in the URL so a filtered list can be linked; weights are a what-if and stay local.
function useFilters() {
  const [params, setParams] = useSearchParams()
  const get = (k: string) => params.get(k) ?? undefined
  const set = (k: string, v: string | undefined) => {
    const next = new URLSearchParams(params)
    if (v) next.set(k, v)
    else next.delete(k)
    setParams(next, { replace: true })
  }
  return { get, set }
}

function applyFilters(items: ShortlistItem[], get: (k: string) => string | undefined) {
  const q = get('q')?.toLowerCase()
  return items.filter(
    (i) =>
      (!get('buyer') || i.buyer_ticker === get('buyer')) &&
      (!get('ta') || (i.therapeutic_area ?? '').split(';').includes(get('ta')!)) &&
      (!get('stage') || i.stage === get('stage')) &&
      (!get('status') || i.research_status === get('status')) &&
      (!get('shortlisted') || i.shortlisted) &&
      (!q || i.ticker.toLowerCase().includes(q) || i.name.toLowerCase().includes(q) || (i.asset ?? '').toLowerCase().includes(q)),
  )
}

function List({ items }: { items: ShortlistItem[] }) {
  const { get, set } = useFilters()
  const navigate = useNavigate()
  const [selected, setSelected] = useState<string[]>([])
  const rows = applyFilters(items, get)
  const buyers = useMemo(
    () => [...new Map(items.filter((i) => i.buyer_ticker).map((i) => [i.buyer_ticker!, i.buyer!])).entries()].sort((a, b) => a[1].localeCompare(b[1])),
    [items],
  )
  const tas = useMemo(
    () => [...new Set(items.flatMap((i) => (i.therapeutic_area ? i.therapeutic_area.split(';') : [])))].sort(),
    [items],
  )
  const stages = STAGE_ORDER.filter((s) => items.some((i) => i.stage === s))

  return (
    <>
      <Space wrap style={{ marginBottom: 12 }}>
        <Input.Search placeholder="公司、代码或资产" allowClear defaultValue={get('q')} onSearch={(v) => set('q', v)} style={{ width: 220 }} />
        <Select placeholder="买方" allowClear value={get('buyer')} onChange={(v) => set('buyer', v)} style={{ width: 180 }}
          options={buyers.map(([t, n]) => ({ value: t, label: n }))} />
        <Select placeholder="治疗领域" allowClear value={get('ta')} onChange={(v) => set('ta', v)} style={{ width: 150 }}
          options={tas.map((t) => ({ value: t, label: TA[t] ?? t }))} />
        <Select placeholder="阶段" allowClear value={get('stage')} onChange={(v) => set('stage', v)} style={{ width: 110 }}
          options={stages.map((s) => ({ value: s, label: STAGE[s] }))} />
        <Select placeholder="研究状态" allowClear value={get('status')} onChange={(v) => set('status', v)} style={{ width: 120 }}
          options={Object.entries(RESEARCH_STATUS).map(([value, l]) => ({ value, label: l }))} />
        <span>
          只看入选 <Switch size="small" checked={!!get('shortlisted')} onChange={(on) => set('shortlisted', on ? '1' : undefined)} />
        </span>
        <Button type="primary" disabled={selected.length < 2} onClick={() => navigate(`/compare?t=${selected.join(',')}`)}>
          对比所选（{selected.length}/{MAX_COMPARE}）
        </Button>
      </Space>
      <Typography.Paragraph type="secondary" style={{ fontSize: 12 }}>
        共 {rows.length} 家（全部 {items.length} 家）。每家公司按其主组合（资产 × 适应症 × 买方）计分；分数 0–4，总分 0–100。
      </Typography.Paragraph>
      <Table
        rowKey="ticker"
        size="small"
        dataSource={rows}
        pagination={{ pageSize: 50, showSizeChanger: false }}
        scroll={{ x: 1300 }}
        rowSelection={{
          selectedRowKeys: selected,
          onChange: (keys) => setSelected((keys as string[]).slice(0, MAX_COMPARE)),
          getCheckboxProps: (r) => ({ disabled: selected.length >= MAX_COMPARE && !selected.includes(r.ticker) }),
          hideSelectAll: true,
        }}
        columns={[
          { title: '排名', dataIndex: 'rank', width: 60, sorter: (a, b) => a.rank - b.rank },
          {
            title: '公司',
            width: 200,
            fixed: 'left',
            sorter: (a, b) => a.name.localeCompare(b.name),
            render: (_, r) => (
              <>
                <Link to={`/targets/${r.ticker}`}>{r.name}</Link> <Typography.Text type="secondary">{r.ticker}</Typography.Text>
                {r.shortlisted && <Tag color="gold" style={{ marginLeft: 4 }}>入选</Tag>}
              </>
            ),
          },
          { title: '资产', dataIndex: 'asset', width: 150, ellipsis: true },
          { title: '适应症', dataIndex: 'indication', width: 180, ellipsis: true },
          { title: '领域', render: (_, r) => taLabel(r.therapeutic_area), width: 100 },
          {
            title: '阶段',
            width: 70,
            render: (_, r) => label(STAGE, r.stage),
            sorter: (a, b) => STAGE_ORDER.indexOf(a.stage ?? 'unknown') - STAGE_ORDER.indexOf(b.stage ?? 'unknown'),
          },
          { title: '买方', dataIndex: 'buyer', width: 130 },
          ...DIMENSIONS.map((d) => ({
            title: d.short,
            width: 56,
            align: 'right' as const,
            render: (_: unknown, r: ShortlistItem) => r.scores[d.key] ?? <Typography.Text type="secondary">—</Typography.Text>,
            sorter: (a: ShortlistItem, b: ShortlistItem) => (a.scores[d.key] ?? -1) - (b.scores[d.key] ?? -1),
          })),
          { title: '保守分', dataIndex: 'conservative', width: 72, align: 'right', sorter: (a, b) => a.conservative - b.conservative, defaultSortOrder: 'descend' },
          { title: '乐观分', dataIndex: 'optimistic', width: 72, align: 'right', sorter: (a, b) => a.optimistic - b.optimistic },
          { title: '覆盖率', width: 70, align: 'right', render: (_, r) => `${Math.round(r.coverage * 100)}%`, sorter: (a, b) => a.coverage - b.coverage },
          { title: '研究状态', width: 84, render: (_, r) => label(RESEARCH_STATUS, r.research_status) },
          { title: '企业价值', width: 90, align: 'right', render: (_, r) => money(r.enterprise_value), sorter: (a, b) => (a.enterprise_value ?? 0) - (b.enterprise_value ?? 0) },
        ]}
      />
    </>
  )
}

export default function Targets() {
  const [draft, setDraft] = useState(DEFAULT_WEIGHTS)
  const [weights, setWeights] = useState<number[] | undefined>()
  const state = useApi(() => fetchShortlist(weights), [weights?.join(',')])
  return (
    <>
      <Typography.Title level={3}>候选公司</Typography.Title>
      <Card size="small" title="评分权重（调整后按新权重重排，不修改快照）" style={{ marginBottom: 16 }}>
        <Space wrap>
          {DIMENSIONS.map((d, i) => (
            <span key={d.key}>
              {d.label}{' '}
              <InputNumber min={0} max={100} size="small" value={draft[i]} style={{ width: 64 }}
                onChange={(v) => setDraft(draft.map((x, j) => (j === i ? (v ?? 0) : x)))} />
            </span>
          ))}
          <Button size="small" type="primary" onClick={() => setWeights(draft)}>应用</Button>
          <Button size="small" onClick={() => { setDraft(DEFAULT_WEIGHTS); setWeights(undefined) }}>恢复默认</Button>
          {state.data && (
            <Typography.Text type="secondary" style={{ fontSize: 12 }}>
              当前：{DIMENSIONS.map((d) => `${d.short} ${Math.round(state.data!.weights[d.key] * 100)}%`).join(' · ')}
            </Typography.Text>
          )}
        </Space>
      </Card>
      <Loaded state={state}>{(s) => <List items={s.items} />}</Loaded>
    </>
  )
}
