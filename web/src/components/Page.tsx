import type { ReactNode } from 'react'

// Page title block shared by every page: serif title, optional ticker, a meta line and a lead paragraph.
export function PageHead({ title, ticker, meta, lead }: { title: ReactNode; ticker?: string; meta?: ReactNode; lead?: ReactNode }) {
  return (
    <header className="page-head">
      <h1>
        {title}
        {ticker && <span className="ticker">{ticker}</span>}
      </h1>
      {meta && <div className="meta">{meta}</div>}
      {lead && <p className="lead">{lead}</p>}
    </header>
  )
}

// One 0–4 dimension score, shaded so a row of five reads as a strip.
export function Score({ value }: { value: number | null | undefined }) {
  if (value == null) return <span className="score score-none">—</span>
  return <span className={`score score-${Math.max(0, Math.min(4, Math.round(value)))}`}>{value}</span>
}
