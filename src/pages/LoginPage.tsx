import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Lock, Mail, ArrowRight } from 'lucide-react'
import { GithubIcon } from '../components/common/BrandIcons'
import { Button } from '../components/common/Button'
import { Input } from '../components/common/Input'
import { useAuth } from '../context/AuthContext'
import { useToast } from '../context/ToastContext'

export function LoginPage() {
  const [email, setEmail] = useState('alex.rivera@cloudforge.io')
  const [password, setPassword] = useState('••••••••••••')
  const [rememberMe, setRememberMe] = useState(true)
  const [loading, setLoading] = useState(false)

  const { login } = useAuth()
  const { showToast } = useToast()
  const navigate = useNavigate()

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setTimeout(() => {
      login(email)
      showToast('Welcome back, Alex!', 'Authenticated to CloudForge Platform session.', 'success')
      navigate('/dashboard')
    }, 600)
  }

  const handleOAuth = (provider: string) => {
    login()
    showToast(`Signed in with ${provider}`, 'Connected via OAuth 2.0 session.', 'success')
    navigate('/dashboard')
  }

  return (
    <div className="min-h-[85vh] flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8 bg-slate-950">
      <div className="max-w-md w-full space-y-8 bg-slate-900/80 border border-slate-800 p-8 rounded-2xl shadow-2xl backdrop-blur-md">
        {/* Brand Header */}
        <div className="text-center">
          <Link to="/" className="inline-flex items-center gap-2 mb-4 group">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500 to-indigo-600 p-0.5 shadow-md shadow-cyan-500/20">
              <div className="w-full h-full bg-slate-950 rounded-[10px] flex items-center justify-center">
                <svg
                  className="w-5 h-5 text-cyan-400"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2.2"
                >
                  <path d="M17.5 19H9a7 7 0 1 1 6.71-9h1.79a4.5 4.5 0 1 1 0 9Z" />
                  <path d="m13 11-3 4h4l-3 4" className="text-cyan-300 fill-cyan-400/40" />
                </svg>
              </div>
            </div>
            <span className="text-lg font-bold text-white tracking-tight">CloudForge</span>
          </Link>
          <h2 className="text-2xl font-extrabold text-white tracking-tight">
            Welcome back, engineer.
          </h2>
          <p className="mt-2 text-xs text-slate-400 font-mono">
            Enter your credentials to resume your cloud engineering workbench.
          </p>
        </div>

        {/* Form */}
        <form className="mt-8 space-y-4" onSubmit={handleSubmit}>
          <Input
            label="Engineering Email"
            type="email"
            value={email}
            onChange={e => setEmail(e.target.value)}
            placeholder="engineer@company.com"
            icon={<Mail className="w-4 h-4" />}
            required
          />

          <Input
            label="Password"
            type="password"
            value={password}
            onChange={e => setPassword(e.target.value)}
            placeholder="••••••••••••"
            icon={<Lock className="w-4 h-4" />}
            required
          />

          <div className="flex items-center justify-between text-xs pt-1">
            <label className="flex items-center gap-2 cursor-pointer select-none text-slate-300">
              <input
                type="checkbox"
                checked={rememberMe}
                onChange={e => setRememberMe(e.target.checked)}
                className="w-3.5 h-3.5 rounded border-slate-700 bg-slate-800 text-cyan-500 focus:ring-cyan-500/20"
              />
              <span>Remember me</span>
            </label>
            <Link
              to="/forgot-password"
              className="font-mono text-cyan-400 hover:text-cyan-300 transition-colors"
            >
              Forgot password?
            </Link>
          </div>

          <Button
            type="submit"
            variant="glow"
            size="md"
            className="w-full mt-2"
            isLoading={loading}
            iconRight={<ArrowRight className="w-4 h-4" />}
          >
            Sign In
          </Button>

          <div className="relative my-6">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-slate-800" />
            </div>
            <div className="relative flex justify-center text-xs uppercase font-mono">
              <span className="bg-slate-900 px-3 text-slate-500">Or continue with</span>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <Button
              type="button"
              variant="secondary"
              size="sm"
              onClick={() => handleOAuth('GitHub')}
              icon={<GithubIcon className="w-4 h-4" />}
            >
              GitHub
            </Button>
            <Button
              type="button"
              variant="secondary"
              size="sm"
              onClick={() => handleOAuth('Google')}
              icon={
                <svg className="w-4 h-4" viewBox="0 0 24 24">
                  <path
                    fill="currentColor"
                    d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                  />
                  <path
                    fill="currentColor"
                    d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                  />
                  <path
                    fill="currentColor"
                    d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"
                  />
                  <path
                    fill="currentColor"
                    d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"
                  />
                </svg>
              }
            >
              Google
            </Button>
          </div>
        </form>

        <div className="text-center pt-2">
          <p className="text-xs text-slate-400">
            Don't have an engineer account?{' '}
            <Link to="/register" className="text-cyan-400 hover:text-cyan-300 font-semibold font-mono">
              Create one now ➔
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}
