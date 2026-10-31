import { ConfigProvider, Layout, Menu, Result, Typography } from 'antd'
import zhCN from 'antd/locale/zh_CN'
import { BrowserRouter, Link, Route, Routes, useLocation } from 'react-router'
import BuyerDetail from './pages/BuyerDetail'
import Buyers from './pages/Buyers'
import Compare from './pages/Compare'
import Overview from './pages/Overview'
import SourceDetail from './pages/SourceDetail'
import TargetDetail from './pages/TargetDetail'
import Targets from './pages/Targets'
import TrialDetail from './pages/TrialDetail'

const NAV = [
  { key: '/', label: <Link to="/">概览</Link> },
  { key: '/buyers', label: <Link to="/buyers">买方</Link> },
  { key: '/targets', label: <Link to="/targets">候选</Link> },
]

function Shell() {
  const { pathname } = useLocation()
  const section = pathname === '/' ? '/' : pathname.startsWith('/buyers') ? '/buyers' : '/targets'
  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Layout.Header style={{ display: 'flex', alignItems: 'center', gap: 24 }}>
        <Typography.Title level={4} style={{ color: '#fff', margin: 0, whiteSpace: 'nowrap' }}>
          全球创新药资产情报平台
        </Typography.Title>
        <Menu theme="dark" mode="horizontal" selectedKeys={[section]} items={NAV} style={{ flex: 1, minWidth: 0 }} />
      </Layout.Header>
      <Layout.Content style={{ padding: 24, maxWidth: 1280, width: '100%', margin: '0 auto' }}>
        <Routes>
          <Route path="/" element={<Overview />} />
          <Route path="/buyers" element={<Buyers />} />
          <Route path="/buyers/:ticker" element={<BuyerDetail />} />
          <Route path="/targets" element={<Targets />} />
          <Route path="/targets/:ticker" element={<TargetDetail />} />
          <Route path="/compare" element={<Compare />} />
          <Route path="/trials/:nct" element={<TrialDetail />} />
          <Route path="/sources/:id" element={<SourceDetail />} />
          <Route path="*" element={<Result status="404" title="页面不存在" extra={<Link to="/">返回概览</Link>} />} />
        </Routes>
      </Layout.Content>
    </Layout>
  )
}

export default function App() {
  return (
    <ConfigProvider locale={zhCN}>
      <BrowserRouter>
        <Shell />
      </BrowserRouter>
    </ConfigProvider>
  )
}
