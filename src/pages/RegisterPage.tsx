import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { User, Mail, Lock, ArrowRight, Check } from 'lucide-react'
import { Button } from '../components/common/Button'
import { Input } from '../components/common/Input'
import { useAuth } from '../context/AuthContext'
import { useToast } from '../context/ToastContext'

export function RegisterPage() {
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [selectedGoal, setSelectedGoal] = useState('DevOps')
  const [loading, setLoading] = useState(false)

  const { login } = useAuth()
  const { showToast } = useToast()
  const navigate = useNavigate()

  const learningGoals = [
    { id: 'Cloud', label: 'Cloud Computing', icon: '☁️', desc: 'AWS & Azure infrastructure architecture' },
    { id: 'DevOps', label: 'DevOps Engineering', icon: '⚙️', desc: 'CI/CD, Docker, and Linux automation' },
    { id: 'DevSecOps', label: 'DevSecOps', icon: '🛡️', desc: 'Supply chain security & SAST automation' },
    { id: 'Kubernetes', label: 'Kubernetes', icon: '☸️', desc: 'Production container orchestration' },
    { id: 'Cloud Security', label: 'Cloud Security', icon: '🔒', desc: 'Zero-trust IAM & KMS architecture' },
    { id: 'AI Engineering', label: 'AI for DevOps', icon: '⚡', desc: 'Autonomous incident triage & agents' },
    { id: 'Certification', label: 'Certification Prep', icon: '🏆', desc: 'AWS, Azure & Kubernetes exam readiness' },
  ]

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (password !== confirmPassword) {
      showToast('Password mismatch', 'Please ensure both passwords match.', 'error')
      return
    }

    setLoading(true)
    setTimeout(() => {
      login(email)
      showToast('Account Created!', `Personalized learning track initialized for ${selectedGoal}.`, 'success')
      navigate('/dashboard')
    }, 600)
  }

  return (
    <div className="min-h-[85vh] flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8 bg-slate-950">
      <div className="max-w-xl w-full space-y-8 bg-slate-900/80 border border-slate-800 p-8 rounded-2xl shadow-2xl backdrop-blur-md">
        {/* Header */}
        <div className="text-center">
          <Link to="/" className="inline-flex items-center gap-2 mb-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-cyan-500 to-indigo-600 p-0.5 shadow-md">
              <div className="w-full h-full bg-slate-950 rounded-[10px] flex items-center justify-center">
                <svg className="w-4 h-4 text-cyan-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2">
                  <path d="M17.5 19H9a7 7 0 1 1 6.71-9h1.79a4.5 4.5 0 1 1 0 9Z" />
                  <path d="m13 11-3 4h4l-3 4" className="text-cyan-300 fill-cyan-400/40" />
                </svg>
              </div>
            </div>
            <span className="text-base font-bold text-white tracking-tight">CloudForge</span>
          </Link>
          <h2 className="text-2xl font-extrabold text-white tracking-tight">
            Create your engineer account
          </h2>
          <p className="mt-1 text-xs text-slate-400 font-mono">
            Get instant access to live cloud environments, real incident sandboxes & AI tools.
          </p>
        </div>

        <form className="space-y-5" onSubmit={handleSubmit}>
          {/* Credentials */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Input
              label="Full Name"
              type="text"
              value={name}
              onChange={e => setName(e.target.value)}
              placeholder="Alex Rivera"
              icon={<User className="w-4 h-4" />}
              required
            />
            <Input
              label="Engineering Email"
              type="email"
              value={email}
              onChange={e => setEmail(e.target.value)}
              placeholder="alex@cloudforge.io"
              icon={<Mail className="w-4 h-4" />}
              required
            />
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Input
              label="Password"
              type="password"
              value={password}
              onChange={e => setPassword(e.target.value)}
              placeholder="••••••••••••"
              icon={<Lock className="w-4 h-4" />}
              required
            />
            <Input
              label="Confirm Password"
              type="password"
              value={confirmPassword}
              onChange={e => setConfirmPassword(e.target.value)}
              placeholder="••••••••••••"
              icon={<Lock className="w-4 h-4" />}
              required
            />
          </div>

          {/* Select Learning Goal Selector */}
          <div className="pt-2">
            <label className="text-xs font-semibold text-slate-200 block mb-2 font-mono">
              SELECT PRIMARY LEARNING GOAL:
            </label>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
              {learningGoals.map(goal => {
                const isSelected = selectedGoal === goal.id
                return (
                  <div
                    key={goal.id}
                    onClick={() => setSelectedGoal(goal.id)}
                    className={`p-3 rounded-xl border transition-all cursor-pointer flex items-center justify-between text-left ${
                      isSelected
                        ? 'bg-slate-800 border-cyan-400/80 shadow-md shadow-cyan-950/20'
                        : 'bg-slate-950/40 border-slate-800/80 hover:border-slate-700 hover:bg-slate-900/60'
                    }`}
                  >
                    <div className="flex items-center gap-2.5 min-w-0">
                      <span className="text-base shrink-0">{goal.icon}</span>
                      <div className="min-w-0">
                        <p className={`text-xs font-semibold truncate ${isSelected ? 'text-cyan-300' : 'text-slate-200'}`}>
                          {goal.label}
                        </p>
                        <p className="text-[10px] text-slate-400 truncate mt-0.5">
                          {goal.desc}
                        </p>
                      </div>
                    </div>
                    {isSelected && (
                      <div className="w-4 h-4 rounded-full bg-cyan-400 flex items-center justify-center shrink-0 ml-1">
                        <Check className="w-3 h-3 text-slate-950" />
                      </div>
                    )}
                  </div>
                )
              })}
            </div>
          </div>

          <Button
            type="submit"
            variant="glow"
            size="md"
            className="w-full mt-4"
            isLoading={loading}
            iconRight={<ArrowRight className="w-4 h-4" />}
          >
            Create Account & Launch Platform
          </Button>
        </form>

        <div className="text-center pt-2">
          <p className="text-xs text-slate-400">
            Already have an account?{' '}
            <Link to="/login" className="text-cyan-400 hover:text-cyan-300 font-semibold font-mono">
              Sign in ➔
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}
