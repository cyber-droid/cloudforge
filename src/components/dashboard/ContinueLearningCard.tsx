import { Link } from 'react-router-dom'
import { Play, BookOpen, Clock, ArrowRight, Server, CheckCircle2 } from 'lucide-react'
import { Button } from '../common/Button'
import { Badge } from '../common/Badge'

interface ContinueLearningCardProps {
  courseTitle?: string
  progress?: number
  currentLesson?: string
  moduleTitle?: string
  estimatedTime?: string
  courseId?: string
  lessonId?: string
}

export function ContinueLearningCard({
  courseTitle = 'Kubernetes Engineering',
  progress = 68,
  currentLesson = 'Debugging CrashLoopBackOff',
  moduleTitle = 'Module 04 — Networking, Services & Health Probes',
  estimatedTime = '18m remaining',
  courseId = 'kubernetes-engineering',
  lessonId = 'k8s-402',
}: ContinueLearningCardProps) {
  return (
    <div className="relative overflow-hidden rounded-2xl border border-cyan-500/40 bg-gradient-to-br from-slate-900 via-slate-900/90 to-cyan-950/20 p-6 sm:p-8 shadow-2xl shadow-cyan-950/20">
      {/* Subtle background glow */}
      <div className="absolute top-0 right-0 -mr-16 -mt-16 w-64 h-64 rounded-full bg-cyan-500/10 blur-3xl pointer-events-none" />

      <div className="relative z-10 flex flex-col lg:flex-row lg:items-center justify-between gap-6">
        <div className="space-y-3 max-w-2xl">
          <div className="flex flex-wrap items-center gap-2">
            <Badge variant="cyan" dot>
              ACTIVE ENROLLMENT
            </Badge>
            <span className="text-xs font-mono text-slate-400">
              {moduleTitle}
            </span>
          </div>

          <h3 className="text-2xl sm:text-3xl font-bold text-white tracking-tight">
            {courseTitle}
          </h3>

          <div className="flex items-center gap-2 text-sm text-slate-300">
            <span className="text-slate-400">Current lesson:</span>
            <span className="font-semibold text-cyan-300 font-mono flex items-center gap-1.5">
              <Server className="w-3.5 h-3.5" />
              {currentLesson}
            </span>
          </div>

          {/* Progress Bar */}
          <div className="space-y-1.5 pt-2">
            <div className="flex justify-between text-xs font-mono">
              <span className="text-slate-400">Course Progress</span>
              <span className="text-cyan-400 font-bold">{progress}% Complete</span>
            </div>
            <div className="w-full h-2.5 rounded-full bg-slate-800 overflow-hidden border border-slate-700/60">
              <div
                className="h-full rounded-full bg-gradient-to-r from-cyan-500 to-indigo-500 transition-all duration-500"
                style={{ width: `${progress}%` }}
              />
            </div>
          </div>
        </div>

        {/* Action Button & Metadata */}
        <div className="flex flex-col sm:flex-row lg:flex-col items-start lg:items-end justify-between gap-3 shrink-0">
          <div className="flex items-center gap-2 text-xs font-mono text-slate-400">
            <Clock className="w-3.5 h-3.5 text-cyan-400" />
            <span>{estimatedTime}</span>
          </div>
          <Link to={`/learn/${courseId}/${lessonId}`}>
            <Button
              variant="glow"
              size="lg"
              icon={<Play className="w-4 h-4 fill-slate-950" />}
              iconRight={<ArrowRight className="w-4 h-4" />}
            >
              Continue Learning
            </Button>
          </Link>
        </div>
      </div>
    </div>
  )
}
