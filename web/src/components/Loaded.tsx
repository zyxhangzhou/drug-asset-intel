import { Alert, Spin } from 'antd'
import type { ReactNode } from 'react'
import type { ApiState } from '../api/useApi'

export function Loaded<T>({ state, children }: { state: ApiState<T>; children: (data: T) => ReactNode }) {
  if (state.error) return <Alert type="error" title="无法读取数据" description={state.error} showIcon />
  if (!state.data) return <Spin style={{ display: 'block', margin: 48 }} />
  return <>{children(state.data)}</>
}
