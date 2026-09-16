import { Link } from 'react-router-dom'
import { CheckCircle2, ShieldCheck, Terminal, Disc as Discord } from 'lucide-react'
import { GithubIcon, TwitterIcon, LinkedinIcon } from '../common/BrandIcons'

export function Footer() {
  return (
    <footer className="border-t border-slate-800/80 bg-slate-950 text-slate-400 text-xs">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 lg:py-16">
        <div className="grid grid-cols-2 md:grid-cols-5 gap-8 lg:gap-12">
          {/* Brand Column */}
          <div className="col-span-2 space-y-4">
            <Link to="/" className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-cyan-500 via-indigo-500 to-purple-600 p-0.5 shadow-md shadow-cyan-500/10">
                <div className="w-full h-full bg-slate-950 rounded-[10px] flex items-center justify-center">
                  <svg
                    className="w-4 h-4 text-cyan-400"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2.2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  >
                    <path d="M17.5 19H9a7 7 0 1 1 6.71-9h1.79a4.5 4.5 0 1 1 0 9Z" />
                    <path d="m13 11-3 4h4l-3 4" className="text-cyan-300 fill-cyan-400/40" />
                  </svg>
                </div>
              </div>
              <span className="text-base font-bold text-white tracking-tight">CloudForge</span>
            </Link>

            <p className="text-slate-300 font-medium text-xs leading-relaxed max-w-sm">
              "Build the skills. Ship the systems."
            </p>
            <p className="text-slate-500 text-xs leading-relaxed max-w-sm">
              Learn cloud engineering by building, breaking, troubleshooting and improving real systems. Powered by contextual AI reasoning and live telemetry sandboxes.
            </p>

            {/* Platform Status */}
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-[11px] font-mono">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              <span className="text-slate-300">All Sandbox Systems Operational</span>
              <span className="text-emerald-400 font-semibold">99.99%</span>
            </div>

            <div className="flex items-center gap-3 pt-2">
              <a href="https://github.com" target="_blank" rel="noreferrer" className="p-2 rounded-lg bg-slate-900 border border-slate-800 hover:text-white hover:border-slate-700 transition-colors">
                <GithubIcon className="w-4 h-4" />
              </a>
              <a href="https://twitter.com" target="_blank" rel="noreferrer" className="p-2 rounded-lg bg-slate-900 border border-slate-800 hover:text-white hover:border-slate-700 transition-colors">
                <TwitterIcon className="w-4 h-4" />
              </a>
              <a href="https://linkedin.com" target="_blank" rel="noreferrer" className="p-2 rounded-lg bg-slate-900 border border-slate-800 hover:text-white hover:border-slate-700 transition-colors">
                <LinkedinIcon className="w-4 h-4" />
              </a>
              <a href="https://discord.com" target="_blank" rel="noreferrer" className="p-2 rounded-lg bg-slate-900 border border-slate-800 hover:text-white hover:border-slate-700 transition-colors">
                <Discord className="w-4 h-4" />
              </a>
            </div>
          </div>

          {/* Learn Links */}
          <div className="space-y-3">
            <h4 className="text-xs font-semibold text-slate-200 uppercase tracking-wider font-mono">
              Learn & Practice
            </h4>
            <ul className="space-y-2 text-xs">
              <li><Link to="/courses" className="hover:text-cyan-300 transition-colors">Course Catalog</Link></li>
              <li><Link to="/roadmaps" className="hover:text-cyan-300 transition-colors">Engineering Roadmaps</Link></li>
              <li><Link to="/skills" className="hover:text-cyan-300 transition-colors">Skills Matrix</Link></li>
              <li><Link to="/projects" className="hover:text-cyan-300 transition-colors">Real-World Projects</Link></li>
              <li><Link to="/troubleshooting" className="hover:text-cyan-300 transition-colors">Troubleshooting Center</Link></li>
            </ul>
          </div>

          {/* Certifications */}
          <div className="space-y-3">
            <h4 className="text-xs font-semibold text-slate-200 uppercase tracking-wider font-mono">
              Certifications
            </h4>
            <ul className="space-y-2 text-xs">
              <li><Link to="/certifications/aws-certified-cloud-practitioner" className="hover:text-cyan-300 transition-colors">AWS Cloud Practitioner</Link></li>
              <li><Link to="/certifications/microsoft-azure-fundamentals" className="hover:text-cyan-300 transition-colors">Azure Fundamentals AZ-900</Link></li>
              <li><Link to="/certifications/microsoft-azure-ai-fundamentals" className="hover:text-cyan-300 transition-colors">Azure AI AI-900</Link></li>
              <li><Link to="/certifications/kubernetes-fundamentals" className="hover:text-cyan-300 transition-colors">Kubernetes Fundamentals</Link></li>
              <li><Link to="/certifications/devops-foundations" className="hover:text-cyan-300 transition-colors">DevOps Foundations</Link></li>
            </ul>
          </div>

          {/* AI & Platform */}
          <div className="space-y-3">
            <h4 className="text-xs font-semibold text-slate-200 uppercase tracking-wider font-mono">
              AI Engineering
            </h4>
            <ul className="space-y-2 text-xs">
              <li><Link to="/ai" className="hover:text-cyan-300 transition-colors">AI Architecture Overview</Link></li>
              <li><Link to="/ai" className="hover:text-cyan-300 transition-colors">CI/CD Failure Analyzer</Link></li>
              <li><Link to="/ai" className="hover:text-cyan-300 transition-colors">Incident Investigator</Link></li>
              <li><Link to="/dashboard" className="hover:text-cyan-300 transition-colors">Student Dashboard</Link></li>
              <li><Link to="/achievements" className="hover:text-cyan-300 transition-colors">Badges & XP</Link></li>
            </ul>
          </div>
        </div>

        {/* Legal and Disclaimer Notice */}
        <div className="mt-12 pt-8 border-t border-slate-800/80 flex flex-col md:flex-row items-center justify-between gap-4 text-[11px] text-slate-500 font-mono">
          <p>© 2026 CloudForge Inc. All rights reserved.</p>
          <p className="max-w-2xl text-center md:text-right leading-relaxed">
            Disclaimer: CloudForge is an independent technical engineering learning platform. AWS, Microsoft Azure, Kubernetes, Docker, and Terraform are trademarks of their respective owners. CloudForge Training Certificates represent platform training completion and do not replace official vendor certification exams.
          </p>
        </div>
      </div>
    </footer>
  )
}
