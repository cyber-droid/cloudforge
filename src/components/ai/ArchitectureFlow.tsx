import { User, Cpu, Database, Wrench, Sparkles, CheckSquare, ArrowRight } from 'lucide-react'

export function ArchitectureFlow() {
  const steps = [
    { title: 'Engineer', subtitle: 'Developer Prompt / Alert', icon: <User className="w-4 h-4 text-slate-200" /> },
    { title: 'AI Gateway', subtitle: 'FastAPI / Rate Limiter', icon: <Cpu className="w-4 h-4 text-cyan-400" /> },
    { title: 'Context Retrieval', subtitle: 'Vector RAG & Runbooks', icon: <Database className="w-4 h-4 text-purple-400" /> },
    { title: 'Tools & Observability', subtitle: 'Prometheus, kubectl, CI', icon: <Wrench className="w-4 h-4 text-amber-400" /> },
    { title: 'AI Reasoning', subtitle: 'Structured Schema LLM', icon: <Sparkles className="w-4 h-4 text-rose-400" /> },
    { title: 'Recommendation', subtitle: 'Root Cause & Diff Patch', icon: <Cpu className="w-4 h-4 text-blue-400" /> },
    { title: 'Human Approval', subtitle: 'Manual Apply Gate', icon: <CheckSquare className="w-4 h-4 text-emerald-400" /> },
  ]

  return (
    <div className="p-6 rounded-2xl border border-slate-800 bg-slate-900/60 space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-4 border-b border-slate-800">
        <div>
          <h3 className="text-base font-bold text-white">
            CloudForge Autonomous AI Architecture
          </h3>
          <p className="text-xs text-slate-400 font-mono mt-0.5">
            Deterministic tool calling with mandatory human-in-the-loop safety boundaries
          </p>
        </div>
        <span className="text-xs font-mono text-cyan-400 bg-cyan-950 px-2.5 py-1 rounded-full border border-cyan-800/60">
          MCP COMPATIBLE
        </span>
      </div>

      {/* Horizontal / Grid Flow */}
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-3">
        {steps.map((step, idx) => (
          <div
            key={step.title}
            className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 flex flex-col justify-between space-y-3 relative group hover:border-slate-700 transition-colors"
          >
            <div className="flex items-center justify-between">
              <div className="p-2 rounded-lg bg-slate-900 border border-slate-800">
                {step.icon}
              </div>
              <span className="text-[10px] font-mono text-slate-500 font-bold">
                0{idx + 1}
              </span>
            </div>

            <div>
              <h4 className="text-xs font-bold text-white group-hover:text-cyan-300 transition-colors">
                {step.title}
              </h4>
              <p className="text-[10px] text-slate-400 font-mono mt-0.5 leading-tight">
                {step.subtitle}
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
