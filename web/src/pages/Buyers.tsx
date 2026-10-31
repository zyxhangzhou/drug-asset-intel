import { Table } from 'antd'
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
                render: (_, b) => (
                  <Link to={`/buyers/${b.ticker}`} style={{ fontSize: 16, fontWeight: 600 }}>
                    {b.name_zh ?? b.name}
                  </Link>
                ),
              },
              { title: '英文名', dataIndex: 'name', render: (v) => <span className="sub" style={{ fontSize: 14 }}>{v}</span> },
              { title: '代码', dataIndex: 'ticker', width: 90 },
              { title: '偏好条目', dataIndex: 'preferences', align: 'right', width: 110, render: (v) => <span className="figure">{v}</span> },
              {
                title: '以其为主组合买方的候选公司',
                dataIndex: 'primary_targets',
                align: 'right',
                width: 220,
                render: (v, b) => (
                  <Link to={`/targets?buyer=${b.ticker}`} className="figure">
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
