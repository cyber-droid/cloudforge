import { useState, useRef, useEffect } from 'react'
import { Link, useNavigate, useLocation } from 'react-router-dom'
import {
  ChevronDown,
  Search,
  Sun,
  Moon,
  Menu,
  BookOpen,
  GitFork,
  Cpu,
  Layers,
  Award,
  FolderGit2,
  AlertTriangle,
  Sparkles,
  Terminal,
  Trophy,
  User,
  LogOut,
  ExternalLink,
} from 'lucide-react'
import { useTheme } from '../../context/ThemeContext'
import { useAuth } from '../../context/AuthContext'
import { NotificationsPopover } from '../notifications/NotificationsPopover'
import { CommandPalette } from '../search/CommandPalette'
import { MobileNav } from './MobileNav'
import { Button } from '../common/Button'
import { cn } from '../../utils/cn'

export function Navbar() {
  const { theme, toggleTheme } = useTheme()
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()

  const [searchOpen, setSearchOpen] = useState(false)
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [activeDropdown, setActiveDropdown] = useState<string | null>(null)
  const [profileOpen, setProfileOpen] = useState(false)

  const dropdownRef = useRef<HTMLDivElement>(null)
  const profileRef = useRef<HTMLDivElement>(null)

  // Close dropdowns on outside click or route change
  useEffect(() => {
    setActiveDropdown(null)
    setProfileOpen(false)
    setMobileMenuOpen(false)
  }, [location.pathname])

  useEffect(() => {
    const handleOutsideClick = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setActiveDropdown(null)
      }
      if (profileRef.current && !profileRef.current.contains(e.target as Node)) {
        setProfileOpen(false)
      }
    }
    document.addEventListener('mousedown', handleOutsideClick)
    return () => document.removeEventListener('mousedown', handleOutsideClick)
  }, [])

  // Global shortcut Cmd/Ctrl + K
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault()
        setSearchOpen(prev => !prev)
      }
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [])

  const navMenus = [
    {
      id: 'learn',
      title: 'Learn',
      items: [
        { title: 'Courses', subtitle: '42+ deep-dive engineering modules', path: '/courses', icon: <BookOpen className="w-4 h-4 text-cyan-400" /> },
        { title: 'Learning Paths', subtitle: 'Step-by-step career roadmaps', path: '/roadmaps', icon: <GitFork className="w-4 h-4 text-purple-400" /> },
        { title: 'Skills Matrix', subtitle: 'Track verified engineering skills', path: '/skills', icon: <Cpu className="w-4 h-4 text-blue-400" /> },
        { title: 'Resources & Docs', subtitle: 'Runbooks, manifests & cheat sheets', path: '/courses', icon: <Layers className="w-4 h-4 text-emerald-400" /> },
      ],
    },
    {
      id: 'certifications',
      title: 'Certifications',
      items: [
        { title: 'AWS Cloud Prep', subtitle: 'CLF-C02 preparation & exams', path: '/certifications/aws-certified-cloud-practitioner', icon: <Award className="w-4 h-4 text-amber-400" /> },
        { title: 'Microsoft Azure', subtitle: 'AZ-900 & AI-900 fundamentals', path: '/certifications/microsoft-azure-fundamentals', icon: <Award className="w-4 h-4 text-blue-400" /> },
        { title: 'Kubernetes Foundations', subtitle: 'CKAD/CKA cluster mastery', path: '/certifications/kubernetes-fundamentals', icon: <Award className="w-4 h-4 text-indigo-400" /> },
        { title: 'DevOps Foundations', subtitle: 'Core CI/CD & Linux baselines', path: '/certifications/devops-foundations', icon: <Award className="w-4 h-4 text-emerald-400" /> },
      ],
    },
    {
      id: 'practice',
      title: 'Practice',
      items: [
        { title: 'Real-World Projects', subtitle: '8 production-grade architectures', path: '/projects', icon: <FolderGit2 className="w-4 h-4 text-emerald-400" /> },
        { title: 'Troubleshooting Center', subtitle: 'Debug live outages & incidents', path: '/troubleshooting', icon: <AlertTriangle className="w-4 h-4 text-rose-400" /> },
        { title: 'Challenges & Drills', subtitle: 'Time-boxed SRE scenarios', path: '/projects', icon: <Terminal className="w-4 h-4 text-cyan-400" /> },
        { title: 'Labs / Simulations', subtitle: 'Browser terminals & sandboxes', path: '/troubleshooting', icon: <Cpu className="w-4 h-4 text-purple-400" /> },
      ],
    },
    {
      id: 'ai',
      title: 'AI Engineering',
      items: [
        { title: 'AI for DevOps', subtitle: 'Autonomous triage & patch generation', path: '/ai', icon: <Sparkles className="w-4 h-4 text-cyan-400" /> },
        { title: 'AI for Cloud', subtitle: 'Terraform & IAM policy reasoning', path: '/ai', icon: <Sparkles className="w-4 h-4 text-blue-400" /> },
        { title: 'AI Assistant', subtitle: 'In-context learning copilot', path: '/ai', icon: <Sparkles className="w-4 h-4 text-purple-400" /> },
        { title: 'Incident Intelligence', subtitle: 'Automated RCA & telemetry correlation', path: '/ai', icon: <Sparkles className="w-4 h-4 text-amber-400" /> },
      ],
    },
    {
      id: 'community',
      title: 'Community',
      items: [
        { title: 'Discussions & RFCs', subtitle: 'Technical architecture debates', path: '/dashboard', icon: <BookOpen className="w-4 h-4 text-slate-400" /> },
        { title: 'Leaderboard', subtitle: 'Top platform engineers by streak & XP', path: '/profile', icon: <Trophy className="w-4 h-4 text-amber-400" /> },
        { title: 'Achievements', subtitle: 'Earned engineering badges & verified certs', path: '/achievements', icon: <Award className="w-4 h-4 text-cyan-400" /> },
      ],
    },
  ]

  return (
    <>
      <header className="sticky top-0 z-40 w-full border-b border-slate-800/80 bg-slate-950/85 backdrop-blur-md transition-colors">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between gap-4">
          {/* Brand Logo */}
          <div className="flex items-center gap-6">
            <Link to="/" className="flex items-center gap-2.5 group">
              <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-cyan-500 via-indigo-500 to-purple-600 p-0.5 shadow-md shadow-cyan-500/10 group-hover:shadow-cyan-500/25 transition-all">
                <div className="w-full h-full bg-slate-950 rounded-[10px] flex items-center justify-center">
                  <svg
                    className="w-5 h-5 text-cyan-400 group-hover:scale-105 transition-transform"
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
              <div className="flex flex-col">
                <span className="text-base font-bold tracking-tight text-white flex items-center gap-1.5">
                  CloudForge
                  <span className="text-[10px] font-mono font-medium px-1.5 py-0.2 rounded bg-cyan-500/10 text-cyan-300 border border-cyan-500/20">
                    BETA
                  </span>
                </span>
                <span className="text-[10px] text-slate-400 font-mono tracking-wider -mt-1 hidden sm:block">
                  ENGINEERING PLATFORM
                </span>
              </div>
            </Link>

            {/* Desktop Navigation Menus */}
            <nav className="hidden lg:flex items-center gap-1" ref={dropdownRef}>
              {navMenus.map(menu => {
                const isActive = activeDropdown === menu.id
                return (
                  <div key={menu.id} className="relative">
                    <button
                      onClick={() => setActiveDropdown(isActive ? null : menu.id)}
                      className={cn(
                        'flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-colors cursor-pointer',
                        isActive
                          ? 'bg-slate-800/80 text-cyan-300'
                          : 'text-slate-300 hover:text-white hover:bg-slate-800/50'
                      )}
                    >
                      <span>{menu.title}</span>
                      <ChevronDown
                        className={cn(
                          'w-3.5 h-3.5 transition-transform duration-150',
                          isActive ? 'rotate-180 text-cyan-400' : 'text-slate-500'
                        )}
                      />
                    </button>

                    {/* Mega Dropdown Menu */}
                    {isActive && (
                      <div className="absolute top-full left-0 mt-2 w-72 rounded-2xl border border-slate-700/80 bg-slate-900 shadow-2xl p-2 z-50 animate-in fade-in-50 zoom-in-95 duration-150">
                        <div className="text-[10px] font-mono text-slate-500 uppercase tracking-wider px-3 py-1.5">
                          {menu.title} Navigation
                        </div>
                        <div className="flex flex-col gap-0.5">
                          {menu.items.map(item => (
                            <Link
                              key={item.title}
                              to={item.path}
                              onClick={() => setActiveDropdown(null)}
                              className="flex items-start gap-3 p-2.5 rounded-xl hover:bg-slate-800/80 transition-colors group text-left"
                            >
                              <div className="p-2 rounded-lg bg-slate-800/80 border border-slate-700/60 shrink-0 mt-0.5 group-hover:border-slate-600 transition-colors">
                                {item.icon}
                              </div>
                              <div className="min-w-0">
                                <p className="text-xs font-semibold text-slate-200 group-hover:text-cyan-300 transition-colors">
                                  {item.title}
                                </p>
                                <p className="text-[11px] text-slate-400 truncate mt-0.5">
                                  {item.subtitle}
                                </p>
                              </div>
                            </Link>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )
              })}
            </nav>
          </div>

          {/* Right Navigation Utilities */}
          <div className="flex items-center gap-2 sm:gap-3">
            {/* Search Trigger (Cmd + K) */}
            <button
              onClick={() => setSearchOpen(true)}
              className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-xl border border-slate-800 bg-slate-900/80 hover:border-slate-700 text-xs text-slate-400 hover:text-slate-200 transition-all cursor-pointer group"
              title="Search across courses, incidents, roadmaps"
            >
              <Search className="w-3.5 h-3.5 text-slate-400 group-hover:text-cyan-400 transition-colors" />
              <span className="hidden md:inline font-sans">Quick search...</span>
              <kbd className="text-[10px] font-mono text-slate-500 px-1.5 py-0.5 rounded bg-slate-800/80 border border-slate-700/60 ml-2">
                ⌘K
              </kbd>
            </button>

            {/* Mobile search icon button */}
            <button
              onClick={() => setSearchOpen(true)}
              className="sm:hidden p-2 rounded-lg text-slate-400 hover:text-slate-100 hover:bg-slate-800 transition-colors"
            >
              <Search className="w-4 h-4" />
            </button>

            {/* Notifications Popover */}
            <NotificationsPopover />

            {/* Theme Toggle */}
            <button
              onClick={toggleTheme}
              className="p-2 rounded-lg text-slate-400 hover:text-slate-100 hover:bg-slate-800 transition-colors cursor-pointer"
              title={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
            >
              {theme === 'dark' ? (
                <Sun className="w-4 h-4 text-amber-400" />
              ) : (
                <Moon className="w-4 h-4 text-slate-600" />
              )}
            </button>

            {/* User Profile or Login */}
            {user ? (
              <div className="relative" ref={profileRef}>
                <button
                  onClick={() => setProfileOpen(!profileOpen)}
                  className="flex items-center gap-2 p-1 pl-2 rounded-xl border border-slate-800 bg-slate-900 hover:border-slate-700 transition-all cursor-pointer"
                >
                  <span className="text-xs font-medium text-slate-200 hidden md:inline">
                    {user.name.split(' ')[0]}
                  </span>
                  <img
                    src={user.avatar}
                    alt={user.name}
                    className="w-7 h-7 rounded-lg object-cover ring-1 ring-cyan-500/30"
                  />
                </button>

                {profileOpen && (
                  <div className="absolute right-0 mt-2 w-64 rounded-2xl border border-slate-700/80 bg-slate-900 shadow-2xl p-2 z-50 animate-in fade-in-50 zoom-in-95 duration-150">
                    <div className="p-3 border-b border-slate-800 flex items-center gap-3">
                      <img
                        src={user.avatar}
                        alt={user.name}
                        className="w-10 h-10 rounded-xl object-cover ring-1 ring-cyan-400/40"
                      />
                      <div className="min-w-0">
                        <p className="text-xs font-semibold text-white truncate">{user.name}</p>
                        <p className="text-[11px] text-cyan-400 font-mono truncate">@{user.handle}</p>
                        <p className="text-[10px] text-slate-400 truncate mt-0.5">{user.role}</p>
                      </div>
                    </div>

                    <div className="py-1.5 flex flex-col gap-0.5">
                      <Link
                        to="/dashboard"
                        onClick={() => setProfileOpen(false)}
                        className="flex items-center gap-2.5 px-3 py-2 rounded-xl hover:bg-slate-800/80 text-xs text-slate-300 hover:text-white transition-colors"
                      >
                        <Cpu className="w-4 h-4 text-cyan-400" />
                        <span>Student Dashboard</span>
                      </Link>
                      <Link
                        to="/profile"
                        onClick={() => setProfileOpen(false)}
                        className="flex items-center gap-2.5 px-3 py-2 rounded-xl hover:bg-slate-800/80 text-xs text-slate-300 hover:text-white transition-colors"
                      >
                        <User className="w-4 h-4 text-blue-400" />
                        <span>Engineer Profile</span>
                      </Link>
                      <Link
                        to="/achievements"
                        onClick={() => setProfileOpen(false)}
                        className="flex items-center gap-2.5 px-3 py-2 rounded-xl hover:bg-slate-800/80 text-xs text-slate-300 hover:text-white transition-colors"
                      >
                        <Award className="w-4 h-4 text-purple-400" />
                        <span>Achievements & Badges</span>
                      </Link>
                      <Link
                        to="/settings"
                        onClick={() => setProfileOpen(false)}
                        className="flex items-center gap-2.5 px-3 py-2 rounded-xl hover:bg-slate-800/80 text-xs text-slate-300 hover:text-white transition-colors"
                      >
                        <Layers className="w-4 h-4 text-slate-400" />
                        <span>Platform Settings</span>
                      </Link>
                    </div>

                    <div className="pt-1.5 border-t border-slate-800">
                      <button
                        onClick={() => {
                          logout()
                          setProfileOpen(false)
                          navigate('/login')
                        }}
                        className="w-full flex items-center gap-2.5 px-3 py-2 rounded-xl hover:bg-rose-950/40 text-xs text-rose-400 hover:text-rose-300 transition-colors"
                      >
                        <LogOut className="w-4 h-4" />
                        <span>Sign Out</span>
                      </button>
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="flex items-center gap-2">
                <Link to="/login">
                  <Button variant="ghost" size="sm">
                    Sign In
                  </Button>
                </Link>
                <Link to="/register">
                  <Button variant="primary" size="sm">
                    Get Started
                  </Button>
                </Link>
              </div>
            )}

            {/* Dashboard Button */}
            <Link to="/dashboard" className="hidden sm:block">
              <Button variant="secondary" size="sm" icon={<Terminal className="w-3.5 h-3.5 text-cyan-400" />}>
                Dashboard
              </Button>
            </Link>

            {/* Mobile Hamburger Drawer Trigger */}
            <button
              onClick={() => setMobileMenuOpen(true)}
              className="lg:hidden p-2 rounded-lg text-slate-400 hover:text-slate-100 hover:bg-slate-800 transition-colors"
              aria-label="Open mobile menu"
            >
              <Menu className="w-5 h-5" />
            </button>
          </div>
        </div>
      </header>

      {/* Command Palette Modal */}
      <CommandPalette isOpen={searchOpen} onClose={() => setSearchOpen(false)} />

      {/* Mobile Drawer Navigation */}
      <MobileNav
        isOpen={mobileMenuOpen}
        onClose={() => setMobileMenuOpen(false)}
        navMenus={navMenus}
      />
    </>
  )
}
