import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import {
  Award,
  Clock,
  BookOpen,
  CheckCircle2,
  Play,
  ArrowRight,
  ShieldCheck,
  Trophy,
  Layers,
  FileQuestion,
  HelpCircle,
  Loader2,
} from 'lucide-react'
import { CERTIFICATIONS } from '../data/certificationsData'
import { PageContainer } from '../components/layout/PageContainer'
import { Card } from '../components/common/Card'
import { Badge } from '../components/common/Badge'
import { Button } from '../components/common/Button'
import { ExamSimulatorModal } from '../components/certs/ExamSimulatorModal'
import { api } from '../services/api'
import type { ApiCertificationDetail, ApiTrainingProgress } from '../services/api'

export function CertificationDetailPage() {
  const { id } = useParams<{ id: string }>()
  const fallbackCert = CERTIFICATIONS.find(c => c.id === id || c.id === 'aws-cloud-practitioner') || CERTIFICATIONS[0]

  const [certData, setCertData] = useState<ApiCertificationDetail | null>(null)
  const [trainingProgress, setTrainingProgress] = useState<ApiTrainingProgress | null>(null)
  const [isLoading, setIsLoading] = useState<boolean>(true)
  const [examModalOpen, setExamModalOpen] = useState(false)
  const [isEnrolling, setIsEnrolling] = useState(false)
  const [isClaiming, setIsClaiming] = useState(false)
  const [claimedCert, setClaimedCert] = useState<any>(null)

  useEffect(() => {
    let isMounted = true
    async function loadData() {
      if (!id) return
      setIsLoading(true)
      try {
        const cert = await api.getCertification(id)
        if (isMounted && cert) {
          setCertData(cert)

          // If training is linked, fetch live progress
          if (cert.trainings && cert.trainings.length > 0) {
            try {
              const prog = await api.getTrainingProgress(cert.trainings[0].id)
              if (isMounted) setTrainingProgress(prog)
            } catch (err) {
              // Not enrolled or anonymous
            }
          }
        }
      } catch (err) {
        console.warn('Backend certification detail fetch failed, using fallback dataset', err)
      } finally {
        if (isMounted) setIsLoading(false)
      }
    }

    loadData()
    return () => { isMounted = false }
  }, [id])

  const cert = certData || (fallbackCert as unknown as ApiCertificationDetail)
  const activeTraining = certData?.trainings?.[0]
  const currentProgress = trainingProgress ? trainingProgress.progress_percentage : (cert.progress || 0)

  const handleEnroll = async () => {
    if (!activeTraining) return
    setIsEnrolling(true)
    try {
      await api.enrollTraining(activeTraining.id)
      const prog = await api.getTrainingProgress(activeTraining.id)
      setTrainingProgress(prog)
    } catch (err) {
      console.error('Failed to enroll in training track', err)
    } finally {
      setIsEnrolling(false)
    }
  }

  const handleClaimCertificate = async () => {
    if (!activeTraining) return
    setIsClaiming(true)
    try {
      const res = await api.completeTraining(activeTraining.id)
      setClaimedCert(res)
      const prog = await api.getTrainingProgress(activeTraining.id)
      setTrainingProgress(prog)
    } catch (err) {
      console.error('Failed to issue certificate', err)
    } finally {
      setIsClaiming(false)
    }
  }

  const certAny = cert as any
  const certTitle = cert.title || cert.name || 'Cloud Certification'
  const trainingCertName = certAny.trainingCertificate || certAny.training_certificate_name || 'Certificate of Completion'
  const practiceQCount = certAny.practice_questions_count || certAny.practiceQuestionsCount || 10
  const examDomainsList = certAny.exam_domains || certAny.domains || certAny.examDomains || []
  const skillsList = certAny.skills_gained || certAny.skillsGained || [
    'Cloud Architectural Principles',
    'Security & IAM Policy Management',
    'High Availability & Disaster Recovery',
    'Cost Optimization & FinOps Fundamentals',
  ]
  const moduleList = activeTraining?.modules || certAny.modules || []

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 pb-16">
      {/* Hero */}
      <div className="border-b border-slate-800 bg-gradient-to-b from-slate-900/90 to-slate-950 py-12">
        <PageContainer>
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
            <div className="lg:col-span-8 space-y-4">
              <Link
                to="/certifications"
                className="text-xs font-mono text-cyan-400 hover:text-cyan-300 flex items-center gap-1 mb-2"
              >
                ← Back to Certification Hub
              </Link>

              <div className="flex flex-wrap items-center gap-2">
                <Badge variant="amber">{cert.provider}</Badge>
                {cert.code && (
                  <span className="text-xs font-mono font-bold text-slate-200 bg-slate-800 px-2 py-0.5 rounded border border-slate-700/60">
                    Exam Code: {cert.code}
                  </span>
                )}
                <span className="text-xs font-mono text-slate-400">•</span>
                <span className="text-xs font-mono text-slate-300">{cert.level} Level</span>
                <span className="text-xs font-mono text-slate-400">•</span>
                <span className="text-xs font-mono text-slate-300">{cert.duration} Track</span>
              </div>

              <h1 className="text-3xl sm:text-5xl font-extrabold text-white tracking-tight">
                {certTitle}
              </h1>

              <p className="text-base text-slate-300 leading-relaxed max-w-3xl">
                {cert.description}
              </p>

              {/* Verified Training Credential badge note */}
              <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800 text-xs font-mono text-slate-300 flex items-center gap-2">
                <ShieldCheck className="w-4 h-4 text-cyan-400 shrink-0" />
                <span>Awarded upon completion: {trainingCertName}</span>
              </div>
            </div>

            {/* Preparation Progress & Launch Card */}
            <div className="lg:col-span-4">
              <Card className="p-6 border-amber-500/30 bg-slate-900/90 shadow-2xl space-y-5">
                <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                  <span className="text-xs font-mono uppercase tracking-wider text-slate-400">
                    Prep Readiness
                  </span>
                  <span className="text-sm font-bold font-mono text-amber-400">
                    {currentProgress}% Ready
                  </span>
                </div>

                <div className="w-full h-2 rounded-full bg-slate-800 overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-amber-500 to-cyan-500 rounded-full transition-all duration-500"
                    style={{ width: `${currentProgress}%` }}
                  />
                </div>

                <div className="text-xs font-mono space-y-2 text-slate-400 pt-1">
                  <div className="flex justify-between">
                    <span>Curriculum Completed:</span>
                    <span className="text-slate-200">
                      {trainingProgress ? `${trainingProgress.completed_lessons} of ${trainingProgress.total_lessons} Lessons` : `${currentProgress}%`}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span>Questions Mastered:</span>
                    <span className="text-slate-200">
                      {Math.round((practiceQCount * currentProgress) / 100)} / {practiceQCount}
                    </span>
                  </div>
                </div>

                <div className="pt-2 space-y-2">
                  <Button
                    variant="glow"
                    size="md"
                    className="w-full"
                    onClick={() => setExamModalOpen(true)}
                    icon={<Play className="w-4 h-4 fill-slate-950" />}
                  >
                    Launch Timed Mock Exam
                  </Button>

                  {trainingProgress?.is_eligible_for_certificate && !claimedCert && !trainingProgress.certificate_id ? (
                    <Button
                      variant="primary"
                      size="sm"
                      className="w-full bg-emerald-600 hover:bg-emerald-500 text-white font-bold"
                      disabled={isClaiming}
                      onClick={handleClaimCertificate}
                    >
                      {isClaiming ? 'Generating Certificate...' : 'Claim CloudForge Certificate 🎓'}
                    </Button>
                  ) : activeTraining && (!trainingProgress || trainingProgress.status === 'not_enrolled') ? (
                    <Button
                      variant="outline"
                      size="sm"
                      className="w-full"
                      disabled={isEnrolling}
                      onClick={handleEnroll}
                    >
                      {isEnrolling ? 'Enrolling...' : 'Enroll in Training Track'}
                    </Button>
                  ) : null}

                  <Link to="/courses" className="block w-full">
                    <Button variant="secondary" size="sm" className="w-full">
                      Review Training Modules
                    </Button>
                  </Link>
                </div>
              </Card>
            </div>
          </div>
        </PageContainer>
      </div>

      <PageContainer>
        {/* Certificate Earned Banner */}
        {(claimedCert || trainingProgress?.certificate_id) && (
          <div className="my-8 p-6 rounded-2xl bg-gradient-to-r from-emerald-950/60 to-cyan-950/60 border border-emerald-500/40 flex flex-col sm:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <Award className="w-8 h-8 text-emerald-400 shrink-0" />
              <div>
                <h4 className="text-base font-bold text-white">CloudForge Certificate Issued!</h4>
                <p className="text-xs text-slate-300 font-mono">
                  Certificate #{claimedCert?.certificate_number || 'CF-VERIFIED'} • Code: {claimedCert?.verification_code || 'Issued'}
                </p>
              </div>
            </div>
            {claimedCert?.verification_url && (
              <a
                href={claimedCert.verification_url}
                target="_blank"
                rel="noreferrer"
                className="px-4 py-2 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-xs font-mono transition-colors"
              >
                Public Verification Link ➔
              </a>
            )}
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-10">
          {/* Main: Domain Breakdown & Modules */}
          <div className="lg:col-span-8 space-y-10">
            {/* Exam Domain Weightings */}
            <div>
              <h2 className="text-xl font-bold text-white mb-2">
                Official Exam Domain Weightings
              </h2>
              <p className="text-xs text-slate-400 font-mono mb-4">
                CloudForge curriculum matches the exact percentages evaluated on the certification.
              </p>
              <div className="space-y-3">
                {examDomainsList.map((d: any) => (
                  <div key={d.name} className="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-1.5">
                    <div className="flex justify-between text-xs font-mono">
                      <span className="font-semibold text-slate-200">{d.name}</span>
                      <span className="text-cyan-400 font-bold">{d.percentage}% of Exam</span>
                    </div>
                    <div className="w-full h-2 rounded-full bg-slate-800 overflow-hidden">
                      <div
                        className="h-full bg-cyan-400 rounded-full"
                        style={{ width: `${d.percentage}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Curriculum Checklist */}
            <div>
              <h2 className="text-xl font-bold text-white mb-4">
                Training Modules Checklist
              </h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {moduleList.map((mod: any, i: number) => (
                  <div
                    key={i}
                    className="p-3 rounded-xl bg-slate-900/60 border border-slate-800 text-xs text-slate-300 flex items-center gap-2.5 font-mono"
                  >
                    <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                    <span className="truncate">{typeof mod === 'string' ? mod : mod.title || `Module ${i + 1}`}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Interactive Question Bank Teaser */}
            <div className="p-6 rounded-2xl border border-slate-800 bg-slate-900/60 space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-base font-bold text-white flex items-center gap-2">
                    <FileQuestion className="w-4 h-4 text-amber-400" />
                    <span>Active Practice Exam Question Bank</span>
                  </h3>
                  <p className="text-xs text-slate-400 font-mono mt-0.5">
                    {practiceQCount}+ technical multiple-choice questions with deep explanations
                  </p>
                </div>
                <Button variant="outline" size="sm" onClick={() => setExamModalOpen(true)}>
                  Take Practice Quiz
                </Button>
              </div>

              {/* Sample question snippet */}
              <div className="p-4 rounded-xl bg-slate-950 border border-slate-800/80 text-xs font-sans space-y-2">
                <span className="text-[11px] font-mono text-cyan-400 uppercase">
                  Sample Practice Blueprint Question:
                </span>
                <p className="text-slate-200 font-medium">
                  {certAny.questions?.[0]?.question || 'Under the Shared Responsibility Model, which operational boundary is managed by the cloud customer?'}
                </p>
              </div>
            </div>
          </div>

          {/* Right Sidebar: Required Skills & Roadmaps */}
          <div className="lg:col-span-4 space-y-6">
            <Card className="p-6 space-y-4">
              <h3 className="text-sm font-bold text-white font-mono uppercase tracking-wider">
                Target Competencies
              </h3>
              <div className="space-y-2">
                {skillsList.map((skill: string, idx: number) => (
                  <div key={idx} className="flex items-start gap-2 text-xs text-slate-300">
                    <CheckCircle2 className="w-3.5 h-3.5 text-cyan-400 shrink-0 mt-0.5" />
                    <span>{skill}</span>
                  </div>
                ))}
              </div>
            </Card>

            <Card className="p-6 space-y-4 border-purple-500/30">
              <div className="flex items-center gap-2 text-purple-400 font-bold text-xs font-mono">
                <Layers className="w-4 h-4" />
                <span>Related Career Roadmap</span>
              </div>
              <p className="text-xs text-slate-300 leading-relaxed">
                This credential forms Stage 4 of the comprehensive Cloud Engineer roadmap.
              </p>
              <Link to="/roadmaps/cloud-engineer">
                <Button variant="secondary" size="xs" className="w-full">
                  View Cloud Engineer Roadmap ➔
                </Button>
              </Link>
            </Card>
          </div>
        </div>
      </PageContainer>

      {/* Interactive Exam Simulator Modal */}
      <ExamSimulatorModal
        certification={cert}
        isOpen={examModalOpen}
        onClose={() => setExamModalOpen(false)}
      />
    </div>
  )
}
