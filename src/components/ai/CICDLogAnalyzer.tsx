import { useState } from 'react'
import { Sparkles, Terminal, CheckCircle2, Play, Copy, Check } from 'lucide-react'
import { Button } from '../common/Button'
import { CodeBlock } from '../common/CodeBlock'

const SAMPLE_LOGS = {
  docker: `Step 6/12 : RUN npm run build
> web-service@1.0.0 build
> tsc && vite build
src/api/auth.ts:42:15 - error TS2339: Property 'refreshToken' does not exist on type 'SessionUser'.
42     if (user.refreshToken) {
                ~~~~~~~~~~~~
Found 1 error in src/api/auth.ts:42
ERROR: Service 'app' failed to build : The command '/bin/sh -c npm run build' returned a non-zero code: 2`,
  helm: `Error: UPGRADE FAILED: pre-upgrade hooks failed: warning: Hook pre-upgrade db-migration failed: 
jobs.batch "db-migration-v2.1" already exists and cannot be modified.
Use helm upgrade --force to recreate or configure helm.sh/hook-delete-policy: hook-succeeded,before-hook-creation`,
  terraform: `Error: Error creating S3 bucket replication configuration: InvalidRequest: The KMS key used to encrypt the source object must have a key policy that grants the replication role kms:Decrypt.
with aws_s3_bucket_replication_configuration.backup,
on replication.tf line 18, in resource "aws_s3_bucket_replication_configuration" "backup":
18: resource "aws_s3_bucket_replication_configuration" "backup" {`,
}

export function CICDLogAnalyzer() {
  const [selectedType, setSelectedType] = useState<'docker' | 'helm' | 'terraform'>('docker')
  const [logText, setLogText] = useState(SAMPLE_LOGS.docker)
  const [analyzing, setAnalyzing] = useState(false)
  const [result, setResult] = useState<{
    rootCause: string
    confidence: number
    suggestedFix: string
    diffPatch: string
  } | null>(null)

  const handleSelectSample = (type: 'docker' | 'helm' | 'terraform') => {
    setSelectedType(type)
    setLogText(SAMPLE_LOGS[type])
    setResult(null)
  }

  const handleAnalyze = () => {
    setAnalyzing(true)
    setResult(null)
    setTimeout(() => {
      setAnalyzing(false)
      if (selectedType === 'docker') {
        setResult({
          rootCause: 'TypeScript compilation failure during Docker multi-stage build: "refreshToken" property is missing on interface SessionUser in src/api/auth.ts:42.',
          confidence: 99,
          suggestedFix: 'Extend SessionUser interface in src/types/user.ts to include optional refreshToken?: string.',
          diffPatch: `// src/types/user.ts
 export interface SessionUser {
   id: string;
   email: string;
+  refreshToken?: string;
 }`,
        })
      } else if (selectedType === 'helm') {
        setResult({
          rootCause: 'Helm pre-upgrade Job "db-migration-v2.1" already exists from a prior failed rollout and Kubernetes Job specs are immutable.',
          confidence: 98,
          suggestedFix: 'Add the helm.sh/hook-delete-policy annotation to delete previous job pods before hook creation.',
          diffPatch: ` metadata:
   annotations:
+    "helm.sh/hook-delete-policy": "before-hook-creation,hook-succeeded"`,
        })
      } else {
        setResult({
          rootCause: 'AWS KMS Decrypt permission missing on source S3 bucket encryption key for IAM replication role.',
          confidence: 97,
          suggestedFix: 'Update the KMS key policy statement to grant kms:Decrypt to the replication role ARN.',
          diffPatch: ` data "aws_iam_policy_document" "kms_replication" {
   statement {
     actions   = ["kms:Decrypt"]
+    principals = [aws_iam_role.s3_replication.arn]
   }
 }`,
        })
      }
    }, 1000)
  }

  return (
    <div className="p-6 rounded-2xl border border-slate-800 bg-slate-900/70 space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-4 border-b border-slate-800">
        <div>
          <div className="flex items-center gap-2">
            <Terminal className="w-4 h-4 text-cyan-400" />
            <h3 className="text-base font-bold text-white">
              Interactive CI/CD Failure Analyzer
            </h3>
          </div>
          <p className="text-xs text-slate-400 font-mono mt-0.5">
            Select a sample pipeline error log or paste your own to generate an automated root-cause patch.
          </p>
        </div>

        {/* Sample Log Switchers */}
        <div className="flex items-center gap-1.5">
          <button
            onClick={() => handleSelectSample('docker')}
            className={`px-2.5 py-1 rounded-lg text-xs font-mono transition-colors ${
              selectedType === 'docker' ? 'bg-cyan-500 text-slate-950 font-bold' : 'bg-slate-800 text-slate-300'
            }`}
          >
            Docker TS Build
          </button>
          <button
            onClick={() => handleSelectSample('helm')}
            className={`px-2.5 py-1 rounded-lg text-xs font-mono transition-colors ${
              selectedType === 'helm' ? 'bg-cyan-500 text-slate-950 font-bold' : 'bg-slate-800 text-slate-300'
            }`}
          >
            Helm Hook
          </button>
          <button
            onClick={() => handleSelectSample('terraform')}
            className={`px-2.5 py-1 rounded-lg text-xs font-mono transition-colors ${
              selectedType === 'terraform' ? 'bg-cyan-500 text-slate-950 font-bold' : 'bg-slate-800 text-slate-300'
            }`}
          >
            Terraform S3 KMS
          </button>
        </div>
      </div>

      {/* Raw log textarea */}
      <div className="space-y-2">
        <label className="text-xs font-mono text-slate-400">
          Raw Pipeline Console Output:
        </label>
        <textarea
          value={logText}
          onChange={e => setLogText(e.target.value)}
          rows={5}
          className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-xs font-mono text-cyan-300 leading-relaxed focus:outline-none focus:border-cyan-500"
        />
      </div>

      <Button
        variant="glow"
        size="md"
        onClick={handleAnalyze}
        isLoading={analyzing}
        icon={<Sparkles className="w-4 h-4 fill-slate-950" />}
      >
        Analyze Build Failure
      </Button>

      {/* Analysis Output */}
      {result && (
        <div className="p-5 rounded-xl border border-cyan-500/40 bg-slate-950/80 space-y-4 animate-in fade-in duration-200">
          <div className="flex items-center justify-between pb-3 border-b border-slate-800">
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              <span className="text-xs font-bold text-white uppercase font-mono">
                Automated Root Cause Diagnosis
              </span>
            </div>
            <span className="text-xs font-mono text-cyan-400 font-bold">
              Confidence: {result.confidence}%
            </span>
          </div>

          <div className="space-y-1">
            <span className="text-[11px] font-mono text-slate-400 uppercase">Reasoning:</span>
            <p className="text-xs text-slate-200 leading-relaxed">{result.rootCause}</p>
          </div>

          <div className="space-y-1">
            <span className="text-[11px] font-mono text-emerald-400 uppercase font-semibold">Suggested Fix:</span>
            <p className="text-xs text-slate-300 leading-relaxed">{result.suggestedFix}</p>
          </div>

          <div>
            <span className="text-[11px] font-mono text-slate-400 uppercase block mb-1">
              Generated Pull Request Git Diff:
            </span>
            <CodeBlock language="diff" showLineNumbers={false} code={result.diffPatch} />
          </div>
        </div>
      )}
    </div>
  )
}
