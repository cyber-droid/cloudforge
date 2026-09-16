import React from 'react'
import { cn } from '../../utils/cn'

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  hover?: boolean
  glow?: boolean
}

export function Card({
  className,
  hover = true,
  glow = false,
  children,
  ...props
}: CardProps) {
  return (
    <div
      className={cn(
        'rounded-xl border border-slate-800 bg-slate-900/60 backdrop-blur-sm p-6 text-slate-100 transition-all duration-200',
        hover && 'hover:border-slate-700 hover:bg-slate-900/80 hover:shadow-xl hover:shadow-cyan-950/10',
        glow && 'border-cyan-500/30 bg-gradient-to-b from-cyan-950/20 to-slate-900/80 shadow-lg shadow-cyan-950/20',
        className
      )}
      {...props}
    >
      {children}
    </div>
  )
}
