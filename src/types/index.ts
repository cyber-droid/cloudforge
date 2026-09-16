export type Level = 'Beginner' | 'Intermediate' | 'Advanced' | 'Beginner → Intermediate'

export interface Lesson {
  id: string
  title: string
  duration: string
  completed: boolean
  current?: boolean
  locked?: boolean
  type?: 'theory' | 'hands-on' | 'troubleshooting' | 'quiz'
  content?: {
    estimatedTime: string
    objectives: string[]
    description: string
    architectureDiagram?: string
    sections: {
      title: string
      body: string
      codeSnippet?: {
        language: string
        filename?: string
        code: string
      }
      callout?: {
        type: 'info' | 'warning' | 'tip' | 'danger'
        text: string
      }
    }[]
    practiceQuestions?: {
      id: string
      question: string
      options: string[]
      correctIndex: number
      explanation: string
    }[]
  }
}

export interface Module {
  id: string
  number: string
  title: string
  lessonCount: number
  duration: string
  completed?: boolean
  lessons: Lesson[]
}

export interface Course {
  id: string
  title: string
  slug: string
  category: 'Cloud' | 'DevOps' | 'DevSecOps' | 'Kubernetes' | 'Security' | 'Observability' | 'AI Engineering' | 'Cloud / DevOps' | 'Cloud Security'
  level: Level
  duration: string
  lessonsCount: number
  description: string
  longDescription?: string
  technologies: string[]
  certificate: boolean
  progress?: number
  instructor: {
    name: string
    role: string
    avatar: string
    verified: boolean
  }
  rating: number
  studentsCount: number
  learningOutcomes: string[]
  modules: Module[]
}

export interface Certification {
  id: string
  code?: string
  title: string
  provider: 'AWS' | 'Microsoft Azure' | 'Kubernetes' | 'DevOps'
  level: 'Foundational' | 'Fundamental' | 'Beginner' | 'Intermediate' | 'Associate'
  badgeIcon: string
  duration: string
  trainingTitle: string
  description: string
  progress: number
  practiceQuestionsCount: number
  mockExamsCount: number
  trainingCertificate: string
  modules: string[]
  skillsGained: string[]
  examDomains: {
    name: string
    percentage: number
  }[]
  questions: {
    id: string
    question: string
    options: string[]
    correctIndex: number
    explanation: string
    domain: string
  }[]
}

export interface RoadmapNode {
  id: string
  title: string
  description: string
  status: 'completed' | 'in-progress' | 'upcoming'
  skills: string[]
  estimatedHours: string
  courseId?: string
}

export interface Roadmap {
  id: string
  slug: string
  title: string
  category: string
  description: string
  duration: string
  skillsCount: number
  projectsCount: number
  progress: number
  nodes: RoadmapNode[]
  certificationsTargeted: string[]
}

export interface Skill {
  id: string
  name: string
  category: 'Cloud' | 'DevOps' | 'DevSecOps' | 'Kubernetes' | 'Security' | 'Observability' | 'AI'
  proficiency: number // 0 - 100
  targetLevel: 'Beginner' | 'Beginner+' | 'Intermediate' | 'Advanced'
  levelLabel: string
  relatedCourses: { id: string; title: string }[]
  relatedProjects: { id: string; title: string }[]
  trend: '+4%' | '+12%' | '+8%' | '+2%'
}

export interface Project {
  id: string
  title: string
  slug: string
  description: string
  difficulty: 'Beginner' | 'Intermediate' | 'Advanced'
  estimatedHours: string
  technologies: string[]
  skills: string[]
  progress: number
  githubUrl?: string
  deliverables: string[]
  architectureOverview: string
  tasks: {
    id: string
    title: string
    completed: boolean
    command?: string
  }[]
}

export interface IncidentTimelineEvent {
  time: string
  message: string
  status: 'info' | 'warning' | 'error' | 'success'
}

export interface Incident {
  id: string
  incidentId: string // e.g., INC-0042
  title: string
  severity: 'P1 - Critical' | 'P2 - High' | 'P3 - Medium' | 'P4 - Low'
  severityColor: 'rose' | 'amber' | 'blue' | 'slate'
  technology: string
  status: 'Active' | 'Investigating' | 'Resolved'
  symptoms: string
  skills: string[]
  difficulty: 'Beginner' | 'Intermediate' | 'Advanced'
  timeElapsed: string
  timeline: IncidentTimelineEvent[]
  logs: {
    timestamp: string
    level: 'INFO' | 'WARN' | 'ERROR' | 'FATAL'
    source: string
    message: string
  }[]
  metrics: {
    label: string
    points: { time: string; value: number }[]
  }[]
  aiInvestigation: {
    possibleRootCause: string
    evidence: string[]
    confidence: number // e.g. 94
    recommendedInvestigation: string[]
    suggestedRemediation: string
    remediationCommand?: string
    remediationPatch?: string
  }
}

export interface Achievement {
  id: string
  title: string
  description: string
  icon: string
  earned: boolean
  earnedDate?: string
  category: 'learning' | 'streaks' | 'specialization' | 'troubleshooting'
  xp: number
}

export interface UserProfile {
  name: string
  handle: string
  role: string
  avatar: string
  overallProgress: number
  learningStreak: number
  learningHours: number
  coursesCompleted: number
  certificatesEarned: number
  currentCourseId: string
  currentLessonId: string
  joinedDate: string
  weeklyHours: { day: string; hours: number }[]
  activityGrid: { date: string; count: number }[]
}

export interface NotificationItem {
  id: string
  title: string
  description: string
  timeAgo: string
  read: boolean
  type: 'course' | 'achievement' | 'cert' | 'incident'
  link?: string
}
