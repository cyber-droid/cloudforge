import { useState, useMemo, useEffect } from 'react'
import { Search, Filter, BookOpen, Layers, Award, Sparkles, X } from 'lucide-react'
import { COURSES } from '../data/coursesData'
import { CourseCard } from '../components/courses/CourseCard'
import { Tabs } from '../components/common/Tabs'
import { PageContainer } from '../components/layout/PageContainer'
import { EmptyState } from '../components/common/EmptyState'
import { api } from '../services/api'
import { mapApiCourseToCourse } from '../utils/courseMapper'
import type { Course } from '../types'

export function CoursesPage() {
  const [coursesList, setCoursesList] = useState<Course[]>(COURSES)
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('All')
  const [selectedLevel, setSelectedLevel] = useState('All')
  const [certificateOnly, setCertificateOnly] = useState(false)
  const [inProgressOnly, setInProgressOnly] = useState(false)
  const [isLoading, setIsLoading] = useState(false)

  const categories = [
    { id: 'All', label: 'All Domains' },
    { id: 'Cloud', label: 'Cloud' },
    { id: 'DevOps', label: 'DevOps' },
    { id: 'DevSecOps', label: 'DevSecOps' },
    { id: 'Kubernetes', label: 'Kubernetes' },
    { id: 'Security', label: 'Security' },
    { id: 'AI', label: 'AI' },
    { id: 'Observability', label: 'Observability' },
    { id: 'Infrastructure as Code', label: 'IaC' },
  ]

  // Fetch backend courses with active API integration
  useEffect(() => {
    let isMounted = true
    async function fetchCourses() {
      try {
        setIsLoading(true)
        const res = await api.getCourses({
          category: selectedCategory !== 'All' ? selectedCategory : undefined,
          difficulty: selectedLevel !== 'All' ? selectedLevel : undefined,
          search: searchQuery.trim() || undefined,
          certificate_available: certificateOnly ? true : undefined,
          page_size: 50,
        })
        if (isMounted && res.items && res.items.length > 0) {
          const mapped = res.items.map(c => mapApiCourseToCourse(c))
          setCoursesList(mapped)
        }
      } catch (err) {
        // Fallback to local data on offline or connection error
        console.warn('Backend courses API unavailable, using local catalog data:', err)
      } finally {
        if (isMounted) setIsLoading(false)
      }
    }

    const timeout = setTimeout(() => {
      fetchCourses()
    }, 150)

    return () => {
      isMounted = false
      clearTimeout(timeout)
    }
  }, [selectedCategory, selectedLevel, searchQuery, certificateOnly])

  const filteredCourses = useMemo(() => {
    return coursesList.filter(course => {
      // In-Progress filter
      if (inProgressOnly && (!course.progress || course.progress === 0)) {
        return false
      }
      return true
    })
  }, [coursesList, inProgressOnly])

  const clearFilters = () => {
    setSearchQuery('')
    setSelectedCategory('All')
    setSelectedLevel('All')
    setCertificateOnly(false)
    setInProgressOnly(false)
  }

  const hasActiveFilters =
    searchQuery !== '' ||
    selectedCategory !== 'All' ||
    selectedLevel !== 'All' ||
    certificateOnly ||
    inProgressOnly

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 pb-16">
      {/* Page Header */}
      <div className="border-b border-slate-800/80 bg-slate-950/80 py-10">
        <PageContainer>
          <div className="max-w-3xl">
            <span className="text-xs font-mono text-cyan-400 uppercase tracking-wider">
              Curriculum Catalog
            </span>
            <h1 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight mt-1">
              Build your engineering foundation.
            </h1>
            <p className="text-sm text-slate-400 mt-2 leading-relaxed">
              Explore 9 rigorous, production-grade cloud and DevOps training modules backed by PostgreSQL. Built by principal engineers and maintainers.
            </p>
          </div>
        </PageContainer>
      </div>

      <PageContainer>
        {/* Search & Domain Tabs */}
        <div className="space-y-4 mb-8">
          <div className="flex flex-col md:flex-row items-stretch md:items-center justify-between gap-4">
            {/* Search input */}
            <div className="relative flex-1 max-w-lg">
              <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
              <input
                type="text"
                value={searchQuery}
                onChange={e => setSearchQuery(e.target.value)}
                placeholder="Search courses, technologies (e.g., Docker, Kubernetes, AWS, Prometheus)..."
                className="w-full bg-slate-900/90 border border-slate-800 rounded-xl pl-10 pr-4 py-2.5 text-xs text-slate-100 placeholder:text-slate-500 focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500/20 font-sans"
              />
              {searchQuery && (
                <button
                  onClick={() => setSearchQuery('')}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300"
                >
                  <X className="w-3.5 h-3.5" />
                </button>
              )}
            </div>

            {/* Quick Secondary Filters */}
            <div className="flex flex-wrap items-center gap-2">
              <select
                value={selectedLevel}
                onChange={e => setSelectedLevel(e.target.value)}
                className="bg-slate-900 border border-slate-800 rounded-xl px-3 py-2 text-xs font-mono text-slate-300 focus:outline-none focus:border-cyan-500"
              >
                <option value="All">Level: All</option>
                <option value="Beginner">Beginner</option>
                <option value="Intermediate">Intermediate</option>
                <option value="Advanced">Advanced</option>
              </select>

              <button
                onClick={() => setCertificateOnly(!certificateOnly)}
                className={`flex items-center gap-1.5 px-3 py-2 rounded-xl text-xs font-mono border transition-all cursor-pointer ${
                  certificateOnly
                    ? 'bg-amber-950/60 border-amber-600 text-amber-300'
                    : 'bg-slate-900 border-slate-800 text-slate-400 hover:text-slate-200'
                }`}
              >
                <Award className="w-3.5 h-3.5" />
                <span>Certificate</span>
              </button>

              <button
                onClick={() => setInProgressOnly(!inProgressOnly)}
                className={`flex items-center gap-1.5 px-3 py-2 rounded-xl text-xs font-mono border transition-all cursor-pointer ${
                  inProgressOnly
                    ? 'bg-cyan-950/60 border-cyan-600 text-cyan-300'
                    : 'bg-slate-900 border-slate-800 text-slate-400 hover:text-slate-200'
                }`}
              >
                <BookOpen className="w-3.5 h-3.5" />
                <span>Enrolled</span>
              </button>

              {hasActiveFilters && (
                <button
                  onClick={clearFilters}
                  className="text-xs font-mono text-slate-400 hover:text-rose-400 px-2 py-1 transition-colors"
                >
                  Reset
                </button>
              )}
            </div>
          </div>

          {/* Domain Tabs */}
          <div className="pt-2 overflow-x-auto">
            <Tabs
              tabs={categories}
              activeTab={selectedCategory}
              onChange={setSelectedCategory}
              variant="pills"
            />
          </div>
        </div>

        {/* Results Counter */}
        <div className="flex items-center justify-between text-xs font-mono text-slate-400 mb-6">
          <span>
            {isLoading ? 'Querying PostgreSQL catalog...' : `Showing ${filteredCourses.length} engineering courses`}
          </span>
          {hasActiveFilters && (
            <span className="text-cyan-400">Filters active</span>
          )}
        </div>

        {/* Course Cards Grid */}
        {filteredCourses.length === 0 ? (
          <EmptyState
            title="No courses found"
            description="We couldn't find any courses matching your current filters. Try changing your search query or resetting filters."
            actionLabel="Reset All Filters"
            onAction={clearFilters}
          />
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredCourses.map(course => (
              <CourseCard key={course.id} course={course} />
            ))}
          </div>
        )}
      </PageContainer>
    </div>
  )
}
