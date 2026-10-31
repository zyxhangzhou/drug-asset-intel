import { Table, Typography } from 'antd'
import { Link } from 'react-router'
import { fetchBuyers } from '../api/client'
import { useApi } from '../api/useApi'
import { Loaded } from '../components/Loaded'

export default function Buyers() {
  const state = useApi(fetchBuyers, [])
  return (
    <>
      <Typography.Title level={3}>买方药企</Typography.Title>
      <Loaded state={state}>
        {(rows) => (
          <Table
            rowKey="ticker"
            size="small"
            pagination={false}
            dataSource={rows}
            columns={[
              {
                title: '买方',
                render: (_, b) => (
                  <Link to={`/buyers/${b.ticker}`}>
                    {b.name_zh ?? b.name}（{b.name}）
                  </Link>
                ),
              },
              { title: '代码', dataIndex: 'ticker' },
              { title: '偏好条目', dataIndex: 'preferences', align: 'right' },
              { title: '以其为主组合买方的候选公司', dataIndex: 'primary_targets', align: 'right' },
            ]}
          />
        )}
      </Loaded>
    </>
  )
}
