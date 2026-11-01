import { Card } from 'antd'
import { Link } from 'react-router'
import { fetchMeta, fetchShortlist, type ShortlistItem } from '../api/client'
import { useApi } from '../api/useApi'
import { Loaded } from '../components/Loaded'
import { PageHead, Score } from '../components/Page'
import { DIMENSIONS, shortAsset } from '../labels'
import { Legend } from '../components/Sourced'

const ENTITY_LABELS: Record<string, string> = {
  buyer: '买方药企',
  buyer_preference: '买方偏好',
  buyer_financial: '买方财务',
  buyer_product_loe: '买方专利到期产品',
  target: '标的公司',
  program: '管线',
  program_indication: '管线适应症',
  trial: '临床试验',
  trial_result: '试验结果',
  catalyst: '催化事件',
  financial_snapshot: '财务快照',
  approved_product: '获批产品',
  match: '买方×标的匹配',
  recommendation: '推荐方向（资产×适应症×买方）',
}

const ROUTE: [string, string, string][] = [
  ['/buyers', '买方画像', '10 家大型药企的治疗领域、技术与交易偏好，以及专利到期压力。'],
  ['/targets', '候选公司', '按买方、治疗领域、阶段筛选；可调评分权重，勾选 2–4 家对比。'],
  ['/targets/VKTX', '公司详情', '复核结论、管线、财务快照、催化事件与全部试验。'],
  ['/trials/NCT06068946', '试验与结果', '试验方案、入组与完成时间，已发布或已抽取的结果。'],
  ['/sources/MAN-RGNX-1', '来源原文', '存档原文中标出声明引用的片段。'],
]

const TOP = 8

function Funnel({ total, items }: { total: number; items: ShortlistItem[] }) {
  const reviewed = items.filter((i) => i.research_status !== 'auto').length
  const picked = items.filter((i) => i.shortlisted).length
  const steps: [number, string, string][] = [
    [total, '标普生物科技指数成分公司', '对方提供的成分股清单'],
    [items.length, '进入打分', `排除 ${total - items.length} 家：已被收购、本身是大型药企、工具或诊断公司`],
    [reviewed, '人工复核', '按乐观分初筛后逐家复核推荐方向、权益与证据'],
    [picked, '入选', '按保守分排序，须已复核、权益已核实、推荐逻辑有来源'],
  ]
  return (
    <ol className="funnel">
      {steps.map(([n, title, text], i) => (
        <li key={title} className={i === steps.length - 1 ? 'last' : undefined}>
          <span className="funnel-n">{n}</span>
          <b>{title}</b>
          <span className="sub">{text}</span>
        </li>
      ))}
    </ol>
  )
}

function TopList({ items }: { items: ShortlistItem[] }) {
  const picked = items.filter((i) => i.shortlisted).sort((a, b) => b.conservative - a.conservative)
  return (
    <Card title={`入选名单 · 前 ${TOP} 家`} extra={<Link to="/targets?shortlisted=1">查看全部 {picked.length} 家 →</Link>} style={{ marginTop: 0 }}>
      <ol className="toplist">
        {picked.slice(0, TOP).map((i, k) => (
          <li key={i.ticker}>
            <span className="toplist-k">{k + 1}</span>
            <div style={{ minWidth: 0 }}>
              <Link to={`/targets/${i.ticker}`} style={{ fontWeight: 600 }}>{i.name}</Link>
              <div className="sub" style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                {shortAsset(i.asset)} × {i.indication ?? '—'} × {i.buyer ?? '—'}
              </div>
            </div>
            <div className="strip-inline" aria-label="五维分数">
              {DIMENSIONS.map((d) => (
                <span key={d.key} title={d.label}><Score value={i.scores[d.key]} /></span>
              ))}
            </div>
            <span className="total">{i.conservative}</span>
            <span className="sub toplist-when" title="下一事件时间">{i.event_timing ?? '—'}</span>
          </li>
        ))}
      </ol>
    </Card>
  )
}

// Single series: shortlisted companies whose primary direction names each buyer.
function ByBuyer({ items }: { items: ShortlistItem[] }) {
  const counts = new Map<string, { name: string; n: number }>()
  // Every buyer named by any primary direction gets a row, so a buyer with none shows 0 rather than vanishing.
  for (const i of items) {
    if (!i.buyer_ticker) continue
    const c = counts.get(i.buyer_ticker) ?? { name: i.buyer ?? i.buyer_ticker, n: 0 }
    if (i.shortlisted) c.n++
    counts.set(i.buyer_ticker, c)
  }
  const rows = [...counts.entries()].sort((a, b) => b[1].n - a[1].n)
  const max = Math.max(1, ...rows.map(([, c]) => c.n))
  return (
    <Card title="入选公司按买方" style={{ marginTop: 0 }}>
      <p className="note">主推荐方向指向该买方的入选公司数。点击查看名单。</p>
      <div className="bars">
        {rows.map(([t, c]) => (
          <Link key={t} to={`/targets?buyer=${t}&shortlisted=1`} className="bar-row" title={`${c.name}：${c.n} 家`}>
            <span className="bar-label">{c.name}</span>
            <span className="bar-track">
              {c.n > 0 && <span className="bar" style={{ width: `${(c.n / max) * 100}%` }} />}
            </span>
            <span className="bar-n">{c.n}</span>
          </Link>
        ))}
      </div>
    </Card>
  )
}

export default function Overview() {
  const meta = useApi(fetchMeta, [])
  const list = useApi(() => fetchShortlist(), [])
  return (
    <Loaded state={meta}>
      {(m) => (
        <>
          <PageHead
            title="候选资产概览"
            meta={
              <>
                <span>快照日（股价） {m.snapshot_date ?? '未知'}</span>
                <span>快照生成于 {m.generated_at ? new Date(m.generated_at).toLocaleString('zh-CN') : '未知'}</span>
              </>
            }
            lead="把 10 家大型药企的资产偏好与标普生物科技指数成分公司的管线对上，筛出有收购或授权潜力的公司。每个带来源的值旁有来源标记，点开可追到一手来源。"
          />
          <Loaded state={list}>
            {(s) => (
              <>
                <Funnel total={m.counts.target ?? 0} items={s.items} />
                <div className="ov-grid">
                  <TopList items={s.items} />
                  <ByBuyer items={s.items} />
                </div>
              </>
            )}
          </Loaded>
          <Card title="演示主线">
            <ol className="route">
              {ROUTE.map(([to, title, text]) => (
                <li key={to}>
                  <b><Link to={to}>{title}</Link></b>
                  <span>{text}</span>
                </li>
              ))}
            </ol>
          </Card>
          <Card title="快照内容">
            <details className="method">
              <summary>各类记录的条数</summary>
              <div className="ledger" style={{ marginTop: 8 }}>
                {Object.entries(m.counts).map(([entity, count]) => (
                  <div key={entity}>
                    <span>{ENTITY_LABELS[entity] ?? entity}</span>
                    <span className="figure">{count.toLocaleString('en-US')}</span>
                  </div>
                ))}
              </div>
            </details>
            <div style={{ marginTop: 12 }}><Legend /></div>
          </Card>
        </>
      )}
    </Loaded>
  )
}
