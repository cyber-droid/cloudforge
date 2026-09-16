import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Award, CheckCircle2, Clock, ArrowRight, ShieldAlert, Sparkles, BookOpen } from 'lucide-react'
import { CERTIFICATIONS } from '../data/certificationsData'
import { PageContainer } from '../components/layout/PageContainer'
import { Card } from '../components/common/Card'
import { Badge } from '../components/common/Badge'
import { Tabs } from '../components/common/Tabs'
import { Button } from '../components/common/Button'
import { api } from '../services/api'
import type { ApiCertificationSummary } from '../services/api'

export function CertificationsPage() {
  const [selectedProvider, setSelectedProvider] = useState<string>('All')
  const [certs, setCerts] = useState<ApiCertificationSummary[]>([])
  const [isLoading, setIsLoading] = useState<boolean>(true)

  const providers = [
    { id: 'All', label: 'All Providers' },
    { id: 'AWS', label: 'AWS' },
    { id: 'Microsoft Azure', label: 'Microsoft Azure' },
    { id: 'Kubernetes', label: 'Kubernetes' },
    { id: 'DevOps', label: 'DevOps' },
  ]

  useEffect(() => {
    let isMounted = true
    async function fetchCerts() {
      setIsLoading(true)
      try {
        const data = await api.getCertifications(selectedProvider !== 'All' ? selectedProvider : undefined)
        if (isMounted && data && Array.isArray(data)) {
          setCerts(data)
        }
      } catch (err) {
        console.warn('Backend certifications fetch failed, falling back to local dataset', err)
        if (isMounted) {
          const fallback = selectedProvider === 'All'
            ? CERTIFICATIONS
            : CERTIFICATIONS.filter(c => c.provider === selectedProvider)
          setCerts(fallback as unknown as ApiCertificationSummary[])
        }
      } finally {
        if (isMounted) setIsLoading(false)
      }
    }

    fetchCerts()
    return () => { isMounted = false }
  }, [selectedProvider])

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 pb-16">
      {/* Header Banner */}
      <div className="border-b border-slate-800 bg-slate-950/80 py-12">
        <PageContainer>
          <div className="max-w-3xl space-y-3">
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-amber-950/60 border border-amber-800/50 text-amber-300 text-xs font-mono">
              <Award className="w-3.5 h-3.5" />
              <span>INDUSTRY CERTIFICATION PREPARATION</span>
            </div>
            <h1 className="text-3xl sm:text-5xl font-extrabold text-white tracking-tight">
              Prepare for industry certifications.
            </h1>
            <p className="text-sm sm:text-base text-slate-300 leading-relaxed">
              Structured preparation tracks engineered around official exam domain weightings. Complete rigorous hands-on modules and test your readiness with full-length timed mock exams.
            </p>

            {/* Crucial Certification Disclaimer */}
            <div className="mt-4 p-3.5 rounded-xl bg-slate-900/90 border border-amber-500/30 text-xs font-mono text-slate-300 flex items-start gap-2.5">
              <ShieldAlert className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
              <p className="leading-relaxed">
                <strong className="text-amber-300">Important Distinction:</strong> CloudForge provides comprehensive exam preparation and issues verified <span className="underline decoration-cyan-400">CloudForge Training Certificates</span>. Official vendor exams (AWS, Azure, CNCF) are administered separately by their respective organizations.
              </p>
            </div>
          </div>
        </PageContainer>
      </div>

      <PageContainer>
        {/* Provider Tabs */}
        <div className="mb-8">
          <Tabs
            tabs={providers}
            activeTab={selectedProvider}
            onChange={setSelectedProvider}
            variant="pills"
          />
        </div>

        {/* Certifications Grid */}
        {isLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2, 3].map(n => (
              <div key={n} className="h-72 rounded-2xl bg-slate-900/60 border border-slate-800 animate-pulse" />
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {certs.map(cert => (
              <Card
                key={cert.id}
                className="p-6 flex flex-col justify-between hover:border-amber-500/40 transition-all group"
              >
                <div>
                  <div className="flex items-start justify-between gap-2 mb-3">
                    <Badge variant={cert.provider === 'AWS' ? 'amber' : cert.provider === 'Microsoft Azure' ? 'blue' : 'purple'}>
                      {cert.provider}
                    </Badge>
                    {cert.code && (
                      <span className="text-xs font-mono font-bold text-slate-200 bg-slate-800 px-2 py-0.5 rounded border border-slate-700/60">
                        {cert.code}
                      </span>
                    )}
                  </div>

                  <Link to={`/certifications/${cert.slug || cert.id}`}>
                    <h3 className="text-lg font-bold text-white group-hover:text-amber-300 transition-colors leading-snug">
                      {cert.title || cert.name}
                    </h3>
                  </Link>

                  <p className="text-xs text-slate-400 mt-2 leading-relaxed line-clamp-3">
                    {cert.description}
                  </p>

                  {/* Progress bar if student has started */}
                  {cert.progress > 0 && (
                    <div className="mt-4 pt-3 border-t border-slate-800/80 space-y-1.5">
                      <div className="flex justify-between text-xs font-mono">
                        <span className="text-slate-400">Preparation Progress</span>
                        <span className="text-amber-400 font-bold">{cert.progress}%</span>
                      </div>
                      <div className="w-full h-1.5 rounded-full bg-slate-800 overflow-hidden">
                        <div
                          className="h-full bg-gradient-to-r from-amber-500 to-cyan-500 rounded-full"
                          style={{ width: `${cert.progress}%` }}
                        />
                      </div>
                    </div>
                  )}

                  {/* Metadata Box */}
                  <div className="mt-4 p-3 rounded-lg bg-slate-950/60 border border-slate-800 text-xs font-mono space-y-1">
                    <div className="flex justify-between text-slate-400">
                      <span>Questions Bank:</span>
                      <span className="text-slate-200">{cert.practice_questions_count || 10}+ Questions</span>
                    </div>
                    <div className="flex justify-between text-slate-400">
                      <span>Full Mock Exams:</span>
                      <span className="text-slate-200">{cert.mock_exams_count || 3} Timed Exams</span>
                    </div>
                    <div className="flex justify-between text-slate-400">
                      <span>Duration:</span>
                      <span className="text-slate-200">{cert.duration || '18h'}</span>
                    </div>
                  </div>
                </div>

                {/* Card Footer */}
                <div className="mt-6 pt-4 border-t border-slate-800 flex items-center justify-between">
                  <span className="text-[11px] font-mono text-slate-500">
                    CloudForge Prep Track
                  </span>
                  <Link to={`/certifications/${cert.slug || cert.id}`}>
                    <Button variant="outline" size="xs" iconRight={<ArrowRight className="w-3 h-3" />}>
                      Start Prep
                    </Button>
                  </Link>
                </div>
              </Card>
            ))}
          </div>
        )}
      </PageContainer>
    </div>
  )
}
