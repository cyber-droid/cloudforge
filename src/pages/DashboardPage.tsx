import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  TrendingUp,
  Flame,
  Clock,
  Award,
  BookCheck,
  Terminal,
  Sparkles,
  AlertTriangle,
  FolderGit2,
  Cpu,
  Loader2,
  RefreshCw,
} from 'lucide-react'
import { PageContainer } from '../components/layout/PageContainer'
import { MetricCard } from '../components/dashboard/MetricCard'
import { ContinueLearningCard } from '../components/dashboard/ContinueLearningCard'
import { ActivityGrid } from '../components/dashboard/ActivityGrid'
import { SkillBars } from '../components/dashboard/SkillBars'
import { RecommendedSteps } from '../components/dashboard/RecommendedSteps'
import { Button } from '../components/common/Button'
import { useAuth } from '../context/AuthContext'
import { api, type ApiDashboard } from '../services/api'

export function DashboardPage() {
  const { user } = useAuth()
  const [dashboardData, setDashboardData] = useState<ApiDashboard | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchDashboard = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await api.getMyDashboard()
      setDashboardData(data)
    } catch (err: any) {
      console.error('Failed to load dashboard data:', err)
      setError(err.message || 'Could not connect to CloudForge backend')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchDashboard()
  }, [])

  const userName = dashboardData?.user?.name
    ? dashboardData.user.name.split(' ')[0]
    : user?.name
    ? user.name.split(' ')[0]
    : 'Engineer'

  // Dynamic values calculated from backend
  const overallProgress = dashboardData?.stats.overall_progress ?? (user?.overallProgress || 42)
  const learningStreak = dashboardData?.stats.current_streak ?? (user?.learningStreak || 12)
  const learningHours = dashboardData?.stats.learning_hours ?? (user?.learningHours || 38.5)
  const coursesCompleted = dashboardData?.stats.courses_completed ?? 1

  // Format activity grid data
  const activityData = dashboardData?.weekly_activity?.map(a => ({
    date: a.date,
    count: a.count,
  })) || user?.activityGrid || []

  const weeklyHours = dashboardData?.weekly_hours?.map(w => ({
    day: w.day,
    hours: w.hours,
  })) || user?.weeklyHours || []

  // Continue learning resolution
  const continueTarget = dashboardData?.continue_learning

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 pb-16">
      <PageContainer>
        {/* Header section */}
        <div className="flex flex-col md:flex-row md:items-center justify-between pb-8 mb-8 border-b border-slate-800/80 gap-4">
          <div>
            <div className="inline-flex items-center gap-2 text-xs font-mono text-cyan-400 mb-2">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              <span>CLOUD WORKBENCH ACTIVE</span>
            </div>
            <h1 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
              Good morning, {userName} 👋
            </h1>
            <p className="text-sm text-slate-400 font-normal mt-1">
              {dashboardData?.stats.courses_enrolled
                ? `${dashboardData.stats.courses_enrolled} active course enrollments. ${dashboardData.stats.lessons_completed} lessons completed.`
                : 'Continue building your engineering skills. 2 milestones remaining this week.'}
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <Link to="/troubleshooting">
              <Button
                variant="secondary"
                size="sm"
                icon={<AlertTriangle className="w-4 h-4 text-rose-400" />}
              >
                Troubleshoot Outage
              </Button>
            </Link>
            <Link to="/ai">
              <Button
                variant="primary"
                size="sm"
                icon={<Sparkles className="w-4 h-4" />}
              >
                AI Workbench
              </Button>
            </Link>
          </div>
        </div>

        {error && (
          <div className="mb-6 p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-sm flex items-center justify-between">
            <span>{error}</span>
            <Button variant="outline" size="sm" onClick={fetchDashboard} icon={<RefreshCw className="w-3.5 h-3.5" />}>
              Retry
            </Button>
          </div>
        )}

        {/* 4 Primary Top Metrics from PostgreSQL */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5 mb-8">
          <MetricCard
            title="Overall Progress"
            value={`${overallProgress}%`}
            trend="+8%"
            trendPositive={true}
            icon={<TrendingUp className="w-5 h-5" />}
            color="cyan"
          />
          <MetricCard
            title="Learning Streak"
            value={learningStreak.toString()}
            unit="days"
            trend="Active streak"
            trendPositive={true}
            icon={<Flame className="w-5 h-5 text-amber-400" />}
            color="amber"
          />
          <MetricCard
            title="Learning Hours"
            value={learningHours.toString()}
            unit="hours"
            trend="Total tracked"
            trendPositive={true}
            icon={<Clock className="w-5 h-5" />}
            color="blue"
          />
          <MetricCard
            title="Courses Completed"
            value={coursesCompleted.toString()}
            unit="courses"
            trend="Graduated"
            trendPositive={true}
            icon={<Award className="w-5 h-5" />}
            color="purple"
          />
        </div>

        {/* Continue Learning Featured Card */}
        <div className="mb-10">
          {continueTarget ? (
            <ContinueLearningCard
              courseTitle={continueTarget.course_title}
              progress={Math.round(continueTarget.progress_percentage)}
              currentLesson={continueTarget.lesson_title}
              moduleTitle={`Module ${continueTarget.module_number} — ${continueTarget.module_title}`}
              estimatedTime={continueTarget.estimated_time_remaining}
              courseId={continueTarget.course_slug || continueTarget.course_id}
              lessonId={continueTarget.lesson_slug || continueTarget.lesson_id}
            />
          ) : (
            <ContinueLearningCard
              courseTitle="Kubernetes Engineering"
              progress={68}
              currentLesson="Understanding ClusterIP & CoreDNS"
              moduleTitle="Module 04 — Services & Networking"
              estimatedTime="15m remaining"
              courseId="kubernetes-engineering"
              lessonId="understanding-clusterip"
            />
          )}
        </div>

        {/* GitHub-style Activity Grid & Weekly Hours */}
        <div className="mb-10">
          <ActivityGrid
            activityData={activityData}
            weeklyHours={weeklyHours}
          />
        </div>

        {/* Skill Progression Matrix */}
        <div className="mb-10">
          <SkillBars />
        </div>

        {/* Recommended Next Steps */}
        <div className="mb-10">
          <RecommendedSteps />
        </div>

        {/* Quick Launch Shortcuts Bar */}
        <div className="p-6 rounded-2xl border border-slate-800 bg-slate-900/60 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-slate-800 border border-slate-700/60 text-cyan-400">
              <Terminal className="w-5 h-5" />
            </div>
            <div>
              <h4 className="text-sm font-bold text-white">CloudForge CLI & Sandboxes</h4>
              <p className="text-xs text-slate-400 font-mono mt-0.5">
                Practice kubectl, docker, and terraform commands directly in your browser.
              </p>
            </div>
          </div>
          <div className="flex items-center gap-3 w-full sm:w-auto">
            <Link to="/courses" className="w-full sm:w-auto">
              <Button variant="outline" size="sm" className="w-full">
                Browse Courses
              </Button>
            </Link>
            <Link to="/certifications" className="w-full sm:w-auto">
              <Button variant="secondary" size="sm" className="w-full">
                Exam Prep
              </Button>
            </Link>
          </div>
        </div>
      </PageContainer>
    </div>
  )
}
