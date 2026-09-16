import { useState, useMemo, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Cpu, BookOpen, FolderGit2, Loader2, RefreshCw } from 'lucide-react'
import { SKILLS } from '../data/skillsData'
import { PageContainer } from '../components/layout/PageContainer'
import { Card } from '../components/common/Card'
import { Tabs } from '../components/common/Tabs'
import { Button } from '../components/common/Button'
import { api, type ApiUserSkill } from '../services/api'

export function SkillsPage() {
  const [selectedCategory, setSelectedCategory] = useState<string>('All')
  const [skills, setSkills] = useState<ApiUserSkill[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [isRecalculating, setIsRecalculating] = useState<string | null>(null)

  const categories = [
    { id: 'All', label: 'All Domains' },
    { id: 'Cloud', label: 'Cloud' },
    { id: 'DevOps', label: 'DevOps' },
    { id: 'DevSecOps', label: 'DevSecOps' },
    { id: 'Kubernetes', label: 'Kubernetes' },
    { id: 'Observability', label: 'Observability' },
    { id: 'AI', label: 'AI Ops' },
  ]

  const loadSkillsData = async () => {
    try {
      // Try fetching authenticated user skills matrix first
      const matrix = await api.getMySkills()
      if (matrix?.skills && matrix.skills.length > 0) {
        setSkills(matrix.skills)
        return
      }
    } catch {
      // If unauthorized or error, fallback to public skills catalog
      try {
        const publicSkills = await api.getSkills()
        if (publicSkills && publicSkills.length > 0) {
          setSkills(
            publicSkills.map(s => ({
              id: s.id,
              skill_id: s.id,
              slug: s.slug,
              name: s.name,
              description: s.description,
              category: s.category,
              current_level: 1,
              current_level_name: 'Beginner',
              target_level: s.target_level,
              target_level_name: s.target_level_name,
              proficiency_percentage: 0,
              trend: s.trend || '+5%',
              related_courses: s.related_courses,
            }))
          )
          return
        }
      } catch (err) {
        console.warn('Could not load skills from API, using fallback data:', err)
      }
    }

    // Final fallback to mock data
    setSkills(
      SKILLS.map(s => ({
        id: s.id,
        skill_id: s.id,
        slug: s.id,
        name: s.name,
        category: s.category,
        current_level: 2,
        current_level_name: s.levelLabel,
        target_level: 4,
        target_level_name: s.targetLevel,
        proficiency_percentage: s.proficiency,
        trend: s.trend,
        related_courses: s.relatedCourses.map(c => ({ id: c.id, title: c.title, slug: c.id })),
      }))
    )
  }

  useEffect(() => {
    async function init() {
      setIsLoading(true)
      await loadSkillsData()
      setIsLoading(false)
    }
    init()
  }, [])

  const handleRecalculate = async (skillSlug: string) => {
    try {
      setIsRecalculating(skillSlug)
      await api.recalculateMySkill(skillSlug)
      await loadSkillsData()
    } catch (err) {
      console.error('Recalculate failed:', err)
    } finally {
      setIsRecalculating(null)
    }
  }

  const filteredSkills = useMemo(() => {
    if (selectedCategory === 'All') return skills
    return skills.filter(s => s.category.toLowerCase() === selectedCategory.toLowerCase())
  }, [selectedCategory, skills])

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 pb-16">
      {/* Header */}
      <div className="border-b border-slate-800 bg-slate-950/80 py-12">
        <PageContainer>
          <div className="max-w-3xl">
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-blue-950/60 border border-blue-800/50 text-blue-300 text-xs font-mono mb-3">
              <Cpu className="w-3.5 h-3.5" />
              <span>COMPETENCY EVALUATION MATRIX</span>
            </div>
            <h1 className="text-3xl sm:text-5xl font-extrabold text-white tracking-tight">
              Technical Skill Matrix
            </h1>
            <p className="text-sm sm:text-base text-slate-300 mt-2 leading-relaxed">
              Track your hands-on proficiency across cloud architectures, container orchestration, GitOps automation, and security baselines.
            </p>
          </div>
        </PageContainer>
      </div>

      <PageContainer>
        {/* Category Tabs */}
        <div className="mb-8">
          <Tabs
            tabs={categories}
            activeTab={selectedCategory}
            onChange={setSelectedCategory}
            variant="pills"
          />
        </div>

        {isLoading ? (
          <div className="flex items-center justify-center py-24 gap-3 text-slate-400 font-mono text-sm">
            <Loader2 className="w-6 h-6 animate-spin text-cyan-400" />
            <span>Calculating technical skill matrix...</span>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {filteredSkills.map(skill => (
              <Card key={skill.id} className="p-6 space-y-5 hover:border-cyan-500/40 transition-all">
                <div className="flex items-start justify-between">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-mono uppercase tracking-wider text-slate-400">
                        {skill.category}
                      </span>
                      <span className="text-slate-600">•</span>
                      <span className="text-xs font-mono text-emerald-400 font-semibold">
                        {skill.trend || '+5%'} this month
                      </span>
                    </div>
                    <h3 className="text-xl font-bold text-white mt-1">{skill.name}</h3>
                  </div>

                  <div className="text-right font-mono">
                    <span className="text-2xl font-extrabold text-cyan-400">
                      {Math.round(skill.proficiency_percentage)}%
                    </span>
                    <div className="text-[11px] text-slate-400">Level: {skill.current_level_name}</div>
                  </div>
                </div>

                {/* Progress Bar & Target Comparison */}
                <div className="space-y-1.5">
                  <div className="flex justify-between text-xs font-mono text-slate-400">
                    <span>Current: {skill.current_level_name} ({Math.round(skill.proficiency_percentage)}%)</span>
                    <span>Target: {skill.target_level_name}</span>
                  </div>
                  <div className="w-full h-2.5 rounded-full bg-slate-800 overflow-hidden border border-slate-700/60">
                    <div
                      className="h-full rounded-full bg-gradient-to-r from-cyan-500 via-blue-500 to-indigo-500 transition-all duration-500"
                      style={{ width: `${skill.proficiency_percentage}%` }}
                    />
                  </div>
                </div>

                {/* Connected Courses & Projects */}
                <div className="pt-3 border-t border-slate-800 grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
                  <div>
                    <span className="text-[11px] font-mono text-slate-500 uppercase tracking-wider block mb-1.5 flex items-center gap-1">
                      <BookOpen className="w-3 h-3 text-cyan-400" />
                      <span>Associated Courses</span>
                    </span>
                    {skill.related_courses && skill.related_courses.length > 0 ? (
                      <ul className="space-y-1">
                        {skill.related_courses.map(c => (
                          <li key={c.id}>
                            <Link
                              to={`/courses/${c.slug || c.id}`}
                              className="text-slate-300 hover:text-cyan-300 transition-colors truncate block"
                            >
                              → {c.title}
                            </Link>
                          </li>
                        ))}
                      </ul>
                    ) : (
                      <span className="text-slate-500 italic">No courses mapped yet</span>
                    )}
                  </div>

                  <div>
                    <span className="text-[11px] font-mono text-slate-500 uppercase tracking-wider block mb-1.5 flex items-center gap-1">
                      <FolderGit2 className="w-3 h-3 text-purple-400" />
                      <span>Applied Knowledge</span>
                    </span>
                    <div className="pt-1">
                      <Button
                        variant="ghost"
                        size="sm"
                        className="text-xs font-mono text-slate-400 hover:text-cyan-300 px-0"
                        onClick={() => handleRecalculate(skill.slug)}
                        disabled={isRecalculating === skill.slug}
                      >
                        {isRecalculating === skill.slug ? (
                          <Loader2 className="w-3 h-3 animate-spin mr-1" />
                        ) : (
                          <RefreshCw className="w-3 h-3 mr-1" />
                        )}
                        <span>Sync Evidence</span>
                      </Button>
                    </div>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        )}
      </PageContainer>
    </div>
  )
}

