import { useState } from 'react'
import { Sparkles, Send, Bot, User, Terminal, CheckCircle2, ChevronRight, X } from 'lucide-react'
import { Button } from '../common/Button'
import { cn } from '../../utils/cn'

interface AIChatPanelProps {
  lessonTitle: string
  courseTitle: string
  isOpen?: boolean
  onClose?: () => void
}

interface Message {
  id: string
  sender: 'user' | 'assistant'
  text: string
  timestamp: string
  codeSnippet?: string
}

export function AIChatPanel({
  lessonTitle,
  courseTitle,
  isOpen = true,
  onClose,
}: AIChatPanelProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'msg-1',
      sender: 'assistant',
      text: `Hello, engineer. I am your CloudForge Contextual AI Copilot for "${lessonTitle}". I have full visibility into your current manifest code and cluster topology. How can I assist?`,
      timestamp: 'Just now',
    },
  ])
  const [input, setInput] = useState('')
  const [isTyping, setIsTyping] = useState(false)

  const quickPrompts = [
    'Explain ClusterIP vs NodePort',
    'Give me a real-world example',
    'Quiz me on this topic',
    'Help me troubleshoot a Service',
  ]

  const handleSend = (userText: string) => {
    if (!userText.trim()) return

    const userMsg: Message = {
      id: Math.random().toString(),
      sender: 'user',
      text: userText,
      timestamp: 'Now',
    }

    setMessages(prev => [...prev, userMsg])
    setInput('')
    setIsTyping(true)

    // Simulate contextual AI technical response
    setTimeout(() => {
      let replyText = ''
      let code = undefined

      if (userText.toLowerCase().includes('clusterip vs nodeport')) {
        replyText = `### Key Architectural Difference:
• **ClusterIP (Default)**: Assigns an internal VIP only accessible within the pod network overlay. Used for intra-cluster communication (e.g., backend API to database).
• **NodePort**: Reserves a high port (30000–32767) on EVERY cluster node and forwards packet arrival to the Service's selector endpoints. Useful when external load balancers aren't available.`
        code = `# NodePort YAML Snippet
apiVersion: v1
kind: Service
metadata:
  name: web-nodeport
spec:
  type: NodePort
  ports:
    - port: 80
      targetPort: 8080
      nodePort: 30080
  selector:
    app: web`
      } else if (userText.toLowerCase().includes('real-world')) {
        replyText = `In a production financial platform:
1. Public Ingress (ALB / NGINX) receives user HTTPS traffic.
2. Ingress proxies to a **ClusterIP** Service for the 'Auth API' (never exposed via NodePort).
3. The Auth API communicates via another **ClusterIP** Service to an internal Redis cache.
4. **NodePort** is almost never exposed directly to the public internet in PCI-DSS environments.`
      } else if (userText.toLowerCase().includes('quiz')) {
        replyText = `Here is a scenario test:
**Scenario**: You deploy a Service with selector \`app: payment-api\`, but running \`kubectl get endpoints payment-service\` returns \`<none>\`.
What are the two most probable root causes?

*Hint: Check pod labels vs selector, and inspect whether the Pods are currently passing their readinessProbe.*`
      } else if (userText.toLowerCase().includes('troubleshoot')) {
        replyText = `Here is the SRE troubleshooting checklist for Services:
1. Run \`kubectl get endpoints <service-name>\` — if empty, selector labels do not match pod labels.
2. Run \`kubectl describe pod <pod-name>\` — verify container port matches \`targetPort\`.
3. Check \`readinessProbe\` failures — unready pods are immediately dropped from endpoints.
4. Test DNS resolution inside the cluster: \`nslookup <service>.<namespace>.svc.cluster.local\`.`
      } else {
        replyText = `Understood. Analyzing "${userText}" in the context of ${lessonTitle}. In Kubernetes, declarative specs specify desired state, and kube-proxy configures the worker node kernel iptables rules to route virtual IP packets to healthy container endpoints.`
      }

      const aiMsg: Message = {
        id: Math.random().toString(),
        sender: 'assistant',
        text: replyText,
        timestamp: 'Just now',
        codeSnippet: code,
      }

      setMessages(prev => [...prev, aiMsg])
      setIsTyping(false)
    }, 700)
  }

  return (
    <div className="flex flex-col h-full bg-slate-900 border-l border-slate-800 text-slate-100">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-slate-800 bg-slate-900/90">
        <div className="flex items-center gap-2.5">
          <div className="p-1.5 rounded-lg bg-cyan-950 border border-cyan-800/60 text-cyan-400">
            <Sparkles className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-xs font-bold text-white uppercase tracking-wider font-mono flex items-center gap-1.5">
              CloudForge AI
              <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-pulse" />
            </h3>
            <p className="text-[10px] text-slate-400 font-mono truncate max-w-[180px]">
              Context: {lessonTitle}
            </p>
          </div>
        </div>
        {onClose && (
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-800"
          >
            <X className="w-4 h-4" />
          </button>
        )}
      </div>

      {/* Suggested Prompts Chips */}
      <div className="p-3 border-b border-slate-800/80 bg-slate-950/40">
        <p className="text-[10px] font-mono text-slate-500 uppercase mb-2">
          Recommended Prompts
        </p>
        <div className="flex flex-wrap gap-1.5">
          {quickPrompts.map(prompt => (
            <button
              key={prompt}
              onClick={() => handleSend(prompt)}
              className="text-[11px] font-mono px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-slate-750 text-slate-300 hover:text-cyan-300 border border-slate-700/60 transition-all text-left cursor-pointer"
            >
              {prompt}
            </button>
          ))}
        </div>
      </div>

      {/* Messages List */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 text-xs font-sans">
        {messages.map(msg => (
          <div
            key={msg.id}
            className={cn(
              'flex flex-col gap-1.5 animate-in fade-in duration-150',
              msg.sender === 'user' ? 'items-end' : 'items-start'
            )}
          >
            <div className="flex items-center gap-1.5 text-[10px] font-mono text-slate-500">
              {msg.sender === 'user' ? (
                <>
                  <span>You</span>
                  <User className="w-3 h-3 text-slate-400" />
                </>
              ) : (
                <>
                  <Bot className="w-3 h-3 text-cyan-400" />
                  <span className="text-cyan-400 font-semibold">CloudForge AI</span>
                </>
              )}
            </div>

            <div
              className={cn(
                'p-3.5 rounded-2xl max-w-[92%] leading-relaxed',
                msg.sender === 'user'
                  ? 'bg-cyan-600 text-white rounded-br-none'
                  : 'bg-slate-800/90 border border-slate-700/60 text-slate-200 rounded-bl-none shadow-sm'
              )}
            >
              <div className="whitespace-pre-line text-xs">{msg.text}</div>
              {msg.codeSnippet && (
                <div className="mt-2.5 p-2 rounded-lg bg-slate-950 font-mono text-[11px] text-cyan-300 border border-slate-800 overflow-x-auto">
                  <pre>{msg.codeSnippet}</pre>
                </div>
              )}
            </div>
          </div>
        ))}

        {isTyping && (
          <div className="flex items-center gap-2 text-xs text-cyan-400 font-mono italic">
            <span className="w-2 h-2 rounded-full bg-cyan-400 animate-ping" />
            <span>Reasoning across Kubernetes manifests...</span>
          </div>
        )}
      </div>

      {/* Input Form */}
      <div className="p-3 border-t border-slate-800 bg-slate-900/90">
        <form
          onSubmit={e => {
            e.preventDefault()
            handleSend(input)
          }}
          className="flex items-center gap-2"
        >
          <input
            type="text"
            value={input}
            onChange={e => setInput(e.target.value)}
            placeholder="Ask AI about this lesson..."
            className="flex-1 bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-100 placeholder:text-slate-500 focus:outline-none focus:border-cyan-500"
          />
          <Button
            type="submit"
            variant="primary"
            size="xs"
            disabled={!input.trim()}
            className="px-3 py-2 rounded-xl"
          >
            <Send className="w-3.5 h-3.5" />
          </Button>
        </form>
      </div>
    </div>
  )
}
