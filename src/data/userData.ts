import type { UserProfile } from '../types'

// Generate 52 weeks of activity grid data (7 days * 52 weeks = 364 days)
function generateActivityGrid(): { date: string; count: number }[] {
  const result: { date: string; count: number }[] = []
  const today = new Date()
  
  for (let i = 364; i >= 0; i--) {
    const d = new Date(today)
    d.setDate(d.getDate() - i)
    const dateStr = d.toISOString().split('T')[0]
    
    // Simulate active engineering pattern (more commits/labs in the last 60 days)
    let count = 0
    if (i < 14) {
      count = Math.floor(Math.random() * 5) + 2 // very active recently (streak)
    } else if (i < 90) {
      count = Math.random() > 0.3 ? Math.floor(Math.random() * 4) + 1 : 0
    } else {
      count = Math.random() > 0.6 ? Math.floor(Math.random() * 3) + 1 : 0
    }
    
    result.push({ date: dateStr, count })
  }
  return result
}

export const USER_PROFILE: UserProfile = {
  name: 'Alex Rivera',
  handle: 'alex-rivera-ops',
  role: 'Cloud & DevOps Engineer in Training',
  avatar: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&auto=format&fit=crop&q=80',
  overallProgress: 42,
  learningStreak: 12,
  learningHours: 38.5,
  coursesCompleted: 2,
  certificatesEarned: 3,
  currentCourseId: 'kubernetes-engineering',
  currentLessonId: 'k8s-402',
  joinedDate: 'July 2026',
  weeklyHours: [
    { day: 'Mon', hours: 3.2 },
    { day: 'Tue', hours: 4.5 },
    { day: 'Wed', hours: 2.8 },
    { day: 'Thu', hours: 5.1 },
    { day: 'Fri', hours: 4.0 },
    { day: 'Sat', hours: 6.5 },
    { day: 'Sun', hours: 4.2 },
  ],
  activityGrid: generateActivityGrid(),
}
