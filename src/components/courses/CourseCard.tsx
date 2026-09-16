import { Link } from 'react-router-dom'
import { Clock, BookOpen, Star, Award, CheckCircle2, ArrowRight } from 'lucide-react'
import type { Course } from '../../types'
import { Card } from '../common/Card'
import { Badge } from '../common/Badge'
import { Button } from '../common/Button'

interface CourseCardProps {
  course: Course
}

export function CourseCard({ course }: CourseCardProps) {
  const isEnrolled = course.progress !== undefined && course.progress > 0
  const isCompleted = course.progress === 100

  return (
    <Card className="flex flex-col justify-between hover:border-slate-700 transition-all group p-6">
      <div>
        {/* Category, Level and Certificate */}
        <div className="flex items-center justify-between gap-2 mb-3">
          <div className="flex items-center gap-2">
            <span className="text-[11px] font-mono font-semibold uppercase tracking-wider text-cyan-400">
              {course.category}
            </span>
            <span className="text-slate-600">•</span>
            <span className="text-xs font-mono text-slate-400">{course.level}</span>
          </div>

          {course.certificate && (
            <span className="flex items-center gap-1 text-[11px] font-mono text-amber-400 bg-amber-950/60 px-2 py-0.5 rounded border border-amber-800/40 shrink-0">
              <Award className="w-3 h-3" />
              <span>Cert</span>
            </span>
          )}
        </div>

        {/* Title */}
        <Link to={`/courses/${course.id}`}>
          <h3 className="text-lg font-bold text-white group-hover:text-cyan-300 transition-colors leading-snug">
            {course.title}
          </h3>
        </Link>

        {/* Description */}
        <p className="text-xs text-slate-400 mt-2 leading-relaxed line-clamp-2">
          {course.description}
        </p>

        {/* Technologies Tags */}
        <div className="flex flex-wrap gap-1.5 mt-4">
          {course.technologies.slice(0, 4).map(tech => (
            <span
              key={tech}
              className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800/80 text-slate-300 border border-slate-700/60"
            >
              {tech}
            </span>
          ))}
          {course.technologies.length > 4 && (
            <span className="text-[10px] font-mono px-1.5 py-0.5 rounded text-slate-500">
              +{course.technologies.length - 4}
            </span>
          )}
        </div>

        {/* Course Progress if enrolled */}
        {isEnrolled && (
          <div className="mt-4 pt-3 border-t border-slate-800/80 space-y-1.5">
            <div className="flex justify-between text-xs font-mono">
              <span className="text-slate-400">
                {isCompleted ? 'Course Completed' : 'Progress'}
              </span>
              <span className={isCompleted ? 'text-emerald-400 font-bold' : 'text-cyan-400 font-bold'}>
                {course.progress}%
              </span>
            </div>
            <div className="w-full h-1.5 rounded-full bg-slate-800 overflow-hidden">
              <div
                className={`h-full rounded-full transition-all duration-300 ${
                  isCompleted ? 'bg-emerald-400' : 'bg-cyan-400'
                }`}
                style={{ width: `${course.progress}%` }}
              />
            </div>
          </div>
        )}
      </div>

      {/* Footer: Instructor & CTA */}
      <div className="mt-6 pt-4 border-t border-slate-800 flex items-center justify-between">
        {/* Instructor info */}
        <div className="flex items-center gap-2.5 min-w-0">
          <img
            src={course.instructor.avatar}
            alt={course.instructor.name}
            className="w-7 h-7 rounded-full object-cover ring-1 ring-slate-700 shrink-0"
          />
          <div className="min-w-0">
            <p className="text-xs font-medium text-slate-200 truncate leading-tight">
              {course.instructor.name}
            </p>
            <div className="flex items-center gap-2 text-[10px] text-slate-500 font-mono">
              <span className="flex items-center gap-0.5 text-amber-400">
                <Star className="w-2.5 h-2.5 fill-amber-400" />
                {course.rating}
              </span>
              <span>•</span>
              <span className="flex items-center gap-1">
                <Clock className="w-2.5 h-2.5" />
                {course.duration}
              </span>
            </div>
          </div>
        </div>

        {/* CTA */}
        <Link to={`/courses/${course.id}`}>
          <Button
            variant={isEnrolled ? (isCompleted ? 'outline' : 'primary') : 'secondary'}
            size="xs"
            iconRight={<ArrowRight className="w-3 h-3" />}
          >
            {isEnrolled ? (isCompleted ? 'Review' : 'Resume') : 'Details'}
          </Button>
        </Link>
      </div>
    </Card>
  )
}
