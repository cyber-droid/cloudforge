import React from 'react'
import { cn } from '../../utils/cn'

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: 'default' | 'cyan' | 'blue' | 'purple' | 'emerald' | 'amber' | 'rose' | 'slate' | 'outline'
  size?: 'sm' | 'md'
  dot?: boolean
}

export function Badge({
  className,
  variant = 'default',
  size = 'sm',
  dot,
  children,
  ...props
}: BadgeProps) {
  const sizeClasses = {
    sm: 'text-[11px] px-2 py-0.5 rounded-md gap-1.5 font-medium tracking-wide',
    md: 'text-xs px-2.5 py-1 rounded-md gap-2 font-medium tracking-wide',
  }

  const variantClasses = {
    default: 'bg-slate-800 text-slate-300 border border-slate-700/80',
    cyan: 'bg-cyan-950/60 text-cyan-300 border border-cyan-800/60',
    blue: 'bg-blue-950/60 text-blue-300 border border-blue-800/60',
    purple: 'bg-purple-950/60 text-purple-300 border border-purple-800/60',
    emerald: 'bg-emerald-950/60 text-emerald-300 border border-emerald-800/60',
    amber: 'bg-amber-950/60 text-amber-300 border border-amber-800/60',
    rose: 'bg-rose-950/60 text-rose-300 border border-rose-800/60',
    slate: 'bg-slate-800/80 text-slate-400 border border-slate-700/60',
    outline: 'bg-transparent text-slate-400 border border-slate-700 hover:border-slate-500',
  }

  const dotColorClasses = {
    default: 'bg-slate-400',
    cyan: 'bg-cyan-400',
    blue: 'bg-blue-400',
    purple: 'bg-purple-400',
    emerald: 'bg-emerald-400',
    amber: 'bg-amber-400',
    rose: 'bg-rose-400',
    slate: 'bg-slate-400',
    outline: 'bg-slate-400',
  }

  return (
    <span
      className={cn(
        'inline-flex items-center font-mono select-none',
        sizeClasses[size],
        variantClasses[variant],
        className
      )}
      {...props}
    >
      {dot && (
        <span
          className={cn('w-1.5 h-1.5 rounded-full shrink-0 animate-pulse', dotColorClasses[variant])}
        />
      )}
      {children}
    </span>
  )
}
