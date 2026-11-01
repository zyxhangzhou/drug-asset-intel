import type { ColumnType } from 'antd/es/table'

// On phones, tables with className "stack" render each row as a card (see index.css).
// Each cell gets its column title as a data-label, shown before the value.
// Column classNames refine the card: "stack-head" (unlabelled, shares the first line),
// "stack-inline" (compact chip on a shared line) and "stack-hide" (dropped on phones).
type Col<T> = ColumnType<T> & { stackLabel?: string }

export function stack<T>(columns: Col<T>[]): ColumnType<T>[] {
  return columns.map(({ stackLabel, ...col }) => {
    const text = stackLabel ?? (typeof col.title === 'string' ? col.title : undefined)
    if (!text) return col
    const onCell = col.onCell
    return {
      ...col,
      onCell: (record: T, index?: number) => ({ ...onCell?.(record, index), 'data-label': text }) as ReturnType<NonNullable<ColumnType<T>['onCell']>>,
    }
  })
}
