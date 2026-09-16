import React from 'react'
import { cn } from '../../utils/cn'

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger' | 'glow'
  size?: 'xs' | 'sm' | 'md' | 'lg'
  icon?: React.ReactNode
  iconRight?: React.ReactNode
  isLoading?: boolean
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      className,
      variant = 'primary',
      size = 'md',
      icon,
      iconRight,
      isLoading,
      disabled,
      children,
      ...props
    },
    ref
  ) => {
    const sizeClasses = {
      xs: 'text-xs px-2.5 py-1 rounded-md gap-1.5',
      sm: 'text-xs px-3 py-1.5 rounded-lg gap-2 font-medium',
      md: 'text-sm px-4 py-2 rounded-lg gap-2 font-medium',
      lg: 'text-base px-5 py-2.5 rounded-xl gap-2.5 font-semibold',
    }

    const variantClasses = {
      primary:
        'bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-semibold shadow-sm hover:shadow-cyan-500/20 active:translate-y-px transition-all',
      secondary:
        'bg-slate-800 hover:bg-slate-700 text-slate-100 border border-slate-700/80 hover:border-slate-600 active:translate-y-px transition-all',
      outline:
        'bg-transparent hover:bg-slate-800/60 text-slate-300 hover:text-white border border-slate-700 hover:border-slate-500 transition-all',
      ghost:
        'bg-transparent hover:bg-slate-800/60 text-slate-400 hover:text-slate-100 transition-all',
      danger:
        'bg-rose-600 hover:bg-rose-500 text-white font-semibold shadow-sm hover:shadow-rose-600/20 transition-all',
      glow:
        'bg-gradient-to-r from-cyan-500 via-blue-500 to-indigo-500 hover:from-cyan-400 hover:to-indigo-400 text-slate-950 font-bold shadow-lg shadow-cyan-500/20 active:translate-y-px transition-all',
    }

    return (
      <button
        ref={ref}
        disabled={disabled || isLoading}
        className={cn(
          'inline-flex items-center justify-center cursor-pointer select-none transition-all duration-150 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none',
          sizeClasses[size],
          variantClasses[variant],
          className
        )}
        {...props}
      >
        {isLoading ? (
          <span className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin shrink-0" />
        ) : (
          icon && <span className="shrink-0">{icon}</span>
        )}
        {children}
        {!isLoading && iconRight && <span className="shrink-0">{iconRight}</span>}
      </button>
    )
  }
)

Button.displayName = 'Button'
