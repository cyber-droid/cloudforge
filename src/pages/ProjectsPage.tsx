import { useState, useMemo } from 'react'
import { Link } from 'react-router-dom'
import { FolderGit2, ArrowRight, Clock } from 'lucide-react'
import { PROJECTS } from '../data/projectsData'
import { PageContainer } from '../components/layout/PageContainer'
import { Card } from '../components/common/Card'
import { Badge } from '../components/common/Badge'
import { Tabs } from '../components/common/Tabs'
import { Button } from '../components/common/Button'

export function ProjectsPage() {
  const [selectedDifficulty, setSelectedDifficulty] = useState<string>('All')

  const difficulties = [
    { id: 'All', label: 'All Projects' },
    { id: 'Beginner', label: 'Beginner' },
    { id: 'Intermediate', label: 'Intermediate' },
    { id: 'Advanced', label: 'Advanced' },
  ]

  const filteredProjects = useMemo(() => {
    if (selectedDifficulty === 'All') return PROJECTS
    return PROJECTS.filter(p => p.difficulty === selectedDifficulty)
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
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredProjects.map(project => (
            <Card
              key={project.id}
              className="p-6 flex flex-col justify-between hover:border-emerald-500/40 transition-all group"
            >
              <div>
                <div className="flex items-center justify-between mb-3">
                  <Badge
                    variant={
                      project.difficulty === 'Advanced'
                        ? 'rose'
                        : project.difficulty === 'Intermediate'
                        ? 'amber'
                        : 'emerald'
                    }
                  >
                    {project.difficulty}
                  </Badge>
                  <span className="text-xs font-mono text-slate-400 flex items-center gap-1">
                    <Clock className="w-3 h-3" />
                    {project.estimatedHours}
                  </span>
                </div>

                <Link to={`/projects/${project.id}`}>
                  <h3 className="text-lg font-bold text-white group-hover:text-emerald-300 transition-colors leading-snug">
                    {project.title}
                  </h3>
                </Link>

                <p className="text-xs text-slate-400 mt-2 leading-relaxed line-clamp-3">
                  {project.description}
                </p>

                {/* Technologies */}
                <div className="flex flex-wrap gap-1.5 mt-4">
                  {project.technologies.slice(0, 4).map(t => (
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
                  {project.tasks.length} Architecture Steps
                </span>
                <Link to={`/projects/${project.id}`}>
                  <Button variant="outline" size="xs" iconRight={<ArrowRight className="w-3 h-3" />}>
                    View Specs
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
