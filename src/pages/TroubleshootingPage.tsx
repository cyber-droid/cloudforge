import { useState, useMemo } from 'react'
import { Link } from 'react-router-dom'
import { AlertTriangle, Clock, ArrowRight, ShieldCheck, CheckCircle2, Flame, Terminal } from 'lucide-react'
import { INCIDENTS } from '../data/incidentsData'
import { PageContainer } from '../components/layout/PageContainer'
import { Card } from '../components/common/Card'
import { Badge } from '../components/common/Badge'
import { Tabs } from '../components/common/Tabs'
import { Button } from '../components/common/Button'

export function TroubleshootingPage() {
  const [selectedStatus, setSelectedStatus] = useState<string>('All')

  const statusTabs = [
    { id: 'All', label: 'All Incidents' },
    { id: 'Active', label: 'Active Outages' },
    { id: 'Investigating', label: 'Under Investigation' },
    { id: 'Resolved', label: 'Resolved Scenarios' },
  ]

  const filteredIncidents = useMemo(() => {
    if (selectedStatus === 'All') return INCIDENTS
    return INCIDENTS.filter(i => i.status === selectedStatus)
  }, [selectedStatus])

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 pb-16">
      {/* Header */}
      <div className="border-b border-slate-800 bg-slate-950/80 py-12">
        <PageContainer>
          <div className="max-w-3xl space-y-3">
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-rose-950/60 border border-rose-800/50 text-rose-300 text-xs font-mono">
              <AlertTriangle className="w-3.5 h-3.5" />
              <span>PRODUCTION OUTAGE DRILLS</span>
            </div>
            <h1 className="text-3xl sm:text-5xl font-extrabold text-white tracking-tight">
              Learn by breaking systems.
            </h1>
            <p className="text-sm sm:text-base text-slate-300 leading-relaxed">
              Step into the shoes of an on-call SRE. Inspect live stdout container logs, analyze distributed telemetry metrics, utilize AI root-cause reasoning, and deploy configuration patches to recover crashed services.
            </p>
          </div>
        </PageContainer>
      </div>

      <PageContainer>
        {/* Status Tabs */}
        <div className="mb-8">
          <Tabs
            tabs={statusTabs}
            activeTab={selectedStatus}
            onChange={setSelectedStatus}
            variant="pills"
          />
        </div>

        {/* Incidents Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredIncidents.map(inc => (
            <Card
              key={inc.id}
              className="p-6 flex flex-col justify-between hover:border-rose-500/40 transition-all group"
            >
              <div>
                <div className="flex items-center justify-between mb-3">
                  <span className="text-xs font-mono font-bold text-slate-300 bg-slate-800 px-2 py-0.5 rounded border border-slate-700/60">
                    {inc.incidentId}
                  </span>
                  <Badge variant={inc.severityColor}>
                    {inc.severity.split(' - ')[0]}
                  </Badge>
                </div>

                <Link to={`/troubleshooting/${inc.id}`}>
                  <h3 className="text-lg font-bold text-white group-hover:text-rose-300 transition-colors leading-snug">
                    {inc.title}
                  </h3>
                </Link>

                <p className="text-xs text-slate-400 mt-2 leading-relaxed line-clamp-3">
                  {inc.symptoms}
                </p>

                {/* Skills tags */}
                <div className="flex flex-wrap gap-1.5 mt-4">
                  {inc.skills.map(s => (
                    <span
                      key={s}
                      className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700/60"
                    >
                      {s}
                    </span>
                  ))}
                </div>
              </div>

              {/* Card Footer */}
              <div className="mt-6 pt-4 border-t border-slate-800 flex items-center justify-between">
                <span className="text-xs font-mono text-slate-500 flex items-center gap-1.5">
                  <span
                    className={`w-2 h-2 rounded-full ${
                      inc.status === 'Resolved'
                        ? 'bg-emerald-400'
                        : inc.status === 'Investigating'
                        ? 'bg-amber-400 animate-ping'
                        : 'bg-rose-400 animate-pulse'
                    }`}
                  />
                  <span>{inc.status}</span>
                </span>
                <Link to={`/troubleshooting/${inc.id}`}>
                  <Button variant="outline" size="xs" iconRight={<ArrowRight className="w-3 h-3" />}>
                    Investigate ➔
                  </Button>
                </Link>
              </div>
            </Card>
          ))}
        </div>
      </PageContainer>
    </div>
  )
}
