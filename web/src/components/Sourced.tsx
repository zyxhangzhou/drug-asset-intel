import { Popover, Space, Tag, Typography } from 'antd'
import type { ReactNode } from 'react'
import { Link } from 'react-router'
import type { Claim, Sources } from '../api/client'
import { RichText } from './RichText'
import { CONFIDENCE, KIND, label, PRODUCED_BY, SOURCE_TYPE } from '../labels'

// Marker colours: fact from an official interface or manual record, inference, LLM extraction.
const COLOR = { fact: 'var(--fact)', inference: 'var(--inference)', llm: 'var(--llm)' }

function claimColor(c: Claim) {
  if (c.produced_by === 'llm') return COLOR.llm
  return c.kind === 'inference' ? COLOR.inference : COLOR.fact
}

// Inference dots are drawn as rings so filled fact and LLM dots stand out where markers are dense.
function Dot({ color }: { color: string }) {
  return <span className={color === COLOR.inference ? 'dot ring' : 'dot'} style={{ background: color }} />
}

function sourceLink(c: Claim) {
  const q = c.quote ? `?q=${encodeURIComponent(c.quote)}` : ''
  return `/sources/${encodeURIComponent(c.source.source_id)}${q}`
}

function ClaimCard({ c }: { c: Claim }) {
  const s = c.source
  const date = s.published_date ?? s.published_date_text
  return (
    <div className="claim">
      <Space size={4} wrap>
        <Dot color={claimColor(c)} />
        <Tag color={c.kind === 'fact' ? 'green' : 'orange'}>{label(KIND, c.kind)}</Tag>
        {c.confidence && <Tag>置信度 {label(CONFIDENCE, c.confidence)}</Tag>}
        <Tag color={c.produced_by === 'llm' ? 'purple' : undefined}>
          {label(PRODUCED_BY, c.produced_by)}
          {c.model ? ` · ${c.model}` : ''}
        </Tag>
        {c.as_of && <Tag>截至 {c.as_of}</Tag>}
      </Space>
      {c.value && (
        <Typography.Paragraph style={{ margin: 0 }} ellipsis={{ rows: 3, expandable: true }}>
          取值：{c.value}
        </Typography.Paragraph>
      )}
      {c.quote && (
        <Typography.Paragraph className="claim-quote" ellipsis={{ rows: 4, expandable: true }}>
          “{c.quote}”
        </Typography.Paragraph>
      )}
      {c.note && <Typography.Paragraph type="secondary" style={{ margin: 0 }}>说明：{c.note}</Typography.Paragraph>}
      <div className="claim-src">
        <Link to={sourceLink(c)}>{s.source_id}</Link>
        {' · '}
        {label(SOURCE_TYPE, s.source_type)}
        {s.title ? ` · ${s.title}` : ''}
        {date ? ` · ${date}` : ''}
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
    <div style={{ display: 'grid', gap: 12, maxWidth: 520, maxHeight: 420, overflowY: 'auto', paddingRight: 4 }}>
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
      <span role="button" tabIndex={0} aria-label="查看来源" className="marker">
        {colors.map((color) => (
          <Dot key={color} color={color} />
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
    <span>
      <Dot color={color} />
      {text}
    </span>
  )
  return (
    <div className="legend">
      <span>来源标记</span>
      {item(COLOR.fact, '事实')}
      {item(COLOR.inference, '推断')}
      {item(COLOR.llm, 'LLM 抽取（附原文片段）')}
      <span>点击标记查看来源</span>
    </div>
  )
}

// Long analyst text, typeset by RichText, with the provenance marker after its last sentence.
export function SourcedText({ sources, field, text }: { sources: Sources; field: string | string[]; text: string | null | undefined }) {
  const fields = Array.isArray(field) ? field : [field]
  const claims = fields.flatMap((f) => sources[f] ?? [])
  return <RichText text={text}>{claims.length > 0 && <Marker claims={claims} />}</RichText>
}
