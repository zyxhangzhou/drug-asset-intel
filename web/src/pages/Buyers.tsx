import { Table, Tag } from 'antd'
import { Link } from 'react-router'
import { fetchBuyers } from '../api/client'
import { useApi } from '../api/useApi'
import { Loaded } from '../components/Loaded'
import { PageHead } from '../components/Page'

export default function Buyers() {
  const state = useApi(fetchBuyers, [])
  return (
    <>
      <PageHead
        title="买方药企"
        lead="偏好口径沿用对方材料《10家大型药企创新药资产偏好分析》。点进买方查看画像、偏好行、财务与匹配的候选公司。"
      />
      <Loaded state={state}>
        {(rows) => (
          <Table
 className="table-panel"
            rowKey="ticker"
            size="middle"
            pagination={false}
            dataSource={rows}
            columns={[
              {
                title: '买方',
                width: 220,
                render: (_, b) => (
                  <div style={{ display: 'grid', gap: 2 }}>
                    <Link to={`/buyers/${b.ticker}`} style={{ fontSize: 'var(--fs-title)', fontWeight: 600 }}>
                      {b.name_zh ?? b.name}
                    </Link>
                    <span className="sub">
                      <span className="mono">{b.ticker}</span>
                    </span>
                  </div>
                ),
              },
              {
                title: '治疗领域偏好（按优先级）',
                render: (_, b) => (
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4 }}>
                    {b.therapeutic_areas.map((t, i) => (
                      <Tag key={t} style={{ margin: 0 }}>{i + 1}. {t}</Tag>
                    ))}
                  </div>
                ),
              },
              {
                title: '专利到期压力（美国，最近两项）',
                width: 360,
                render: (_, b) =>
                  b.loe.length ? (
                    <div style={{ display: 'grid', gap: 2 }}>
                      {b.loe.slice(0, 2).map((l) => (
                        <span key={l.product}>
                          {l.product.split('（')[0]} <span className="sub">{l.us_loe}</span>
                        </span>
                      ))}
                    </div>
                  ) : (
                    <span className="sub">—</span>
                  ),
              },
              {
                title: '主推荐方向指向该买方的候选公司',
                dataIndex: 'primary_targets',
                align: 'right',
                width: 200,
                render: (v, b) => (
                  <Link to={`/targets?buyer=${b.ticker}`} className="total">
                    {v}
                  </Link>
                ),
              },
            ]}
          />
        )}
      </Loaded>
    </>
  )
}
