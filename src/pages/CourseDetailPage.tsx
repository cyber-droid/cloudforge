import { useState, useEffect } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import {
  Clock,
  BookOpen,
  Award,
  Star,
  CheckCircle2,
  Lock,
  Play,
  ChevronDown,
  ChevronUp,
  ArrowRight,
  ShieldCheck,
  Server,
  Layers,
  Sparkles,
} from 'lucide-react'
import { COURSES } from '../data/coursesData'
import { PageContainer } from '../components/layout/PageContainer'
import { Badge } from '../components/common/Badge'
import { Button } from '../components/common/Button'
import { Card } from '../components/common/Card'
import { useToast } from '../context/ToastContext'
import { api } from '../services/api'
import { mapApiCourseToCourse } from '../utils/courseMapper'
import type { Course } from '../types'

export function CourseDetailPage() {
  const { courseId } = useParams<{ courseId: string }>()
  const navigate = useNavigate()
  const { showToast } = useToast()

  const defaultCourse = COURSES.find(c => c.id === courseId || c.slug === courseId) || COURSES[1]
  const [course, setCourse] = useState<Course>(defaultCourse)
  const [isEnrolled, setIsEnrolled] = useState(false)
  const [isEnrolling, setIsEnrolling] = useState(false)

  // Fetch course from backend API
  useEffect(() => {
    let isMounted = true
    async function loadCourse() {
      if (!courseId) return
      try {
        const apiData = await api.getCourse(courseId)
        if (isMounted && apiData) {
          setCourse(mapApiCourseToCourse(apiData, isEnrolled))
        }
      } catch (err) {
        console.warn('Using local fallback course data:', err)
      }
    }

    async function checkEnrollment() {
      if (!courseId) return
      try {
        const enrollment = await api.getMyCourseEnrollment(courseId)
        if (isMounted && enrollment && enrollment.status === 'active') {
          setIsEnrolled(true)
        }
      } catch {
        // Not enrolled or not logged in
      }
    }

    loadCourse()
    checkEnrollment()

    return () => {
      isMounted = false
    }
  }, [courseId, isEnrolled])

  // State to track expanded modules
  const [expandedModules, setExpandedModules] = useState<Record<string, boolean>>({
    [course.modules[0]?.id || 'mod-01']: true,
    [course.modules[1]?.id || 'mod-02']: true,
  })

  const toggleModule = (id: string) => {
    setExpandedModules(prev => ({ ...prev, [id]: !prev[id] }))
  }

  const expandAll = () => {
    const allExpanded = course.modules.reduce((acc, m) => ({ ...acc, [m.id]: true }), {})
    setExpandedModules(allExpanded)
  }

  const collapseAll = () => {
    setExpandedModules({})
  }

  // Find next lesson to play
  const nextLesson = course.modules
    .flatMap(m => m.lessons)
    .find(l => l.current || (!l.completed && !l.locked)) || course.modules[0]?.lessons[0]

  const handleEnroll = async () => {
    try {
      setIsEnrolling(true)
      await api.enrollCourse(course.slug || course.id)
      setIsEnrolled(true)
      showToast('Course Enrolled', `You are now enrolled in ${course.title}. Progress tracking active.`, 'success')
      if (nextLesson) {
        navigate(`/learn/${course.id}/${nextLesson.id}`)
      }
    } catch (err: any) {
      // If error indicates already enrolled, proceed to lesson
      if (err.message?.includes('already enrolled')) {
        setIsEnrolled(true)
        if (nextLesson) {
          navigate(`/learn/${course.id}/${nextLesson.id}`)
        }
      } else {
        showToast('Enrollment Notification', err.message || 'Please log in to track course progress.', 'info')
        if (nextLesson) {
          navigate(`/learn/${course.id}/${nextLesson.id}`)
        }
      }
    } finally {
      setIsEnrolling(false)
    }
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 pb-16">
      {/* Course Hero Banner */}
      <div className="border-b border-slate-800 bg-gradient-to-b from-slate-900/90 to-slate-950 py-12">
        <PageContainer>
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
            <div className="lg:col-span-8 space-y-4">
              <div className="flex flex-wrap items-center gap-2">
                <Badge variant="cyan">{course.category}</Badge>
                <span className="text-xs font-mono text-slate-400">•</span>
                <span className="text-xs font-mono text-slate-300">{course.level}</span>
                <span className="text-xs font-mono text-slate-400">•</span>
                <span className="text-xs font-mono text-slate-300">{course.duration}</span>
                {course.certificate && (
                  <span className="flex items-center gap-1 text-[11px] font-mono text-amber-300 bg-amber-950/60 px-2 py-0.5 rounded border border-amber-800/60 ml-2">
                    <Award className="w-3 h-3 text-amber-400" />
                    <span>Training Certificate</span>
                  </span>
                )}
              </div>

              <h1 className="text-3xl sm:text-5xl font-extrabold text-white tracking-tight leading-tight">
                {course.title}
              </h1>

              <p className="text-base text-slate-300 leading-relaxed max-w-3xl">
                {course.longDescription || course.description}
              </p>

              {/* Technologies Tag Strip */}
              <div className="flex flex-wrap gap-2 pt-2">
                {course.technologies.map(t => (
                  <span
                    key={t}
                    className="text-xs font-mono px-2.5 py-1 rounded-lg bg-slate-800/80 text-slate-200 border border-slate-700/60"
                  >
                    {t}
                  </span>
                ))}
              </div>

              {/* Instructor snippet */}
              <div className="flex items-center gap-3 pt-3">
                <img
                  src={course.instructor.avatar}
                  alt={course.instructor.name}
                  className="w-10 h-10 rounded-full border border-cyan-500/40 object-cover"
                />
                <div>
                  <div className="flex items-center gap-1.5">
                    <span className="text-xs font-bold text-white">{course.instructor.name}</span>
                    {course.instructor.verified && (
                      <ShieldCheck className="w-3.5 h-3.5 text-cyan-400" />
                    )}
                  </div>
                  <span className="text-[11px] font-mono text-slate-400">{course.instructor.role}</span>
                </div>
              </div>
            </div>

            {/* Quick Action Card (Sticky on Large Screens) */}
            <div className="lg:col-span-4">
              <Card className="p-6 bg-slate-900/90 border-slate-700/80 shadow-2xl space-y-6">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-1.5 text-amber-400">
                    <Star className="w-4 h-4 fill-amber-400" />
                    <span className="text-sm font-bold">{course.rating}</span>
                    <span className="text-xs text-slate-400">({course.studentsCount.toLocaleString()} enrolled)</span>
                  </div>
                  <span className="text-xs font-mono px-2 py-0.5 rounded bg-emerald-950/60 text-emerald-400 border border-emerald-800/60">
                    Active Curriculum
                  </span>
                </div>

                <div className="space-y-3">
                  <Button
                    variant="glow"
                    size="lg"
                    className="w-full justify-center text-sm font-bold"
                    onClick={handleEnroll}
                    disabled={isEnrolling}
                  >
                    <Play className="w-4 h-4 fill-current mr-2" />
                    <span>
                      {isEnrolling ? 'Enrolling...' : isEnrolled ? 'Continue Learning' : 'Enroll in Course'}
                    </span>
                  </Button>

                  {nextLesson && (
                    <Link to={`/learn/${course.id}/${nextLesson.id}`}>
                      <Button variant="secondary" size="sm" className="w-full justify-center text-xs mt-2">
                        <span>Preview Syllabus</span>
                        <ArrowRight className="w-3.5 h-3.5 ml-1.5" />
                      </Button>
                    </Link>
                  )}
                </div>

                <div className="pt-4 border-t border-slate-800/80 space-y-2.5 text-xs text-slate-300 font-mono">
                  <div className="flex items-center justify-between">
                    <span className="text-slate-400 flex items-center gap-1.5">
                      <Layers className="w-3.5 h-3.5 text-cyan-400" /> Modules
                    </span>
                    <span className="font-bold">{course.modules.length} modules</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-slate-400 flex items-center gap-1.5">
                      <BookOpen className="w-3.5 h-3.5 text-cyan-400" /> Total Lessons
                    </span>
                    <span className="font-bold">{course.lessonsCount} lessons</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-slate-400 flex items-center gap-1.5">
                      <Clock className="w-3.5 h-3.5 text-cyan-400" /> Duration
                    </span>
                    <span className="font-bold">{course.duration}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-slate-400 flex items-center gap-1.5">
                      <Award className="w-3.5 h-3.5 text-amber-400" /> Certificate
                    </span>
                    <span className="font-bold text-amber-400">Included</span>
                  </div>
                </div>
              </Card>
            </div>
          </div>
        </PageContainer>
      </div>

      <PageContainer className="mt-10">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          {/* Main Column: Learning Outcomes & Full Syllabus Tree */}
          <div className="lg:col-span-8 space-y-10">
            {/* Learning Outcomes Section */}
            <div className="space-y-4">
              <h2 className="text-lg font-bold text-white flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-cyan-400" />
                <span>What You'll Master</span>
              </h2>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {course.learningOutcomes.map((outcome, idx) => (
                  <div
                    key={idx}
                    className="flex items-start gap-3 p-3 rounded-xl bg-slate-900/60 border border-slate-800/80 text-xs text-slate-200"
                  >
                    <CheckCircle2 className="w-4 h-4 text-cyan-400 shrink-0 mt-0.5" />
                    <span>{outcome}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Course Syllabus Accordion */}
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-bold text-white flex items-center gap-2">
                  <BookOpen className="w-5 h-5 text-cyan-400" />
                  <span>Curriculum Syllabus</span>
                </h2>
                <div className="flex items-center gap-2 text-xs font-mono">
                  <button
                    onClick={expandAll}
                    className="text-cyan-400 hover:text-cyan-300 transition-colors"
                  >
                    Expand All
                  </button>
                  <span className="text-slate-600">|</span>
                  <button
                    onClick={collapseAll}
                    className="text-slate-400 hover:text-slate-300 transition-colors"
                  >
                    Collapse All
                  </button>
                </div>
              </div>

              <div className="space-y-3">
                {course.modules.map((module) => {
                  const isExpanded = expandedModules[module.id]

                  return (
                    <div
                      key={module.id}
                      className="border border-slate-800/80 rounded-xl overflow-hidden bg-slate-900/40 transition-all"
                    >
                      {/* Module Header Bar */}
                      <button
                        onClick={() => toggleModule(module.id)}
                        className="w-full flex items-center justify-between p-4 text-left hover:bg-slate-900/80 transition-colors cursor-pointer"
                      >
                        <div className="flex items-center gap-3 min-w-0">
                          <span className="text-xs font-mono font-bold text-cyan-400 bg-slate-800 px-2 py-0.5 rounded border border-slate-700/60">
                            {module.number}
                          </span>
                          <span className="text-sm font-semibold text-white truncate">
                            {module.title}
                          </span>
                        </div>
                        <div className="flex items-center gap-4 text-xs font-mono text-slate-400 shrink-0">
                          <span className="hidden sm:inline">
                            {module.lessonCount} lessons • {module.duration}
                          </span>
                          {isExpanded ? (
                            <ChevronUp className="w-4 h-4 text-slate-400" />
                          ) : (
                            <ChevronDown className="w-4 h-4 text-slate-400" />
                          )}
                        </div>
                      </button>

                      {/* Module Lessons List */}
                      {isExpanded && (
                        <div className="border-t border-slate-800/80 bg-slate-950/40 divide-y divide-slate-800/60">
                          {module.lessons.map((lesson) => {
                            const isCurrent = lesson.current
                            const isCompleted = lesson.completed
                            const isLocked = lesson.locked

                            return (
                              <div
                                key={lesson.id}
                                className={`flex items-center justify-between p-3.5 pl-6 text-xs transition-colors ${
                                  isCurrent
                                    ? 'bg-cyan-950/20 text-cyan-300 font-semibold'
                                    : 'text-slate-300 hover:bg-slate-900/60'
                                }`}
                              >
                                <div className="flex items-center gap-3 min-w-0">
                                  {isCompleted ? (
                                    <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                                  ) : isCurrent ? (
                                    <Play className="w-4 h-4 text-cyan-400 fill-cyan-400 shrink-0" />
                                  ) : isLocked ? (
                                    <Lock className="w-4 h-4 text-slate-600 shrink-0" />
                                  ) : (
                                    <span className="w-4 h-4 rounded-full border border-slate-600 shrink-0" />
                                  )}
                                  <span className="truncate">{lesson.title}</span>
                                </div>

                                <div className="flex items-center gap-3 shrink-0 font-mono text-slate-500">
                                  <span>{lesson.duration}</span>
                                  {!isLocked ? (
                                    <Link to={`/learn/${course.id}/${lesson.id}`}>
                                      <Button variant={isCurrent ? 'glow' : 'secondary'} size="xs">
                                        {isCompleted ? 'Review' : isCurrent ? 'Play' : 'Start'}
                                      </Button>
                                    </Link>
                                  ) : (
                                    <span className="text-[10px] text-slate-600 font-mono">Locked</span>
                                  )}
                                </div>
                              </div>
                            )
                          })}
                        </div>
                      )}
                    </div>
                  )
                })}
              </div>
            </div>
          </div>

          {/* Right Sidebar: Prerequisites & Certification Alignment */}
          <div className="lg:col-span-4 space-y-6">
            <Card className="p-6 space-y-4">
              <h3 className="text-sm font-bold text-white font-mono uppercase tracking-wider">
                Prerequisites & Tools
              </h3>
              <ul className="text-xs text-slate-400 space-y-2 font-mono">
                <li>• Basic terminal / command line familiarity</li>
                <li>• Web browser with modern HTML5 support</li>
                <li>• No local Kubernetes or AWS account required (CloudForge provisions sandbox environments)</li>
              </ul>
            </Card>

            <Card className="p-6 space-y-4 border-amber-500/30">
              <div className="flex items-center gap-2 text-amber-400 font-bold text-xs font-mono">
                <Award className="w-4 h-4" />
                <span>Certification Alignment</span>
              </div>
              <p className="text-xs text-slate-300 leading-relaxed">
                This curriculum directly covers exam domains tested in CKA, CKAD, and AWS Solutions Architect industry certifications.
              </p>
              <Link to="/certifications">
                <Button variant="outline" size="xs" className="w-full">
                  Explore Mock Exam Tracks ➔
                </Button>
              </Link>
            </Card>
          </div>
        </div>
      </PageContainer>
    </div>
  )
}
