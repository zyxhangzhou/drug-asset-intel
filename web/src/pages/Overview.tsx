import { Card, Descriptions, Statistic, Typography } from 'antd'
import { Link } from 'react-router'
import { fetchMeta } from '../api/client'
import { useApi } from '../api/useApi'
import { Loaded } from '../components/Loaded'

const ENTITY_LABELS: Record<string, string> = {
  buyer: '买方药企',
  buyer_preference: '买方偏好',
  buyer_financial: '买方财务',
  buyer_product_loe: '买方专利到期产品',
  target: '标的公司',
  program: '管线',
  program_indication: '管线适应症',
  trial: '临床试验',
  trial_result: '试验结果',
  catalyst: '催化事件',
  financial_snapshot: '财务快照',
  approved_product: '获批产品',
  match: '买方×标的匹配',
  recommendation: '资产×适应症×买方组合',
}

export default function Overview() {
  const state = useApi(fetchMeta, [])
  return (
    <Loaded state={state}>
      {(meta) => (
        <>
          <Typography.Title level={3}>数据快照</Typography.Title>
          <Typography.Paragraph>
            从 <Link to="/buyers">买方画像</Link> 进入匹配的候选公司，或在 <Link to="/targets">候选列表</Link>{' '}
            按买方、治疗领域与阶段筛选。每个带来源的值旁有来源标记，点开可追到一手来源。
          </Typography.Paragraph>
          <Descriptions size="small" column={1} style={{ marginBottom: 24 }}>
            <Descriptions.Item label="快照日（行情与财务截至）">{meta.snapshot_date ?? '未知'}</Descriptions.Item>
            <Descriptions.Item label="数据快照时间">
              {meta.generated_at ? new Date(meta.generated_at).toLocaleString('zh-CN') : '未知'}
            </Descriptions.Item>
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
      )}
    </Loaded>
  )
}
