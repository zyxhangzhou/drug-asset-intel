// Callers pass the deps of `load`, as with useEffect itself; the rule cannot see through that.
/* oxlint-disable react-hooks/exhaustive-deps */
import { type DependencyList, useEffect, useState } from 'react'

export interface ApiState<T> {
  data: T | null
  error: string | null
}

// Fetch on mount and whenever deps change; a stale response never overwrites a newer one.
export function useApi<T>(load: () => Promise<T>, deps: DependencyList): ApiState<T> {
  const [state, setState] = useState<ApiState<T>>({ data: null, error: null })
  useEffect(() => {
    let live = true
    setState({ data: null, error: null })
    load()
      .then((data) => live && setState({ data, error: null }))
      .catch((e: Error) => live && setState({ data: null, error: e.message }))
    return () => {
      live = false
    }
  }, deps)
  return state
}
