import { Alert, Card, ConfigProvider, Descriptions, Layout, Spin, Statistic, Typography } from 'antd'
import zhCN from 'antd/locale/zh_CN'
import { useEffect, useState } from 'react'
import { fetchMeta, type SnapshotMeta } from './api/client'

const ENTITY_LABELS: Record<string, string> = {
  buyer: '买方药企',
  buyer_preference: '买方偏好',
  target: '标的公司',
  program: '管线',
  program_indication: '管线适应症',
  trial: '临床试验',
  trial_result: '试验结果',
  catalyst: '催化事件',
  financial_snapshot: '财务快照',
  match: '买方×标的匹配',
}

function SnapshotOverview({ meta }: { meta: SnapshotMeta }) {
  const generated = meta.generated_at ? new Date(meta.generated_at).toLocaleString('zh-CN') : '未知'
  return (
    <>
      <Descriptions size="small" column={1} style={{ marginBottom: 24 }}>
        <Descriptions.Item label="数据快照时间">{generated}</Descriptions.Item>
        <Descriptions.Item label="生成程序">{meta.generator ?? '未知'}</Descriptions.Item>
      </Descriptions>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(160px, 1fr))', gap: 16 }}>
        {Object.entries(meta.counts).map(([entity, count]) => (
          <Card key={entity} size="small">
            <Statistic title={ENTITY_LABELS[entity] ?? entity} value={count} />
          </Card>
        ))}
      </div>
    </>
  )
}

export default function App() {
  const [meta, setMeta] = useState<SnapshotMeta | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchMeta().then(setMeta).catch((e: Error) => setError(e.message))
  }, [])

  return (
    <ConfigProvider locale={zhCN}>
      <Layout style={{ minHeight: '100vh' }}>
        <Layout.Header style={{ display: 'flex', alignItems: 'center' }}>
          <Typography.Title level={4} style={{ color: '#fff', margin: 0 }}>
            全球创新药资产情报平台
          </Typography.Title>
        </Layout.Header>
        <Layout.Content style={{ padding: 24, maxWidth: 1200, width: '100%', margin: '0 auto' }}>
          {error && <Alert type="error" title="无法读取数据快照" description={error} showIcon />}
          {!error && !meta && <Spin />}
          {meta && <SnapshotOverview meta={meta} />}
        </Layout.Content>
      </Layout>
    </ConfigProvider>
  )
}
