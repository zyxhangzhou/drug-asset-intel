import { Card, Descriptions } from 'antd'
import { Link, useParams } from 'react-router'
import { fetchTrial, type TrialDetail as Detail } from '../api/client'
import { useApi } from '../api/useApi'
import { Loaded } from '../components/Loaded'
import { PageHead } from '../components/Page'
import { Legend, Sourced, SourcedText } from '../components/Sourced'
import { DATE_TYPE, label, STAGE, taLabel } from '../labels'
import { ResultsTable } from './TargetDetail'

function View({ d }: { d: Detail }) {
  const t = d.trial
  const s = t.sources
  const dated = (v: string | null, type: string | null) => (v ? `${v}${type ? `（${label(DATE_TYPE, type)}）` : ''}` : '—')
  return (
    <>
      <PageHead
        title={<Sourced sources={s} field="title">{t.title ?? t.nct_id}</Sourced>}
        meta={
          <>
            <b className="mono" style={{ color: 'var(--ink)' }}>{t.nct_id}</b>
            <span>{label(STAGE, t.phase)} · {t.status ?? '状态未知'}</span>
            <Link to={`/targets/${d.ticker}`}>{d.company}（{d.ticker}）</Link>
          </>
        }
      />
      <Legend />
      <Card size="small" title="方案与进度">
        <Descriptions column={{ xs: 1, md: 2 }} size="small" bordered>
          <Descriptions.Item label="阶段"><Sourced sources={s} field="phase">{label(STAGE, t.phase)}</Sourced></Descriptions.Item>
          <Descriptions.Item label="状态"><Sourced sources={s} field="status">{t.status ?? '—'}</Sourced></Descriptions.Item>
          <Descriptions.Item label="入组人数">
            <Sourced sources={s} field="enrollment">{t.enrollment == null ? '—' : `${t.enrollment}（${label(DATE_TYPE, t.enrollment_type)}）`}</Sourced>
          </Descriptions.Item>
          <Descriptions.Item label="开始日期"><Sourced sources={s} field="start_date">{t.start_date ?? '—'}</Sourced></Descriptions.Item>
          <Descriptions.Item label="主要完成日期（预计结束）">
            <Sourced sources={s} field="primary_completion_date">{dated(t.primary_completion_date, t.primary_completion_type)}</Sourced>
          </Descriptions.Item>
          <Descriptions.Item label="研究完成日期"><Sourced sources={s} field="completion_date">{t.completion_date ?? '—'}</Sourced></Descriptions.Item>
          <Descriptions.Item label="预计数据读出" span={2}>
            <Sourced sources={s} field="expected_readout">{t.expected_readout ?? '未披露（可参考主要完成日期）'}</Sourced>
          </Descriptions.Item>
          <Descriptions.Item label="方案设计" span={2}>
            <SourcedText sources={s} field="design" text={t.design} />
          </Descriptions.Item>
          <Descriptions.Item label="疾病" span={2}><Sourced sources={s} field="conditions">{t.conditions ?? '—'}</Sourced></Descriptions.Item>
          <Descriptions.Item label="干预" span={2}><Sourced sources={s} field="interventions">{t.interventions ?? '—'}</Sourced></Descriptions.Item>
          <Descriptions.Item label="归入管线" span={2}>
            {d.indication ? (
              <>
                {d.asset} · <Sourced sources={d.indication.sources} field="indication">{d.indication.indication}</Sourced>
                {' · '}{taLabel(d.indication.therapeutic_area)}
                {' · '}<Sourced sources={d.indication.sources} field="stage">{label(STAGE, d.indication.stage)}</Sourced>
              </>
            ) : '未归入管线'}
          </Descriptions.Item>
        </Descriptions>
      </Card>
      <Card size="small" title={`结果（${d.results.length}）`}>
        {d.results.length ? <ResultsTable results={d.results} showTrial={false} /> : <p className="note">无已发布或已抽取的结果</p>}
      </Card>
    </>
  )
}

export default function TrialDetail() {
  const { nct = '' } = useParams()
  const state = useApi(() => fetchTrial(nct), [nct])
  return <Loaded state={state}>{(d) => <View d={d} />}</Loaded>
}
