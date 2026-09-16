import React from 'react'
import { cn } from '../../utils/cn'

interface PageContainerProps {
  children: React.ReactNode
  className?: string
  maxWidth?: '5xl' | '6xl' | '7xl' | 'full'
}

export function PageContainer({
  children,
  className,
  maxWidth = '7xl',
}: PageContainerProps) {
  const maxWidthClasses = {
    '5xl': 'max-w-5xl',
    '6xl': 'max-w-6xl',
    '7xl': 'max-w-7xl',
    full: 'max-w-full',
  }

  return (
    <div
      className={cn(
        'mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-10 w-full',
        maxWidthClasses[maxWidth],
        className
      )}
    >
      {children}
    </div>
  )
}
