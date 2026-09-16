import { useState } from 'react'
import { CheckCircle2, AlertCircle, HelpCircle, Check, X } from 'lucide-react'
import { Card } from '../common/Card'
import { Button } from '../common/Button'

interface PracticeQuestion {
  id: string
  question: string
  options: string[]
  correctIndex: number
  explanation: string
}

interface PracticeQuizProps {
  questions: PracticeQuestion[]
}

export function PracticeQuiz({ questions }: PracticeQuizProps) {
  const [selectedAnswers, setSelectedAnswers] = useState<Record<string, number>>({})
  const [revealed, setRevealed] = useState<Record<string, boolean>>({})

  const handleSelect = (questionId: string, optionIdx: number) => {
    setSelectedAnswers(prev => ({ ...prev, [questionId]: optionIdx }))
    setRevealed(prev => ({ ...prev, [questionId]: true }))
  }

  if (!questions || questions.length === 0) return null

  return (
    <div className="mt-10 pt-8 border-t border-slate-800 space-y-6">
      <div className="flex items-center gap-2">
        <HelpCircle className="w-5 h-5 text-cyan-400" />
        <h3 className="text-lg font-bold text-white">Knowledge Check & Practice Drill</h3>
      </div>
      <p className="text-xs text-slate-400 font-mono">
        Test your understanding of the concepts covered in this lesson before proceeding.
      </p>

      <div className="space-y-6">
        {questions.map((q, qIndex) => {
          const selected = selectedAnswers[q.id]
          const isRevealed = !!revealed[q.id]
          const isCorrect = selected === q.correctIndex

          return (
            <Card key={q.id} className="p-6 bg-slate-900/70 space-y-4">
              <div className="flex items-start gap-3">
                <span className="text-xs font-mono font-bold text-cyan-400 bg-slate-800 px-2 py-0.5 rounded border border-slate-700/60">
                  Q{qIndex + 1}
                </span>
                <p className="text-sm font-semibold text-white leading-relaxed">
                  {q.question}
                </p>
              </div>

              <div className="space-y-2 pt-2">
                {q.options.map((option, idx) => {
                  const isThisSelected = selected === idx
                  const isThisCorrect = q.correctIndex === idx

                  let optionStyle = 'border-slate-800 bg-slate-950/60 hover:border-slate-700 text-slate-300'
                  if (isRevealed) {
                    if (isThisCorrect) {
                      optionStyle = 'border-emerald-500/80 bg-emerald-950/30 text-emerald-200 font-semibold'
                    } else if (isThisSelected) {
                      optionStyle = 'border-rose-500/80 bg-rose-950/30 text-rose-200 line-through'
                    }
                  }

                  return (
                    <button
                      key={idx}
                      onClick={() => handleSelect(q.id, idx)}
                      disabled={isRevealed}
                      className={`w-full text-left p-3.5 rounded-xl border text-xs transition-all flex items-center justify-between cursor-pointer ${optionStyle}`}
                    >
                      <span>{option}</span>
                      {isRevealed && isThisCorrect && (
                        <Check className="w-4 h-4 text-emerald-400 shrink-0 ml-2" />
                      )}
                      {isRevealed && isThisSelected && !isThisCorrect && (
                        <X className="w-4 h-4 text-rose-400 shrink-0 ml-2" />
                      )}
                    </button>
                  )
                })}
              </div>

              {/* Explanation Reveal */}
              {isRevealed && (
                <div
                  className={`p-3.5 rounded-xl text-xs font-mono leading-relaxed border ${
                    isCorrect
                      ? 'bg-emerald-950/30 border-emerald-800/60 text-emerald-300'
                      : 'bg-rose-950/30 border-rose-800/60 text-rose-300'
                  }`}
                >
                  <p className="font-semibold mb-1">
                    {isCorrect ? '✓ Correct Answer!' : '✗ Incorrect'}
                  </p>
                  <p className="text-slate-300 font-sans text-xs">{q.explanation}</p>
                </div>
              )}
            </Card>
          )
        })}
      </div>
    </div>
  )
}
