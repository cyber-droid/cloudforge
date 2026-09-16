import { cn } from '../../utils/cn'

export function LoadingSkeleton({
  className,
  count = 1,
}: {
  className?: string
  count?: number
}) {
  return (
    <>
      {Array.from({ length: count }).map((_, i) => (
        <div
          key={i}
          className={cn(
            'animate-pulse rounded-lg bg-slate-800/60 border border-slate-800/40',
            className
          )}
        />
      ))}
    </>
  )
}

export function CourseCardSkeleton() {
  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-5 flex flex-col gap-4 animate-pulse">
      <div className="flex justify-between items-center">
        <div className="h-5 w-24 bg-slate-800 rounded-md" />
        <div className="h-5 w-16 bg-slate-800 rounded-md" />
      </div>
      <div className="h-6 w-3/4 bg-slate-800 rounded-md mt-1" />
      <div className="h-4 w-full bg-slate-800/60 rounded-md" />
      <div className="h-4 w-5/6 bg-slate-800/60 rounded-md" />
      <div className="flex gap-2 mt-2">
        <div className="h-5 w-14 bg-slate-800 rounded-md" />
        <div className="h-5 w-14 bg-slate-800 rounded-md" />
        <div className="h-5 w-14 bg-slate-800 rounded-md" />
      </div>
      <div className="mt-4 pt-4 border-t border-slate-800 flex justify-between items-center">
        <div className="h-8 w-24 bg-slate-800 rounded-full" />
        <div className="h-8 w-20 bg-slate-800 rounded-lg" />
      </div>
    </div>
  )
}
