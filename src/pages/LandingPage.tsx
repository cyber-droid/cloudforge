import { useState } from 'react'
import { Link } from 'react-router-dom'
import {
  ArrowRight,
  CheckCircle2,
  Terminal,
  Shield,
  Server,
  GitBranch,
  Layers,
  Activity,
  Sparkles,
  Zap,
  Play,
  Award,
  AlertTriangle,
  Cpu,
  RefreshCw,
  Eye,
  FileCode2,
  ExternalLink,
} from 'lucide-react'
import { Button } from '../components/common/Button'
import { Badge } from '../components/common/Badge'
import { Card } from '../components/common/Card'
import { PageContainer } from '../components/layout/PageContainer'
import { COURSES } from '../data/coursesData'
import { CERTIFICATIONS } from '../data/certificationsData'
import { PROJECTS } from '../data/projectsData'
import { INCIDENTS } from '../data/incidentsData'

export function LandingPage() {
  const [activePipelineStep, setActivePipelineStep] = useState<number>(4) // default to Kubernetes
  const [activeLifecycleTab, setActiveLifecycleTab] = useState<string>('troubleshoot')

  // Technical pipeline stages
  const pipelineStages = [
    { id: 0, title: 'Code', tool: 'Git / TypeScript', detail: 'Feature branch with pre-commit hooks & semantic commits', icon: <FileCode2 className="w-4 h-4 text-slate-300" /> },
    { id: 1, title: 'CI', tool: 'GitHub Actions', detail: 'Automated parallel test matrix & artifact build caching', icon: <GitBranch className="w-4 h-4 text-blue-400" /> },
    { id: 2, title: 'Security', tool: 'Semgrep & Trivy', detail: 'Zero-trust secret detection, SAST & OCI image CVE audit', icon: <Shield className="w-4 h-4 text-emerald-400" /> },
    { id: 3, title: 'Container', tool: 'Docker OCI', detail: 'Distroless multi-stage build, minimal attack surface', icon: <Layers className="w-4 h-4 text-cyan-400" /> },
    { id: 4, title: 'Kubernetes', tool: 'EKS / K8s', detail: 'Multi-AZ cluster scheduling, HPA & pod disruption budgets', icon: <Server className="w-4 h-4 text-indigo-400" /> },
    { id: 5, title: 'GitOps', tool: 'Argo CD', detail: 'Automated declarative reconciliation & zero-drift delivery', icon: <RefreshCw className="w-4 h-4 text-amber-400" /> },
    { id: 6, title: 'Observability', tool: 'Prometheus & OTel', detail: 'Distributed tracing spans, high-cardinality metrics & Loki logs', icon: <Eye className="w-4 h-4 text-purple-400" /> },
    { id: 7, title: 'AI Ops', tool: 'CloudForge AI', detail: 'Automated incident root cause reasoning & patch proposals', icon: <Sparkles className="w-4 h-4 text-rose-400" /> },
  ]

  // Tech stack ecosystem logos/badges
  const techLogos = [
    { name: 'AWS', color: 'text-amber-400' },
    { name: 'Microsoft Azure', color: 'text-blue-400' },
    { name: 'Docker', color: 'text-cyan-400' },
    { name: 'Kubernetes', color: 'text-indigo-400' },
    { name: 'Terraform', color: 'text-purple-400' },
    { name: 'Ansible', color: 'text-rose-400' },
    { name: 'GitHub Actions', color: 'text-slate-200' },
    { name: 'Argo CD', color: 'text-amber-300' },
    { name: 'Prometheus', color: 'text-orange-400' },
    { name: 'Grafana', color: 'text-amber-500' },
    { name: 'OpenTelemetry', color: 'text-blue-300' },
  ]

  // 7-phase Lifecycle descriptions
  const lifecycleSteps = [
    { id: 'learn', label: 'Learn', subtitle: 'Deep technical fundamentals', desc: 'Deconstruct internal operating mechanics of the Linux kernel, Kubernetes control plane, and cloud network virtualization rather than shallow syntax tutorials.' },
    { id: 'build', label: 'Build', subtitle: 'Production architectures', desc: 'Provision multi-tier VPCs, write hardened Helm charts, author reusable Terraform modules, and assemble declarative CI/CD delivery pipelines.' },
    { id: 'break', label: 'Break', subtitle: 'Simulated chaos injection', desc: 'Purposefully trigger network partitions, memory exhaustion (OOM), expired certificates, IAM permission boundary lockouts, and DNS lookup degradation.' },
    { id: 'troubleshoot', label: 'Troubleshoot', subtitle: 'Live incident triage', desc: 'Analyze real stdout/stderr container logs, trace latency bottlenecks across spans in Tempo, and diagnose CrashLoopBackOff exit codes in a browser sandbox.' },
    { id: 'deploy', label: 'Deploy', subtitle: 'Zero-downtime rollouts', desc: 'Execute GitOps reconciliations, progressive canary releases with Argo Rollouts, and automated blue/green traffic shifts validated against metrics.' },
    { id: 'observe', label: 'Observe', subtitle: 'Telemetry & SLO budgets', desc: 'Establish Service Level Indicators (SLIs), craft high-signal Alertmanager routes, and correlate metrics, logs, and traces into unified Grafana dashboards.' },
    { id: 'improve', label: 'Improve', subtitle: 'Continuous SRE hardening', desc: 'Conduct blameless post-mortems, optimize cloud FinOps unit costs, automate runbooks, and leverage AI to prevent recurring failure patterns.' },
  ]

  // Domains
  const domains = [
    { title: 'Cloud Computing', count: '4 Courses', icon: <Layers className="w-5 h-5 text-cyan-400" />, desc: 'AWS & Azure multi-region VPC design, IAM least-privilege, and cloud economics.' },
    { title: 'DevOps Engineering', count: '6 Courses', icon: <GitBranch className="w-5 h-5 text-blue-400" />, desc: 'Linux system internals, Git trunk-based hygiene, and resilient GitHub Actions pipelines.' },
    { title: 'DevSecOps', count: '3 Courses', icon: <Shield className="w-5 h-5 text-emerald-400" />, desc: 'Pre-commit secret detection, Semgrep SAST, Trivy OCI scanning, and signed SBOMs.' },
    { title: 'Kubernetes Orchestration', count: '5 Courses', icon: <Server className="w-5 h-5 text-indigo-400" />, desc: 'Pod lifecycles, CNI networking, ingress controllers, RBAC, and Helm packaging.' },
    { title: 'Infrastructure as Code', count: '3 Courses', icon: <Cpu className="w-5 h-5 text-purple-400" />, desc: 'Declarative Terraform HCL2, remote S3 state locks, and zero-duplication modules.' },
    { title: 'Cloud Security', count: '3 Courses', icon: <Shield className="w-5 h-5 text-rose-400" />, desc: 'IMDSv2 defense, KMS customer key rotation, GuardDuty, and CIS compliance.' },
    { title: 'Observability & SRE', count: '4 Courses', icon: <Activity className="w-5 h-5 text-amber-400" />, desc: 'Prometheus metrics, Loki logging, OpenTelemetry tracing, and SLO error budgets.' },
    { title: 'AI for Cloud & DevOps', count: '3 Courses', icon: <Sparkles className="w-5 h-5 text-cyan-300" />, desc: 'LLM agents, RAG over runbooks, automated CI failure triage, and MCP integrations.' },
  ]

  return (
    <div className="flex flex-col min-h-screen bg-slate-950 text-slate-100 selection:bg-cyan-500/20 selection:text-cyan-300">
      {/* Hero Section */}
      <section className="relative pt-12 pb-20 lg:pt-20 lg:pb-28 overflow-hidden bg-grid-pattern border-b border-slate-800/80">
        <div className="absolute inset-0 bg-radial-glow pointer-events-none" />

        <PageContainer>
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-8 items-center">
            {/* Left Hero Content */}
            <div className="lg:col-span-7 flex flex-col items-start text-left">
              {/* Engineering Tag Badge */}
              <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-900/90 border border-slate-800 text-xs font-mono text-cyan-300 mb-6 shadow-sm">
                <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
                <span>AI-Assisted Cloud & DevOps Engineering Platform</span>
              </div>

              {/* Headline */}
              <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold text-white tracking-tight leading-[1.1] mb-6">
                Master Cloud & DevOps by{' '}
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-sky-300 to-indigo-400">
                  Building Real Systems.
                </span>
              </h1>

              {/* Supporting text */}
              <p className="text-base sm:text-lg text-slate-300 max-w-2xl leading-relaxed mb-8 font-normal">
                CloudForge combines structured learning, real-world projects, DevSecOps practices, Kubernetes, GitOps, observability and AI-assisted engineering into one platform.
              </p>

              {/* CTAs */}
              <div className="flex flex-wrap items-center gap-4 w-full sm:w-auto">
                <Link to="/courses">
                  <Button variant="glow" size="lg" iconRight={<ArrowRight className="w-4 h-4" />}>
                    Start Learning
                  </Button>
                </Link>
                <Link to="/roadmaps">
                  <Button variant="secondary" size="lg" icon={<GitBranch className="w-4 h-4 text-purple-400" />}>
                    Explore Learning Paths
                  </Button>
                </Link>
                <Link to="/troubleshooting" className="text-xs font-mono text-slate-400 hover:text-cyan-300 flex items-center gap-1.5 px-3 py-2 transition-colors">
                  <Terminal className="w-3.5 h-3.5 text-rose-400" />
                  <span>Try Incident Sandbox ➔</span>
                </Link>
              </div>

              {/* Stats Bar */}
              <div className="mt-12 pt-8 border-t border-slate-800/80 grid grid-cols-3 gap-6 sm:gap-10 w-full">
                <div>
                  <div className="text-2xl font-bold font-mono text-white">42+</div>
                  <div className="text-xs text-slate-400 mt-0.5">Deep Modules</div>
                </div>
                <div>
                  <div className="text-2xl font-bold font-mono text-cyan-400">8</div>
                  <div className="text-xs text-slate-400 mt-0.5">Production Projects</div>
                </div>
                <div>
                  <div className="text-2xl font-bold font-mono text-indigo-400">6</div>
                  <div className="text-xs text-slate-400 mt-0.5">Cert Prep Tracks</div>
                </div>
              </div>
            </div>

            {/* Right Hero Visual: Interactive Engineering Pipeline Visualizer */}
            <div className="lg:col-span-5">
              <div className="relative rounded-2xl border border-slate-800 bg-slate-900/90 shadow-2xl p-5 backdrop-blur-xl">
                {/* Header terminal controls */}
                <div className="flex items-center justify-between pb-3 mb-4 border-b border-slate-800 text-xs font-mono text-slate-400">
                  <div className="flex items-center gap-2">
                    <span className="w-2.5 h-2.5 rounded-full bg-rose-500/80" />
                    <span className="w-2.5 h-2.5 rounded-full bg-amber-500/80" />
                    <span className="w-2.5 h-2.5 rounded-full bg-emerald-500/80" />
                    <span className="text-[11px] text-slate-300 font-medium ml-2">cloudforge-pipeline.yml</span>
                  </div>
                  <span className="text-[10px] text-cyan-400 bg-cyan-950/60 px-2 py-0.5 rounded border border-cyan-800/40">
                    LIVE TELEMETRY
                  </span>
                </div>

                {/* Pipeline Flow Steps */}
                <div className="space-y-2">
                  {pipelineStages.map((stage, idx) => {
                    const isSelected = activePipelineStep === stage.id
                    return (
                      <div
                        key={stage.id}
                        onClick={() => setActivePipelineStep(stage.id)}
                        className={`p-2.5 rounded-xl border transition-all cursor-pointer flex items-center justify-between ${
                          isSelected
                            ? 'bg-slate-800/90 border-cyan-500/50 shadow-md shadow-cyan-950/20'
                            : 'bg-slate-950/40 border-slate-800/80 hover:border-slate-700 hover:bg-slate-900/60'
                        }`}
                      >
                        <div className="flex items-center gap-3 min-w-0">
                          <div className={`p-1.5 rounded-lg border ${isSelected ? 'bg-slate-900 border-cyan-500/40' : 'bg-slate-900/80 border-slate-800'}`}>
                            {stage.icon}
                          </div>
                          <div className="min-w-0">
                            <div className="flex items-center gap-2">
                              <span className={`text-xs font-semibold ${isSelected ? 'text-cyan-300' : 'text-slate-200'}`}>
                                {stage.title}
                              </span>
                              <span className="text-[10px] font-mono text-slate-500">
                                {stage.tool}
                              </span>
                            </div>
                            {isSelected && (
                              <p className="text-[11px] text-slate-400 mt-0.5 animate-in fade-in duration-200">
                                {stage.detail}
                              </p>
                            )}
                          </div>
                        </div>

                        <div className="flex items-center gap-2 shrink-0">
                          {idx < pipelineStages.length - 1 && (
                            <span className="text-slate-600 text-xs font-mono">↓</span>
                          )}
                          <span className={`w-2 h-2 rounded-full ${isSelected ? 'bg-cyan-400 animate-ping' : 'bg-slate-700'}`} />
                        </div>
                      </div>
                    )
                  })}
                </div>

                {/* Selected Node Status Footer */}
                <div className="mt-4 p-3 rounded-xl bg-slate-950/80 border border-slate-800 text-xs font-mono flex items-center justify-between">
                  <div className="flex items-center gap-2 text-slate-400">
                    <Terminal className="w-3.5 h-3.5 text-cyan-400" />
                    <span>State:</span>
                    <span className="text-emerald-400 font-semibold">RECONCILED (0 errors)</span>
                  </div>
                  <Link to="/courses" className="text-cyan-400 hover:text-cyan-300 flex items-center gap-1 text-[11px]">
                    <span>Inspect</span>
                    <ExternalLink className="w-3 h-3" />
                  </Link>
                </div>
              </div>
            </div>
          </div>
        </PageContainer>
      </section>

      {/* 2. Trusted Technology Ecosystem */}
      <section className="py-12 border-b border-slate-800/80 bg-slate-950/60">
        <PageContainer>
          <p className="text-center text-xs font-mono uppercase tracking-widest text-slate-500 mb-8">
            Engineered for the Modern Cloud & DevOps Stack
          </p>
          <div className="flex flex-wrap items-center justify-center gap-3 sm:gap-4 max-w-5xl mx-auto">
            {techLogos.map(tech => (
              <div
                key={tech.name}
                className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-slate-900/80 border border-slate-800/90 text-xs font-mono font-medium hover:border-slate-700 hover:bg-slate-900 transition-all cursor-default group"
              >
                <span className={`font-bold ${tech.color}`}>◆</span>
                <span className="text-slate-300 group-hover:text-white transition-colors">{tech.name}</span>
              </div>
            ))}
          </div>
        </PageContainer>
      </section>

      {/* 3. "Learn the complete engineering lifecycle" */}
      <section className="py-20 border-b border-slate-800/80 bg-slate-900/20">
        <PageContainer>
          <div className="text-center max-w-3xl mx-auto mb-12">
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-cyan-950/60 border border-cyan-800/50 text-cyan-300 text-xs font-mono mb-4">
              <Zap className="w-3.5 h-3.5" />
              <span>THE ENGINEERING LIFECYCLE</span>
            </div>
            <h2 className="text-3xl sm:text-4xl font-bold text-white tracking-tight">
              Learn the Complete Engineering Lifecycle
            </h2>
            <p className="text-slate-400 text-sm sm:text-base mt-3 leading-relaxed">
              Don't just watch videos. Step inside a full continuous delivery feedback loop: code it, containerize it, trigger chaos, investigate the logs, and optimize production performance.
            </p>
          </div>

          {/* Interactive Lifecycle Tabs */}
          <div className="flex flex-wrap items-center justify-center gap-2 mb-8">
            {lifecycleSteps.map(step => {
              const isActive = activeLifecycleTab === step.id
              return (
                <button
                  key={step.id}
                  onClick={() => setActiveLifecycleTab(step.id)}
                  className={`px-4 py-2 rounded-xl text-xs font-mono uppercase tracking-wider font-semibold transition-all cursor-pointer ${
                    isActive
                      ? 'bg-cyan-500 text-slate-950 shadow-md shadow-cyan-500/20'
                      : 'bg-slate-900 text-slate-400 hover:text-white hover:bg-slate-800 border border-slate-800'
                  }`}
                >
                  {step.label}
                </button>
              )
            })}
          </div>

          {/* Active Lifecycle Display Card */}
          {(() => {
            const current = lifecycleSteps.find(s => s.id === activeLifecycleTab) || lifecycleSteps[0]
            return (
              <div className="max-w-3xl mx-auto p-8 rounded-2xl border border-slate-800 bg-slate-900/80 shadow-xl backdrop-blur-sm animate-in fade-in duration-150">
                <div className="flex items-center justify-between mb-4">
                  <span className="text-xs font-mono text-cyan-400 uppercase tracking-wider">
                    Phase: {current.label}
                  </span>
                  <span className="text-xs text-slate-400 font-medium">
                    {current.subtitle}
                  </span>
                </div>
                <h3 className="text-xl font-bold text-white mb-3">
                  How CloudForge trains "{current.label}"
                </h3>
                <p className="text-slate-300 text-sm leading-relaxed mb-6">
                  {current.desc}
                </p>
                <div className="flex items-center gap-4 pt-4 border-t border-slate-800">
                  <Link to="/courses">
                    <Button variant="secondary" size="sm" iconRight={<ArrowRight className="w-3.5 h-3.5" />}>
                      Explore {current.label} Modules
                    </Button>
                  </Link>
                  <Link to="/troubleshooting" className="text-xs font-mono text-slate-400 hover:text-cyan-300 transition-colors">
                    View Sandbox Scenarios ➔
                  </Link>
                </div>
              </div>
            )
          })()}
        </PageContainer>
      </section>

      {/* 4. Learning Domains */}
      <section className="py-20 border-b border-slate-800/80">
        <PageContainer>
          <div className="flex flex-col md:flex-row md:items-end justify-between mb-12 gap-4">
            <div>
              <span className="text-xs font-mono text-cyan-400 uppercase tracking-wider">Core Specializations</span>
              <h2 className="text-3xl font-bold text-white tracking-tight mt-1">
                Engineering Domains
              </h2>
            </div>
            <Link to="/courses">
              <Button variant="outline" size="sm" iconRight={<ArrowRight className="w-3.5 h-3.5" />}>
                Browse All 9 Deep-Dive Courses
              </Button>
            </Link>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
            {domains.map(d => (
              <Card key={d.title} className="flex flex-col justify-between hover:border-slate-700 transition-all group">
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <div className="p-2.5 rounded-xl bg-slate-800/80 border border-slate-700/60 group-hover:border-slate-600 transition-colors">
                      {d.icon}
                    </div>
                    <span className="text-[11px] font-mono text-slate-500">{d.count}</span>
                  </div>
                  <h3 className="text-base font-semibold text-white group-hover:text-cyan-300 transition-colors">
                    {d.title}
                  </h3>
                  <p className="text-xs text-slate-400 mt-2 leading-relaxed">
                    {d.desc}
                  </p>
                </div>
                <div className="mt-6 pt-4 border-t border-slate-800/80 flex items-center justify-between">
                  <Link
                    to="/courses"
                    className="text-xs font-mono text-slate-400 group-hover:text-cyan-400 flex items-center gap-1 transition-colors"
                  >
                    <span>View Curriculum</span>
                    <ArrowRight className="w-3 h-3 group-hover:translate-x-0.5 transition-transform" />
                  </Link>
                </div>
              </Card>
            ))}
          </div>
        </PageContainer>
      </section>

      {/* 5. Industry Certification Preparation */}
      <section className="py-20 border-b border-slate-800/80 bg-slate-900/20">
        <PageContainer>
          <div className="flex flex-col md:flex-row md:items-end justify-between mb-12 gap-4">
            <div>
              <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-amber-950/60 border border-amber-800/50 text-amber-300 text-xs font-mono mb-2">
                <Award className="w-3.5 h-3.5" />
                <span>EXAM PREPARATION TRACKS</span>
              </div>
              <h2 className="text-3xl font-bold text-white tracking-tight">
                Prepare for Industry Certifications
              </h2>
              <p className="text-xs text-slate-400 mt-1 font-mono">
                Prepare with CloudForge training courses and realistic timed mock assessments.
              </p>
            </div>
            <Link to="/certifications">
              <Button variant="secondary" size="sm" iconRight={<ArrowRight className="w-3.5 h-3.5" />}>
                View All Certification Hubs
              </Button>
            </Link>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {CERTIFICATIONS.slice(0, 6).map(cert => (
              <Card key={cert.id} className="flex flex-col justify-between hover:border-amber-500/40 transition-all group">
                <div>
                  <div className="flex items-start justify-between gap-2 mb-3">
                    <Badge variant={cert.provider === 'AWS' ? 'amber' : cert.provider === 'Microsoft Azure' ? 'blue' : 'purple'}>
                      {cert.provider}
                    </Badge>
                    {cert.code && (
                      <span className="text-xs font-mono font-bold text-slate-300 bg-slate-800 px-2 py-0.5 rounded border border-slate-700/60">
                        {cert.code}
                      </span>
                    )}
                  </div>

                  <h3 className="text-lg font-bold text-white group-hover:text-amber-300 transition-colors">
                    {cert.title}
                  </h3>
                  <p className="text-xs text-slate-400 mt-2 leading-relaxed line-clamp-2">
                    {cert.description}
                  </p>

                  <div className="mt-4 p-3 rounded-lg bg-slate-950/60 border border-slate-800 text-xs font-mono space-y-1.5">
                    <div className="flex justify-between text-slate-400">
                      <span>Practice Question Bank:</span>
                      <span className="text-slate-200">{cert.practiceQuestionsCount}+ Qs</span>
                    </div>
                    <div className="flex justify-between text-slate-400">
                      <span>Mock Exams Included:</span>
                      <span className="text-slate-200">{cert.mockExamsCount} Full Exams</span>
                    </div>
                  </div>
                </div>

                <div className="mt-6 pt-4 border-t border-slate-800 flex items-center justify-between">
                  <span className="text-[11px] text-slate-500 font-mono">
                    CloudForge Training Track
                  </span>
                  <Link to={`/certifications/${cert.id}`}>
                    <Button variant="outline" size="sm">
                      Start Prep ➔
                    </Button>
                  </Link>
                </div>
              </Card>
            ))}
          </div>

          {/* Explicit disclaimer callout */}
          <div className="mt-8 p-4 rounded-xl bg-slate-900/60 border border-slate-800 text-xs font-mono text-slate-400 text-center max-w-2xl mx-auto">
            ℹ️ CloudForge issues verified Training Certificates upon course completion. Official certification exams (AWS, Azure, Linux Foundation) must be scheduled directly through vendor testing centers.
          </div>
        </PageContainer>
      </section>

      {/* 6. Real-World Production Projects */}
      <section className="py-20 border-b border-slate-800/80">
        <PageContainer>
          <div className="flex flex-col md:flex-row md:items-end justify-between mb-12 gap-4">
            <div>
              <span className="text-xs font-mono text-cyan-400 uppercase tracking-wider">Applied Engineering</span>
              <h2 className="text-3xl font-bold text-white tracking-tight mt-1">
                Real-World Projects
              </h2>
              <p className="text-xs text-slate-400 mt-1">
                Build portfolio-ready architectures tested against real production workloads.
              </p>
            </div>
            <Link to="/projects">
              <Button variant="outline" size="sm" iconRight={<ArrowRight className="w-3.5 h-3.5" />}>
                Explore All 8 Projects
              </Button>
            </Link>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {PROJECTS.slice(0, 6).map(proj => (
              <Card key={proj.id} className="flex flex-col justify-between hover:border-cyan-500/40 transition-all group">
                <div>
                  <div className="flex items-center justify-between mb-3">
                    <Badge variant={proj.difficulty === 'Advanced' ? 'rose' : proj.difficulty === 'Intermediate' ? 'amber' : 'emerald'}>
                      {proj.difficulty}
                    </Badge>
                    <span className="text-xs font-mono text-slate-400">{proj.estimatedHours}</span>
                  </div>

                  <h3 className="text-base font-bold text-white group-hover:text-cyan-300 transition-colors">
                    {proj.title}
                  </h3>
                  <p className="text-xs text-slate-400 mt-2 leading-relaxed line-clamp-3">
                    {proj.description}
                  </p>

                  <div className="flex flex-wrap gap-1.5 mt-4">
                    {proj.technologies.slice(0, 4).map(t => (
                      <span key={t} className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800/80 text-slate-300 border border-slate-700/60">
                        {t}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="mt-6 pt-4 border-t border-slate-800 flex items-center justify-between">
                  <span className="text-xs font-mono text-slate-500">
                    {proj.tasks.length} Architecture Milestones
                  </span>
                  <Link to={`/projects/${proj.id}`}>
                    <Button variant="secondary" size="xs">
                      View Specs ➔
                    </Button>
                  </Link>
                </div>
              </Card>
            ))}
          </div>
        </PageContainer>
      </section>

      {/* 7. AI Engineering Section */}
      <section className="py-20 border-b border-slate-800/80 bg-slate-900/30">
        <PageContainer>
          <div className="text-center max-w-3xl mx-auto mb-14">
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-purple-950/60 border border-purple-800/50 text-purple-300 text-xs font-mono mb-3">
              <Sparkles className="w-3.5 h-3.5" />
              <span>AI THAT UNDERSTANDS INFRASTRUCTURE</span>
            </div>
            <h2 className="text-3xl sm:text-4xl font-bold text-white tracking-tight">
              AI That Understands Your Engineering Context
            </h2>
            <p className="text-slate-400 text-sm sm:text-base mt-3 leading-relaxed">
              Generic chatbots guess. CloudForge AI parses real Kubernetes manifests, inspects container exit codes, correlates Prometheus metrics, and generates verified diff patches.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <Card className="hover:border-purple-500/40 transition-all">
              <div className="p-2.5 w-fit rounded-xl bg-purple-950/60 border border-purple-800/50 mb-4">
                <Sparkles className="w-5 h-5 text-purple-400" />
              </div>
              <h3 className="text-base font-bold text-white">AI Learning Assistant</h3>
              <p className="text-xs text-slate-400 mt-2 leading-relaxed">
                Integrated directly inside lesson players. Asks diagnostic questions, generates YAML manifests on demand, and explains subtle architectural tradeoffs.
              </p>
            </Card>

            <Card className="hover:border-cyan-500/40 transition-all">
              <div className="p-2.5 w-fit rounded-xl bg-cyan-950/60 border border-cyan-800/50 mb-4">
                <Terminal className="w-5 h-5 text-cyan-400" />
              </div>
              <h3 className="text-base font-bold text-white">AI CI/CD Failure Analyzer</h3>
              <p className="text-xs text-slate-400 mt-2 leading-relaxed">
                Paste or stream raw GitHub Actions runners build logs. The analyzer isolates fatal stack traces and produces a git-diff pull request ready to apply.
              </p>
            </Card>

            <Card className="hover:border-rose-500/40 transition-all">
              <div className="p-2.5 w-fit rounded-xl bg-rose-950/60 border border-rose-800/50 mb-4">
                <AlertTriangle className="w-5 h-5 text-rose-400" />
              </div>
              <h3 className="text-base font-bold text-white">AI Incident Investigator</h3>
              <p className="text-xs text-slate-400 mt-2 leading-relaxed">
                Triages production alerts by correlating pod readiness probes, ingress HTTP 502 logs, and resource exhaustion without claiming certainty prematurely.
              </p>
            </Card>

            <Card className="hover:border-blue-500/40 transition-all">
              <div className="p-2.5 w-fit rounded-xl bg-blue-950/60 border border-blue-800/50 mb-4">
                <Layers className="w-5 h-5 text-blue-400" />
              </div>
              <h3 className="text-base font-bold text-white">AI Documentation Assistant</h3>
              <p className="text-xs text-slate-400 mt-2 leading-relaxed">
                Generates architecture decision records (ADRs), Runbook run-steps, and OpenAPI specs directly from your verified Terraform and K8s manifests.
              </p>
            </Card>

            <Card className="hover:border-indigo-500/40 transition-all">
              <div className="p-2.5 w-fit rounded-xl bg-indigo-950/60 border border-indigo-800/50 mb-4">
                <Cpu className="w-5 h-5 text-indigo-400" />
              </div>
              <h3 className="text-base font-bold text-white">RAG Knowledge Assistant</h3>
              <p className="text-xs text-slate-400 mt-2 leading-relaxed">
                Vector-indexed against official AWS, Kubernetes, and HashiCorp documentation to provide cited, accurate answers with zero hallucination.
              </p>
            </Card>

            <Card className="hover:border-emerald-500/40 transition-all">
              <div className="p-2.5 w-fit rounded-xl bg-emerald-950/60 border border-emerald-800/50 mb-4">
                <Shield className="w-5 h-5 text-emerald-400" />
              </div>
              <h3 className="text-base font-bold text-white">Autonomous Agent Playground</h3>
              <p className="text-xs text-slate-400 mt-2 leading-relaxed">
                Experiment with Model Context Protocol (MCP) tool-calling agents that can query cluster APIs safely with mandatory human approval gates.
              </p>
            </Card>
          </div>

          <div className="mt-10 text-center">
            <Link to="/ai">
              <Button variant="primary" size="md" iconRight={<ArrowRight className="w-4 h-4" />}>
                Explore AI Engineering Workbench
              </Button>
            </Link>
          </div>
        </PageContainer>
      </section>

      {/* 8. Troubleshooting Section Preview */}
      <section className="py-20 border-b border-slate-800/80">
        <PageContainer>
          <div className="flex flex-col md:flex-row md:items-end justify-between mb-12 gap-4">
            <div>
              <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-rose-950/60 border border-rose-800/50 text-rose-300 text-xs font-mono mb-2">
                <AlertTriangle className="w-3.5 h-3.5" />
                <span>REALISTIC INCIDENTS</span>
              </div>
              <h2 className="text-3xl font-bold text-white tracking-tight">
                Learn by Breaking Real Systems
              </h2>
              <p className="text-xs text-slate-400 mt-1">
                Solve real production outages: examine terminal logs, inspect metrics, and fix configurations.
              </p>
            </div>
            <Link to="/troubleshooting">
              <Button variant="secondary" size="sm" iconRight={<ArrowRight className="w-3.5 h-3.5" />}>
                Launch Troubleshooting Center
              </Button>
            </Link>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {INCIDENTS.slice(0, 6).map(inc => (
              <Card key={inc.id} className="flex flex-col justify-between hover:border-rose-500/40 transition-all group">
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-mono font-bold text-slate-300 bg-slate-800 px-2 py-0.5 rounded border border-slate-700/60">
                      {inc.incidentId}
                    </span>
                    <Badge variant={inc.severityColor}>
                      {inc.severity.split(' - ')[0]}
                    </Badge>
                  </div>

                  <h3 className="text-base font-bold text-white group-hover:text-rose-300 transition-colors mt-2">
                    {inc.title}
                  </h3>

                  <p className="text-xs text-slate-400 mt-2 leading-relaxed line-clamp-2">
                    {inc.symptoms}
                  </p>

                  <div className="mt-4 flex flex-wrap gap-1.5">
                    {inc.skills.map(s => (
                      <span key={s} className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300">
                        {s}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="mt-6 pt-4 border-t border-slate-800 flex items-center justify-between">
                  <span className="text-[11px] font-mono text-slate-500">
                    Status: <span className={inc.status === 'Resolved' ? 'text-emerald-400' : 'text-amber-400'}>{inc.status}</span>
                  </span>
                  <Link to={`/troubleshooting/${inc.id}`}>
                    <Button variant="outline" size="xs">
                      Investigate ➔
                    </Button>
                  </Link>
                </div>
              </Card>
            ))}
          </div>
        </PageContainer>
      </section>

      {/* 9. Final CTA */}
      <section className="py-24 relative overflow-hidden bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950 border-t border-slate-800">
        <div className="absolute inset-0 bg-radial-glow pointer-events-none" />
        <PageContainer>
          <div className="max-w-3xl mx-auto text-center space-y-6">
            <h2 className="text-3xl sm:text-5xl font-extrabold text-white tracking-tight">
              Build Your Cloud Engineering Career.
            </h2>
            <p className="text-slate-300 text-base sm:text-lg leading-relaxed">
              Stop memorizing slide decks. Start deploying, debugging, and observing production-grade cloud systems with AI assistance today.
            </p>
            <div className="flex flex-wrap items-center justify-center gap-4 pt-4">
              <Link to="/courses">
                <Button variant="glow" size="lg" iconRight={<ArrowRight className="w-4 h-4" />}>
                  Explore CloudForge
                </Button>
              </Link>
              <Link to="/register">
                <Button variant="secondary" size="lg">
                  Create Free Account
                </Button>
              </Link>
            </div>
          </div>
        </PageContainer>
      </section>
    </div>
  )
}
