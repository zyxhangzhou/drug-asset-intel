import type { ReactNode } from 'react'
import { Link } from 'react-router'

// Typesets long analyst text without changing it: one paragraph per sentence, English source quotes set
// apart from the analysis, source IDs turned into links, and key figures (%, p, n) in bold.

// Source ID shapes from the source registry; buyer-material IDs are one or two digits so drug codes
// such as ABBV-400 and words such as FDA-approved stay plain text.
const SOURCE_ID = [
  '(?:SEC|MAN|DOC|CTG|NASDAQ|PR|MNC|SPSIBI)-[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*',
  'FDA-(?:BLA|NDA|LAB)[A-Za-z0-9-]*',
  '(?:ABBV|AZ|BMY|GSK|JNJ|MRK|NVO|NVS|PFE|ROCHE)-\\d{1,2}(?![\\w-])',
].join('|')
const QUOTE = /"[^"\n]{2,}"|“[^”\n]{2,}”/g
const INLINE = new RegExp(
  [
    `(?<src>\\b(?:${SOURCE_ID}))`,
    '(?<path>\\bdata/[\\w./-]+)',
    '(?<num>[≥≤<>~]?\\s?-?\\d+(?:\\.\\d+)?\\s?%|\\b[pP]\\s?[<=≤]\\s?0?\\.\\d+|\\b[nN]\\s?=\\s?\\d+)',
  ].join('|'),
  'g',
)

function inline(text: string, key: string): ReactNode[] {
  const out: ReactNode[] = []
  let last = 0
  for (const m of text.matchAll(INLINE)) {
    const at = m.index!
    if (at > last) out.push(text.slice(last, at))
    const g = m.groups!
    if (g.src) out.push(<Link key={`${key}-${at}`} className="src-chip" to={`/sources/${g.src}`}>{g.src}</Link>)
    else if (g.path) out.push(<code key={`${key}-${at}`} className="mono">{g.path}</code>)
    else out.push(<span key={`${key}-${at}`} className="num">{m[0]}</span>)
    last = at + m[0].length
  }
  if (last < text.length) out.push(text.slice(last))
  return out
}

// Sentence breaks only outside quotes, so a quoted English passage never splits.
function paragraphs(text: string): string[] {
  const out: string[] = []
  let buf = ''
  let inQuote: string | null = null
  for (const ch of text) {
    buf += ch
    if (inQuote) {
      if (ch === inQuote) inQuote = null
    } else if (ch === '"') inQuote = '"'
    else if (ch === '“') inQuote = '”'
    else if (ch === '。' || ch === '\n') {
      if (buf.trim()) out.push(buf.trim())
      buf = ''
    }
  }
  if (buf.trim()) out.push(buf.trim())
  return out
}

function sentence(text: string, key: string): ReactNode[] {
  const out: ReactNode[] = []
  let last = 0
  for (const m of text.matchAll(QUOTE)) {
    const at = m.index!
    if (at > last) out.push(...inline(text.slice(last, at), `${key}-${last}`))
    out.push(<q key={`${key}-q${at}`}>{m[0].slice(1, -1)}</q>)
    last = at + m[0].length
  }
  if (last < text.length) out.push(...inline(text.slice(last), `${key}-${last}`))
  return out
}

export function RichText({ text, children }: { text: string | null | undefined; children?: ReactNode }) {
  if (!text) return <span className="sub">—{children}</span>
  const paras = paragraphs(text)
  return (
    <div className="rich">
      {paras.map((p, i) => (
        <p key={i}>
          {sentence(p, String(i))}
          {i === paras.length - 1 && children}
        </p>
      ))}
    </div>
  )
}
