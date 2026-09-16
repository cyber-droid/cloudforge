import { useMemo } from 'react'
import { Card } from '../common/Card'
import { Calendar, Clock, CheckCircle2, GitCommit } from 'lucide-react'

interface ActivityGridProps {
  activityData: { date: string; count: number }[]
  weeklyHours: { day: string; hours: number }[]
}

export function ActivityGrid({ activityData, weeklyHours }: ActivityGridProps) {
  // Total contributions count
  const totalContributions = useMemo(() => {
    return activityData.reduce((acc, curr) => acc + curr.count, 0)
  }, [activityData])

  // Split activity into 52 weeks of 7 days
  const weeks = useMemo(() => {
    const result: { date: string; count: number }[][] = []
    let currentWeek: { date: string; count: number }[] = []

    activityData.forEach((item, index) => {
      currentWeek.push(item)
      if (currentWeek.length === 7 || index === activityData.length - 1) {
        result.push(currentWeek)
        currentWeek = []
      }
    })
    return result
  }, [activityData])

  const getCellColor = (count: number) => {
    if (count === 0) return 'bg-slate-800/60'
    if (count === 1) return 'bg-cyan-950 border border-cyan-800/60 text-cyan-400'
    if (count === 2) return 'bg-cyan-800/80 border border-cyan-700/60 text-cyan-200'
    if (count === 3) return 'bg-cyan-600 border border-cyan-500 text-white'
    return 'bg-cyan-400 border border-cyan-300 shadow-sm shadow-cyan-400/50'
  }

  // Max weekly hours for scale
  const maxHours = Math.max(...weeklyHours.map(w => w.hours), 8)

  return (
    <Card className="p-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-5 mb-5 border-b border-slate-800 gap-4">
        <div>
          <div className="flex items-center gap-2">
            <GitCommit className="w-4 h-4 text-cyan-400" />
            <h3 className="text-base font-bold text-white">Engineering Activity</h3>
          </div>
          <p className="text-xs text-slate-400 font-mono mt-0.5">
            {totalContributions} learning commits & lab tasks in the last 365 days
          </p>
        </div>

        {/* Legend */}
        <div className="flex items-center gap-1.5 text-[11px] font-mono text-slate-400">
          <span>Less</span>
          <div className="w-2.5 h-2.5 rounded-sm bg-slate-800/60" />
          <div className="w-2.5 h-2.5 rounded-sm bg-cyan-950 border border-cyan-800/60" />
          <div className="w-2.5 h-2.5 rounded-sm bg-cyan-800/80" />
          <div className="w-2.5 h-2.5 rounded-sm bg-cyan-600" />
          <div className="w-2.5 h-2.5 rounded-sm bg-cyan-400" />
          <span>More</span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
        {/* GitHub-style Heatmap Grid (scrollable on mobile) */}
        <div className="lg:col-span-8 overflow-x-auto pb-2">
          <div className="min-w-[640px]">
            <div className="flex gap-1">
              {weeks.map((week, wIdx) => (
                <div key={wIdx} className="flex flex-col gap-1">
                  {week.map(day => (
                    <div
                      key={day.date}
                      title={`${day.date}: ${day.count} engineering activity events`}
                      className={`w-3 h-3 rounded-[3px] transition-all hover:scale-125 cursor-pointer ${getCellColor(
                        day.count
                      )}`}
                    />
                  ))}
                </div>
              ))}
            </div>
            <div className="flex justify-between text-[10px] font-mono text-slate-500 mt-2 px-1">
              <span>Oct</span>
              <span>Dec</span>
              <span>Feb</span>
              <span>Apr</span>
              <span>Jun</span>
              <span>Aug</span>
              <span>Sep (Current)</span>
            </div>
          </div>
        </div>

        {/* Weekly Learning Hours Chart */}
        <div className="lg:col-span-4 p-4 rounded-xl bg-slate-950/60 border border-slate-800/80">
          <div className="flex items-center justify-between mb-4">
            <span className="text-xs font-mono font-medium text-slate-300 flex items-center gap-1.5">
              <Clock className="w-3.5 h-3.5 text-cyan-400" />
              Weekly Hours
            </span>
            <span className="text-xs font-mono text-cyan-400 font-bold">27.9h Total</span>
          </div>

          <div className="flex items-end justify-between h-28 pt-4 px-1 gap-2">
            {weeklyHours.map(item => {
              const heightPercent = Math.round((item.hours / maxHours) * 100)
              return (
                <div key={item.day} className="flex-1 flex flex-col items-center gap-1.5 h-full justify-end group">
                  <span className="text-[9px] font-mono text-slate-400 opacity-0 group-hover:opacity-100 transition-opacity">
                    {item.hours}h
                  </span>
                  <div className="w-full rounded-t-md bg-slate-800 overflow-hidden h-full flex items-end">
                    <div
                      className="w-full bg-gradient-to-t from-cyan-600 to-cyan-400 rounded-t-md transition-all duration-300 group-hover:brightness-125"
                      style={{ height: `${heightPercent}%` }}
                    />
                  </div>
                  <span className="text-[10px] font-mono text-slate-500">{item.day}</span>
                </div>
              )
            })}
          </div>
        </div>
      </div>
    </Card>
  )
}
