import { Button, Card, Input, InputNumber, Select, Switch, Table, Tag, Tooltip, Typography } from 'antd'
import { useMemo, useState } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router'
import { fetchShortlist, type ShortlistItem } from '../api/client'
import { useApi } from '../api/useApi'
import { Loaded } from '../components/Loaded'
import { PageHead, Score } from '../components/Page'
import { DIMENSIONS, label, money, RESEARCH_STATUS, shortAsset, STAGE, STAGE_ORDER, TA, taLabel } from '../labels'

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
      <div className="toolbar">
        <Input.Search placeholder="公司、代码或资产" allowClear defaultValue={get('q')} onSearch={(v) => set('q', v)} style={{ width: 220 }} />
        <Select placeholder="买方" allowClear value={get('buyer')} onChange={(v) => set('buyer', v)} style={{ width: 170 }}
          options={buyers.map(([t, n]) => ({ value: t, label: n }))} />
        <Select placeholder="治疗领域" allowClear value={get('ta')} onChange={(v) => set('ta', v)} style={{ width: 140 }}
          options={tas.map((t) => ({ value: t, label: TA[t] ?? t }))} />
        <Select placeholder="阶段" allowClear value={get('stage')} onChange={(v) => set('stage', v)} style={{ width: 100 }}
          options={stages.map((s) => ({ value: s, label: STAGE[s] }))} />
        <Select placeholder="研究状态" allowClear value={get('status')} onChange={(v) => set('status', v)} style={{ width: 120 }}
          options={Object.entries(RESEARCH_STATUS).map(([value, l]) => ({ value, label: l }))} />
        <label style={{ display: 'inline-flex', gap: 6, alignItems: 'center' }}>
          <Switch size="small" checked={!!get('shortlisted')} onChange={(on) => set('shortlisted', on ? '1' : undefined)} />
          只看入选
        </label>
        <span className="spacer" />
        <Button type="primary" disabled={selected.length < 2} onClick={() => navigate(`/compare?t=${selected.join(',')}`)}>
          对比所选（{selected.length}/{MAX_COMPARE}）
        </Button>
      </div>
      <details className="method">
        <summary>
          共 <b>{rows.length}</b> 家（全部 {items.length} 家）· 评分方法
        </summary>
        <p>
          每家公司按其主推荐方向（资产 × 适应症 × 买方）计分：五个维度各 0–4 分，加权为 0–100。保守分把缺失维度按 0 分计，乐观分按 4
          分计；两者差距越大，研究越不充分。勾选 2–4 家可对比。
        </p>
      </details>
      <Table
 className="table-panel"
        rowKey="ticker"
        size="small"
        dataSource={rows}
        pagination={{ pageSize: 50, showSizeChanger: false, hideOnSinglePage: true }}
        scroll={{ x: 1190 }}
        rowSelection={{
          selectedRowKeys: selected,
          onChange: (keys) => setSelected((keys as string[]).slice(0, MAX_COMPARE)),
          getCheckboxProps: (r) => ({ disabled: selected.length >= MAX_COMPARE && !selected.includes(r.ticker) }),
          hideSelectAll: true,
          columnWidth: 36,
        }}
        columns={[
          { title: '排名', dataIndex: 'rank', width: 66, align: 'right', sorter: (a, b) => a.rank - b.rank, render: (v) => <span className="figure">{v}</span> },
          {
            title: '公司',
            width: 210,
            sorter: (a, b) => a.name.localeCompare(b.name),
            render: (_, r) => (
              <div style={{ display: 'grid', gap: 2 }}>
                <Link to={`/targets/${r.ticker}`} style={{ fontWeight: 600 }}>{r.name}</Link>
                <span className="sub">
                  {r.ticker} · {label(RESEARCH_STATUS, r.research_status)}
                  {r.shortlisted && <Tag className="tag-pick" style={{ marginLeft: 6, marginRight: 0 }}>入选</Tag>}
                </span>
              </div>
            ),
          },
          {
            title: '主推荐方向：资产 · 适应症',
            width: 170,
            render: (_, r) => (
              <div style={{ display: 'grid', gap: 2, minWidth: 0 }}>
                <Typography.Text ellipsis={{ tooltip: r.asset }} style={{ fontWeight: 500 }}>{shortAsset(r.asset)}</Typography.Text>
                <Typography.Text ellipsis={{ tooltip: r.indication }} type="secondary" style={{ fontSize: 'var(--fs-small)' }}>
                  {r.indication ?? '—'} · {taLabel(r.therapeutic_area)}
                </Typography.Text>
              </div>
            ),
          },
          {
            title: <span style={{ whiteSpace: 'nowrap' }}>研发阶段</span>,
            width: 96,
            render: (_, r) => label(STAGE, r.stage),
            sorter: (a, b) => STAGE_ORDER.indexOf(a.stage ?? 'unknown') - STAGE_ORDER.indexOf(b.stage ?? 'unknown'),
          },
          { title: '买方', dataIndex: 'buyer', width: 104, ellipsis: true },
          ...DIMENSIONS.map((d) => ({
            title: <Tooltip title={d.label}><span style={{ whiteSpace: 'nowrap' }}>{d.short}</span></Tooltip>,
            width: 62,
            align: 'center' as const,
            render: (_: unknown, r: ShortlistItem) => <Score value={r.scores[d.key]} />,
            sorter: (a: ShortlistItem, b: ShortlistItem) => (a.scores[d.key] ?? -1) - (b.scores[d.key] ?? -1),
          })),
          {
            title: '保守 / 乐观',
            width: 100,
            align: 'right',
            sorter: (a, b) => a.conservative - b.conservative,
            defaultSortOrder: 'descend',
            render: (_, r) => (
              <>
                <span className="total">{r.conservative}</span>
                <span className="sub"> / {r.optimistic}</span>
              </>
            ),
          },
          { title: '覆盖率', width: 82, align: 'right', render: (_, r) => `${Math.round(r.coverage * 100)}%`, sorter: (a, b) => a.coverage - b.coverage },
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
      <PageHead
        title="候选公司"
        lead="每家公司一行，按主推荐方向的保守分排序。调整评分权重只在本页重排，不修改数据快照。"
      />
      <Card size="small" title="评分权重" style={{ marginTop: 0, marginBottom: 24 }}>
        <div className="toolbar" style={{ marginBottom: 0 }}>
          {DIMENSIONS.map((d, i) => (
            <label key={d.key} style={{ display: 'inline-flex', gap: 6, alignItems: 'center' }}>
              {d.label}
              <InputNumber min={0} max={100} size="small" value={draft[i]} style={{ width: 60 }}
                onChange={(v) => setDraft(draft.map((x, j) => (j === i ? (v ?? 0) : x)))} />
            </label>
          ))}
          <Button size="small" type="primary" onClick={() => setWeights(draft)}>应用</Button>
          <Button size="small" onClick={() => { setDraft(DEFAULT_WEIGHTS); setWeights(undefined) }}>恢复默认</Button>
          {state.data && (
            <span className="sub">
              当前：{DIMENSIONS.map((d) => `${d.short} ${Math.round(state.data!.weights[d.key] * 100)}%`).join(' · ')}
            </span>
          )}
        </div>
      </Card>
      <Loaded state={state}>{(s) => <List items={s.items} />}</Loaded>
    </>
  )
}
