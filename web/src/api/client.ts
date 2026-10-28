export interface SnapshotMeta {
  generated_at: string | null
  generator: string | null
  counts: Record<string, number>
}

async function getJson<T>(path: string): Promise<T> {
  const resp = await fetch(path)
  if (!resp.ok) throw new Error(`${path} → HTTP ${resp.status}`)
  return resp.json() as Promise<T>
}

export const fetchMeta = () => getJson<SnapshotMeta>('/api/meta')
