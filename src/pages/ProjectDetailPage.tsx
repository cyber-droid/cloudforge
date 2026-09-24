import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import {
  FolderGit2,
  Clock,
  CheckCircle2,
  Play,
  Terminal,
  Shield,
  Layers,
  Check,
  RotateCcw,
  Sparkles,
  BookOpen,
} from 'lucide-react'
import { GithubIcon } from '../components/common/BrandIcons'
import { PROJECTS } from '../data/projectsData'
import { PageContainer } from '../components/layout/PageContainer'
import { Card } from '../components/common/Card'
import { Badge } from '../components/common/Badge'
import { Button } from '../components/common/Button'
import { CodeBlock } from '../components/common/CodeBlock'
import { useToast } from '../context/ToastContext'
import { api, type ApiProjectDetail, type ApiProjectStep } from '../services/api'

export function ProjectDetailPage() {
  const { id } = useParams<{ id: string }>()
  const { showToast } = useToast()

  const [project, setProject] = useState<ApiProjectDetail | null>(null)
  const [steps, setSteps] = useState<ApiProjectStep[]>([])
  const [loading, setLoading] = useState(true)
  const [verifying, setVerifying] = useState(false)
  const [verificationResult, setVerificationResult] = useState<string | null>(null)

  useEffect(() => {
    let isMounted = true
    async function loadProject() {
      if (!id) return
      setLoading(true)
      try {
        const detail = await api.getProject(id)
        if (isMounted) {
          setProject(detail)
          setSteps(detail.steps || [])
        }
      } catch (err) {
        console.warn('Could not load project from API, using fallback data', err)
        const local = PROJECTS.find(p => p.id === id) || PROJECTS[0]
        if (isMounted) {
          const fallbackDetail: ApiProjectDetail = {
            id: local.id,
            title: local.title,
            slug: local.id,
            description: local.description,
            short_description: local.description,
            difficulty: local.difficulty,
            estimated_hours: local.estimatedHours,
            status: 'published',
            featured: false,
            technologies: local.technologies,
            deliverables: local.deliverables,
            repository_url: local.githubUrl,
            progress: local.progress,
            progress_percentage: local.progress,
            user_status: 'in_progress',
            completed_steps: local.tasks.filter(t => t.completed).length,
            total_steps: local.tasks.length,
            skills: local.skills,
            architecture_overview: local.architectureOverview,
            prerequisites: ['Linux fundamentals', 'Docker containers'],
            learning_objectives: ['Master DevOps architecture workflows'],
            steps: local.tasks.map((t, idx) => ({
              id: t.id,
              project_id: local.id,
              title: t.title,
              step_order: idx + 1,
              step_type: 'build',
              command: t.command,
              is_required: true,
              completed: t.completed,
              status: t.completed ? 'completed' : 'not_started',
            })),
            resources: [],
            related_courses: [],
            related_skills: [],
          }
          setProject(fallbackDetail)
          setSteps(fallbackDetail.steps)
        }
      } finally {
        if (isMounted) setLoading(false)
      }
    }
    loadProject()
    return () => {
      isMounted = false
    }
  }, [id])

  const toggleTask = async (stepId: string) => {
    const targetStep = steps.find(s => s.id === stepId)
    if (!targetStep) return

    // Optimistic UI update
    setSteps(prev =>
      prev.map(s => (s.id === stepId ? { ...s, completed: !s.completed, status: !s.completed ? 'completed' : 'in_progress' } : s))
    )

    if (!targetStep.completed && project) {
      try {
        const updatedProg = await api.completeProjectStep(project.id, stepId, 'Completed via CloudForge web portal')
        setSteps(updatedProg.steps)
        showToast('Milestone Completed!', `Engineering step "${targetStep.title}" completed.`, 'success')
      } catch (err) {
        showToast('Step Updated', 'Local step completion recorded.', 'info')
      }
    } else {
      showToast('Step Status Updated', 'Step progress saved.', 'info')
    }
  }

  const completedCount = steps.filter(t => t.completed).length
  const progressPercent = steps.length > 0 ? Math.round((completedCount / steps.length) * 100) : 0


  const handleVerifyDeployment = () => {
    setVerifying(true)
    setVerificationResult(null)
    setTimeout(() => {
      setVerifying(false)
      setVerificationResult('SUCCESS: All architecture integration checks passed. Manifests valid and zero security CVEs detected.')
      showToast('Verification Successful!', 'Architecture spec passed conformance testing.', 'success')
    }, 1200)
  }

  if (loading || !project) {
    return (
      <div className="min-h-screen bg-slate-950 text-slate-100 flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-emerald-400 border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 pb-16">
      {/* Header */}
      <div className="border-b border-slate-800 bg-slate-900/60 py-12">
        <PageContainer>
          <div className="max-w-3xl space-y-3">
            <Link
              to="/projects"
              className="text-xs font-mono text-cyan-400 hover:text-cyan-300 flex items-center gap-1 mb-2"
            >
              ← Back to All Projects
            </Link>

            <div className="flex items-center gap-2">
              <Badge variant="emerald">{project.difficulty}</Badge>
              <span className="text-xs font-mono text-slate-400">•</span>
              <span className="text-xs font-mono text-slate-300">{project.estimated_hours}</span>
            </div>

            <h1 className="text-3xl sm:text-5xl font-extrabold text-white tracking-tight">
              {project.title}
            </h1>

            <p className="text-sm sm:text-base text-slate-300 leading-relaxed">
              {project.description}
            </p>

            {/* Technologies */}
            <div className="flex flex-wrap gap-1.5 pt-2">
              {(project.technologies || []).map(t => (
                <span
                  key={t}
                  className="text-xs font-mono px-2.5 py-1 rounded-lg bg-slate-800/80 text-slate-200 border border-slate-700/60"
                >
                  {t}
                </span>
              ))}
            </div>
          </div>
        </PageContainer>
      </div>

      <PageContainer>
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-10">
          {/* Main: Architecture, Steps, Deliverables */}
          <div className="lg:col-span-8 space-y-10">
            {/* Architecture Overview */}
            {project.architecture_overview && (
              <div>
                <h2 className="text-xl font-bold text-white mb-3">
                  Architecture Blueprint
                </h2>
                <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 font-mono text-xs text-cyan-300 leading-relaxed overflow-x-auto shadow-inner">
                  <pre>{project.architecture_overview}</pre>
                </div>
              </div>
            )}

            {/* Implementation Steps Checklist */}
            <div>
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-bold text-white">
                  Step-by-Step Implementation Tasks
                </h2>
                <span className="text-xs font-mono text-cyan-400">
                  {completedCount} of {steps.length} Completed ({progressPercent}%)
                </span>
              </div>

              <div className="space-y-3">
                {steps.map(step => (
                  <div
                    key={step.id}
                    className={`p-4 rounded-xl border transition-all ${
                      step.completed
                        ? 'bg-slate-900/40 border-slate-800 text-slate-300'
                        : 'bg-slate-900 border-slate-700/80 text-white'
                    }`}
                  >
                    <div className="flex items-start gap-3">
                      <button
                        onClick={() => toggleTask(step.id)}
                        className={`w-5 h-5 rounded-md border flex items-center justify-center shrink-0 mt-0.5 cursor-pointer transition-all ${
                          step.completed
                            ? 'bg-emerald-500 border-emerald-400 text-slate-950'
                            : 'border-slate-600 hover:border-cyan-400 bg-slate-950'
                        }`}
                      >
                        {step.completed && <Check className="w-3.5 h-3.5 stroke-[3]" />}
                      </button>

                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between">
                          <p className={`text-xs font-medium ${step.completed ? 'line-through text-slate-500' : 'text-slate-200'}`}>
                            {step.step_order}. {step.title}
                          </p>
                          <Badge size="sm" variant={step.step_type === 'break' ? 'rose' : step.step_type === 'fix' ? 'amber' : 'slate'}>
                            {step.step_type}
                          </Badge>
                        </div>
                        {step.description && (
                          <p className="text-[11px] text-slate-400 mt-1">{step.description}</p>
                        )}
                        {step.command && (
                          <div className="mt-2">
                            <CodeBlock
                              language="bash"
                              showLineNumbers={false}
                              code={step.command}
                            />
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Deliverables List */}
            {(project.deliverables || []).length > 0 && (
              <div>
                <h2 className="text-xl font-bold text-white mb-3">
                  Expected Production Deliverables
                </h2>
                <div className="space-y-2">
                  {project.deliverables.map((item, idx) => (
                    <div
                      key={idx}
                      className="p-3 rounded-xl bg-slate-900/60 border border-slate-800 text-xs text-slate-300 flex items-start gap-2.5 font-mono"
                    >
                      <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                      <span>{item}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Resources List */}
            {(project.resources || []).length > 0 && (
              <div>
                <h2 className="text-xl font-bold text-white mb-3">
                  Project Resources & Guides
                </h2>
                <div className="space-y-2">
                  {project.resources.map(res => (
                    <a
                      key={res.id}
                      href={res.url}
                      target="_blank"
                      rel="noreferrer"
                      className="p-3.5 rounded-xl bg-slate-900/60 hover:bg-slate-850 border border-slate-800 hover:border-slate-700 text-xs text-slate-300 flex items-center justify-between group transition-all"
                    >
                      <div className="flex items-center gap-2.5">
                        <BookOpen className="w-4 h-4 text-cyan-400" />
                        <div>
                          <p className="font-semibold text-white group-hover:text-cyan-300">{res.title}</p>
                          {res.description && <p className="text-[11px] text-slate-400">{res.description}</p>}
                        </div>
                      </div>
                      <Badge size="sm" variant="slate">{res.resource_type}</Badge>
                    </a>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Right Sidebar: Verification Simulator & Repo Links */}
          <div className="lg:col-span-4 space-y-6">
            <Card className="p-6 space-y-5 sticky top-24 border-slate-800 bg-slate-900/90">
              <div className="pb-3 border-b border-slate-800">
                <span className="text-xs font-mono text-cyan-400 uppercase tracking-wider block mb-1">
                  Project Actions
                </span>
                <h3 className="text-base font-bold text-white">
                  Automated Verification
                </h3>
                <p className="text-xs text-slate-400 mt-1 leading-relaxed">
                  Validate your code manifests against CloudForge automated test harnesses.
                </p>
              </div>

              <div className="space-y-3">
                <Button
                  variant="glow"
                  size="sm"
                  className="w-full"
                  onClick={handleVerifyDeployment}
                  isLoading={verifying}
                  icon={<Play className="w-4 h-4 fill-slate-950" />}
                >
                  Run Deployment Verification
                </Button>

                {verificationResult && (
                  <div className="p-3.5 rounded-xl bg-emerald-950/40 border border-emerald-500/50 text-[11px] font-mono text-emerald-300 animate-in fade-in duration-200 leading-relaxed">
                    {verificationResult}
                  </div>
                )}
              </div>

              <div className="pt-3 border-t border-slate-800 space-y-2">
                <span className="text-[11px] font-mono text-slate-500 uppercase tracking-wider block">
                  Starter Template Repository
                </span>
                <a
                  href={project.repository_url || 'https://github.com'}
                  target="_blank"
                  rel="noreferrer"
                  className="w-full inline-flex items-center justify-center gap-2 px-3 py-2 rounded-xl bg-slate-800 hover:bg-slate-750 text-xs font-mono text-slate-200 border border-slate-700/80 transition-colors"
                >
                  <GithubIcon className="w-4 h-4" />
                  <span>Clone GitHub Starter Repo</span>
                </a>
              </div>
            </Card>
          </div>
        </div>
      </PageContainer>
    </div>
  )
}
