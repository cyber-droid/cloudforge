/**
 * CloudForge Frontend API Client
 * 
 * Communicates with the FastAPI backend at /api/v1.
 * Handles JWT token storage, authenticated requests, and error normalization.
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

export interface ApiCourse {
  id: string
  slug: string
  title: string
  description: string
  long_description?: string
  category: string
  difficulty: string
  duration_minutes: number
  thumbnail_url?: string
  rating: number
  students_count: number
  certificate_available: boolean
  published: boolean
  technologies: string[]
  learning_outcomes: string[]
  instructor_name?: string
  instructor_role?: string
  instructor_avatar?: string
  instructor_verified?: boolean
  modules_count?: number
  lessons_count?: number
  modules?: ApiModule[]
}

export interface ApiModule {
  id: string
  course_id: string
  module_number: string
  title: string
  description?: string
  order_index: number
  published: boolean
  lessons_count?: number
  lessons?: ApiLesson[]
}

export interface ApiLesson {
  id: string
  module_id?: string
  title: string
  slug: string
  description?: string
  content?: string
  lesson_type: string
  estimated_minutes: number
  order_index: number
  video_url?: string
  published: boolean
  resources?: ApiLessonResource[]
}

export interface ApiLessonResource {
  id: string
  lesson_id: string
  title: string
  resource_type: string
  url: string
  description?: string
  order_index: number
}

export interface ApiEnrollment {
  id: string
  user_id: string
  course_id: string
  status: string
  enrolled_at: string
  completed_at?: string
  course?: ApiCourse
}

export interface ApiLessonProgress {
  id: string
  user_id: string
  lesson_id: string
  status: string
  started_at: string
  completed_at?: string
  time_spent_seconds: number
  last_accessed_at: string
}

export interface ApiCourseProgress {
  course_id: string
  course_slug: string
  course_title: string
  total_lessons: number
  completed_lessons: number
  in_progress_lessons: number
  progress_percentage: number
  status: string
  started_at?: string
  last_accessed_at?: string
  completed_at?: string
}

export interface ApiContinueLearning {
  course_id: string
  course_slug: string
  course_title: string
  module_id: string
  module_title: string
  module_number: string
  lesson_id: string
  lesson_slug: string
  lesson_title: string
  progress_percentage: number
  estimated_time_remaining: string
  last_accessed_at: string
}

export interface ApiLearningActivity {
  id: string
  activity_type: string
  title: string
  course_slug?: string
  course_title?: string
  lesson_slug?: string
  lesson_title?: string
  duration_seconds: number
  created_at: string
}

export interface ApiDailyActivity {
  date: string
  count: number
  lessons_completed: number
  time_spent_seconds: number
}

export interface ApiWeeklyHour {
  day: string
  hours: number
}

export interface ApiOverallProgress {
  overall_progress_percentage: number
  enrolled_courses: number
  completed_courses: number
  in_progress_courses: number
  completed_lessons: number
  total_lessons: number
  learning_hours: number
  current_streak: number
  longest_streak: number
}

export interface ApiDashboardStats {
  overall_progress: number
  learning_hours: number
  current_streak: number
  longest_streak: number
  courses_completed: number
  courses_enrolled: number
  lessons_completed: number
}

export interface ApiDashboard {
  user: {
    id: string
    email: string
    name: string
    role: string
    avatar_url?: string
    learning_goal?: string
  }
  stats: ApiDashboardStats
  continue_learning?: ApiContinueLearning
  recent_activity: ApiLearningActivity[]
  weekly_activity: ApiDailyActivity[]
  weekly_hours: ApiWeeklyHour[]
  course_progress: ApiCourseProgress[]
}

export interface CourseListParams {
  page?: number
  page_size?: number
  category?: string
  difficulty?: string
  technology?: string
  search?: string
  certificate_available?: boolean
}

class ApiClient {
  private getToken(): string | null {
    return localStorage.getItem('cloudforge_access_token')
  }

  public setTokens(accessToken: string, refreshToken?: string) {
    localStorage.setItem('cloudforge_access_token', accessToken)
    if (refreshToken) {
      localStorage.setItem('cloudforge_refresh_token', refreshToken)
    }
  }

  public clearTokens() {
    localStorage.removeItem('cloudforge_access_token')
    localStorage.removeItem('cloudforge_refresh_token')
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const token = this.getToken()
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...(options.headers as Record<string, string>),
    }

    if (token) {
      headers['Authorization'] = `Bearer ${token}`
    }

    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers,
    })

    if (!response.ok) {
      let errorMessage = `HTTP Error ${response.status}`
      try {
        const errorData = await response.json()
        errorMessage = errorData.message || errorData.detail || errorMessage
      } catch {
        // use default
      }
      throw new Error(errorMessage)
    }

    return response.json() as Promise<T>
  }

  // Course Endpoints
  async getCourses(params: CourseListParams = {}) {
    const query = new URLSearchParams()
    if (params.page) query.append('page', params.page.toString())
    if (params.page_size) query.append('page_size', params.page_size.toString())
    if (params.category && params.category !== 'All') query.append('category', params.category)
    if (params.difficulty && params.difficulty !== 'All') query.append('difficulty', params.difficulty)
    if (params.technology) query.append('technology', params.technology)
    if (params.search) query.append('search', params.search)
    if (params.certificate_available !== undefined) query.append('certificate_available', params.certificate_available.toString())

    const qs = query.toString() ? `?${query.toString()}` : ''
    return this.request<{ items: ApiCourse[]; total: number; page: number; page_size: number; total_pages: number }>(`/courses${qs}`)
  }

  async getCourse(courseIdOrSlug: string) {
    return this.request<ApiCourse>(`/courses/${courseIdOrSlug}`)
  }

  async getCourseCurriculum(courseIdOrSlug: string) {
    return this.request<{ course_id: string; course_title: string; course_slug: string; modules: ApiModule[] }>(`/courses/${courseIdOrSlug}/curriculum`)
  }

  async getLesson(courseId: string, lessonId: string) {
    return this.request<ApiLesson>(`/courses/${courseId}/lessons/${lessonId}`)
  }

  async enrollCourse(courseIdOrSlug: string) {
    return this.request<ApiEnrollment>(`/courses/${courseIdOrSlug}/enroll`, {
      method: 'POST',
    })
  }

  async unenrollCourse(courseIdOrSlug: string) {
    return this.request<{ message: string }>(`/courses/${courseIdOrSlug}/enroll`, {
      method: 'DELETE',
    })
  }

  async getMyCourses() {
    return this.request<ApiEnrollment[]>('/users/me/courses')
  }

  async getMyCourseEnrollment(courseIdOrSlug: string) {
    return this.request<ApiEnrollment>(`/users/me/courses/${courseIdOrSlug}`)
  }

  // Phase 4: Lesson Progress & Time Tracking Endpoints
  async startLesson(lessonId: string) {
    return this.request<ApiLessonProgress>(`/lessons/${lessonId}/start`, {
      method: 'POST',
    })
  }

  async recordLessonProgress(lessonId: string, timeSpentSeconds: number, status?: string) {
    return this.request<ApiLessonProgress>(`/lessons/${lessonId}/progress`, {
      method: 'POST',
      body: JSON.stringify({ time_spent_seconds: timeSpentSeconds, status }),
    })
  }

  async completeLesson(lessonId: string, timeSpentSeconds: number = 0) {
    return this.request<ApiLessonProgress>(`/lessons/${lessonId}/complete`, {
      method: 'POST',
      body: JSON.stringify({ time_spent_seconds: timeSpentSeconds }),
    })
  }

  // Phase 4: User Progress & Dashboard Endpoints
  async getMyOverallProgress() {
    return this.request<ApiOverallProgress>('/users/me/progress')
  }

  async getMyCourseProgress(courseIdOrSlug: string) {
    return this.request<ApiCourseProgress>(`/users/me/courses/${courseIdOrSlug}/progress`)
  }

  async getMyContinueLearning() {
    return this.request<ApiContinueLearning | null>('/users/me/continue-learning')
  }

  async getMyActivity(period: string = 'month') {
    return this.request<ApiDailyActivity[]>(`/users/me/activity?period=${period}`)
  }

  async getMyRecentActivity(limit: number = 10) {
    return this.request<ApiLearningActivity[]>(`/users/me/activity/recent?limit=${limit}`)
  }

  async getMyDashboard() {
    return this.request<ApiDashboard>('/users/me/dashboard')
  }

  // Phase 5: Roadmaps Endpoints
  async getRoadmaps(params?: { category?: string; difficulty?: string; search?: string }) {
    const searchParams = new URLSearchParams()
    if (params?.category && params.category !== 'All') searchParams.append('category', params.category)
    if (params?.difficulty) searchParams.append('difficulty', params.difficulty)
    if (params?.search) searchParams.append('search', params.search)
    const qs = searchParams.toString()
    return this.request<ApiRoadmapList>(`/roadmaps${qs ? `?${qs}` : ''}`)
  }

  async getRoadmap(roadmapIdOrSlug: string) {
    return this.request<ApiRoadmapDetail>(`/roadmaps/${roadmapIdOrSlug}`)
  }

  async getRoadmapSteps(roadmapIdOrSlug: string) {
    return this.request<ApiRoadmapStep[]>(`/roadmaps/${roadmapIdOrSlug}/steps`)
  }

  async startRoadmap(roadmapIdOrSlug: string) {
    return this.request<ApiUserRoadmapProgress>(`/roadmaps/${roadmapIdOrSlug}/start`, {
      method: 'POST',
    })
  }

  async getMyRoadmaps() {
    return this.request<ApiUserRoadmapProgress[]>('/users/me/roadmaps')
  }

  async getMyRoadmapProgress(roadmapIdOrSlug: string) {
    return this.request<ApiUserRoadmapProgress>(`/users/me/roadmaps/${roadmapIdOrSlug}`)
  }

  // Phase 5: Skills Endpoints
  async getSkills(category?: string) {
    const qs = category && category !== 'All' ? `?category=${category}` : ''
    return this.request<ApiSkillSummary[]>(`/skills${qs}`)
  }

  async getSkill(skillIdOrSlug: string) {
    return this.request<ApiSkillSummary>(`/skills/${skillIdOrSlug}`)
  }

  async getMySkills() {
    return this.request<ApiUserSkillMatrix>('/users/me/skills')
  }

  async getMySkill(skillIdOrSlug: string) {
    return this.request<ApiUserSkill>(`/users/me/skills/${skillIdOrSlug}`)
  }

  async recalculateMySkill(skillIdOrSlug: string) {
    return this.request<ApiUserSkill>(`/users/me/skills/${skillIdOrSlug}/recalculate`, {
      method: 'POST',
    })
  }

  // Phase 6: Certifications & Training Endpoints
  async getCertifications(provider?: string) {
    const qs = provider && provider !== 'All' ? `?provider=${encodeURIComponent(provider)}` : ''
    return this.request<ApiCertificationSummary[]>(`/certifications${qs}`)
  }

  async getCertification(slugOrId: string) {
    return this.request<ApiCertificationDetail>(`/certifications/${slugOrId}`)
  }

  async getCertificationTrainings(certificationId: string) {
    return this.request<ApiTrainingSummary[]>(`/certifications/${certificationId}/trainings`)
  }

  async getTraining(trainingIdOrSlug: string) {
    return this.request<ApiTrainingDetail>(`/trainings/${trainingIdOrSlug}`)
  }

  async enrollTraining(trainingIdOrSlug: string) {
    return this.request<ApiTrainingSummary>(`/trainings/${trainingIdOrSlug}/enroll`, {
      method: 'POST',
    })
  }

  async getTrainingProgress(trainingIdOrSlug: string) {
    return this.request<ApiTrainingProgress>(`/trainings/${trainingIdOrSlug}/progress`)
  }

  async completeTraining(trainingIdOrSlug: string) {
    return this.request<ApiCertificate>(`/trainings/${trainingIdOrSlug}/complete`, {
      method: 'POST',
    })
  }

  // Phase 6: Practice Exams & Quiz Simulator
  async startPracticeAttempt(
    certificationId: string,
    payload?: { attempt_type?: string; limit?: number; question_count?: number; domain?: string }
  ) {
    return this.request<ApiPracticeAttemptDetail>(`/certifications/${certificationId}/practice-attempts`, {
      method: 'POST',
      body: JSON.stringify(payload || { attempt_type: 'practice_quiz', question_count: 5 }),
    })
  }

  async getPracticeAttempt(attemptId: string) {
    return this.request<ApiPracticeAttemptDetail>(`/practice-attempts/${attemptId}`)
  }

  async submitPracticeAttempt(
    attemptId: string,
    answers: { question_id: string; selected_option: number }[] | Record<string, number>,
    timeSpentSeconds: number = 0
  ) {
    return this.request<ApiPracticeAttemptResult>(`/practice-attempts/${attemptId}/submit`, {
      method: 'POST',
      body: JSON.stringify({ answers, time_spent_seconds: timeSpentSeconds }),
    })
  }

  async getPracticeAttemptResults(attemptId: string) {
    return this.request<ApiPracticeAttemptResult>(`/practice-attempts/${attemptId}/results`)
  }

  async getMyPracticeAttempts(params?: { certification_id?: string; attempt_type?: string; passed?: boolean }) {
    const sp = new URLSearchParams()
    if (params?.certification_id) sp.append('certification_id', params.certification_id)
    if (params?.attempt_type) sp.append('attempt_type', params.attempt_type)
    if (params?.passed !== undefined) sp.append('passed', String(params.passed))
    const qs = sp.toString()
    return this.request<ApiPracticeAttemptSummary[]>(`/practice-attempts${qs ? `?${qs}` : ''}`)
  }

  // Phase 6: Certificates & Verification
  async getMyCertificates() {
    return this.request<ApiCertificate[]>('/certificates')
  }

  async getCertificate(certificateId: string) {
    return this.request<ApiCertificate>(`/certificates/${certificateId}`)
  }

  async verifyCertificate(verificationCode: string) {
    return this.request<ApiCertificateVerify>(`/certificates/verify/${verificationCode}`)
  }
}

export interface ApiSkillCourseReference {
  id: string
  title: string
  slug?: string
}

export interface ApiSkillSummary {
  id: string
  slug: string
  name: string
  description?: string
  category: string
  target_level: number
  target_level_name: string
  trend?: string
  courses_count: number
  related_courses: ApiSkillCourseReference[]
}

export interface ApiUserSkill {
  id: string
  skill_id: string
  slug: string
  name: string
  description?: string
  category: string
  current_level: number
  current_level_name: string
  target_level: number
  target_level_name: string
  proficiency_percentage: number
  trend?: string
  related_courses: ApiSkillCourseReference[]
  last_updated_at?: string
}

export interface ApiUserSkillMatrix {
  total_skills: number
  average_proficiency: number
  top_skills: ApiUserSkill[]
  skills: ApiUserSkill[]
}

export interface ApiRoadmapStep {
  id: string
  title: string
  description?: string
  step_type: string
  order_index: number
  required: boolean
  estimated_hours?: string
  skills_covered: string[]
  course_id?: string
  skill_id?: string
  status?: string
  completed?: boolean
  progress_percentage?: number
  linked_course?: {
    id: string
    title: string
    slug: string
    difficulty?: string
    duration_minutes?: number
  }
  linked_skill?: {
    id: string
    name: string
    slug: string
    category?: string
    target_level?: number
  }
}

export interface ApiRoadmapSummary {
  id: string
  slug: string
  title: string
  description?: string
  category: string
  difficulty: string
  duration_label?: string
  estimated_duration_hours?: number
  skills_count: number
  projects_count: number
  certifications_targeted: string[]
  step_count: number
  nodes: ApiRoadmapStep[]
  progress_percentage?: number
  status?: string
}

export interface ApiRoadmapDetail extends ApiRoadmapSummary {}

export interface ApiRoadmapList {
  total: number
  page: number
  limit: number
  items: ApiRoadmapSummary[]
}

export interface ApiUserRoadmapProgress {
  id: string
  roadmap_id: string
  status: string
  progress_percentage: number
  completed_steps: number
  total_required_steps: number
  started_at?: string
  completed_at?: string
  last_activity_at?: string
  roadmap?: ApiRoadmapDetail
}

export interface ApiExamDomain {
  name: string
  percentage: number
}

export interface ApiCertificationSummary {
  id: string
  code?: string
  title: string
  name: string
  slug: string
  provider: string
  vendor: string
  level: string
  category: string
  badge_icon: string
  duration: string
  training_title: string
  description: string
  training_certificate_name: string
  official_url?: string
  is_official_certification: boolean
  is_published: boolean
  domains: ApiExamDomain[]
  skills_gained: string[]
  practice_questions_count: number
  mock_exams_count: number
  progress: number
  created_at?: string
}

export interface ApiTrainingSummary {
  id: string
  certification_id: string
  title: string
  slug: string
  description: string
  level: string
  estimated_hours: string | number
  course_id?: string
  modules: string[]
  is_published: boolean
  progress_percentage: number
  status: string
  created_at?: string
}

export interface ApiCertificationDetail extends ApiCertificationSummary {
  trainings: ApiTrainingSummary[]
}

export interface ApiTrainingDetail extends ApiTrainingSummary {
  course_title?: string
  course_slug?: string
  total_lessons: number
  completed_lessons: number
}

export interface ApiTrainingProgress {
  training_id: string
  certification_id: string
  status: string
  progress_percentage: number
  completed_lessons: number
  total_lessons: number
  completed_modules: number
  total_modules: number
  is_eligible_for_certificate: boolean
  certificate_id?: string
}

export interface ApiPracticeQuestion {
  id: string
  question_text: string
  question_type: string
  options: string[]
  topic?: string
  domain?: string
  difficulty: string
  points: number
}

export interface ApiPracticeAttemptDetail {
  id: string
  certification_id: string
  attempt_type: string
  total_questions: number
  score: number
  percentage: number
  passed: boolean
  passing_percentage: number
  correct_answers: number
  time_spent_seconds: number
  started_at: string
  submitted_at?: string
  questions: ApiPracticeQuestion[]
}

export interface ApiQuestionReview {
  id?: string
  question_id?: string
  question_text: string
  options: string[]
  topic?: string
  domain?: string
  difficulty: string
  selected_option?: number
  correct_option?: number
  is_correct: boolean
  explanation: string
  points_earned: number
}

export interface ApiPracticeAttemptResult {
  id: string
  certification_id: string
  attempt_type: string
  score: number
  percentage: number
  passed: boolean
  passing_percentage: number
  total_questions: number
  correct_answers: number
  time_spent_seconds: number
  started_at: string
  submitted_at?: string
  results: ApiQuestionReview[]
  question_results: ApiQuestionReview[]
}

export interface ApiPracticeAttemptSummary {
  id: string
  certification_id: string
  certification_title?: string
  certification_code?: string
  attempt_type: string
  score: number
  percentage: number
  passed: boolean
  total_questions: number
  correct_answers: number
  time_spent_seconds: number
  started_at: string
  submitted_at?: string
}

export interface ApiCertificate {
  id: string
  certificate_number: string
  verification_code: string
  training_id: string
  training_title: string
  certification_id?: string
  recipient_name: string
  issued_at: string
  status: string
  completion_percentage: number
  verification_url: string
}

export interface ApiCertificateVerify {
  is_valid: boolean
  certificate_number: string
  recipient_name: string
  training_title: string
  issued_at: string
  status: string
  completion_percentage: number
  message: string
}

export const api = new ApiClient()

