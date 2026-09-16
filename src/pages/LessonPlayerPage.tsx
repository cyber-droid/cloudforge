import { useState, useMemo } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import {
  ChevronLeft,
  ChevronRight,
  CheckCircle2,
  Lock,
  Play,
  Sparkles,
  BookOpen,
  Clock,
  Menu,
  X,
  FileCode2,
  Terminal,
  Share2,
  AlertCircle,
  Check,
} from 'lucide-react'
import { COURSES } from '../data/coursesData'
import { AIChatPanel } from '../components/lesson/AIChatPanel'
import { PracticeQuiz } from '../components/lesson/PracticeQuiz'
import { CodeBlock } from '../components/common/CodeBlock'
import { Button } from '../components/common/Button'
import { useToast } from '../context/ToastContext'

export function LessonPlayerPage() {
  const { courseId, lessonId } = useParams<{ courseId: string; lessonId: string }>()
  const navigate = useNavigate()
  const { showToast } = useToast()

  const [aiSidebarOpen, setAiSidebarOpen] = useState(true)
  const [curriculumSidebarOpen, setCurriculumSidebarOpen] = useState(true)
  const [completed, setCompleted] = useState(false)

  // Find course
  const course = COURSES.find(c => c.id === courseId) || COURSES[2] // default to K8s

  // Flatten all lessons with module info
  const allLessons = useMemo(() => {
    const list: {
      lesson: (typeof course.modules)[0]['lessons'][0]
      moduleTitle: string
      index: number
    }[] = []
    let idx = 0
    course.modules.forEach(m => {
      m.lessons.forEach(l => {
        list.push({ lesson: l, moduleTitle: m.title, index: idx++ })
      })
    })
    return list
  }, [course])

  const currentIndex = allLessons.findIndex(item => item.lesson.id === lessonId)
  const safeIndex = currentIndex >= 0 ? currentIndex : 7 // default to a lesson
  const currentItem = allLessons[safeIndex]
  const currentLesson = currentItem.lesson

  const prevItem = safeIndex > 0 ? allLessons[safeIndex - 1] : null
  const nextItem = safeIndex < allLessons.length - 1 ? allLessons[safeIndex + 1] : null

  // Fallback demo content if not populated
  const objectives = currentLesson.content?.objectives || [
    'Understand how kube-proxy routes virtual ClusterIP traffic to endpoints',
    'Compare ClusterIP, NodePort, and LoadBalancer use-cases',
    'Examine iptables NAT translation rules for service endpoints',
    'Troubleshoot Service endpoint mismatch bugs',
  ]

  const handleMarkComplete = () => {
    setCompleted(true)
    showToast('Lesson Marked Complete!', `+50 XP earned. Progress updated for ${course.title}.`, 'success')
  }

  return (
    <div className="flex flex-col h-[calc(100vh-4rem)] bg-slate-950 text-slate-100 overflow-hidden">
      {/* Top Learning Navigation Bar */}
      <div className="h-12 border-b border-slate-800 bg-slate-900/90 px-4 flex items-center justify-between gap-4 shrink-0">
        <div className="flex items-center gap-3">
          <button
            onClick={() => setCurriculumSidebarOpen(!curriculumSidebarOpen)}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
            title="Toggle Curriculum Sidebar"
          >
            <Menu className="w-4 h-4" />
          </button>
          <Link
            to={`/courses/${course.id}`}
            className="text-xs font-semibold text-slate-300 hover:text-cyan-300 transition-colors truncate max-w-xs sm:max-w-md"
          >
            {course.title}
          </Link>
          <span className="text-slate-600">/</span>
          <span className="text-xs font-mono text-cyan-400 truncate">
            {currentLesson.title}
          </span>
        </div>

        <div className="flex items-center gap-2 sm:gap-3">
          <span className="text-xs font-mono text-slate-400 hidden sm:inline">
            Lesson {safeIndex + 1} of {allLessons.length}
          </span>

          <button
            onClick={() => setAiSidebarOpen(!aiSidebarOpen)}
            className={`flex items-center gap-1.5 px-3 py-1 rounded-lg text-xs font-mono border transition-all cursor-pointer ${
              aiSidebarOpen
                ? 'bg-cyan-950 border-cyan-700 text-cyan-300'
                : 'bg-slate-800 border-slate-700 text-slate-300 hover:text-white'
            }`}
          >
            <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
            <span className="hidden sm:inline">CloudForge AI</span>
          </button>
        </div>
      </div>

      {/* 3-Pane Body */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Curriculum Sidebar */}
        {curriculumSidebarOpen && (
          <aside className="w-72 sm:w-80 border-r border-slate-800 bg-slate-900/60 overflow-y-auto shrink-0 flex flex-col">
            <div className="p-3.5 border-b border-slate-800/80 flex items-center justify-between">
              <span className="text-xs font-bold text-white font-mono uppercase tracking-wider">
                Curriculum
              </span>
              <span className="text-[11px] font-mono text-slate-400">
                {course.modules.length} Modules
              </span>
            </div>

            <div className="flex-1 overflow-y-auto divide-y divide-slate-800/40">
              {course.modules.map(module => (
                <div key={module.id} className="p-2">
                  <div className="px-2 py-1.5 text-[11px] font-mono font-semibold text-slate-400 uppercase tracking-wider">
                    {module.number} {module.title}
                  </div>
                  <div className="space-y-0.5 mt-1">
                    {module.lessons.map(lesson => {
                      const isThisActive = lesson.id === currentLesson.id
                      return (
                        <Link
                          key={lesson.id}
                          to={`/learn/${course.id}/${lesson.id}`}
                          className={`flex items-center justify-between p-2 rounded-lg text-xs transition-all ${
                            isThisActive
                              ? 'bg-cyan-950/60 border border-cyan-800/60 text-cyan-300 font-semibold'
                              : 'text-slate-300 hover:bg-slate-800/60 hover:text-white'
                          }`}
                        >
                          <div className="flex items-center gap-2 min-w-0">
                            {lesson.completed || (isThisActive && completed) ? (
                              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                            ) : isThisActive ? (
                              <Play className="w-3.5 h-3.5 text-cyan-400 fill-cyan-400 shrink-0" />
                            ) : (
                              <span className="w-3.5 h-3.5 rounded-full border border-slate-700 shrink-0" />
                            )}
                            <span className="truncate">{lesson.title}</span>
                          </div>
                          <span className="text-[10px] font-mono text-slate-500 shrink-0 ml-1">
                            {lesson.duration}
                          </span>
                        </Link>
                      )
                    })}
                  </div>
                </div>
              ))}
            </div>
          </aside>
        )}

        {/* Center Main Lesson Content Viewer */}
        <main className="flex-1 overflow-y-auto p-6 sm:p-10 max-w-4xl mx-auto w-full">
          {/* Lesson Header */}
          <div className="space-y-3 pb-6 border-b border-slate-800">
            <div className="flex items-center gap-2 text-xs font-mono text-cyan-400">
              <Clock className="w-3.5 h-3.5" />
              <span>{currentLesson.content?.estimatedTime || '20m'}</span>
              <span>•</span>
              <span>Hands-On Engineering Walkthrough</span>
            </div>
            <h1 className="text-2xl sm:text-4xl font-extrabold text-white tracking-tight">
              {currentLesson.title}
            </h1>
            <p className="text-sm text-slate-300 leading-relaxed">
              {currentLesson.content?.description ||
                'In Kubernetes, Pods are ephemeral; their IP addresses change every time they recreate. A Service provides a stable network endpoint (IP and DNS name) that dynamically abstracts a changing set of backend Pod replicas using label selectors.'}
            </p>
          </div>

          {/* Learning Objectives Box */}
          <div className="my-6 p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-2">
            <h3 className="text-xs font-mono uppercase font-bold text-slate-300 tracking-wider">
              Learning Objectives
            </h3>
            <ul className="space-y-1.5 text-xs text-slate-300 font-sans">
              {objectives.map((obj, i) => (
                <li key={i} className="flex items-start gap-2">
                  <Check className="w-3.5 h-3.5 text-cyan-400 shrink-0 mt-0.5" />
                  <span>{obj}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Architecture Diagram Visualization */}
          <div className="my-6 space-y-2">
            <h3 className="text-xs font-mono uppercase font-bold text-slate-400 tracking-wider">
              Service Packet Routing Topology
            </h3>
            <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 font-mono text-xs text-cyan-300 leading-relaxed overflow-x-auto shadow-inner">
              <pre>
{`[ External Client / Ingress Controller ]
                  │
                  ▼ (Port 80 HTTP)
     ┌────────────────────────────┐
     │  Virtual IP: 10.96.0.12    │
     │  Service: order-service    │
     └─────────────┬──────────────┘
                   │
    kube-proxy iptables NAT table
                   │
    ┌──────────────┴──────────────┐
    ▼ (10.244.1.15:8080)          ▼ (10.244.2.22:8080)
┌──────────────────────┐      ┌──────────────────────┐
│  Pod: order-api-1    │      │  Pod: order-api-2    │
│  Status: Ready (2/2) │      │  Status: Ready (2/2) │
└──────────────────────┘      └──────────────────────┘`}
              </pre>
            </div>
          </div>

          {/* Lesson Content Sections */}
          <div className="space-y-6 text-sm text-slate-300 leading-relaxed font-sans">
            <div>
              <h3 className="text-lg font-bold text-white mb-2">
                1. Service Types: ClusterIP vs NodePort vs LoadBalancer
              </h3>
              <p className="text-xs sm:text-sm text-slate-300 leading-relaxed mb-3">
                Kubernetes provides multiple abstraction tiers for traffic routing. ClusterIP creates a virtual IP inside the cluster overlay network. NodePort opens a static port on every physical/virtual worker node. LoadBalancer interacts with your cloud provider (AWS NLB, Azure Load Balancer) to provision an external IP that routes to the NodePorts.
              </p>
              <CodeBlock
                language="yaml"
                filename="service-clusterip.yaml"
                code={`apiVersion: v1
kind: Service
metadata:
  name: order-service
  namespace: production
  labels:
    app: order-service
spec:
  type: ClusterIP
  selector:
    app: order-service
    tier: backend
  ports:
    - name: http
      port: 80
      targetPort: 8080
      protocol: TCP`}
              />
            </div>

            <div>
              <h3 className="text-lg font-bold text-white mb-2">
                2. Endpoint Resolution & Readiness Checks
              </h3>
              <p className="text-xs sm:text-sm text-slate-300 leading-relaxed mb-3">
                Whenever a Pod crashes or fails its configured <code className="text-cyan-300">readinessProbe</code>, the EndpointSlice controller immediately strips its IP address from the routing table. Traffic is guaranteed to reach only healthy, active containers.
              </p>
              <CodeBlock
                language="bash"
                filename="verify-endpoints.sh"
                code={`# Inspect active backend endpoints registered for this service
kubectl get endpoints order-service -n production

# Verify readiness status across pod replicas
kubectl get pods -l app=order-service -n production -o wide`}
              />
            </div>
          </div>

          {/* Interactive Practice Quiz */}
          <PracticeQuiz
            questions={
              currentLesson.content?.practiceQuestions || [
                {
                  id: 'q1',
                  question: 'What happens when a Pod backing a ClusterIP service fails its readinessProbe?',
                  options: [
                    'The Pod is terminated and recreated immediately',
                    'The Pod remains running, but its IP is removed from the Service Endpoints',
                    'The ClusterIP address changes',
                    'The Node hosting the Pod is cordoned',
                  ],
                  correctIndex: 1,
                  explanation: 'Readiness probes signal whether a pod is ready to accept traffic. If it fails, Kubernetes stops routing service traffic to it without restarting the container.',
                },
                {
                  id: 'q2',
                  question: 'Which component translates ClusterIP virtual addresses to active Pod IP destinations?',
                  options: ['CoreDNS', 'kube-scheduler', 'kube-proxy', 'containerd'],
                  correctIndex: 2,
                  explanation: 'kube-proxy runs on each worker node and programs iptables or IPVS rules to load-balance traffic from the virtual ClusterIP to healthy Pod IPs.',
                },
              ]
            }
          />

          {/* Bottom Bar: Previous, Mark Complete, Next Lesson */}
          <div className="mt-12 pt-6 border-t border-slate-800 flex flex-col sm:flex-row items-center justify-between gap-4">
            <div>
              {prevItem ? (
                <Link to={`/learn/${course.id}/${prevItem.lesson.id}`}>
                  <Button variant="outline" size="sm" icon={<ChevronLeft className="w-4 h-4" />}>
                    Previous Lesson
                  </Button>
                </Link>
              ) : (
                <div />
              )}
            </div>

            <div className="flex items-center gap-3 w-full sm:w-auto justify-end">
              <Button
                variant={completed ? 'secondary' : 'glow'}
                size="sm"
                onClick={handleMarkComplete}
                icon={completed ? <CheckCircle2 className="w-4 h-4 text-emerald-400" /> : undefined}
              >
                {completed ? 'Completed (✓)' : 'Mark Lesson Complete'}
              </Button>

              {nextItem && (
                <Link to={`/learn/${course.id}/${nextItem.lesson.id}`}>
                  <Button variant="primary" size="sm" iconRight={<ChevronRight className="w-4 h-4" />}>
                    Next Lesson
                  </Button>
                </Link>
              )}
            </div>
          </div>
        </main>

        {/* Right AI Assistant Sidebar */}
        {aiSidebarOpen && (
          <aside className="w-80 sm:w-96 shrink-0 h-full">
            <AIChatPanel
              lessonTitle={currentLesson.title}
              courseTitle={course.title}
              onClose={() => setAiSidebarOpen(false)}
            />
          </aside>
        )}
      </div>
    </div>
  )
}
