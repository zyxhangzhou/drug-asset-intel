import { ConfigProvider, Result } from 'antd'
import zhCN from 'antd/locale/zh_CN'
import { BrowserRouter, Link, Route, Routes, useLocation } from 'react-router'
import { fetchMeta } from './api/client'
import { useApi } from './api/useApi'
import BuyerDetail from './pages/BuyerDetail'
import Buyers from './pages/Buyers'
import Compare from './pages/Compare'
import Overview from './pages/Overview'
import SourceDetail from './pages/SourceDetail'
import TargetDetail from './pages/TargetDetail'
import Targets from './pages/Targets'
import TrialDetail from './pages/TrialDetail'
import { theme } from './theme'

const NAV = [
  { to: '/', label: '概览' },
  { to: '/buyers', label: '买方' },
  { to: '/targets', label: '候选' },
]

// Company, compare, trial and source pages all sit under 候选 in the navigation.
function section(pathname: string) {
  if (pathname === '/') return '/'
  return pathname.startsWith('/buyers') ? '/buyers' : '/targets'
}

function Shell() {
  const meta = useApi(fetchMeta, [])
  const current = section(useLocation().pathname)
  const snapshot = meta.data?.snapshot_date
  return (
    <>
      <header className="masthead">
        <div className="frame">
          <div className="masthead-row">
            <Link to="/" className="brand">
              <svg className="brand-mark" width="28" height="28" viewBox="0 0 28 28" aria-hidden>
                <rect width="28" height="28" rx="7" fill="var(--accent)" />
                <path d="M9 9.5 19 18.5" stroke="#fff" strokeOpacity=".55" strokeWidth="1.6" />
                <circle cx="9" cy="9.5" r="3" fill="#fff" />
                <circle cx="19" cy="18.5" r="3" fill="none" stroke="#fff" strokeWidth="1.6" />
              </svg>
              <span className="brand-text">
                <span className="brand-name">全球创新药资产情报平台</span>
                <span className="brand-sub">
                  10 家大型药企 × 标普生物科技指数成分公司{snapshot ? ` · 数据截至 ${snapshot}` : ''}
                </span>
              </span>
            </Link>
            <nav className="nav" aria-label="主导航">
              {NAV.map((n) => (
                <Link key={n.to} to={n.to} aria-current={n.to === current ? 'page' : undefined}>
                  {n.label}
                </Link>
              ))}
            </nav>
          </div>
        </div>
      </header>
      <main className="frame content">
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
      </main>
      <footer className="frame">
        <div className="colophon">每个带来源的值都可追溯到一手来源。事实、推断与 LLM 抽取分开标注；找不到来源的字段留空。</div>
      </footer>
    </>
  )
}

export default function App() {
  return (
    <ConfigProvider locale={zhCN} theme={theme}>
      <BrowserRouter>
        <Shell />
      </BrowserRouter>
    </ConfigProvider>
  )
}
