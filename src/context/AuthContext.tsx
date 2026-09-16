import React, { createContext, useContext, useState } from 'react'
import type { UserProfile } from '../types'
import { USER_PROFILE } from '../data/userData'

interface AuthContextType {
  user: UserProfile | null
  isAuthenticated: boolean
  login: (email?: string) => void
  logout: () => void
  selectedGoal: string
  setSelectedGoal: (goal: string) => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<UserProfile | null>(USER_PROFILE)
  const [selectedGoal, setSelectedGoal] = useState<string>('DevOps')

  const login = () => {
    setUser(USER_PROFILE)
  }

  const logout = () => {
    setUser(null)
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        login,
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
