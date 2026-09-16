import { Sparkles, Terminal, AlertTriangle, Layers, Cpu, Shield, ArrowRight } from 'lucide-react'
import { PageContainer } from '../components/layout/PageContainer'
import { Card } from '../components/common/Card'
import { ArchitectureFlow } from '../components/ai/ArchitectureFlow'
import { CICDLogAnalyzer } from '../components/ai/CICDLogAnalyzer'
import { Button } from '../components/common/Button'
import { Link } from 'react-router-dom'

export function AIEngineeringPage() {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 pb-16">
      {/* Header */}
      <div className="border-b border-slate-800 bg-slate-950/80 py-12">
        <PageContainer>
          <div className="max-w-3xl space-y-3">
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-purple-950/60 border border-purple-800/50 text-purple-300 text-xs font-mono">
              <Sparkles className="w-3.5 h-3.5" />
              <span>CONTEXTUAL SRE INTELLIGENCE</span>
            </div>
            <h1 className="text-3xl sm:text-5xl font-extrabold text-white tracking-tight">
              AI for Cloud & DevOps
            </h1>
            <p className="text-sm sm:text-base text-slate-300 leading-relaxed">
              Use AI to understand systems, investigate failures, and accelerate engineering workflows. Designed with deterministic JSON outputs and human-in-the-loop safeguards.
            </p>
          </div>
        </PageContainer>
      </div>

      <PageContainer>
        <div className="space-y-12">
          {/* Architecture Pipeline Visualizer */}
          <ArchitectureFlow />

          {/* Interactive Tool: Live CI/CD Log Analyzer */}
          <CICDLogAnalyzer />

          {/* Feature Suite Cards */}
          <div>
            <h2 className="text-xl font-bold text-white mb-4">
              AI Engineering Capabilities
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              <Card className="p-6 space-y-3 hover:border-purple-500/40 transition-all">
                <div className="p-2.5 w-fit rounded-xl bg-purple-950/60 border border-purple-800/50 text-purple-400">
                  <Sparkles className="w-5 h-5" />
                </div>
                <h3 className="text-base font-bold text-white">AI Learning Assistant</h3>
                <p className="text-xs text-slate-400 leading-relaxed">
                  Interactive copilot in every lesson player. Can quiz your architectural knowledge, break down complex concepts, and generate custom Kubernetes manifests.
                </p>
              </Card>

              <Card className="p-6 space-y-3 hover:border-cyan-500/40 transition-all">
                <div className="p-2.5 w-fit rounded-xl bg-cyan-950/60 border border-cyan-800/50 text-cyan-400">
                  <Terminal className="w-5 h-5" />
                </div>
                <h3 className="text-base font-bold text-white">AI CI/CD Failure Analyzer</h3>
                <p className="text-xs text-slate-400 leading-relaxed">
                  Parses build and test logs from GitHub Actions, Jenkins, or GitLab CI to extract fatal errors and suggest concrete code changes.
                </p>
              </Card>

              <Card className="p-6 space-y-3 hover:border-rose-500/40 transition-all">
                <div className="p-2.5 w-fit rounded-xl bg-rose-950/60 border border-rose-800/50 text-rose-400">
                  <AlertTriangle className="w-5 h-5" />
                </div>
                <h3 className="text-base font-bold text-white">AI Incident Investigator</h3>
                <p className="text-xs text-slate-400 leading-relaxed">
                  Correlates telemetry metrics, logs, and traces during active outages to produce reasoned root-cause hypotheses with confidence ratings.
                </p>
              </Card>

              <Card className="p-6 space-y-3 hover:border-blue-500/40 transition-all">
                <div className="p-2.5 w-fit rounded-xl bg-blue-950/60 border border-blue-800/50 text-blue-400">
                  <Layers className="w-5 h-5" />
                </div>
                <h3 className="text-base font-bold text-white">AI Documentation Assistant</h3>
                <p className="text-xs text-slate-400 leading-relaxed">
                  Extracts infrastructure topology from Terraform and Kubernetes manifests to generate accurate runbooks and architecture docs.
                </p>
              </Card>

              <Card className="p-6 space-y-3 hover:border-indigo-500/40 transition-all">
                <div className="p-2.5 w-fit rounded-xl bg-indigo-950/60 border border-indigo-800/50 text-indigo-400">
                  <Cpu className="w-5 h-5" />
                </div>
                <h3 className="text-base font-bold text-white">RAG Knowledge Assistant</h3>
                <p className="text-xs text-slate-400 leading-relaxed">
                  Vector-indexed against official cloud provider docs, Kubernetes APIs, and CNCF projects for hallucination-free technical guidance.
                </p>
              </Card>

              <Card className="p-6 space-y-3 hover:border-emerald-500/40 transition-all">
                <div className="p-2.5 w-fit rounded-xl bg-emerald-950/60 border border-emerald-800/50 text-emerald-400">
                  <Shield className="w-5 h-5" />
                </div>
                <h3 className="text-base font-bold text-white">AI Agent Playground</h3>
                <p className="text-xs text-slate-400 leading-relaxed">
                  Test autonomous DevOps agents with tool-calling capabilities adhering to strict read-only and human-approval safety gates.
                </p>
              </Card>
            </div>
          </div>
        </div>
      </PageContainer>
    </div>
  )
}
