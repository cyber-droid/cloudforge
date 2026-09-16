import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Card } from '../common/Card'
import { Cpu, ArrowRight } from 'lucide-react'
import { SKILLS } from '../../data/skillsData'
import { api, type ApiUserSkill } from '../../services/api'

export function SkillBars() {
  const [skills, setSkills] = useState<{ id: string; name: string; levelLabel: string; proficiency: number }[]>([])

  useEffect(() => {
    async function loadSkills() {
      try {
        const matrix = await api.getMySkills()
        if (matrix?.skills && matrix.skills.length > 0) {
          // Take top skills or first 6 skills
          const items = (matrix.top_skills?.length > 0 ? matrix.top_skills : matrix.skills)
            .slice(0, 6)
            .map((s: ApiUserSkill) => ({
              id: s.slug || s.id,
              name: s.name,
              levelLabel: s.current_level_name,
              proficiency: Math.round(s.proficiency_percentage),
            }))
          setSkills(items)
          return
        }
      } catch (err) {
        console.warn('Could not load user skills for dashboard, using fallback:', err)
      }

      // Fallback
      setSkills(
        SKILLS.slice(0, 6).map(s => ({
          id: s.id,
          name: s.name,
          levelLabel: s.levelLabel,
          proficiency: s.proficiency,
        }))
      )
    }
    loadSkills()
  }, [])

  return (
    <Card className="p-6">
      <div className="flex items-center justify-between pb-4 mb-4 border-b border-slate-800">
        <div>
          <div className="flex items-center gap-2">
            <Cpu className="w-4 h-4 text-cyan-400" />
            <h3 className="text-base font-bold text-white">Skill Progression Matrix</h3>
          </div>
          <p className="text-xs text-slate-400 font-mono mt-0.5">
            Verified mastery based on course completion and hands-on training
          </p>
        </div>
        <Link
          to="/skills"
          className="text-xs font-mono text-cyan-400 hover:text-cyan-300 flex items-center gap-1 transition-colors"
        >
          <span>Full Matrix</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </Link>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-4">
        {skills.map(skill => (
          <div key={skill.id} className="space-y-1.5">
            <div className="flex items-center justify-between text-xs">
              <span className="font-medium text-slate-200">{skill.name}</span>
              <div className="flex items-center gap-2 font-mono">
                <span className="text-slate-400 text-[11px]">{skill.levelLabel}</span>
                <span className="text-cyan-400 font-bold">{skill.proficiency}%</span>
              </div>
            </div>
            <div className="w-full h-2 rounded-full bg-slate-800 overflow-hidden border border-slate-750">
              <div
                className="h-full rounded-full bg-gradient-to-r from-cyan-500 to-indigo-500 transition-all duration-500"
                style={{ width: `${skill.proficiency}%` }}
              />
            </div>
          </div>
        ))}
      </div>
    </Card>
  )
}

