import { Button } from 'antd'
import { type ReactNode, useState } from 'react'
import type { Sources } from '../api/client'
import { parseThesis, splitCategory } from '../lib/thesis'
import { RichText } from './RichText'
import { Sourced } from './Sourced'

// Bold the lead phrase (before `sep`) of an exact substring, keeping the rest as typeset text.
function Lead({ text, sep }: { text: string; sep: string }) {
  const at = text.indexOf(sep)
  if (at <= 0) return <RichText text={text} />
  return (
    <div className="rich">
      <p>
        <b>{text.slice(0, at)}</b>
        {text.slice(at)}
      </p>
    </div>
  )
}

function Row({ tag, tone, children }: { tag: string; tone: string; children: ReactNode }) {
  return (
    <div className="brief-row">
      <span className={`brief-tag tone-${tone}`}>{tag}</span>
      <div style={{ minWidth: 0 }}>{children}</div>
    </div>
  )
}

// 推荐逻辑 split into its template parts (need → asset → reason; evidence, next event, obstacle).
// Text that does not follow the template is shown whole.
export function Thesis({ text, sources }: { text: string; sources: Sources }) {
  const [whole, setWhole] = useState(false)
  const parts = parseThesis(text)
  const head = (
    <div className="brief-head">
      <Sourced sources={sources} field="thesis">
        <b style={{ fontSize: 15 }}>推荐逻辑</b>
      </Sourced>
      <span className="sub">买方需求与资产的对应；证据、下一事件与主要障碍</span>
      {parts && (
        <Button type="link" size="small" onClick={() => setWhole(!whole)} style={{ marginLeft: 'auto', paddingInline: 0 }}>
          {whole ? '分项显示' : '显示原文整段'}
        </Button>
      )}
    </div>
  )
  if (!parts || whole)
    return (
      <div className="brief">
        {head}
        <p className="thesis">{text}</p>
      </div>
    )
  const [category, obstacle] = parts.obstacle ? splitCategory(parts.obstacle) : [null, '']
  return (
    <div className="brief">
      {head}
      <div className="brief-group">
        <div className="brief-title">为什么匹配</div>
        <Row tag="买方需求" tone="buyer"><Lead text={parts.need} sep="需要" /></Row>
        <Row tag="对应资产" tone="asset"><Lead text={parts.asset} sep="（" /></Row>
        <Row tag="匹配理由" tone="reason"><RichText text={parts.reason} /></Row>
      </div>
      <div className="brief-group">
        <div className="brief-title">证据与风险</div>
        <Row tag="关键证据" tone="evidence"><RichText text={parts.evidence} /></Row>
        {parts.next && <Row tag="下一事件" tone="next"><RichText text={parts.next} /></Row>}
        {parts.obstacle && (
          <Row tag="主要障碍" tone="risk">
            {category ? (
              <div className="rich">
                <p>
                  <span className="risk-cat">{category}</span>
                  {obstacle}
                </p>
              </div>
            ) : (
              <RichText text={parts.obstacle} />
            )}
          </Row>
        )}
      </div>
    </div>
  )
}
