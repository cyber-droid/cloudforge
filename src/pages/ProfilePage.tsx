import { Link } from 'react-router-dom'
import {
  User,
  Award,
  Clock,
  Flame,
  CheckCircle2,
  FolderGit2,
  BookOpen,
  ShieldCheck,
  Settings,
  ExternalLink,
  Share2,
} from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import { PageContainer } from '../components/layout/PageContainer'
import { Card } from '../components/common/Card'
import { Badge } from '../components/common/Badge'
import { Button } from '../components/common/Button'
import { SKILLS } from '../data/skillsData'
import { ACHIEVEMENTS } from '../data/achievementsData'
import { CERTIFICATIONS } from '../data/certificationsData'

export function ProfilePage() {
  const { user } = useAuth()

  if (!user) return null

  const earnedAchievements = ACHIEVEMENTS.filter(a => a.earned)

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 pb-16">
      {/* Profile Header */}
      <div className="border-b border-slate-800 bg-slate-900/60 py-12">
        <PageContainer>
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
            <div className="flex items-center gap-5">
              <img
                src={user.avatar}
                alt={user.name}
                className="w-20 h-20 sm:w-24 sm:h-24 rounded-2xl object-cover ring-4 ring-cyan-500/20 shadow-xl"
              />
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
                    {user.name}
                  </h1>
                  <ShieldCheck className="w-5 h-5 text-cyan-400" />
                </div>
                <p className="text-xs font-mono text-cyan-400">@{user.handle}</p>
                <p className="text-xs sm:text-sm text-slate-300 font-medium">
                  {user.role}
                </p>
                <p className="text-[11px] font-mono text-slate-500">
                  Member since {user.joinedDate} • Verified Engineer ID #CF-8492
                </p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <Link to="/settings">
                <Button variant="secondary" size="sm" icon={<Settings className="w-4 h-4" />}>
                  Settings
                </Button>
              </Link>
              <Button variant="outline" size="sm" icon={<Share2 className="w-4 h-4" />}>
                Share Profile
              </Button>
            </div>
          </div>
        </PageContainer>
      </div>

      <PageContainer>
        {/* Core Profile Stats Strip */}
        <div className="grid grid-cols-2 sm:grid-cols-5 gap-4 mb-10">
          <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 text-center">
            <span className="text-xs font-mono text-slate-400 block mb-1">Courses</span>
            <span className="text-2xl font-bold font-mono text-white">
              {user.coursesCompleted}
            </span>
          </div>
          <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 text-center">
            <span className="text-xs font-mono text-slate-400 block mb-1">Projects</span>
            <span className="text-2xl font-bold font-mono text-cyan-400">2 Active</span>
          </div>
          <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 text-center">
            <span className="text-xs font-mono text-slate-400 block mb-1">Certificates</span>
            <span className="text-2xl font-bold font-mono text-purple-400">
              {user.certificatesEarned}
            </span>
          </div>
          <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 text-center">
            <span className="text-xs font-mono text-slate-400 block mb-1">Learning Hours</span>
            <span className="text-2xl font-bold font-mono text-white">
              {user.learningHours}h
            </span>
          </div>
          <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 text-center col-span-2 sm:col-span-1">
            <span className="text-xs font-mono text-slate-400 block mb-1">Streak</span>
            <span className="text-2xl font-bold font-mono text-amber-400 flex items-center justify-center gap-1">
              <Flame className="w-5 h-5 fill-amber-400" />
              {user.learningStreak}d
            </span>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          {/* Left Column: Verified Certificates & Skills */}
          <div className="lg:col-span-7 space-y-8">
            {/* Verified CloudForge Training Certificates */}
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-base font-bold text-white flex items-center gap-2">
                  <Award className="w-4 h-4 text-amber-400" />
                  <span>Verified CloudForge Certificates</span>
                </h3>
                <span className="text-xs font-mono text-slate-400">
                  {user.certificatesEarned} Earned
                </span>
              </div>

              <div className="space-y-3">
                <Card className="p-4 border-amber-500/30 bg-slate-900/80 flex items-center justify-between">
                  <div>
                    <span className="text-[10px] font-mono text-amber-400 uppercase font-bold">
                      Training Certificate
                    </span>
                    <h4 className="text-sm font-bold text-white">
                      Cloud Computing Foundations
                    </h4>
                    <p className="text-[11px] text-slate-400 font-mono mt-0.5">
                      Issued: August 14, 2026 • Credential ID: CF-CERT-90214
                    </p>
                  </div>
                  <Button variant="outline" size="xs">
                    Verify ➔
                  </Button>
                </Card>

                <Card className="p-4 border-amber-500/30 bg-slate-900/80 flex items-center justify-between">
                  <div>
                    <span className="text-[10px] font-mono text-amber-400 uppercase font-bold">
                      Training Certificate
                    </span>
                    <h4 className="text-sm font-bold text-white">
                      AWS Cloud Computing Foundations
                    </h4>
                    <p className="text-[11px] text-slate-400 font-mono mt-0.5">
                      Issued: July 28, 2026 • Credential ID: CF-CERT-77312
                    </p>
                  </div>
                  <Button variant="outline" size="xs">
                    Verify ➔
                  </Button>
                </Card>

                <Card className="p-4 border-amber-500/30 bg-slate-900/80 flex items-center justify-between">
                  <div>
                    <span className="text-[10px] font-mono text-amber-400 uppercase font-bold">
                      Training Certificate
                    </span>
                    <h4 className="text-sm font-bold text-white">
                      DevOps Foundations Professional Prep
                    </h4>
                    <p className="text-[11px] text-slate-400 font-mono mt-0.5">
                      Issued: September 04, 2026 • Credential ID: CF-CERT-88410
                    </p>
                  </div>
                  <Button variant="outline" size="xs">
                    Verify ➔
                  </Button>
                </Card>
              </div>
            </div>

            {/* Top Verified Skills */}
            <div className="space-y-4">
              <h3 className="text-base font-bold text-white">Top Technical Skills</h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {SKILLS.slice(0, 6).map(skill => (
                  <div
                    key={skill.id}
                    className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800 space-y-2"
                  >
                    <div className="flex justify-between text-xs font-mono">
                      <span className="font-semibold text-slate-200">{skill.name}</span>
                      <span className="text-cyan-400 font-bold">{skill.proficiency}%</span>
                    </div>
                    <div className="w-full h-1.5 rounded-full bg-slate-800 overflow-hidden">
                      <div
                        className="h-full bg-cyan-400 rounded-full"
                        style={{ width: `${skill.proficiency}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Right Column: Achievements & Activity Log */}
          <div className="lg:col-span-5 space-y-6">
            <Card className="p-6 space-y-4">
              <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                <h3 className="text-sm font-bold text-white font-mono uppercase tracking-wider">
                  Unlocked Achievements ({earnedAchievements.length})
                </h3>
                <Link to="/achievements" className="text-xs font-mono text-cyan-400 hover:text-cyan-300">
                  View All
                </Link>
              </div>

              <div className="space-y-3">
                {earnedAchievements.slice(0, 5).map(ach => (
                  <div key={ach.id} className="flex items-center gap-3 text-xs">
                    <div className="p-2 rounded-xl bg-slate-800 border border-slate-700 text-cyan-400 shrink-0">
                      <Award className="w-4 h-4" />
                    </div>
                    <div className="min-w-0">
                      <p className="font-semibold text-white truncate">{ach.title}</p>
                      <p className="text-[11px] text-slate-400 truncate">{ach.description}</p>
                    </div>
                    <span className="text-[10px] font-mono text-amber-400 shrink-0 ml-auto">
                      +{ach.xp} XP
                    </span>
                  </div>
                ))}
              </div>
            </Card>

            <Card className="p-6 space-y-3">
              <h3 className="text-sm font-bold text-white font-mono uppercase tracking-wider">
                Recent Engineering Logs
              </h3>
              <ul className="text-xs font-mono text-slate-400 space-y-2">
                <li>• Completed "Linux Troubleshooting Lab" (18m)</li>
                <li>• Deployed "Containerized Web Platform" Docker stack</li>
                <li>• Diagnosed Incident INC-0042 (502 Bad Gateway)</li>
                <li>• Scored 84% on AWS Cloud Practitioner Mock Exam</li>
              </ul>
            </Card>
          </div>
        </div>
      </PageContainer>
    </div>
  )
}
