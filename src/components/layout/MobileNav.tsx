import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { X, ChevronDown, Terminal, LogIn, UserPlus, LogOut } from 'lucide-react'
import { useAuth } from '../../context/AuthContext'
import { Button } from '../common/Button'
import { cn } from '../../utils/cn'

interface MobileNavProps {
  isOpen: boolean
  onClose: () => void
  navMenus: {
    id: string
    title: string
    items: {
      title: string
      subtitle: string
      path: string
      icon: React.ReactNode
    }[]
  }[]
}

export function MobileNav({ isOpen, onClose, navMenus }: MobileNavProps) {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [expandedMenu, setExpandedMenu] = useState<string | null>('learn')

  if (!isOpen) return null

  const toggleAccordion = (id: string) => {
    setExpandedMenu(prev => (prev === id ? null : id))
  }

  return (
    <div className="fixed inset-0 z-50 lg:hidden flex justify-end">
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm animate-in fade-in duration-200"
        onClick={onClose}
      />

      {/* Drawer */}
      <div className="relative w-full max-w-xs sm:max-w-sm bg-slate-900 border-l border-slate-800 shadow-2xl h-full flex flex-col z-10 animate-in slide-in-from-right duration-250 text-slate-100">
        {/* Drawer Header */}
        <div className="flex items-center justify-between p-4 border-b border-slate-800 bg-slate-900/90">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-lg bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400 font-bold text-xs">
              CF
            </div>
            <span className="text-sm font-bold text-white tracking-tight">CloudForge</span>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-100 hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* User Card if logged in */}
        {user ? (
          <div className="p-4 border-b border-slate-800 bg-slate-950/50 flex items-center gap-3">
            <img
              src={user.avatar}
              alt={user.name}
              className="w-10 h-10 rounded-xl object-cover ring-1 ring-cyan-500/40"
            />
            <div className="min-w-0">
              <p className="text-xs font-semibold text-white truncate">{user.name}</p>
              <p className="text-[11px] text-cyan-400 font-mono">@{user.handle}</p>
              <p className="text-[10px] text-slate-400 truncate">{user.role}</p>
            </div>
          </div>
        ) : (
          <div className="p-4 border-b border-slate-800 grid grid-cols-2 gap-2 bg-slate-950/40">
            <Link to="/login" onClick={onClose}>
              <Button variant="outline" size="sm" className="w-full" icon={<LogIn className="w-3.5 h-3.5" />}>
                Sign In
              </Button>
            </Link>
            <Link to="/register" onClick={onClose}>
              <Button variant="primary" size="sm" className="w-full" icon={<UserPlus className="w-3.5 h-3.5" />}>
                Sign Up
              </Button>
            </Link>
          </div>
        )}

        {/* Accordion Navigation Links */}
        <div className="flex-1 overflow-y-auto p-4 space-y-2">
          <Link
            to="/dashboard"
            onClick={onClose}
            className="flex items-center justify-between p-3 rounded-xl bg-slate-800/80 border border-slate-700/60 text-xs font-semibold text-cyan-300 hover:bg-slate-800"
          >
            <div className="flex items-center gap-2">
              <Terminal className="w-4 h-4 text-cyan-400" />
              <span>Student Dashboard</span>
            </div>
            <span className="text-[10px] font-mono bg-cyan-950 text-cyan-400 px-2 py-0.5 rounded border border-cyan-800/40">
              42%
            </span>
          </Link>

          {navMenus.map(menu => {
            const isExpanded = expandedMenu === menu.id
            return (
              <div key={menu.id} className="rounded-xl border border-slate-800/80 overflow-hidden bg-slate-950/30">
                <button
                  onClick={() => toggleAccordion(menu.id)}
                  className="w-full flex items-center justify-between p-3 text-xs font-semibold text-slate-300 hover:text-white transition-colors"
                >
                  <span>{menu.title}</span>
                  <ChevronDown
                    className={cn(
                      'w-4 h-4 text-slate-500 transition-transform duration-200',
                      isExpanded && 'rotate-180 text-cyan-400'
                    )}
                  />
                </button>

                {isExpanded && (
                  <div className="p-2 pt-0 flex flex-col gap-1 border-t border-slate-800/60 bg-slate-900/50">
                    {menu.items.map(item => (
                      <Link
                        key={item.title}
                        to={item.path}
                        onClick={onClose}
                        className="flex items-center gap-2.5 p-2 rounded-lg hover:bg-slate-800/70 text-xs text-slate-300 hover:text-cyan-300 transition-colors"
                      >
                        <div className="shrink-0">{item.icon}</div>
                        <div className="min-w-0">
                          <p className="font-medium truncate">{item.title}</p>
                          <p className="text-[10px] text-slate-500 truncate">{item.subtitle}</p>
                        </div>
                      </Link>
                    ))}
                  </div>
                )}
              </div>
            )
          })}
        </div>

        {/* Drawer Footer */}
        {user && (
          <div className="p-4 border-t border-slate-800 bg-slate-950/80">
            <button
              onClick={() => {
                logout()
                onClose()
                navigate('/login')
              }}
              className="w-full flex items-center justify-center gap-2 py-2 rounded-xl text-xs font-medium text-rose-400 hover:bg-rose-950/30 border border-rose-900/30 transition-colors"
            >
              <LogOut className="w-4 h-4" />
              <span>Sign Out</span>
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
