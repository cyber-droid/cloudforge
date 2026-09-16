import { useState, useEffect } from 'react'
import { CheckCircle2, AlertCircle, Clock, Trophy, Award, X, ArrowRight, RotateCcw, Loader2 } from 'lucide-react'
import { Modal } from '../common/Modal'
import { Button } from '../common/Button'
import type { Certification } from '../../types'
import { api } from '../../services/api'
import type { ApiPracticeAttemptDetail, ApiPracticeAttemptResult, ApiPracticeQuestion } from '../../services/api'

interface ExamSimulatorModalProps {
  certification: Certification | { id: string; code?: string; title: string; questions?: any[] }
  isOpen: boolean
  onClose: () => void
}

export function ExamSimulatorModal({
  certification,
  isOpen,
  onClose,
}: ExamSimulatorModalProps) {
  const [attempt, setAttempt] = useState<ApiPracticeAttemptDetail | null>(null)
  const [result, setResult] = useState<ApiPracticeAttemptResult | null>(null)
  const [currentIndex, setCurrentIndex] = useState(0)
  const [selectedAnswers, setSelectedAnswers] = useState<Record<string, number>>({})
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [isLoadingQuestions, setIsLoadingQuestions] = useState(false)
  const [timeSpentSeconds, setTimeSpentSeconds] = useState(0)

  // Start attempt when modal opens
  useEffect(() => {
    let timer: ReturnType<typeof setInterval> | undefined
    if (isOpen) {
      handleStartAttempt()
      timer = setInterval(() => {
        setTimeSpentSeconds(prev => prev + 1)
      }, 1000)
    } else {
      handleReset()
    }
    return () => {
      if (timer) clearInterval(timer)
    }
  }, [isOpen, certification.id])

  const handleStartAttempt = async () => {
    setIsLoadingQuestions(true)
    setResult(null)
    setSelectedAnswers({})
    setCurrentIndex(0)
    setTimeSpentSeconds(0)

    try {
      const data = await api.startPracticeAttempt(certification.id, {
        attempt_type: 'practice_exam',
        question_count: 5,
      })
      if (data && data.questions && data.questions.length > 0) {
        setAttempt(data)
      } else {
        throw new Error('No practice questions returned from API')
      }
    } catch (err) {
      console.warn('Backend practice attempt initialization failed, falling back to local dataset', err)
      // Fallback to static mock questions
      const localQs = ('questions' in certification && Array.isArray(certification.questions))
        ? certification.questions.map((q: any, i: number) => ({
            id: q.id || `q-${i}`,
            question_text: q.question,
            question_type: 'single_choice',
            options: q.options,
            topic: q.domain || 'Cloud Architecture',
            domain: q.domain || 'Domain Prep',
            difficulty: 'medium',
            points: 10,
          }))
        : []

      setAttempt({
        id: `mock-attempt-${Date.now()}`,
        certification_id: certification.id,
        attempt_type: 'practice_exam',
        total_questions: localQs.length,
        score: 0,
        percentage: 0,
        passed: false,
        passing_percentage: 70,
        correct_answers: 0,
        time_spent_seconds: 0,
        started_at: new Date().toISOString(),
        questions: localQs,
      })
    } finally {
      setIsLoadingQuestions(false)
    }
  }

  const handleSelect = (optionIdx: number) => {
    if (result) return
    const currentQ = attempt?.questions[currentIndex]
    if (currentQ) {
      setSelectedAnswers(prev => ({ ...prev, [currentQ.id]: optionIdx }))
    }
  }

  const handleReset = () => {
    setSelectedAnswers({})
    setResult(null)
    setCurrentIndex(0)
    setTimeSpentSeconds(0)
  }

  const handleSubmit = async () => {
    if (!attempt || isSubmitting) return
    setIsSubmitting(true)

    try {
      // Real backend evaluation
      const res = await api.submitPracticeAttempt(attempt.id, selectedAnswers, timeSpentSeconds)
      setResult(res)
    } catch (err) {
      console.warn('Backend submit attempt failed, evaluating client-side fallback', err)
      // Fallback local scoring if offline
      const staticQs = ('questions' in certification && Array.isArray(certification.questions)) ? certification.questions : []
      let correct = 0
      const reviews = attempt.questions.map((q, idx) => {
        const userSel = selectedAnswers[q.id]
        const staticQ = staticQs[idx]
        const correctOpt = staticQ ? staticQ.correctIndex : 0
        const isCorr = userSel === correctOpt
        if (isCorr) correct++
        return {
          question_id: q.id,
          question_text: q.question_text,
          options: q.options,
          topic: q.topic,
          domain: q.domain,
          difficulty: q.difficulty,
          selected_option: userSel,
          correct_option: correctOpt,
          is_correct: isCorr,
          explanation: staticQ?.explanation || 'Detailed architectural review and explanation for this concept.',
          points_earned: isCorr ? 10 : 0,
        }
      })

      const pct = attempt.questions.length > 0 ? Math.round((correct / attempt.questions.length) * 100) : 0
      setResult({
        id: attempt.id,
        certification_id: certification.id,
        attempt_type: attempt.attempt_type,
        score: correct * 10,
        percentage: pct,
        passed: pct >= 70,
        passing_percentage: 70,
        total_questions: attempt.questions.length,
        correct_answers: correct,
        time_spent_seconds: timeSpentSeconds,
        started_at: attempt.started_at,
        results: reviews,
        question_results: reviews,
      })
    } finally {
      setIsSubmitting(false)
    }
  }

  const questions: ApiPracticeQuestion[] = attempt?.questions || []
  const currentQ = questions[currentIndex]
  const isPassing = result ? result.passed : false

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={`${certification.code || 'CloudForge'} Practice Exam Simulator`}
      subtitle={`Simulated domain assessment for ${certification.title}`}
      maxWidth="2xl"
    >
      {isLoadingQuestions ? (
        <div className="py-16 text-center space-y-3">
          <Loader2 className="w-8 h-8 text-amber-400 animate-spin mx-auto" />
          <p className="text-xs font-mono text-slate-400">Loading simulated exam questions from server...</p>
        </div>
      ) : !result ? (
        <div className="space-y-6">
          {/* Header info */}
          <div className="flex items-center justify-between p-3 rounded-xl bg-slate-950 border border-slate-800 text-xs font-mono">
            <span className="text-cyan-400">
              Question {currentIndex + 1} of {questions.length}
            </span>
            <span className="text-slate-400">Domain: {currentQ?.domain || currentQ?.topic || 'Exam Blueprint'}</span>
            <div className="flex items-center gap-1 text-amber-400">
              <Clock className="w-3.5 h-3.5" />
              <span>Time: {Math.floor(timeSpentSeconds / 60)}:{(timeSpentSeconds % 60).toString().padStart(2, '0')}</span>
            </div>
          </div>

          {/* Question text */}
          <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800">
            <p className="text-sm font-semibold text-white leading-relaxed">
              {currentQ?.question_text}
            </p>
          </div>

          {/* Options */}
          <div className="space-y-2.5">
            {currentQ?.options?.map((opt, idx) => {
              const isSelected = selectedAnswers[currentQ.id] === idx
              return (
                <button
                  key={idx}
                  onClick={() => handleSelect(idx)}
                  className={`w-full text-left p-3.5 rounded-xl border text-xs font-sans transition-all flex items-center justify-between cursor-pointer ${
                    isSelected
                      ? 'border-cyan-500 bg-cyan-950/40 text-cyan-200 font-semibold ring-1 ring-cyan-500/30'
                      : 'border-slate-800 bg-slate-950/40 hover:border-slate-700 text-slate-300'
                  }`}
                >
                  <span>{opt}</span>
                  <span
                    className={`w-4 h-4 rounded-full border flex items-center justify-center text-[10px] shrink-0 ml-2 ${
                      isSelected
                        ? 'border-cyan-400 bg-cyan-400 text-slate-950 font-bold'
                        : 'border-slate-700 text-slate-500'
                    }`}
                  >
                    {String.fromCharCode(65 + idx)}
                  </span>
                </button>
              )
            })}
          </div>

          {/* Navigation Controls */}
          <div className="pt-4 border-t border-slate-800 flex items-center justify-between">
            <Button
              variant="outline"
              size="sm"
              disabled={currentIndex === 0}
              onClick={() => setCurrentIndex(prev => prev - 1)}
            >
              Previous
            </Button>

            {currentIndex < questions.length - 1 ? (
              <Button
                variant="primary"
                size="sm"
                onClick={() => setCurrentIndex(prev => prev + 1)}
              >
                Next Question
              </Button>
            ) : (
              <Button
                variant="glow"
                size="sm"
                disabled={isSubmitting}
                onClick={handleSubmit}
              >
                {isSubmitting ? 'Evaluating Server-Side...' : 'Submit Exam'}
              </Button>
            )}
          </div>
        </div>
      ) : (
        /* Results View */
        <div className="space-y-6 text-center py-4">
          <div
            className={`w-16 h-16 rounded-2xl mx-auto flex items-center justify-center border ${
              isPassing
                ? 'bg-emerald-950/60 border-emerald-500 text-emerald-400'
                : 'bg-amber-950/60 border-amber-500 text-amber-400'
            }`}
          >
            {isPassing ? <Trophy className="w-8 h-8" /> : <AlertCircle className="w-8 h-8" />}
          </div>

          <div>
            <h3 className="text-2xl font-extrabold text-white">
              {isPassing ? 'Assessment Passed!' : 'Requires Further Study'}
            </h3>
            <p className="text-xs text-slate-400 mt-1 font-mono">
              Score: <span className="font-bold text-white">{result.percentage}%</span> ({result.correct_answers} / {result.total_questions} correct) • Passing bar: {result.passing_percentage}%
            </p>
          </div>

          {/* Review of each question */}
          <div className="space-y-4 text-left max-h-[40vh] overflow-y-auto p-1">
            {(result.question_results || result.results || []).map((q, idx) => {
              const isCorrect = q.is_correct
              return (
                <div
                  key={q.question_id || idx}
                  className={`p-4 rounded-xl border text-xs space-y-2 ${
                    isCorrect
                      ? 'border-emerald-800/60 bg-emerald-950/20'
                      : 'border-rose-800/60 bg-rose-950/20'
                  }`}
                >
                  <div className="flex items-start justify-between gap-2">
                    <p className="font-semibold text-white">
                      Q{idx + 1}: {q.question_text}
                    </p>
                    <span
                      className={`text-[10px] font-mono px-2 py-0.5 rounded font-bold uppercase shrink-0 ${
                        isCorrect ? 'bg-emerald-900 text-emerald-300' : 'bg-rose-900 text-rose-300'
                      }`}
                    >
                      {isCorrect ? 'Correct' : 'Incorrect'}
                    </span>
                  </div>
                  <p className="text-slate-400 text-xs">
                    <span className="font-semibold text-slate-300">Correct Answer:</span>{' '}
                    {q.options && q.correct_option !== undefined && q.options[q.correct_option]
                      ? q.options[q.correct_option]
                      : `Option ${String.fromCharCode(65 + (q.correct_option || 0))}`}
                  </p>
                  <p className="text-slate-400 text-[11px] font-mono italic">
                    Explanation: {q.explanation}
                  </p>
                </div>
              )
            })}
          </div>

          <div className="pt-4 border-t border-slate-800 flex items-center justify-center gap-3">
            <Button variant="secondary" size="sm" onClick={handleStartAttempt} icon={<RotateCcw className="w-3.5 h-3.5" />}>
              Retake Assessment
            </Button>
            <Button variant="primary" size="sm" onClick={onClose}>
              Done Reviewing
            </Button>
          </div>
        </div>
      )}
    </Modal>
  )
}
