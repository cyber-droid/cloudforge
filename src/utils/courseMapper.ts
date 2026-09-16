import type { ApiCourse } from '../services/api'
import type { Course, Level } from '../types'

/**
 * Maps an API course response to the frontend Course model.
 */
export function mapApiCourseToCourse(apiCourse: ApiCourse, enrolled = false, progress = 0): Course {
  const durationHours = Math.round(apiCourse.duration_minutes / 60) || 8
  const levelStr = apiCourse.difficulty.includes('to')
    ? 'Beginner → Intermediate'
    : (apiCourse.difficulty as Level)

  return {
    id: apiCourse.slug || apiCourse.id,
    slug: apiCourse.slug,
    title: apiCourse.title,
    category: apiCourse.category as any,
    level: levelStr as Level,
    duration: `${durationHours} hours`,
    lessonsCount: apiCourse.lessons_count || 30,
    rating: apiCourse.rating || 4.9,
    studentsCount: apiCourse.students_count || 1200,
    certificate: apiCourse.certificate_available,
    progress: enrolled ? (progress || 15) : undefined,
    description: apiCourse.description,
    longDescription: apiCourse.long_description || apiCourse.description,
    technologies: apiCourse.technologies || [],
    instructor: {
      name: apiCourse.instructor_name || 'CloudForge Staff',
      role: apiCourse.instructor_role || 'Principal Architect',
      avatar: apiCourse.instructor_avatar || 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&auto=format&fit=crop&q=80',
      verified: apiCourse.instructor_verified ?? true,
    },
    learningOutcomes: apiCourse.learning_outcomes || [],
    modules: (apiCourse.modules || []).map(m => ({
      id: m.id,
      number: m.module_number,
      title: m.title,
      lessonCount: m.lessons_count || (m.lessons || []).length,
      duration: '45m',
      completed: false,
      lessons: (m.lessons || []).map(l => ({
        id: l.slug || l.id,
        title: l.title,
        duration: `${l.estimated_minutes || 15}m`,
        completed: false,
        type: (l.lesson_type as any) || 'theory',
      })),
    })),
  }
}
