import { useState } from 'react'
import { PageContainer } from '../components/layout/PageContainer'
import { Card } from '../components/common/Card'
import { Input } from '../components/common/Input'
import { Button } from '../components/common/Button'
import { useAuth } from '../context/AuthContext'
import { useToast } from '../context/ToastContext'
import { useTheme } from '../context/ThemeContext'
import { Save, User, Bell, Terminal, Shield, Moon, Sun } from 'lucide-react'

export function SettingsPage() {
  const { user } = useAuth()
  const { showToast } = useToast()
  const { theme, toggleTheme } = useTheme()

  const [name, setName] = useState(user?.name || 'Alex Rivera')
  const [handle, setHandle] = useState(user?.handle || 'alex-rivera-ops')
  const [role, setRole] = useState(user?.role || 'Cloud & DevOps Engineer in Training')
  const [notifyOutages, setNotifyOutages] = useState(true)
  const [notifyProgress, setNotifyProgress] = useState(true)
  const [terminalFontSize, setTerminalFontSize] = useState('13px')
  const [saving, setSaving] = useState(false)

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault()
    setSaving(true)
    setTimeout(() => {
      setSaving(false)
      showToast('Settings Saved', 'Your platform and terminal preferences have been updated.', 'success')
    }, 600)
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 pb-16">
      <div className="border-b border-slate-800 bg-slate-950/80 py-10">
        <PageContainer>
          <div className="max-w-3xl">
            <h1 className="text-3xl font-bold text-white tracking-tight">
              Platform Settings
            </h1>
            <p className="text-xs text-slate-400 font-mono mt-1">
              Configure your engineering profile, notification alerts, and sandbox terminal environment.
            </p>
          </div>
        </PageContainer>
      </div>

      <PageContainer>
        <form onSubmit={handleSave} className="max-w-3xl space-y-8">
          {/* Section 1: Profile Information */}
          <Card className="p-6 space-y-5">
            <div className="flex items-center gap-2 pb-3 border-b border-slate-800">
              <User className="w-4 h-4 text-cyan-400" />
              <h3 className="text-sm font-bold text-white uppercase font-mono tracking-wider">
                Engineer Profile Details
              </h3>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <Input
                label="Full Name"
                value={name}
                onChange={e => setName(e.target.value)}
              />
              <Input
                label="Public Handle"
                value={handle}
                onChange={e => setHandle(e.target.value)}
              />
            </div>

            <Input
              label="Professional Headline / Current Goal"
              value={role}
              onChange={e => setRole(e.target.value)}
            />
          </Card>

          {/* Section 2: Terminal Sandbox Configuration */}
          <Card className="p-6 space-y-5">
            <div className="flex items-center gap-2 pb-3 border-b border-slate-800">
              <Terminal className="w-4 h-4 text-purple-400" />
              <h3 className="text-sm font-bold text-white uppercase font-mono tracking-wider">
                Sandbox Terminal & Theme
              </h3>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="space-y-1.5">
                <label className="text-xs font-medium text-slate-300">Terminal Font Size</label>
                <select
                  value={terminalFontSize}
                  onChange={e => setTerminalFontSize(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-xs font-mono text-slate-200 focus:outline-none focus:border-cyan-500"
                >
                  <option value="12px">12px (Compact)</option>
                  <option value="13px">13px (Default)</option>
                  <option value="14px">14px (Comfortable)</option>
                  <option value="16px">16px (Large)</option>
                </select>
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-medium text-slate-300">Interface Color Scheme</label>
                <div className="flex items-center gap-2">
                  <Button
                    type="button"
                    variant={theme === 'dark' ? 'primary' : 'outline'}
                    size="sm"
                    onClick={toggleTheme}
                    icon={theme === 'dark' ? <Moon className="w-3.5 h-3.5" /> : <Sun className="w-3.5 h-3.5" />}
                  >
                    {theme === 'dark' ? 'Dark Theme (Active)' : 'Light Theme (Active)'}
                  </Button>
                </div>
              </div>
            </div>
          </Card>

          {/* Section 3: Incident & Alert Notifications */}
          <Card className="p-6 space-y-4">
            <div className="flex items-center gap-2 pb-3 border-b border-slate-800">
              <Bell className="w-4 h-4 text-amber-400" />
              <h3 className="text-sm font-bold text-white uppercase font-mono tracking-wider">
                Notification Subscriptions
              </h3>
            </div>

            <div className="space-y-3 text-xs">
              <label className="flex items-center justify-between p-3 rounded-xl bg-slate-950 border border-slate-800 cursor-pointer">
                <div>
                  <p className="font-semibold text-white">Live Outage & Incident Drills</p>
                  <p className="text-slate-400 text-[11px] font-mono mt-0.5">
                    Receive simulated SRE pager alerts when new incident troubleshooting labs are released.
                  </p>
                </div>
                <input
                  type="checkbox"
                  checked={notifyOutages}
                  onChange={e => setNotifyOutages(e.target.checked)}
                  className="w-4 h-4 rounded border-slate-700 bg-slate-900 text-cyan-500"
                />
              </label>

              <label className="flex items-center justify-between p-3 rounded-xl bg-slate-950 border border-slate-800 cursor-pointer">
                <div>
                  <p className="font-semibold text-white">Learning Streak & Milestone Reminders</p>
                  <p className="text-slate-400 text-[11px] font-mono mt-0.5">
                    Daily notifications when your 12-day engineering streak is at risk.
                  </p>
                </div>
                <input
                  type="checkbox"
                  checked={notifyProgress}
                  onChange={e => setNotifyProgress(e.target.checked)}
                  className="w-4 h-4 rounded border-slate-700 bg-slate-900 text-cyan-500"
                />
              </label>
            </div>
          </Card>

          <Button
            type="submit"
            variant="glow"
            size="md"
            isLoading={saving}
            icon={<Save className="w-4 h-4 fill-slate-950" />}
          >
            Save Preferences
          </Button>
        </form>
      </PageContainer>
    </div>
  )
}
