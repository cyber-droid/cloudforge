import React, { createContext, useContext, useState, useEffect } from 'react'
import type { UserProfile } from '../types'
import { api, type ApiUserResponse } from '../services/api'

interface AuthContextType {
  user: UserProfile | null
  isAuthenticated: boolean
  loading: boolean
  login: (email: string, password: string) => Promise<void>
  register: (payload: { email: string; password: string; name?: string; role?: string; learning_goal?: string }) => Promise<void>
  logout: () => void
  selectedGoal: string
  setSelectedGoal: (goal: string) => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function mapBackendUserToProfile(backendUser: ApiUserResponse): UserProfile {
  const handle = backendUser.email
    ? backendUser.email.split('@')[0].toLowerCase().replace(/[^a-z0-9]/g, '-')
    : 'engineer'
  const defaultAvatar =
    'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&auto=format&fit=crop&q=80'

  const roleLabel =
    backendUser.role === 'admin'
      ? 'Platform Administrator'
      : backendUser.role === 'instructor'
      ? 'Cloud Instructor'
      : 'Cloud & DevOps Engineer in Training'

  return {
    id: backendUser.id,
    email: backendUser.email,
    name: backendUser.name || 'CloudForge Engineer',
    handle,
    role: roleLabel,
    avatar: backendUser.avatar_url || defaultAvatar,
    overallProgress: 0,
    learningStreak: 1,
    learningHours: 0,
    coursesCompleted: 0,
    certificatesEarned: 0,
    currentCourseId: '',
    currentLessonId: '',
    joinedDate: backendUser.created_at
      ? new Date(backendUser.created_at).toLocaleDateString('en-US', { month: 'short', year: 'numeric' })
      : 'Recently',
    weeklyHours: [
      { day: 'Mon', hours: 0 },
      { day: 'Tue', hours: 0 },
      { day: 'Wed', hours: 0 },
      { day: 'Thu', hours: 0 },
      { day: 'Fri', hours: 0 },
      { day: 'Sat', hours: 0 },
      { day: 'Sun', hours: 0 },
    ],
    activityGrid: [],
  }
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<UserProfile | null>(null)
  const [loading, setLoading] = useState<boolean>(true)
  const [selectedGoal, setSelectedGoal] = useState<string>('DevOps')

  useEffect(() => {
    let isMounted = true

    const initAuth = async () => {
      const token = api.getToken()
      if (!token) {
        if (isMounted) {
          setUser(null)
          setLoading(false)
        }
        return
      }

      try {
        const me = await api.getMe()
        if (isMounted) {
          setUser(mapBackendUserToProfile(me))
          if (me.learning_goal) {
            setSelectedGoal(me.learning_goal)
          }
        }
      } catch (err) {
        console.warn('Session verification failed:', err)
        api.clearTokens()
        if (isMounted) {
          setUser(null)
        }
      } finally {
        if (isMounted) {
          setLoading(false)
        }
      }
    }

    initAuth()

    return () => {
      isMounted = false
    }
  }, [])

  const login = async (email: string, password: string) => {
    const res = await api.login({ email, password })
    setUser(mapBackendUserToProfile(res.user))
    if (res.user.learning_goal) {
      setSelectedGoal(res.user.learning_goal)
    }
  }

  const register = async (payload: {
    email: string
    password: string
    name?: string
    role?: string
    learning_goal?: string
  }) => {
    const res = await api.register(payload)
    setUser(mapBackendUserToProfile(res.user))
    if (res.user.learning_goal) {
      setSelectedGoal(res.user.learning_goal)
    }
  }

  const logout = () => {
    api.logout()
    setUser(null)
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        loading,
        login,
        register,
        logout,
        selectedGoal,
        setSelectedGoal,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) throw new Error('useAuth must be used within AuthProvider')
  return context
}
