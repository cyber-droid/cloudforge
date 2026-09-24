import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { FolderGit2, ArrowRight, Clock } from 'lucide-react'
import { PROJECTS } from '../data/projectsData'
import { PageContainer } from '../components/layout/PageContainer'
import { Card } from '../components/common/Card'
import { Badge } from '../components/common/Badge'
import { Tabs } from '../components/common/Tabs'
import { Button } from '../components/common/Button'
import { api, type ApiProjectSummary } from '../services/api'

export function ProjectsPage() {
  const [selectedDifficulty, setSelectedDifficulty] = useState<string>('All')
  const [projects, setProjects] = useState<ApiProjectSummary[]>([])
  const [loading, setLoading] = useState<boolean>(true)

  const difficulties = [
    { id: 'All', label: 'All Projects' },
    { id: 'Beginner', label: 'Beginner' },
    { id: 'Intermediate', label: 'Intermediate' },
    { id: 'Advanced', label: 'Advanced' },
  ]

  useEffect(() => {
    let isMounted = true
    async function fetchProjects() {
      setLoading(true)
      try {
        const res = await api.getProjects({
          difficulty: selectedDifficulty !== 'All' ? selectedDifficulty : undefined,
          page_size: 50,
        })
        if (isMounted) {
          setProjects(res.items)
        }
      } catch (err) {
        console.warn('Backend projects API unreachable, falling back to local dataset', err)
        if (isMounted) {
          const fallback = selectedDifficulty === 'All'
            ? PROJECTS
            : PROJECTS.filter(p => p.difficulty.toLowerCase() === selectedDifficulty.toLowerCase())
          setProjects(
            fallback.map(p => ({
              id: p.id,
              title: p.title,
              slug: p.id,
              short_description: p.description,
              description: p.description,
              difficulty: p.difficulty,
              estimated_hours: p.estimatedHours,
              status: 'published',
              featured: false,
              technologies: p.technologies,
              deliverables: p.deliverables,
              progress: p.progress,
              progress_percentage: p.progress,
              user_status: p.progress > 0 ? 'in_progress' : 'not_started',
              completed_steps: Math.round((p.progress / 100) * p.tasks.length),
              total_steps: p.tasks.length,
              skills: p.skills,
            }))
          )
        }
      } finally {
        if (isMounted) setLoading(false)
      }
    }
    fetchProjects()
    return () => {
      isMounted = false
    }
  }, [selectedDifficulty])


  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 pb-16">
      {/* Header */}
      <div className="border-b border-slate-800 bg-slate-950/80 py-12">
        <PageContainer>
          <div className="max-w-3xl space-y-3">
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-950/60 border border-emerald-800/50 text-emerald-300 text-xs font-mono">
              <FolderGit2 className="w-3.5 h-3.5" />
              <span>HANDS-ON PRODUCTION CAPSTONES</span>
            </div>
            <h1 className="text-3xl sm:text-5xl font-extrabold text-white tracking-tight">
              Build what you learn.
            </h1>
            <p className="text-sm sm:text-base text-slate-300 leading-relaxed">
              Ship production-grade cloud architectures. Real GitHub repositories, multi-stage Docker builds, Kubernetes manifests, and declarative Terraform code.
            </p>
          </div>
        </PageContainer>
      </div>

      <PageContainer>
        {/* Difficulty Filter Tabs */}
        <div className="mb-8">
          <Tabs
            tabs={difficulties}
            activeTab={selectedDifficulty}
            onChange={setSelectedDifficulty}
            variant="pills"
          />
        </div>

        {/* Projects Grid */}
        {loading ? (
          <div className="flex items-center justify-center py-20">
            <div className="w-8 h-8 border-2 border-emerald-400 border-t-transparent rounded-full animate-spin" />
          </div>
        ) : projects.length === 0 ? (
          <div className="text-center py-16 bg-slate-900/40 rounded-xl border border-slate-800">
            <FolderGit2 className="w-12 h-12 text-slate-600 mx-auto mb-3" />
            <p className="text-slate-400 text-sm">No engineering projects found matching the selected filter.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {projects.map(project => (
              <Card
                key={project.id}
                className="p-6 flex flex-col justify-between hover:border-emerald-500/40 transition-all group"
              >
                <div>
                  <div className="flex items-center justify-between mb-3">
                    <Badge
                      variant={
                        project.difficulty.toLowerCase() === 'advanced'
                          ? 'rose'
                          : project.difficulty.toLowerCase() === 'intermediate'
                          ? 'amber'
                          : 'emerald'
                      }
                    >
                      {project.difficulty}
                    </Badge>
                    <span className="text-xs font-mono text-slate-400 flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      {project.estimated_hours}
                    </span>
                  </div>

                  <Link to={`/projects/${project.slug || project.id}`}>
                    <h3 className="text-lg font-bold text-white group-hover:text-emerald-300 transition-colors leading-snug">
                      {project.title}
                    </h3>
                  </Link>

                  <p className="text-xs text-slate-400 mt-2 leading-relaxed line-clamp-3">
                    {project.short_description || project.description}
                  </p>

                  {/* Technologies */}
                  <div className="flex flex-wrap gap-1.5 mt-4">
                    {(project.technologies || []).slice(0, 4).map(t => (
                      <span
                        key={t}
                        className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800/80 text-slate-300 border border-slate-700/60"
                      >
                        {t}
                      </span>
                    ))}
                  </div>

                  {/* Progress bar if active */}
                  {project.progress > 0 && (
                    <div className="mt-4 pt-3 border-t border-slate-800/80 space-y-1.5">
                      <div className="flex justify-between text-xs font-mono">
                        <span className="text-slate-400">Implementation Progress</span>
                        <span className="text-emerald-400 font-bold">{project.progress}%</span>
                      </div>
                      <div className="w-full h-1.5 rounded-full bg-slate-800 overflow-hidden">
                        <div
                          className="h-full bg-emerald-400 rounded-full"
                          style={{ width: `${project.progress}%` }}
                        />
                      </div>
                    </div>
                  )}
                </div>

                <div className="mt-6 pt-4 border-t border-slate-800 flex items-center justify-between">
                  <span className="text-xs font-mono text-slate-500">
                    {project.total_steps || 0} Architecture Steps
                  </span>
                  <Link to={`/projects/${project.slug || project.id}`}>
                    <Button variant="outline" size="xs" iconRight={<ArrowRight className="w-3 h-3" />}>
                      View Specs
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
