import React from 'react'
import { Card } from '../common/Card'
import { cn } from '../../utils/cn'

interface MetricCardProps {
  title: string
  value: string | number
  unit?: string
  trend?: string
  trendPositive?: boolean
  icon: React.ReactNode
  color?: 'cyan' | 'purple' | 'amber' | 'emerald' | 'blue'
}

export function MetricCard({
  title,
  value,
  unit,
  trend,
  trendPositive = true,
  icon,
  color = 'cyan',
}: MetricCardProps) {
  const colorMap = {
    cyan: 'text-cyan-400 bg-cyan-950/40 border-cyan-800/50',
    purple: 'text-purple-400 bg-purple-950/40 border-purple-800/50',
    amber: 'text-amber-400 bg-amber-950/40 border-amber-800/50',
    emerald: 'text-emerald-400 bg-emerald-950/40 border-emerald-800/50',
    blue: 'text-blue-400 bg-blue-950/40 border-blue-800/50',
  }

  return (
    <Card className="p-5 flex flex-col justify-between">
      <div className="flex items-center justify-between">
        <span className="text-xs font-mono uppercase tracking-wider text-slate-400">
          {title}
        </span>
        <div className={cn('p-2 rounded-xl border', colorMap[color])}>
          {icon}
        </div>
      </div>

      <div className="mt-4 flex items-baseline gap-2">
        <span className="text-3xl font-extrabold font-mono text-white tracking-tight">
          {value}
        </span>
        {unit && <span className="text-xs font-mono text-slate-400">{unit}</span>}
      </div>

      {trend && (
        <div className="mt-2 text-xs font-mono flex items-center gap-1.5">
          <span className={trendPositive ? 'text-emerald-400 font-semibold' : 'text-rose-400 font-semibold'}>
            {trend}
          </span>
          <span className="text-slate-500">vs last month</span>
        </div>
      )}
    </Card>
  )
}
