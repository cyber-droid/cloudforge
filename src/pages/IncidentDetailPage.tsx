import { useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import {
  AlertTriangle,
  Clock,
  Sparkles,
  Terminal,
  Activity,
  Layers,
  CheckCircle2,
  Search,
  Check,
  ShieldCheck,
  Play,
  RotateCcw,
} from 'lucide-react'
import { INCIDENTS } from '../data/incidentsData'
import { PageContainer } from '../components/layout/PageContainer'
import { Card } from '../components/common/Card'
import { Badge } from '../components/common/Badge'
import { Button } from '../components/common/Button'
import { Tabs } from '../components/common/Tabs'
import { CodeBlock } from '../components/common/CodeBlock'
import { useToast } from '../context/ToastContext'

export function IncidentDetailPage() {
  const { id } = useParams<{ id: string }>()
  const incident = INCIDENTS.find(i => i.id === id) || INCIDENTS[0]
  const { showToast } = useToast()

  const [activeTab, setActiveTab] = useState<string>('overview')
  const [logFilter, setLogFilter] = useState<'ALL' | 'ERROR' | 'WARN'>('ALL')
  const [logSearch, setLogSearch] = useState('')
  const [aiAnalyzing, setAiAnalyzing] = useState(false)
  const [aiReportRevealed, setAiReportRevealed] = useState(false)
  const [status, setStatus] = useState(incident.status)
  const [remediationApplied, setRemediationApplied] = useState(false)

  const tabs = [
    { id: 'overview', label: 'Overview & Timeline' },
    { id: 'logs', label: 'Terminal Logs', badge: incident.logs.length },
    { id: 'metrics', label: 'Telemetry Metrics' },
    { id: 'traces', label: 'Distributed Traces' },
    { id: 'investigation', label: 'AI Investigation' },
    { id: 'resolution', label: 'Remediation Fix' },
  ]

  const filteredLogs = incident.logs.filter(log => {
    if (logFilter !== 'ALL' && log.level !== logFilter) return false
    if (logSearch && !log.message.toLowerCase().includes(logSearch.toLowerCase())) return false
    return true
  })

  const handleRunAIAnalysis = () => {
    setAiAnalyzing(true)
    setTimeout(() => {
      setAiAnalyzing(false)
      setAiReportRevealed(true)
      setActiveTab('investigation')
      showToast('AI Investigation Completed', `Synthesized ${incident.logs.length} logs and metrics. Confidence: ${incident.aiInvestigation.confidence}%.`, 'success')
    }, 1000)
  }

  const handleApplyRemediation = () => {
    setRemediationApplied(true)
    setStatus('Resolved')
    showToast('Remediation Applied!', 'Configuration patch committed. Ingress health probes returning 200 OK.', 'success')
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 pb-16">
      {/* Incident Header */}
      <div className="border-b border-slate-800 bg-slate-900/80 py-10">
        <PageContainer>
          <div className="space-y-4">
            <div className="flex flex-wrap items-center justify-between gap-4">
              <Link
                to="/troubleshooting"
                className="text-xs font-mono text-cyan-400 hover:text-cyan-300 flex items-center gap-1"
              >
                ← Back to Incident Queue
              </Link>
              <div className="flex items-center gap-2">
                <span className="text-xs font-mono text-slate-400">Status:</span>
                <span
                  className={`text-xs font-mono font-bold px-2.5 py-0.5 rounded-full border uppercase ${
                    status === 'Resolved'
                      ? 'bg-emerald-950/80 border-emerald-500/60 text-emerald-300'
                      : status === 'Investigating'
                      ? 'bg-amber-950/80 border-amber-500/60 text-amber-300 animate-pulse'
                      : 'bg-rose-950/80 border-rose-500/60 text-rose-300'
                  }`}
                >
                  {status}
                </span>
              </div>
            </div>

            <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
              <div>
                <div className="flex items-center gap-3 mb-2">
                  <span className="text-sm font-mono font-bold text-white bg-slate-800 px-2.5 py-1 rounded-md border border-slate-700">
                    {incident.incidentId}
                  </span>
                  <Badge variant={incident.severityColor}>
                    {incident.severity}
                  </Badge>
                  <span className="text-xs font-mono text-slate-400">
                    {incident.technology}
                  </span>
                </div>
                <h1 className="text-2xl sm:text-4xl font-extrabold text-white tracking-tight">
                  {incident.title}
                </h1>
              </div>

              {/* Action Buttons */}
              <div className="flex flex-wrap items-center gap-3">
                <Button
                  variant="glow"
                  size="md"
                  onClick={handleRunAIAnalysis}
                  isLoading={aiAnalyzing}
                  icon={<Sparkles className="w-4 h-4 fill-slate-950" />}
                >
                  Analyze Incident with AI
                </Button>
                {status !== 'Resolved' && (
                  <Button
                    variant="secondary"
                    size="md"
                    onClick={handleApplyRemediation}
                    icon={<CheckCircle2 className="w-4 h-4 text-emerald-400" />}
                  >
                    Apply Remediation
                  </Button>
                )}
              </div>
            </div>
          </div>
        </PageContainer>
      </div>

      <PageContainer>
        {/* Navigation Tabs */}
        <div className="mb-6">
          <Tabs
            tabs={tabs}
            activeTab={activeTab}
            onChange={setActiveTab}
            variant="underline"
          />
        </div>

        {/* Tab 1: Overview & Timeline */}
        {activeTab === 'overview' && (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
            <div className="lg:col-span-7 space-y-6">
              <Card className="p-6 space-y-4">
                <h3 className="text-base font-bold text-white">Reported Symptoms</h3>
                <p className="text-xs sm:text-sm text-slate-300 leading-relaxed">
                  {incident.symptoms}
                </p>
                <div className="pt-2">
                  <span className="text-xs font-mono text-slate-400 block mb-2">
                    Evaluated Skill Domains:
                  </span>
                  <div className="flex flex-wrap gap-1.5">
                    {incident.skills.map(s => (
                      <span key={s} className="text-xs font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-200">
                        {s}
                      </span>
                    ))}
                  </div>
                </div>
              </Card>

              {/* Quick Incident Metrics Snapshot */}
              <Card className="p-6 space-y-3">
                <h3 className="text-sm font-bold text-white font-mono uppercase tracking-wider">
                  Impact Scope
                </h3>
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 text-xs font-mono">
                  <div className="p-3 rounded-lg bg-slate-950 border border-slate-800">
                    <span className="text-slate-500 block">5xx Error Rate</span>
                    <span className="text-lg font-bold text-rose-400">48.7%</span>
                  </div>
                  <div className="p-3 rounded-lg bg-slate-950 border border-slate-800">
                    <span className="text-slate-500 block">Affected Replicas</span>
                    <span className="text-lg font-bold text-amber-400">4 of 4 Pods</span>
                  </div>
                  <div className="p-3 rounded-lg bg-slate-950 border border-slate-800">
                    <span className="text-slate-500 block">Time to Detect</span>
                    <span className="text-lg font-bold text-cyan-400">42 seconds</span>
                  </div>
                </div>
              </Card>
            </div>

            {/* Timeline */}
            <div className="lg:col-span-5">
              <Card className="p-6 space-y-4">
                <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                  <h3 className="text-sm font-bold text-white font-mono uppercase tracking-wider">
                    Chronological Timeline
                  </h3>
                  <span className="text-[11px] font-mono text-slate-400">UTC Time</span>
                </div>

                <div className="relative pl-5 space-y-4 before:absolute before:left-2 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-800">
                  {incident.timeline.map((event, idx) => (
                    <div key={idx} className="relative text-xs">
                      <div
                        className={`absolute -left-[19px] top-1 w-2.5 h-2.5 rounded-full ${
                          event.status === 'error'
                            ? 'bg-rose-500'
                            : event.status === 'warning'
                            ? 'bg-amber-500'
                            : event.status === 'success'
                            ? 'bg-emerald-500'
                            : 'bg-cyan-500'
                        }`}
                      />
                      <div className="flex items-center gap-2 font-mono text-[11px] text-slate-400">
                        <span>{event.time}</span>
                      </div>
                      <p className="text-slate-200 mt-0.5 leading-relaxed">{event.message}</p>
                    </div>
                  ))}
                </div>
              </Card>
            </div>
          </div>
        )}

        {/* Tab 2: Logs */}
        {activeTab === 'logs' && (
          <div className="space-y-4">
            <div className="flex flex-wrap items-center justify-between gap-3 p-3 rounded-xl bg-slate-900 border border-slate-800">
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setLogFilter('ALL')}
                  className={`px-2.5 py-1 rounded-md text-xs font-mono ${
                    logFilter === 'ALL' ? 'bg-cyan-500 text-slate-950 font-bold' : 'text-slate-400 hover:text-white'
                  }`}
                >
                  ALL
                </button>
                <button
                  onClick={() => setLogFilter('ERROR')}
                  className={`px-2.5 py-1 rounded-md text-xs font-mono ${
                    logFilter === 'ERROR' ? 'bg-rose-500 text-white font-bold' : 'text-slate-400 hover:text-white'
                  }`}
                >
                  ERROR
                </button>
                <button
                  onClick={() => setLogFilter('WARN')}
                  className={`px-2.5 py-1 rounded-md text-xs font-mono ${
                    logFilter === 'WARN' ? 'bg-amber-500 text-slate-950 font-bold' : 'text-slate-400 hover:text-white'
                  }`}
                >
                  WARN
                </button>
              </div>

              <div className="relative">
                <Search className="w-3.5 h-3.5 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  type="text"
                  value={logSearch}
                  onChange={e => setLogSearch(e.target.value)}
                  placeholder="Filter logs (e.g., connection refused)..."
                  className="bg-slate-950 border border-slate-800 rounded-lg pl-8 pr-3 py-1.5 text-xs text-slate-200 placeholder:text-slate-500 focus:outline-none focus:border-cyan-500 w-64"
                />
              </div>
            </div>

            {/* Terminal console */}
            <div className="rounded-xl border border-slate-800 bg-slate-950 font-mono text-xs overflow-x-auto shadow-2xl p-4 divide-y divide-slate-900 leading-relaxed">
              {filteredLogs.map((log, idx) => (
                <div key={idx} className="py-2 flex items-start gap-3 hover:bg-slate-900/40">
                  <span className="text-slate-600 text-[11px] shrink-0">{log.timestamp}</span>
                  <span
                    className={`text-[10px] px-1.5 py-0.2 rounded font-bold shrink-0 ${
                      log.level === 'ERROR' || log.level === 'FATAL'
                        ? 'bg-rose-950 text-rose-400 border border-rose-800/60'
                        : log.level === 'WARN'
                        ? 'bg-amber-950 text-amber-400 border border-amber-800/60'
                        : 'bg-slate-800 text-slate-300'
                    }`}
                  >
                    {log.level}
                  </span>
                  <span className="text-cyan-400 text-[11px] shrink-0 font-semibold">[{log.source}]</span>
                  <span className="text-slate-200 whitespace-pre-wrap">{log.message}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Tab 3: Metrics */}
        {activeTab === 'metrics' && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {incident.metrics.map(metric => (
              <Card key={metric.label} className="p-6 space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-mono font-semibold text-slate-300">{metric.label}</span>
                  <span className="text-[10px] font-mono text-slate-500">Prometheus Rate (5m)</span>
                </div>
                {/* Visual Bar representation */}
                <div className="flex items-end justify-between h-40 pt-6 gap-3">
                  {metric.points.map((pt, i) => {
                    const maxVal = Math.max(...metric.points.map(p => p.value), 1)
                    const height = Math.round((pt.value / maxVal) * 100)
                    return (
                      <div key={i} className="flex-1 flex flex-col items-center gap-1.5 h-full justify-end group">
                        <span className="text-[10px] font-mono text-slate-400 group-hover:text-white">
                          {pt.value}
                        </span>
                        <div className="w-full bg-slate-800 rounded-t h-full flex items-end">
                          <div
                            className={`w-full rounded-t transition-all ${
                              pt.value > 20
                                ? 'bg-rose-500'
                                : 'bg-cyan-500'
                            }`}
                            style={{ height: `${height}%` }}
                          />
                        </div>
                        <span className="text-[10px] font-mono text-slate-500">{pt.time}</span>
                      </div>
                    )
                  })}
                </div>
              </Card>
            ))}
          </div>
        )}

        {/* Tab 4: Distributed Traces */}
        {activeTab === 'traces' && (
          <Card className="p-6 space-y-4">
            <h3 className="text-base font-bold text-white">Distributed Traces (Tempo / OpenTelemetry)</h3>
            <div className="space-y-3 font-mono text-xs">
              <div className="p-3 rounded-lg bg-slate-950 border border-slate-800 flex items-center justify-between">
                <span className="text-cyan-400">Trace ID: 7f89a2bc91024e12</span>
                <span className="text-rose-400 font-semibold">Total Duration: 5002ms (Timeout)</span>
              </div>

              {/* Spans */}
              <div className="space-y-2 pt-2">
                <div className="p-2.5 rounded bg-slate-900 border border-slate-800 flex items-center justify-between pl-4 border-l-4 border-l-cyan-500">
                  <span>ingress-nginx: POST /v1/auth/token</span>
                  <span className="text-slate-400">5002ms</span>
                </div>
                <div className="p-2.5 rounded bg-slate-900 border border-slate-800 flex items-center justify-between pl-8 border-l-4 border-l-indigo-500">
                  <span>auth-service: HandleAuthRequest()</span>
                  <span className="text-slate-400">5000ms</span>
                </div>
                <div className="p-2.5 rounded bg-rose-950/30 border border-rose-800/60 flex items-center justify-between pl-12 border-l-4 border-l-rose-500 text-rose-300">
                  <span>redis.connect(redis-master:6379) - DEADLINE_EXCEEDED</span>
                  <span className="font-bold">5000ms</span>
                </div>
              </div>
            </div>
          </Card>
        )}

        {/* Tab 5: AI Investigation */}
        {activeTab === 'investigation' && (
          <div className="space-y-6">
            <div className="p-6 rounded-2xl border border-cyan-500/40 bg-slate-900/90 shadow-2xl space-y-6">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-slate-800 gap-2">
                <div className="flex items-center gap-2.5">
                  <div className="p-2 rounded-xl bg-cyan-950 border border-cyan-700/60 text-cyan-400">
                    <Sparkles className="w-5 h-5" />
                  </div>
                  <div>
                    <h3 className="text-base font-bold text-white">
                      CloudForge AI Diagnostic Report
                    </h3>
                    <p className="text-xs text-slate-400 font-mono">
                      Correlated against container runtime logs, endpoint controllers, and network metrics
                    </p>
                  </div>
                </div>

                {/* Confidence Meter */}
                <div className="flex items-center gap-2 bg-slate-950 px-3 py-1.5 rounded-xl border border-slate-800 text-xs font-mono">
                  <span className="text-slate-400">Confidence:</span>
                  <span className="text-cyan-400 font-bold">
                    {incident.aiInvestigation.confidence}%
                  </span>
                </div>
              </div>

              {/* Root Cause */}
              <div className="space-y-2">
                <h4 className="text-xs font-mono uppercase font-bold text-cyan-400 tracking-wider">
                  Hypothesized Root Cause
                </h4>
                <p className="text-sm text-slate-200 leading-relaxed bg-slate-950/60 p-4 rounded-xl border border-slate-800">
                  {incident.aiInvestigation.possibleRootCause}
                </p>
              </div>

              {/* Evidence */}
              <div className="space-y-2">
                <h4 className="text-xs font-mono uppercase font-bold text-slate-300 tracking-wider">
                  Corroborating Evidence
                </h4>
                <div className="space-y-2">
                  {incident.aiInvestigation.evidence.map((ev, i) => (
                    <div key={i} className="flex items-start gap-2.5 text-xs text-slate-300 p-2.5 rounded-lg bg-slate-950/40 border border-slate-800 font-mono">
                      <CheckCircle2 className="w-4 h-4 text-cyan-400 shrink-0 mt-0.5" />
                      <span>{ev}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Suggested Remediation */}
              <div className="space-y-2">
                <h4 className="text-xs font-mono uppercase font-bold text-emerald-400 tracking-wider">
                  Suggested Remediation
                </h4>
                <p className="text-xs text-slate-300">
                  {incident.aiInvestigation.suggestedRemediation}
                </p>
                {incident.aiInvestigation.remediationCommand && (
                  <CodeBlock
                    language="bash"
                    code={incident.aiInvestigation.remediationCommand}
                  />
                )}
                {incident.aiInvestigation.remediationPatch && (
                  <CodeBlock
                    language="yaml"
                    code={incident.aiInvestigation.remediationPatch}
                  />
                )}
              </div>

              <div className="pt-2">
                <Button
                  variant="glow"
                  size="md"
                  onClick={handleApplyRemediation}
                  icon={<Play className="w-4 h-4 fill-slate-950" />}
                >
                  Apply Remediation Patch
                </Button>
              </div>
            </div>
          </div>
        )}

        {/* Tab 6: Resolution */}
        {activeTab === 'resolution' && (
          <Card className="p-8 space-y-6 text-center max-w-2xl mx-auto">
            {remediationApplied || status === 'Resolved' ? (
              <div className="space-y-4">
                <div className="w-16 h-16 rounded-full bg-emerald-950/60 border border-emerald-500 text-emerald-400 mx-auto flex items-center justify-center">
                  <CheckCircle2 className="w-8 h-8" />
                </div>
                <h3 className="text-2xl font-bold text-white">Incident Resolved!</h3>
                <p className="text-xs text-slate-300 font-mono leading-relaxed">
                  The Redis connection hostname was successfully updated to `redis.database.svc.cluster.local`. Upstream pods passed all readiness probes and traffic error rates returned to 0.00%.
                </p>
                <div className="pt-4 flex items-center justify-center gap-3">
                  <Link to="/troubleshooting">
                    <Button variant="secondary" size="sm">
                      Back to Incidents Queue
                    </Button>
                  </Link>
                  <Link to="/achievements">
                    <Button variant="primary" size="sm">
                      View Earned Achievements (+800 XP)
                    </Button>
                  </Link>
                </div>
              </div>
            ) : (
              <div className="space-y-4">
                <AlertTriangle className="w-12 h-12 text-amber-400 mx-auto" />
                <h3 className="text-xl font-bold text-white">Remediation Pending</h3>
                <p className="text-xs text-slate-400 font-mono">
                  Inspect the AI diagnostic report or review the logs to deploy the configuration fix.
                </p>
                <Button variant="glow" size="sm" onClick={handleApplyRemediation}>
                  Execute Automated Fix
                </Button>
              </div>
            )}
          </Card>
        )}
      </PageContainer>
    </div>
  )
}
