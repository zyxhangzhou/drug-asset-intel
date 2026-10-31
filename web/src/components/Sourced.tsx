import { Popover, Space, Tag, Typography } from 'antd'
import type { ReactNode } from 'react'
import { Link } from 'react-router'
import type { Claim, Sources } from '../api/client'
import { CONFIDENCE, KIND, label, PRODUCED_BY, SOURCE_TYPE } from '../labels'

// Marker colours: fact from an official interface or manual record, inference, LLM extraction.
const COLOR = { fact: '#389e0d', inference: '#d48806', llm: '#722ed1' }

function claimColor(c: Claim) {
  if (c.produced_by === 'llm') return COLOR.llm
  return c.kind === 'inference' ? COLOR.inference : COLOR.fact
}

function sourceLink(c: Claim) {
  const q = c.quote ? `?q=${encodeURIComponent(c.quote)}` : ''
  return `/sources/${encodeURIComponent(c.source.source_id)}${q}`
}

function ClaimCard({ c }: { c: Claim }) {
  const s = c.source
  return (
    <div style={{ borderLeft: `3px solid ${claimColor(c)}`, paddingLeft: 8 }}>
      <Space size={4} wrap>
        <Tag color={c.kind === 'fact' ? 'green' : 'orange'}>{label(KIND, c.kind)}</Tag>
        {c.confidence && <Tag>置信度 {label(CONFIDENCE, c.confidence)}</Tag>}
        <Tag color={c.produced_by === 'llm' ? 'purple' : undefined}>
          {label(PRODUCED_BY, c.produced_by)}
          {c.model ? ` · ${c.model}` : ''}
        </Tag>
        {c.as_of && <Tag>截至 {c.as_of}</Tag>}
      </Space>
      {c.value && (
        <Typography.Paragraph style={{ margin: '4px 0' }} ellipsis={{ rows: 3, expandable: true }}>
          取值：{c.value}
        </Typography.Paragraph>
      )}
      {c.quote && (
        <Typography.Paragraph type="secondary" style={{ margin: '4px 0' }} ellipsis={{ rows: 4, expandable: true }}>
          原文：“{c.quote}”
        </Typography.Paragraph>
      )}
      {c.note && <Typography.Paragraph type="secondary" style={{ margin: '4px 0' }}>说明：{c.note}</Typography.Paragraph>}
      <div style={{ fontSize: 12 }}>
        <Link to={sourceLink(c)}>{s.source_id}</Link>
        {' · '}
        {label(SOURCE_TYPE, s.source_type)}
        {s.title ? ` · ${s.title}` : ''}
        {(s.published_date ?? s.published_date_text) ? ` · ${s.published_date ?? s.published_date_text}` : ''}
        {s.url && (
          <>
            {' · '}
            <a href={s.url} target="_blank" rel="noreferrer">
              原网址
            </a>
          </>
        )}
      </div>
    </div>
  )
}

export function ClaimList({ claims }: { claims: Claim[] }) {
  return (
    <div style={{ display: 'grid', gap: 12, maxWidth: 520, maxHeight: 420, overflowY: 'auto' }}>
      {claims.map((c, i) => (
        <ClaimCard key={i} c={c} />
      ))}
    </div>
  )
}

function Marker({ claims }: { claims: Claim[] }) {
  // One dot per distinct kind of support, so a value backed by fact and inference shows both.
  const colors = [...new Set(claims.map(claimColor))]
  return (
    <Popover content={<ClaimList claims={claims} />} title={`来源声明（${claims.length}）`} trigger="click">
      <span
        role="button"
        tabIndex={0}
        aria-label="查看来源"
        style={{ cursor: 'pointer', marginLeft: 4, whiteSpace: 'nowrap', verticalAlign: 'super', fontSize: 10 }}
      >
        {colors.map((color) => (
          <span key={color} style={{ display: 'inline-block', width: 7, height: 7, borderRadius: 4, background: color, marginRight: 1 }} />
        ))}
      </span>
    </Popover>
  )
}

// A value with its provenance marker; fields without claims render the value alone.
export function Sourced({ sources, field, children }: { sources: Sources; field: string | string[]; children?: ReactNode }) {
  const fields = Array.isArray(field) ? field : [field]
  const claims = fields.flatMap((f) => sources[f] ?? [])
  return (
    <>
      {children}
      {claims.length > 0 && <Marker claims={claims} />}
    </>
  )
}

export function Legend() {
  const item = (color: string, text: string) => (
    <span style={{ marginRight: 12, whiteSpace: 'nowrap' }}>
      <span style={{ display: 'inline-block', width: 8, height: 8, borderRadius: 4, background: color, marginRight: 4 }} />
      {text}
    </span>
  )
  return (
    <Typography.Text type="secondary" style={{ fontSize: 12 }}>
      来源标记：{item(COLOR.fact, '事实')}
      {item(COLOR.inference, '推断')}
      {item(COLOR.llm, 'LLM 抽取（附原文片段）')}点击标记查看来源
    </Typography.Text>
  )
}
