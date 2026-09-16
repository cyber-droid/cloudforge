import { useState } from 'react'
import { Check, Copy, Terminal } from 'lucide-react'
import { cn } from '../../utils/cn'

interface CodeBlockProps {
  code: string
  language?: string
  filename?: string
  showLineNumbers?: boolean
  className?: string
}

export function CodeBlock({
  code,
  language = 'bash',
  filename,
  showLineNumbers = true,
  className,
}: CodeBlockProps) {
  const [copied, setCopied] = useState(false)

  const handleCopy = () => {
    navigator.clipboard.writeText(code)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const lines = code.trim().split('\n')

  return (
    <div
      className={cn(
        'rounded-xl border border-slate-800 bg-slate-950 text-slate-100 overflow-hidden text-xs my-3 shadow-md',
        className
      )}
    >
      <div className="flex items-center justify-between px-4 py-2 border-b border-slate-800/80 bg-slate-900/60">
        <div className="flex items-center gap-2 text-slate-400 font-mono text-[11px]">
          {language === 'bash' || language === 'sh' ? (
            <Terminal className="w-3.5 h-3.5 text-cyan-400" />
          ) : (
            <span className="w-2.5 h-2.5 rounded-full bg-cyan-400/80" />
          )}
          <span>{filename || language}</span>
        </div>
        <button
          onClick={handleCopy}
          className="flex items-center gap-1.5 px-2 py-1 rounded bg-slate-800/60 hover:bg-slate-800 text-slate-300 hover:text-slate-100 text-[11px] font-mono transition-colors"
          title="Copy code"
        >
          {copied ? (
            <>
              <Check className="w-3 h-3 text-emerald-400" />
              <span className="text-emerald-400">Copied</span>
            </>
          ) : (
            <>
              <Copy className="w-3 h-3 text-slate-400" />
              <span>Copy</span>
            </>
          )}
        </button>
      </div>

      <div className="p-4 overflow-x-auto font-mono leading-relaxed selection:bg-cyan-500/20">
        <table className="w-full border-collapse">
          <tbody>
            {lines.map((line, idx) => (
              <tr key={idx} className="hover:bg-slate-900/40">
                {showLineNumbers && (
                  <td className="pr-4 select-none text-right text-slate-600 w-8 align-top text-[11px]">
                    {idx + 1}
                  </td>
                )}
                <td className="whitespace-pre text-slate-200">
                  {line.startsWith('#') ? (
                    <span className="text-slate-500 italic">{line}</span>
                  ) : line.startsWith('+') ? (
                    <span className="text-emerald-400 font-semibold">{line}</span>
                  ) : line.startsWith('-') ? (
                    <span className="text-rose-400 font-semibold">{line}</span>
                  ) : line.includes('kubectl') || line.includes('docker') || line.includes('terraform') || line.includes('git') ? (
                    <span className="text-cyan-300">{line}</span>
                  ) : (
                    line
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
