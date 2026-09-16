import { useState } from 'react'
import { Link } from 'react-router-dom'
import { Mail, ArrowLeft, ArrowRight, CheckCircle2 } from 'lucide-react'
import { Button } from '../components/common/Button'
import { Input } from '../components/common/Input'
import { useToast } from '../context/ToastContext'

export function ForgotPasswordPage() {
  const [email, setEmail] = useState('')
  const [submitted, setSubmitted] = useState(false)
  const [loading, setLoading] = useState(false)
  const { showToast } = useToast()

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setTimeout(() => {
      setSubmitted(true)
      setLoading(false)
      showToast('Reset Instructions Sent', `Check ${email} for password recovery steps.`, 'success')
    }, 600)
  }

  return (
    <div className="min-h-[80vh] flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8 bg-slate-950">
      <div className="max-w-md w-full space-y-6 bg-slate-900/80 border border-slate-800 p-8 rounded-2xl shadow-2xl backdrop-blur-md">
        <div className="text-center">
          <Link to="/" className="inline-flex items-center gap-2 mb-3">
            <span className="text-base font-bold text-white tracking-tight">CloudForge</span>
          </Link>
          <h2 className="text-xl font-bold text-white">Reset Account Password</h2>
          <p className="mt-1 text-xs text-slate-400 font-mono">
            Enter your email to receive recovery instructions.
          </p>
        </div>

        {submitted ? (
          <div className="p-6 rounded-xl bg-slate-950/60 border border-emerald-500/30 text-center space-y-3">
            <CheckCircle2 className="w-10 h-10 text-emerald-400 mx-auto" />
            <h3 className="text-sm font-semibold text-white">Recovery Email Dispatched</h3>
            <p className="text-xs text-slate-400">
              We've dispatched a secure token link to <span className="text-cyan-400 font-mono">{email}</span>. Follow the link to configure your new credentials.
            </p>
            <div className="pt-2">
              <Link to="/login">
                <Button variant="secondary" size="sm" icon={<ArrowLeft className="w-4 h-4" />}>
                  Return to Sign In
                </Button>
              </Link>
            </div>
          </div>
        ) : (
          <form className="space-y-4" onSubmit={handleSubmit}>
            <Input
              label="Registered Email Address"
              type="email"
              value={email}
              onChange={e => setEmail(e.target.value)}
              placeholder="engineer@company.com"
              icon={<Mail className="w-4 h-4" />}
              required
            />

            <Button
              type="submit"
              variant="glow"
              size="md"
              className="w-full"
              isLoading={loading}
              iconRight={<ArrowRight className="w-4 h-4" />}
            >
              Send Recovery Link
            </Button>

            <div className="text-center pt-2">
              <Link to="/login" className="text-xs text-slate-400 hover:text-slate-200 flex items-center justify-center gap-1">
                <ArrowLeft className="w-3.5 h-3.5" />
                <span>Back to Sign In</span>
              </Link>
            </div>
          </form>
        )}
      </div>
    </div>
  )
}
