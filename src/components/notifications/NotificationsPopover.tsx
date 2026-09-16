import { useState, useRef, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Bell, CheckCheck, BookOpen, Award, AlertTriangle, Sparkles } from 'lucide-react'
import { NOTIFICATIONS } from '../../data/notificationsData'
import type { NotificationItem } from '../../types'
import { cn } from '../../utils/cn'

export function NotificationsPopover() {
  const [isOpen, setIsOpen] = useState(false)
  const [notifications, setNotifications] = useState<NotificationItem[]>(NOTIFICATIONS)
  const popoverRef = useRef<HTMLDivElement>(null)

  const unreadCount = notifications.filter(n => !n.read).length

  const markAllAsRead = () => {
    setNotifications(prev => prev.map(n => ({ ...n, read: true })))
  }

  const markAsRead = (id: string) => {
    setNotifications(prev =>
      prev.map(n => (n.id === id ? { ...n, read: true } : n))
    )
    setIsOpen(false)
  }

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (popoverRef.current && !popoverRef.current.contains(e.target as Node)) {
        setIsOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const getIcon = (type: NotificationItem['type']) => {
    switch (type) {
      case 'course':
        return <BookOpen className="w-4 h-4 text-cyan-400" />
      case 'cert':
        return <Award className="w-4 h-4 text-amber-400" />
      case 'incident':
        return <AlertTriangle className="w-4 h-4 text-rose-400" />
      case 'achievement':
        return <Sparkles className="w-4 h-4 text-purple-400" />
      default:
        return <Bell className="w-4 h-4 text-blue-400" />
    }
  }

  return (
    <div className="relative" ref={popoverRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="relative p-2 rounded-lg text-slate-400 hover:text-slate-100 hover:bg-slate-800/80 transition-colors cursor-pointer"
        title="Notifications"
        aria-label="Notifications"
      >
        <Bell className="w-4 h-4" />
        {unreadCount > 0 && (
          <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-cyan-400 animate-pulse ring-2 ring-slate-950" />
        )}
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-80 sm:w-96 rounded-2xl border border-slate-700/80 bg-slate-900 shadow-2xl shadow-slate-950/80 overflow-hidden z-50 animate-in fade-in-50 zoom-in-95 duration-150">
          <div className="flex items-center justify-between px-4 py-3 border-b border-slate-800 bg-slate-900/90">
            <div className="flex items-center gap-2">
              <h4 className="text-sm font-semibold text-slate-100">Notifications</h4>
              {unreadCount > 0 && (
                <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-cyan-950/80 text-cyan-300 border border-cyan-800/60 font-semibold">
                  {unreadCount} new
                </span>
              )}
            </div>
            {unreadCount > 0 && (
              <button
                onClick={markAllAsRead}
                className="flex items-center gap-1 text-[11px] text-slate-400 hover:text-cyan-300 transition-colors font-mono"
              >
                <CheckCheck className="w-3.5 h-3.5" />
                <span>Mark all read</span>
              </button>
            )}
          </div>

          <div className="max-h-[380px] overflow-y-auto divide-y divide-slate-800/60">
            {notifications.length === 0 ? (
              <div className="p-8 text-center text-slate-500 text-xs">
                No notifications right now
              </div>
            ) : (
              notifications.map(item => (
                <Link
                  key={item.id}
                  to={item.link || '#'}
                  onClick={() => markAsRead(item.id)}
                  className={cn(
                    'flex items-start gap-3 p-3.5 hover:bg-slate-800/60 transition-colors text-left group',
                    !item.read && 'bg-slate-800/20'
                  )}
                >
                  <div className="p-2 rounded-lg bg-slate-800/80 border border-slate-700/60 shrink-0 mt-0.5">
                    {getIcon(item.type)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between gap-1">
                      <p
                        className={cn(
                          'text-xs font-semibold truncate',
                          item.read ? 'text-slate-300' : 'text-slate-100 group-hover:text-cyan-300'
                        )}
                      >
                        {item.title}
                      </p>
                      <span className="text-[10px] text-slate-500 font-mono shrink-0">
                        {item.timeAgo}
                      </span>
                    </div>
                    <p className="text-xs text-slate-400 mt-1 line-clamp-2 leading-relaxed">
                      {item.description}
                    </p>
                  </div>
                  {!item.read && (
                    <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 shrink-0 mt-2" />
                  )}
                </Link>
              ))
            )}
          </div>

          <div className="px-4 py-2.5 bg-slate-950/60 border-t border-slate-800/80 text-center">
            <Link
              to="/dashboard"
              onClick={() => setIsOpen(false)}
              className="text-[11px] font-mono text-cyan-400 hover:text-cyan-300 transition-colors"
            >
              View Engineering Activity Center ➔
            </Link>
          </div>
        </div>
      )}
    </div>
  )
}
