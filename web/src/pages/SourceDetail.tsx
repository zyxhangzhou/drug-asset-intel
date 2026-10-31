import { Alert, Card, Descriptions, Spin, Typography } from 'antd'
import { useEffect, useRef } from 'react'
import { useParams, useSearchParams } from 'react-router'
import { fetchSource, fetchSourceText, type SourceDetail as Detail } from '../api/client'
import { useApi } from '../api/useApi'
import { Loaded } from '../components/Loaded'
import { PageHead } from '../components/Page'
import { label, SOURCE_TYPE } from '../labels'

const QUOTES: Record<string, string> = { '‘': "'", '’': "'", '“': '"', '”': '"', ' ': ' ' }

// Collapse whitespace and unify quote marks, keeping a map back to the original offsets.
function normalize(text: string): { norm: string; map: number[] } {
  let norm = ''
  const map: number[] = []
  for (let i = 0; i < text.length; i++) {
    const ch = QUOTES[text[i]] ?? text[i]
    if (/\s/.test(ch)) {
      if (norm.endsWith(' ') || norm === '') continue
      norm += ' '
    } else norm += ch
    map.push(i)
  }
  return { norm, map }
}

function locate(text: string, quote: string): [number, number] | null {
  const t = normalize(text)
  const q = normalize(quote).norm.trim()
  if (!q) return null
  const at = t.norm.indexOf(q)
  if (at < 0) return null
  return [t.map[at], t.map[at + q.length - 1] + 1]
}

function ArchivedText({ id, quote }: { id: string; quote: string | null }) {
  const state = useApi(() => fetchSourceText(id), [id])
  const mark = useRef<HTMLElement>(null)
  const span = state.data && quote ? locate(state.data, quote) : null
  const start = span?.[0]
  useEffect(() => mark.current?.scrollIntoView({ block: 'center' }), [start])
  if (state.error) return <Alert type="error" title="无法读取存档原文" description={state.error} />
  if (state.data == null) return <Spin />
  const text = state.data
  return (
    <>
      {quote && !span && <Alert type="warning" title="片段未在原文中定位" description={quote} style={{ marginBottom: 12 }} />}
      <pre className="archived">
        {span ? (
          <>
            {text.slice(0, span[0])}
            <mark ref={mark}>{text.slice(span[0], span[1])}</mark>
            {text.slice(span[1])}
          </>
        ) : text}
      </pre>
    </>
  )
}

function View({ d, quote }: { d: Detail; quote: string | null }) {
  return (
    <>
      <PageHead
        title={d.title ?? d.source_id}
        meta={
          <>
            <b className="mono" style={{ color: 'var(--ink)' }}>{d.source_id}</b>
            <span>{label(SOURCE_TYPE, d.source_type)}{d.doc_kind ? ` · ${d.doc_kind}` : ''}</span>
            {d.publisher && <span>{d.publisher}</span>}
          </>
        }
      />
      <Descriptions column={{ xs: 1, md: 2 }} size="small" bordered>
        <Descriptions.Item label="来源 ID">{d.source_id}</Descriptions.Item>
        <Descriptions.Item label="类型">{label(SOURCE_TYPE, d.source_type)}{d.doc_kind ? ` · ${d.doc_kind}` : ''}</Descriptions.Item>
        <Descriptions.Item label="发布者">{d.publisher ?? '—'}</Descriptions.Item>
        <Descriptions.Item label="发布日期">{d.published_date ?? d.published_date_text ?? '—'}</Descriptions.Item>
        <Descriptions.Item label="抓取时间">{new Date(d.fetched_at).toLocaleString('zh-CN')}</Descriptions.Item>
        <Descriptions.Item label="引用该来源的声明">{d.claims}</Descriptions.Item>
        <Descriptions.Item label="原网址" span={2}>
          {d.url ? <a href={d.url} target="_blank" rel="noreferrer">{d.url}</a> : '—'}
        </Descriptions.Item>
        <Descriptions.Item label="文本指纹（SHA-256）" span={2}>
          <Typography.Text code style={{ wordBreak: 'break-all' }}>{d.content_hash ?? '—'}</Typography.Text>
        </Descriptions.Item>
        {d.note && <Descriptions.Item label="说明" span={2}>{d.note}</Descriptions.Item>}
      </Descriptions>
      <Card size="small" title={quote ? '存档原文（已标出引用片段）' : '存档原文'}>
        {d.has_text ? (
          <ArchivedText id={d.source_id} quote={quote} />
        ) : (
          <Typography.Text type="secondary">
            没有存档原文。{quote ? `声明引用的片段：“${quote}”。` : ''}请通过原网址查看。
          </Typography.Text>
        )}
      </Card>
    </>
  )
}

export default function SourceDetail() {
  const { id = '' } = useParams()
  const [params] = useSearchParams()
  const state = useApi(() => fetchSource(id), [id])
  return <Loaded state={state}>{(d) => <View d={d} quote={params.get('q')} />}</Loaded>
}
