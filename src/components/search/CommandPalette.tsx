import { useEffect, useState, useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Search,
  BookOpen,
  Award,
  AlertTriangle,
  FolderGit2,
  GitFork,
  Cpu,
  Layers,
  Sparkles,
  ArrowRight,
  X,
} from 'lucide-react'
import { COURSES } from '../../data/coursesData'
import { CERTIFICATIONS } from '../../data/certificationsData'
import { ROADMAPS } from '../../data/roadmapsData'
import { PROJECTS } from '../../data/projectsData'
import { INCIDENTS } from '../../data/incidentsData'
import { SKILLS } from '../../data/skillsData'

interface CommandPaletteProps {
  isOpen: boolean
  onClose: () => void
}

interface SearchItem {
  id: string
  title: string
  subtitle: string
  category: 'Course' | 'Certification' | 'Roadmap' | 'Project' | 'Incident' | 'Skill' | 'AI'
  url: string
  icon: React.ReactNode
}

export function CommandPalette({ isOpen, onClose }: CommandPaletteProps) {
  const [query, setQuery] = useState('')
  const navigate = useNavigate()

  // Collect all searchable records
  const allItems: SearchItem[] = useMemo(() => {
    const items: SearchItem[] = []

    COURSES.forEach(c => {
      items.push({
        id: `course-${c.id}`,
        title: c.title,
        subtitle: `${c.category} • ${c.level} • ${c.duration}`,
        category: 'Course',
        url: `/courses/${c.id}`,
        icon: <BookOpen className="w-4 h-4 text-cyan-400" />,
      })
    })

    CERTIFICATIONS.forEach(cert => {
      items.push({
        id: `cert-${cert.id}`,
        title: `${cert.title} (${cert.code || 'Prep'})`,
        subtitle: `CloudForge Training Prep • ${cert.provider}`,
        category: 'Certification',
        url: `/certifications/${cert.id}`,
        icon: <Award className="w-4 h-4 text-amber-400" />,
      })
    })

    ROADMAPS.forEach(r => {
      items.push({
        id: `roadmap-${r.id}`,
        title: r.title,
        subtitle: `${r.duration} • ${r.skillsCount} skills • ${r.projectsCount} projects`,
        category: 'Roadmap',
        url: `/roadmaps/${r.id}`,
        icon: <GitFork className="w-4 h-4 text-purple-400" />,
      })
    })

    PROJECTS.forEach(p => {
      items.push({
        id: `project-${p.id}`,
        title: p.title,
        subtitle: `${p.difficulty} • ${p.technologies.slice(0, 3).join(', ')}`,
        category: 'Project',
        url: `/projects/${p.id}`,
        icon: <FolderGit2 className="w-4 h-4 text-emerald-400" />,
      })
    })

    INCIDENTS.forEach(inc => {
      items.push({
        id: `incident-${inc.id}`,
        title: `${inc.incidentId}: ${inc.title}`,
        subtitle: `${inc.severity} • ${inc.technology} • ${inc.status}`,
        category: 'Incident',
        url: `/troubleshooting/${inc.id}`,
        icon: <AlertTriangle className="w-4 h-4 text-rose-400" />,
      })
    })

    SKILLS.forEach(s => {
      items.push({
        id: `skill-${s.id}`,
        title: `${s.name} (${s.proficiency}%)`,
        subtitle: `${s.category} Matrix • Target: ${s.targetLevel}`,
        category: 'Skill',
        url: `/skills`,
        icon: <Cpu className="w-4 h-4 text-blue-400" />,
      })
    })

    // AI Tools
    items.push({
      id: 'ai-cicd-analyzer',
      title: 'AI CI/CD Failure Analyzer',
      subtitle: 'Analyze build logs and generate pull-request patches',
      category: 'AI',
      url: '/ai',
      icon: <Sparkles className="w-4 h-4 text-cyan-400" />,
    })
    items.push({
      id: 'ai-incident-investigator',
      title: 'AI Incident Investigator',
      subtitle: 'Synthesize telemetry and identify root-cause hypotheses',
      category: 'AI',
      url: '/ai',
      icon: <Sparkles className="w-4 h-4 text-cyan-400" />,
    })

    return items
  }, [])

  // Filter items based on query
  const filtered = useMemo(() => {
    if (!query.trim()) return allItems.slice(0, 8)
    const q = query.toLowerCase()
    return allItems.filter(
      item =>
        item.title.toLowerCase().includes(q) ||
        item.subtitle.toLowerCase().includes(q) ||
        item.category.toLowerCase().includes(q)
    )
  }, [allItems, query])

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault()
        if (isOpen) onClose()
        else {
          // Open handled by parent or trigger
        }
      }
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [isOpen, onClose])

  if (!isOpen) return null

  const handleSelect = (url: string) => {
    onClose()
    setQuery('')
    navigate(url)
  }

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-20 px-4 bg-slate-950/80 backdrop-blur-md animate-in fade-in duration-150">
      <div className="fixed inset-0" onClick={onClose} />
      <div className="relative w-full max-w-2xl bg-slate-900 border border-slate-700/80 rounded-2xl shadow-2xl overflow-hidden z-10 animate-in zoom-in-95 duration-150 flex flex-col">
        {/* Search Input Bar */}
        <div className="flex items-center px-4 py-3.5 border-b border-slate-800 bg-slate-900/90 gap-3">
          <Search className="w-5 h-5 text-cyan-400 shrink-0" />
          <input
            type="text"
            value={query}
            onChange={e => setQuery(e.target.value)}
            placeholder="Search courses, lessons, roadmaps, skills, certifications, incidents..."
            className="w-full bg-transparent text-sm text-slate-100 placeholder:text-slate-500 focus:outline-none font-sans"
            autoFocus
          />
          {query && (
            <button
              onClick={() => setQuery('')}
              className="text-slate-400 hover:text-slate-200 p-1"
            >
              <X className="w-4 h-4" />
            </button>
          )}
          <span className="text-[10px] font-mono text-slate-500 px-1.5 py-0.5 rounded border border-slate-800 bg-slate-800/60 shrink-0">
            ESC
          </span>
        </div>

        {/* Results List */}
        <div className="max-h-[60vh] overflow-y-auto p-2">
          {filtered.length === 0 ? (
            <div className="py-12 text-center text-slate-400">
              <Layers className="w-8 h-8 mx-auto text-slate-600 mb-2" />
              <p className="text-sm font-medium">No engineering resources found</p>
              <p className="text-xs text-slate-500 mt-1">
                Try searching for "Kubernetes", "AWS", "502", or "Terraform"
              </p>
            </div>
          ) : (
            <div className="flex flex-col gap-1">
              {filtered.map(item => (
                <button
                  key={item.id}
                  onClick={() => handleSelect(item.url)}
                  className="flex items-center justify-between p-3 rounded-xl hover:bg-slate-800/80 text-left transition-colors group cursor-pointer"
                >
                  <div className="flex items-center gap-3 min-w-0">
                    <div className="p-2 rounded-lg bg-slate-800/80 border border-slate-700/50 group-hover:border-slate-600 transition-colors shrink-0">
                      {item.icon}
                    </div>
                    <div className="min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-semibold text-slate-200 group-hover:text-cyan-300 transition-colors truncate">
                          {item.title}
                        </span>
                        <span className="text-[10px] font-mono uppercase px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700/60 shrink-0">
                          {item.category}
                        </span>
                      </div>
                      <p className="text-xs text-slate-400 truncate mt-0.5">{item.subtitle}</p>
                    </div>
                  </div>
                  <ArrowRight className="w-4 h-4 text-slate-600 group-hover:text-cyan-400 group-hover:translate-x-0.5 transition-all shrink-0 ml-2" />
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Footer shortcuts */}
        <div className="px-4 py-2.5 bg-slate-950/60 border-t border-slate-800/80 flex items-center justify-between text-[11px] font-mono text-slate-500">
          <div className="flex items-center gap-3">
            <span>
              <kbd className="px-1 py-0.5 bg-slate-800 rounded text-slate-300">↑</kbd>{' '}
              <kbd className="px-1 py-0.5 bg-slate-800 rounded text-slate-300">↓</kbd> navigate
            </span>
            <span>
              <kbd className="px-1.5 py-0.5 bg-slate-800 rounded text-slate-300">↵</kbd> select
            </span>
          </div>
          <span>CloudForge Command Engine</span>
        </div>
      </div>
    </div>
  )
}
