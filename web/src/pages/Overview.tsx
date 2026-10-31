import { Card } from 'antd'
import { Link } from 'react-router'
import { fetchMeta } from '../api/client'
import { useApi } from '../api/useApi'
import { Loaded } from '../components/Loaded'
import { PageHead } from '../components/Page'
import { Legend } from '../components/Sourced'

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

const ROUTE: [string, string, string][] = [
  ['/buyers', '买方画像', '10 家大型药企的治疗领域、技术与交易偏好，以及专利到期压力。'],
  ['/targets', '候选公司', '按买方、治疗领域、阶段筛选；可调评分权重，勾选 2–4 家对比。'],
  ['/targets/VKTX', '公司详情', '复核结论、管线、财务快照、催化事件与全部试验。'],
  ['/trials/NCT06068946', '试验与结果', '试验方案、入组与完成时间，已发布或已抽取的结果。'],
  ['/sources/MAN-RGNX-1', '来源原文', '存档原文中标出声明引用的片段。'],
]

export default function Overview() {
  const state = useApi(fetchMeta, [])
  return (
    <Loaded state={state}>
      {(meta) => (
        <>
          <PageHead
            title="数据快照"
            meta={
              <>
                <span>快照日（行情与财务截至）{meta.snapshot_date ?? '未知'}</span>
                <span>生成时间 {meta.generated_at ? new Date(meta.generated_at).toLocaleString('zh-CN') : '未知'}</span>
                <span>{meta.generator ?? ''}</span>
              </>
            }
            lead="把 10 家大型药企的资产偏好与标普生物科技指数成分公司的管线对上，筛出有收购或授权潜力的公司。每个带来源的值旁有来源标记，点开可追到一手来源。"
          />
          <Legend />
          <Card title="演示主线">
            <ol className="route">
              {ROUTE.map(([to, title, text]) => (
                <li key={to}>
                  <b><Link to={to}>{title}</Link></b>
                  <span>{text}</span>
                </li>
              ))}
            </ol>
          </Card>
          <Card title="快照内容">
            <div className="ledger">
              {Object.entries(meta.counts).map(([entity, count]) => (
                <div key={entity}>
                  <span>{ENTITY_LABELS[entity] ?? entity}</span>
                  <span className="figure">{count.toLocaleString('en-US')}</span>
                </div>
              ))}
            </div>
          </Card>
        </>
      )}
    </Loaded>
  )
}
