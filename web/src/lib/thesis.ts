// Splits a 推荐逻辑 written to the template in docs/scoring-rules.md §7 into its labelled parts:
//   〈买方〉需要〈需求〉；〈公司〉的〈资产〉…对应这一需求，因为〈理由〉。
//   证据是〈…〉；下一事件是〈…〉；主要障碍是〈…〉。
// Every part is an exact substring of the original; when the text does not follow the template the
// caller shows it unsplit, so nothing is ever dropped or reworded.

export interface ThesisParts {
  need: string
  asset: string
  reason: string
  evidence: string
  next: string | null
  obstacle: string | null
}

const OPEN = '（(「“"'
const CLOSE = '）)」”"'

// Index of the first `ch` outside brackets and quotes at or after `from`, or -1.
function topLevel(text: string, ch: string, from = 0): number {
  let depth = 0
  let inAscii = false
  for (let i = from; i < text.length; i++) {
    const c = text[i]
    if (c === '"') inAscii = !inAscii
    else if (!inAscii && OPEN.includes(c)) depth++
    else if (!inAscii && CLOSE.includes(c)) depth = Math.max(0, depth - 1)
    else if (depth === 0 && !inAscii && text.startsWith(ch, i)) return i
  }
  return -1
}

export function parseThesis(text: string): ThesisParts | null {
  const at = text.indexOf('对应这一需求')
  if (at < 0) return null
  const head = text.slice(0, at)
  const semi = topLevel(head, '；')
  if (semi < 0) return null
  // Usually 「对应这一需求，因为…」; a qualified match such as 「对应这一需求中的「泌尿」肿瘤，因为…」 keeps its qualifier.
  const because = topLevel(text, '因为', at)
  if (because < 0) return null
  const plain = text.slice(at, because) === '对应这一需求，'
  const reasonFrom = plain ? because + 2 : at
  const end = topLevel(text, '。', because)
  if (end < 0) return null
  const rest = text.slice(end + 1)
  const nextAt = topLevel(rest, '；下一事件是')
  const obstacleAt = topLevel(rest, '；主要障碍是')
  const evidenceEnd = nextAt >= 0 ? nextAt : obstacleAt >= 0 ? obstacleAt : rest.length
  const parts: ThesisParts = {
    need: head.slice(0, semi),
    asset: head.slice(semi + 1),
    reason: text.slice(reasonFrom, end + 1),
    evidence: rest.slice(0, evidenceEnd).replace(/^证据是/, ''),
    next: nextAt >= 0 ? rest.slice(nextAt + '；下一事件是'.length, obstacleAt > nextAt ? obstacleAt : undefined) : null,
    obstacle: obstacleAt >= 0 ? rest.slice(obstacleAt + '；主要障碍是'.length) : null,
  }
  return parts.evidence.trim() ? parts : null
}

// 「成本：…」 → ['成本', '…'] so the obstacle's category can be shown as a tag.
export function splitCategory(text: string): [string | null, string] {
  const m = /^([^：:，。；]{1,8})[：:]/.exec(text)
  return m ? [m[1], text.slice(m[0].length)] : [null, text]
}
