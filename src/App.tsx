import { Routes, Route, useLocation } from 'react-router-dom'
import { Navbar } from './components/layout/Navbar'
import { Footer } from './components/layout/Footer'
import { ScrollToTop } from './components/common/ScrollToTop'

// Pages
import { LandingPage } from './pages/LandingPage'
import { LoginPage } from './pages/LoginPage'
import { RegisterPage } from './pages/RegisterPage'
import { ForgotPasswordPage } from './pages/ForgotPasswordPage'
import { DashboardPage } from './pages/DashboardPage'
import { CoursesPage } from './pages/CoursesPage'
import { CourseDetailPage } from './pages/CourseDetailPage'
import { LessonPlayerPage } from './pages/LessonPlayerPage'
import { RoadmapsPage } from './pages/RoadmapsPage'
import { RoadmapDetailPage } from './pages/RoadmapDetailPage'
import { SkillsPage } from './pages/SkillsPage'
import { CertificationsPage } from './pages/CertificationsPage'
import { CertificationDetailPage } from './pages/CertificationDetailPage'
import { ProjectsPage } from './pages/ProjectsPage'
import { ProjectDetailPage } from './pages/ProjectDetailPage'
import { TroubleshootingPage } from './pages/TroubleshootingPage'
import { IncidentDetailPage } from './pages/IncidentDetailPage'
import { AIEngineeringPage } from './pages/AIEngineeringPage'
import { AchievementsPage } from './pages/AchievementsPage'
import { ProfilePage } from './pages/ProfilePage'
import { SettingsPage } from './pages/SettingsPage'

export function App() {
  const location = useLocation()
  const isLessonPlayer = location.pathname.startsWith('/learn/')

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans antialiased selection:bg-cyan-500/20 selection:text-cyan-300">
      <ScrollToTop />
      
      {/* Global Navbar */}
      <Navbar />

      {/* Main Content Viewport */}
      <main className="flex-1 flex flex-col">
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/forgot-password" element={<ForgotPasswordPage />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/courses" element={<CoursesPage />} />
          <Route path="/courses/:courseId" element={<CourseDetailPage />} />
          <Route path="/learn/:courseId/:lessonId" element={<LessonPlayerPage />} />
          <Route path="/roadmaps" element={<RoadmapsPage />} />
          <Route path="/roadmaps/:id" element={<RoadmapDetailPage />} />
          <Route path="/skills" element={<SkillsPage />} />
          <Route path="/certifications" element={<CertificationsPage />} />
          <Route path="/certifications/:id" element={<CertificationDetailPage />} />
          <Route path="/projects" element={<ProjectsPage />} />
          <Route path="/projects/:id" element={<ProjectDetailPage />} />
          <Route path="/troubleshooting" element={<TroubleshootingPage />} />
          <Route path="/troubleshooting/:id" element={<IncidentDetailPage />} />
          <Route path="/ai" element={<AIEngineeringPage />} />
          <Route path="/achievements" element={<AchievementsPage />} />
          <Route path="/profile" element={<ProfilePage />} />
          <Route path="/settings" element={<SettingsPage />} />
        </Routes>
      </main>

      {/* Global Footer (omitted only inside the 3-pane Lesson Player) */}
      {!isLessonPlayer && <Footer />}
    </div>
  )
}

export default App
