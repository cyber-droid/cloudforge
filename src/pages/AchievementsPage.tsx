import { useState } from 'react'
import {
  Award,
  Flame,
  Box,
  Server,
  Layers,
  ShieldCheck,
  AlertTriangle,
  GitPullRequest,
  Activity,
  Sparkles,
  Zap,
  GraduationCap,
  CheckCircle2,
  Lock,
} from 'lucide-react'
import { ACHIEVEMENTS } from '../data/achievementsData'
import { PageContainer } from '../components/layout/PageContainer'
import { Card } from '../components/common/Card'
import { Badge } from '../components/common/Badge'
import { Tabs } from '../components/common/Tabs'

export function AchievementsPage() {
  const [selectedCategory, setSelectedCategory] = useState<string>('all')

  const categories = [
    { id: 'all', label: 'All Badges' },
    { id: 'learning', label: 'Learning' },
    { id: 'streaks', label: 'Streaks' },
    { id: 'specialization', label: 'Specializations' },
    { id: 'troubleshooting', label: 'Incidents' },
  ]

  const totalXP = ACHIEVEMENTS.filter(a => a.earned).reduce((acc, curr) => acc + curr.xp, 0)
  const earnedCount = ACHIEVEMENTS.filter(a => a.earned).length

  const filtered = ACHIEVEMENTS.filter(a => {
    if (selectedCategory === 'all') return true
    return a.category === selectedCategory
  })

  const getIcon = (iconName: string) => {
    switch (iconName) {
      case 'GraduationCap': return <GraduationCap className="w-5 h-5" />
      case 'Award': return <Award className="w-5 h-5" />
      case 'Flame': return <Flame className="w-5 h-5" />
      case 'Box': return <Box className="w-5 h-5" />
      case 'Server': return <Server className="w-5 h-5" />
      case 'Layers': return <Layers className="w-5 h-5" />
      case 'ShieldCheck': return <ShieldCheck className="w-5 h-5" />
      case 'AlertTriangle': return <AlertTriangle className="w-5 h-5" />
      case 'GitPullRequest': return <GitPullRequest className="w-5 h-5" />
      case 'Activity': return <Activity className="w-5 h-5" />
      case 'Sparkles': return <Sparkles className="w-5 h-5" />
      case 'Zap': return <Zap className="w-5 h-5" />
      default: return <Award className="w-5 h-5" />
    }
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 pb-16">
      {/* Header */}
      <div className="border-b border-slate-800 bg-slate-950/80 py-12">
        <PageContainer>
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
            <div className="max-w-2xl space-y-2">
              <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-cyan-950/60 border border-cyan-800/50 text-cyan-300 text-xs font-mono">
                <Award className="w-3.5 h-3.5" />
                <span>ENGINEERING MILESTONES</span>
              </div>
              <h1 className="text-3xl sm:text-5xl font-extrabold text-white tracking-tight">
                Achievements & Badges
              </h1>
              <p className="text-sm text-slate-300">
                Tasteful engineering credentials earned through consistent daily labs, complex multi-tier projects, and live incident rescues.
              </p>
            </div>

            {/* Total XP Card */}
            <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 flex items-center gap-5 shrink-0 shadow-lg">
              <div className="p-3 rounded-xl bg-cyan-950/80 border border-cyan-700/60 text-cyan-400">
                <Trophy className="w-8 h-8" />
              </div>
              <div>
                <span className="text-xs font-mono text-slate-400 uppercase tracking-wider block">
                  Earned Engineering XP
                </span>
                <span className="text-3xl font-extrabold font-mono text-white">
                  {totalXP.toLocaleString()} XP
                </span>
                <span className="text-[11px] font-mono text-cyan-400 block mt-0.5">
                  {earnedCount} of {ACHIEVEMENTS.length} Badges Unlocked
                </span>
              </div>
            </div>
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

        {/* Badges Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {filtered.map(ach => (
            <Card
              key={ach.id}
              className={`p-6 flex flex-col justify-between transition-all ${
                ach.earned
                  ? 'border-slate-800 bg-slate-900/80 hover:border-cyan-500/40 shadow-sm'
                  : 'border-slate-850 bg-slate-950/40 opacity-60'
              }`}
            >
              <div>
                <div className="flex items-start justify-between mb-4">
                  <div
                    className={`p-3 rounded-2xl border ${
                      ach.earned
                        ? 'bg-cyan-950/80 border-cyan-700/60 text-cyan-400 shadow-md shadow-cyan-950/20'
                        : 'bg-slate-900 border-slate-800 text-slate-600'
                    }`}
                  >
                    {getIcon(ach.icon)}
                  </div>
                  <span className="text-xs font-mono text-slate-400 bg-slate-800/80 px-2 py-0.5 rounded border border-slate-700/60">
                    +{ach.xp} XP
                  </span>
                </div>

                <h3 className="text-base font-bold text-white mb-1.5 flex items-center gap-2">
                  <span>{ach.title}</span>
                  {!ach.earned && <Lock className="w-3.5 h-3.5 text-slate-600" />}
                </h3>

                <p className="text-xs text-slate-400 leading-relaxed">
                  {ach.description}
                </p>
              </div>

              <div className="mt-6 pt-3 border-t border-slate-800/80 flex items-center justify-between text-[11px] font-mono">
                {ach.earned ? (
                  <span className="text-emerald-400 flex items-center gap-1.5">
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    <span>Unlocked on {ach.earnedDate}</span>
                  </span>
                ) : (
                  <span className="text-slate-600">Locked Milestone</span>
                )}
              </div>
            </Card>
          ))}
        </div>
      </PageContainer>
    </div>
  )
}

function Trophy(props: React.SVGProps<SVGSVGElement>) {
  return (
    <svg
      {...props}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M6 9H4.5a2.5 2.5 0 0 1 0-5H6" />
      <path d="M18 9h1.5a2.5 2.5 0 0 0 0-5H18" />
      <path d="M4 22h16" />
      <path d="M10 14.66V17c0 .55-.47.98-.97 1.21C7.85 18.75 7 20.24 7 22" />
      <path d="M14 14.66V17c0 .55.47.98.97 1.21C16.15 18.75 17 20.24 17 22" />
      <path d="M18 2H6v7a6 6 0 0 0 12 0V2Z" />
    </svg>
  )
}
