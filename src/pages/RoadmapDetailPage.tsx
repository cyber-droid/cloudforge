import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import {
  CheckCircle2,
  Clock,
  ArrowRight,
  Loader2,
  PlayCircle,
} from 'lucide-react'
import { ROADMAPS } from '../data/roadmapsData'
import { PageContainer } from '../components/layout/PageContainer'
import { Card } from '../components/common/Card'
import { Badge } from '../components/common/Badge'
import { Button } from '../components/common/Button'
import { api, type ApiRoadmapDetail } from '../services/api'

export function RoadmapDetailPage() {
  const { id } = useParams<{ id: string }>()
  const [roadmap, setRoadmap] = useState<ApiRoadmapDetail | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [activeNodeIndex, setActiveNodeIndex] = useState<number>(0)
  const [isStarting, setIsStarting] = useState(false)

  useEffect(() => {
    async function loadRoadmap() {
      if (!id) return
      try {
        const res = await api.getRoadmap(id)
        if (res) {
          setRoadmap(res)
          // Find first in-progress or upcoming node
          const inProgressIdx = res.nodes?.findIndex(n => n.status === 'in-progress' || !n.completed)
          if (inProgressIdx !== undefined && inProgressIdx >= 0) {
            setActiveNodeIndex(inProgressIdx)
          }
        }
      } catch (err) {
        console.warn('Could not load live roadmap detail, falling back to mock:', err)
        const fallback = ROADMAPS.find(r => r.id === id || r.slug === id) || ROADMAPS[1]
        setRoadmap({
          id: fallback.id,
          slug: fallback.slug,
          title: fallback.title,
          category: fallback.category,
          difficulty: 'Intermediate',
          duration_label: fallback.duration,
          skills_count: fallback.skillsCount,
          projects_count: fallback.projectsCount,
          description: fallback.description,
          certifications_targeted: fallback.certificationsTargeted,
          step_count: fallback.nodes.length,
          progress_percentage: fallback.progress,
          nodes: fallback.nodes.map((n, idx) => ({
            id: n.id,
            title: n.title,
            description: n.description,
            step_type: 'course',
            order_index: idx,
            required: true,
            estimated_hours: n.estimatedHours,
            skills_covered: n.skills,
            status: n.status,
            completed: n.status === 'completed',
          })),
        })
      } finally {
        setIsLoading(false)
      }
    }
    loadRoadmap()
  }, [id])

  const handleStartRoadmap = async () => {
    if (!roadmap) return
    try {
      setIsStarting(true)
      const res = await api.startRoadmap(roadmap.slug || roadmap.id)
      if (res?.roadmap) {
        setRoadmap(res.roadmap)
      }
    } catch (err) {
      console.error('Failed to start roadmap:', err)
    } finally {
      setIsStarting(false)
    }
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-slate-950 text-slate-100 flex items-center justify-center">
        <div className="flex items-center gap-3 text-slate-400 font-mono text-sm">
          <Loader2 className="w-6 h-6 animate-spin text-purple-400" />
          <span>Loading roadmap architecture pipeline...</span>
        </div>
      </div>
    )
  }

  if (!roadmap) {
    return (
      <div className="min-h-screen bg-slate-950 text-slate-100 py-16">
        <PageContainer>
          <div className="text-center py-16 space-y-4">
            <h2 className="text-2xl font-bold text-white">Roadmap Not Found</h2>
            <Link to="/roadmaps">
              <Button variant="secondary">Back to All Roadmaps</Button>
            </Link>
          </div>
        </PageContainer>
      </div>
    )
  }

  const activeNode = roadmap.nodes?.[activeNodeIndex] || roadmap.nodes?.[0]

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 pb-16">
      {/* Header */}
      <div className="border-b border-slate-800 bg-slate-900/60 py-12">
        <PageContainer>
          <div className="max-w-3xl space-y-3">
            <Link
              to="/roadmaps"
              className="text-xs font-mono text-cyan-400 hover:text-cyan-300 flex items-center gap-1 mb-2"
            >
              ← Back to All Roadmaps
            </Link>
            <div className="flex items-center gap-2">
              <Badge variant="purple">{roadmap.category}</Badge>
              <span className="text-xs font-mono text-slate-400">•</span>
              <span className="text-xs font-mono text-slate-300">{roadmap.duration_label || '6 months'}</span>
              <span className="text-xs font-mono text-slate-400">•</span>
              <span className="text-xs font-mono text-purple-400 font-bold">
                {Math.round(roadmap.progress_percentage || 0)}% Complete
              </span>
            </div>
            <h1 className="text-3xl sm:text-5xl font-extrabold text-white tracking-tight">
              {roadmap.title}
            </h1>
            <p className="text-sm sm:text-base text-slate-300 leading-relaxed">
              {roadmap.description}
            </p>

            {/* Targeted certs & Start button */}
            <div className="pt-2 flex flex-wrap items-center justify-between gap-4">
              <div className="flex flex-wrap items-center gap-2">
                <span className="text-xs font-mono text-slate-400">Target Certifications:</span>
                {roadmap.certifications_targeted?.map(cert => (
                  <span
                    key={cert}
                    className="text-xs font-mono px-2 py-0.5 rounded bg-amber-950/60 text-amber-300 border border-amber-800/40"
                  >
                    🏆 {cert}
                  </span>
                ))}
              </div>

              <div>
                <Button
                  variant="primary"
                  size="sm"
                  onClick={handleStartRoadmap}
                  disabled={isStarting}
                  iconRight={isStarting ? <Loader2 className="w-4 h-4 animate-spin" /> : <PlayCircle className="w-4 h-4" />}
                >
                  {roadmap.status === 'in_progress' ? 'Roadmap In Progress' : 'Start Career Pathway'}
                </Button>
              </div>
            </div>
          </div>
        </PageContainer>
      </div>

      <PageContainer>
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-10">
          {/* Visual Vertical Pipeline Flow */}
          <div className="lg:col-span-7 space-y-4">
            <h2 className="text-lg font-bold text-white font-mono uppercase tracking-wider mb-4">
              Architecture Progression Pipeline
            </h2>

            <div className="relative pl-6 space-y-6 before:absolute before:left-2.5 before:top-3 before:bottom-3 before:w-0.5 before:bg-slate-800">
              {roadmap.nodes?.map((node, index) => {
                const isSelected = activeNodeIndex === index
                const isCompleted = node.completed || node.status === 'completed'
                const isInProgress = node.status === 'in-progress' || node.status === 'in_progress'

                return (
                  <div
                    key={node.id}
                    onClick={() => setActiveNodeIndex(index)}
                    className={`relative p-5 rounded-2xl border transition-all cursor-pointer ${
                      isSelected
                        ? 'bg-slate-900 border-cyan-400 shadow-xl shadow-cyan-950/20 ring-1 ring-cyan-500/20'
                        : 'bg-slate-900/40 border-slate-800 hover:border-slate-700 hover:bg-slate-900/60'
                    }`}
                  >
                    {/* Circle Node Marker on Timeline */}
                    <div
                      className={`absolute -left-[27px] top-6 w-4 h-4 rounded-full border-2 flex items-center justify-center ${
                        isCompleted
                          ? 'bg-emerald-500 border-emerald-400'
                          : isInProgress
                          ? 'bg-cyan-500 border-cyan-300 animate-pulse'
                          : 'bg-slate-900 border-slate-700'
                      }`}
                    />

                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-mono font-bold text-slate-400">
                          Step {index + 1}
                        </span>
                        <span className="text-slate-600">•</span>
                        <span
                          className={`text-xs font-mono uppercase font-semibold ${
                            isCompleted
                              ? 'text-emerald-400'
                              : isInProgress
                              ? 'text-cyan-400'
                              : 'text-slate-500'
                          }`}
                        >
                          {node.step_type} ({node.status || (isCompleted ? 'completed' : 'upcoming')})
                        </span>
                      </div>
                      <span className="text-xs font-mono text-slate-500">{node.estimated_hours || '25h'}</span>
                    </div>

                    <h3 className="text-base font-bold text-white mb-1">
                      {node.title}
                    </h3>
                    <p className="text-xs text-slate-400 leading-relaxed">
                      {node.description}
                    </p>

                    <div className="flex flex-wrap gap-1.5 mt-3">
                      {node.skills_covered?.map(s => (
                        <span
                          key={s}
                          className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700/60"
                        >
                          {s}
                        </span>
                      ))}
                    </div>
                  </div>
                )
              })}
            </div>
          </div>

          {/* Active Node Detail Inspector Sidebar */}
          {activeNode && (
            <div className="lg:col-span-5 space-y-6">
              <Card className="p-6 sticky top-24 border-slate-800 space-y-5 bg-slate-900/90">
                <div className="pb-4 border-b border-slate-800">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-xs font-mono text-cyan-400 uppercase tracking-wider block">
                      Milestone Inspector
                    </span>
                    <Badge variant={activeNode.completed ? 'emerald' : 'default'}>
                      {activeNode.step_type.toUpperCase()}
                    </Badge>
                  </div>
                  <h3 className="text-xl font-bold text-white">
                    {activeNode.title}
                  </h3>
                  <p className="text-xs text-slate-400 mt-1 leading-relaxed">
                    {activeNode.description}
                  </p>
                </div>

                <div className="space-y-3 text-xs font-mono">
                  <div className="flex justify-between py-1.5 border-b border-slate-800/80">
                    <span className="text-slate-400">Estimated Commitment:</span>
                    <span className="text-slate-200">{activeNode.estimated_hours || '25h'}</span>
                  </div>
                  <div className="flex justify-between py-1.5 border-b border-slate-800/80">
                    <span className="text-slate-400">Current Status:</span>
                    <span className={`uppercase font-semibold ${activeNode.completed ? 'text-emerald-400' : 'text-cyan-400'}`}>
                      {activeNode.status || (activeNode.completed ? 'completed' : 'upcoming')}
                    </span>
                  </div>
                  <div className="space-y-1.5 pt-1">
                    <span className="text-slate-400">Core Competencies:</span>
                    <div className="flex flex-wrap gap-1.5">
                      {activeNode.skills_covered?.map(s => (
                        <span key={s} className="px-2 py-0.5 rounded bg-slate-800 text-slate-200">
                          {s}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>

                <div className="pt-3 space-y-3">
                  {activeNode.linked_course ? (
                    <Link to={`/courses/${activeNode.linked_course.slug || activeNode.linked_course.id}`}>
                      <Button variant="glow" size="sm" className="w-full" iconRight={<ArrowRight className="w-4 h-4" />}>
                        Go to Course: {activeNode.linked_course.title}
                      </Button>
                    </Link>
                  ) : activeNode.linked_skill ? (
                    <Link to="/skills">
                      <Button variant="glow" size="sm" className="w-full" iconRight={<ArrowRight className="w-4 h-4" />}>
                        View Skill: {activeNode.linked_skill.name}
                      </Button>
                    </Link>
                  ) : (
                    <Link to="/courses">
                      <Button variant="glow" size="sm" className="w-full" iconRight={<ArrowRight className="w-4 h-4" />}>
                        Explore Course Catalog
                      </Button>
                    </Link>
                  )}
                </div>
              </Card>
            </div>
          )}
        </div>
      </PageContainer>
    </div>
  )
}

