import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { GitFork, ArrowRight, Clock, CheckCircle2, Loader2 } from 'lucide-react'
import { ROADMAPS } from '../data/roadmapsData'
import { PageContainer } from '../components/layout/PageContainer'
import { Card } from '../components/common/Card'
import { Badge } from '../components/common/Badge'
import { Button } from '../components/common/Button'
import { api, type ApiRoadmapSummary } from '../services/api'

export function RoadmapsPage() {
  const [roadmaps, setRoadmaps] = useState<ApiRoadmapSummary[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    async function loadRoadmaps() {
      try {
        const res = await api.getRoadmaps()
        if (res?.items && res.items.length > 0) {
          setRoadmaps(res.items)
        } else {
          // Fallback to initial seed data if empty
          setRoadmaps(
            ROADMAPS.map(r => ({
              id: r.id,
              slug: r.slug,
              title: r.title,
              description: r.description,
              category: r.category,
              difficulty: 'Intermediate',
              duration_label: r.duration,
              skills_count: r.skillsCount,
              projects_count: r.projectsCount,
              certifications_targeted: r.certificationsTargeted,
              step_count: r.nodes.length,
              nodes: r.nodes.map((n, idx) => ({
                id: n.id,
                title: n.title,
                description: n.description,
                step_type: 'course',
                order_index: idx,
                required: true,
                skills_covered: n.skills,
                status: n.status,
              })),
              progress_percentage: r.progress,
            }))
          )
        }
      } catch (err) {
        console.warn('Could not load live roadmaps from API, using fallback data:', err)
        setRoadmaps(
          ROADMAPS.map(r => ({
            id: r.id,
            slug: r.slug,
            title: r.title,
            description: r.description,
            category: r.category,
            difficulty: 'Intermediate',
            duration_label: r.duration,
            skills_count: r.skillsCount,
            projects_count: r.projectsCount,
            certifications_targeted: r.certificationsTargeted,
            step_count: r.nodes.length,
            nodes: r.nodes.map((n, idx) => ({
              id: n.id,
              title: n.title,
              description: n.description,
              step_type: 'course',
              order_index: idx,
              required: true,
              skills_covered: n.skills,
              status: n.status,
            })),
            progress_percentage: r.progress,
          }))
        )
      } finally {
        setIsLoading(false)
      }
    }
    loadRoadmaps()
  }, [])

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 pb-16">
      {/* Header */}
      <div className="border-b border-slate-800 bg-slate-950/80 py-12">
        <PageContainer>
          <div className="max-w-3xl">
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-purple-950/60 border border-purple-800/50 text-purple-300 text-xs font-mono mb-3">
              <GitFork className="w-3.5 h-3.5" />
              <span>STRUCTURED CAREER PATHWAYS</span>
            </div>
            <h1 className="text-3xl sm:text-5xl font-extrabold text-white tracking-tight">
              Choose your engineering path.
            </h1>
            <p className="text-sm sm:text-base text-slate-300 mt-3 leading-relaxed">
              Step-by-step technical roadmaps connecting Linux internals, Kubernetes orchestration, infrastructure as code, and AI operations into a coherent career progression.
            </p>
          </div>
        </PageContainer>
      </div>

      <PageContainer>
        {isLoading ? (
          <div className="flex items-center justify-center py-24 gap-3 text-slate-400 font-mono text-sm">
            <Loader2 className="w-6 h-6 animate-spin text-purple-400" />
            <span>Loading career roadmaps...</span>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {roadmaps.map(roadmap => (
              <Card
                key={roadmap.id}
                className="p-8 flex flex-col justify-between hover:border-purple-500/40 transition-all group"
              >
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <Badge variant="purple">{roadmap.category}</Badge>
                    <span className="text-xs font-mono text-slate-400 flex items-center gap-1">
                      <Clock className="w-3.5 h-3.5" />
                      {roadmap.duration_label || '4-6 months'}
                    </span>
                  </div>

                  <Link to={`/roadmaps/${roadmap.slug || roadmap.id}`}>
                    <h2 className="text-2xl font-bold text-white group-hover:text-purple-300 transition-colors">
                      {roadmap.title}
                    </h2>
                  </Link>

                  <p className="text-xs sm:text-sm text-slate-400 mt-2 leading-relaxed">
                    {roadmap.description}
                  </p>

                  {/* Progress bar if active */}
                  <div className="mt-6 p-4 rounded-xl bg-slate-950/60 border border-slate-800/80 space-y-2">
                    <div className="flex justify-between text-xs font-mono">
                      <span className="text-slate-400">Path Progression</span>
                      <span className="text-purple-400 font-bold">{Math.round(roadmap.progress_percentage || 0)}%</span>
                    </div>
                    <div className="w-full h-2 rounded-full bg-slate-800 overflow-hidden">
                      <div
                        className="h-full rounded-full bg-gradient-to-r from-purple-500 to-cyan-500 transition-all duration-500"
                        style={{ width: `${roadmap.progress_percentage || 0}%` }}
                      />
                    </div>
                  </div>

                  {/* Milestones Preview List */}
                  <div className="mt-6 space-y-2">
                    <span className="text-[11px] font-mono text-slate-500 uppercase tracking-wider block">
                      Curriculum Milestones ({roadmap.nodes?.length || roadmap.step_count || 0} Stages)
                    </span>
                    <div className="flex flex-wrap gap-2">
                      {roadmap.nodes?.map((node, i) => (
                        <span
                          key={node.id}
                          className={`text-xs font-mono px-2.5 py-1 rounded-lg border flex items-center gap-1.5 ${
                            node.status === 'completed'
                              ? 'bg-slate-900 border-emerald-500/40 text-emerald-300'
                              : node.status === 'in-progress'
                              ? 'bg-slate-900 border-cyan-500/40 text-cyan-300 font-semibold'
                              : 'bg-slate-950 border-slate-800 text-slate-400'
                          }`}
                        >
                          {node.status === 'completed' && (
                            <CheckCircle2 className="w-3 h-3 text-emerald-400" />
                          )}
                          <span>
                            {i + 1}. {node.title}
                          </span>
                        </span>
                      ))}
                    </div>
                  </div>
                </div>

                {/* Bottom Card Footer */}
                <div className="mt-8 pt-6 border-t border-slate-800 flex items-center justify-between">
                  <div className="flex items-center gap-4 text-xs font-mono text-slate-400">
                    <span>{roadmap.skills_count || 12} Skills</span>
                    <span>•</span>
                    <span>{roadmap.projects_count || 3} Projects</span>
                  </div>
                  <Link to={`/roadmaps/${roadmap.slug || roadmap.id}`}>
                    <Button variant="primary" size="sm" iconRight={<ArrowRight className="w-4 h-4" />}>
                      Explore Roadmap
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

