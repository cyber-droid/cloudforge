import type { Incident } from '../types'

export const INCIDENTS: Incident[] = [
  {
    id: 'inc-0042',
    incidentId: 'INC-0042',
    title: 'Kubernetes API returning 502 Bad Gateway',
    severity: 'P1 - Critical',
    severityColor: 'rose',
    technology: 'Kubernetes / Ingress',
    status: 'Investigating',
    symptoms: 'Public traffic reaching api.cloudforge.internal receives HTTP 502 Bad Gateway. Ingress controller is healthy but upstream pods are failing health probes.',
    skills: ['Networking', 'Ingress', 'Services', 'Readiness Probes'],
    difficulty: 'Intermediate',
    timeElapsed: '24m active',
    timeline: [
      { time: '10:42:00', message: 'Deployment rollout triggered for auth-service:v2.4.1', status: 'info' },
      { time: '10:43:15', message: 'Pods scheduled on worker-node-04 and worker-node-07', status: 'info' },
      { time: '10:44:20', message: 'Traffic error rate surged from 0.02% to 48.7%', status: 'error' },
      { time: '10:45:00', message: 'Alertmanager triggered: High5xxRateAuthService (Severity: Critical)', status: 'error' },
      { time: '10:46:12', message: 'Ingress logs show: connect() failed (111: Connection refused) while connecting to upstream', status: 'warning' },
      { time: '10:48:30', message: 'On-call SRE initiated CloudForge AI Incident Investigation', status: 'info' },
    ],
    logs: [
      { timestamp: '10:44:18.231', level: 'ERROR', source: 'ingress-nginx', message: '2026/09/15 10:44:18 [error] 42#42: *14892 connect() failed (111: Connection refused) while connecting to upstream, client: 192.168.1.104, server: api.cloudforge.internal, request: "POST /v1/auth/token HTTP/1.1", upstream: "http://10.244.2.89:8080/v1/auth/token"' },
      { timestamp: '10:44:19.012', level: 'WARN', source: 'kubelet', message: 'Readiness probe failed: HTTP probe failed with statuscode: 503 for pod "auth-service-7f6d89b4c-kx92p_production(8e31f01c)"' },
      { timestamp: '10:44:20.449', level: 'ERROR', source: 'auth-service', message: 'FATAL: Failed to initialize Redis connection pool at redis-master.production.svc.cluster.local:6379 - dial tcp: i/o timeout' },
      { timestamp: '10:44:22.110', level: 'ERROR', source: 'ingress-nginx', message: '2026/09/15 10:44:22 [error] 42#42: *14901 no live upstreams while connecting to upstream, request: "GET /healthz HTTP/1.1"' },
      { timestamp: '10:44:25.801', level: 'WARN', source: 'endpoint-controller', message: 'Removing pod auth-service-7f6d89b4c-kx92p from EndpointSlice auth-service-k29x (Pod is Unready)' },
    ],
    metrics: [
      {
        label: 'HTTP 5xx Error Rate (%)',
        points: [
          { time: '10:40', value: 0.1 },
          { time: '10:42', value: 0.2 },
          { time: '10:44', value: 48.7 },
          { time: '10:46', value: 62.4 },
          { time: '10:48', value: 58.1 },
          { time: '10:50', value: 55.0 },
        ],
      },
      {
        label: 'Upstream Pod Healthy Endpoints',
        points: [
          { time: '10:40', value: 4 },
          { time: '10:42', value: 4 },
          { time: '10:44', value: 1 },
          { time: '10:46', value: 0 },
          { time: '10:48', value: 0 },
          { time: '10:50', value: 0 },
        ],
      },
    ],
    aiInvestigation: {
      possibleRootCause: 'The auth-service pods are crashing readiness checks because the application attempts to synchronously connect to Redis at startup using an outdated service DNS name (redis-master.production.svc.cluster.local), which times out after NetworkPolicy or Service renaming.',
      evidence: [
        'Ingress logs show "Connection refused" and "no live upstreams" starting immediately at 10:44:18.',
        'Container logs report "FATAL: Failed to initialize Redis connection pool - dial tcp: i/o timeout".',
        'Endpoint controller removed all 4 pods from the EndpointSlice due to failed readinessProbe on port 8080.',
      ],
      confidence: 94,
      recommendedInvestigation: [
        'Check if the Redis service exists in the production namespace via: kubectl get svc -n production',
        'Verify whether a NetworkPolicy was recently applied blocking egress on port 6379 from the auth-service namespace.',
        'Check ConfigMap auth-service-config for the REDIS_HOST environment variable value.',
      ],
      suggestedRemediation: 'Update the auth-service ConfigMap REDIS_HOST to "redis.database.svc.cluster.local:6379" or ensure the Redis NetworkPolicy permits ingress traffic from namespace production.',
      remediationCommand: 'kubectl set env deployment/auth-service REDIS_HOST="redis.database.svc.cluster.local" -n production',
      remediationPatch: `apiVersion: apps/v1
kind: Deployment
metadata:
  name: auth-service
  namespace: production
spec:
  template:
    spec:
      containers:
      - name: auth-service
        env:
        - name: REDIS_HOST
-         value: "redis-master.production.svc.cluster.local"
+         value: "redis.database.svc.cluster.local"`,
    },
  },
  {
    id: 'inc-0043',
    incidentId: 'INC-0043',
    title: 'Pod in CrashLoopBackOff: Exit Code 137 (OOMKilled)',
    severity: 'P2 - High',
    severityColor: 'amber',
    technology: 'Kubernetes',
    status: 'Active',
    symptoms: 'The analytics-worker deployment has 3 of 4 replicas restarting every 90 seconds with CrashLoopBackOff. Kubelet reports container killed due to out of memory.',
    skills: ['Resource Limits', 'QoS', 'Cgroups', 'Memory Profiling'],
    difficulty: 'Intermediate',
    timeElapsed: '45m active',
    timeline: [
      { time: '09:15:00', message: 'Batch ingestion job started processing CSV payload', status: 'info' },
      { time: '09:18:22', message: 'Container memory exceeded limit of 512Mi', status: 'error' },
      { time: '09:18:25', message: 'Kernel OOM-killer terminated PID 1249 with SIGKILL', status: 'error' },
      { time: '09:20:00', message: 'Pod restarted, back-off delay increased to 40s', status: 'warning' },
    ],
    logs: [
      { timestamp: '09:18:24.890', level: 'ERROR', source: 'kernel', message: 'Memory cgroup out of memory: Kill process 1249 (python3) score 982 or sacrifice child' },
      { timestamp: '09:18:25.102', level: 'WARN', source: 'kubelet', message: 'Container analytics-worker in pod analytics-worker-5d78-r92xp failed: ExitCode: 137 (OOMKilled)' },
      { timestamp: '09:18:26.441', level: 'INFO', source: 'kubelet', message: 'Back-off restarting failed container analytics-worker in pod analytics-worker-5d78-r92xp' },
    ],
    metrics: [
      {
        label: 'Memory Usage vs Limit (MB)',
        points: [
          { time: '09:10', value: 180 },
          { time: '09:14', value: 320 },
          { time: '09:18', value: 512 },
          { time: '09:20', value: 120 },
          { time: '09:22', value: 490 },
        ],
      },
    ],
    aiInvestigation: {
      possibleRootCause: 'The container memory limit is capped at 512Mi in the deployment spec, but the pandas batch chunking algorithm buffers the full 1.2GB dataset into RAM, triggering kernel cgroup OOM termination (exit code 137).',
      evidence: [
        'Kernel dmesg log confirms "Memory cgroup out of memory: Kill process 1249".',
        'Pod lastState terminated reason is explicitly "OOMKilled" with exit code 137.',
        'Memory consumption graph shows immediate linear spike up to 512Mi threshold.',
      ],
      confidence: 98,
      recommendedInvestigation: [
        'Inspect current deployment resources limits: kubectl get deployment analytics-worker -o jsonpath="{.spec.template.spec.containers[0].resources}"',
        'Check memory consumption of single chunk processing in test environment.',
      ],
      suggestedRemediation: 'Increase memory limit to 2Gi or refactor data processor to stream records using chunksizes.',
      remediationCommand: 'kubectl set resources deployment/analytics-worker --limits=memory=2Gi --requests=memory=1Gi',
    },
  },
  {
    id: 'inc-0044',
    incidentId: 'INC-0044',
    title: 'GitHub Actions Pipeline Failure on OIDC AWS Auth',
    severity: 'P2 - High',
    severityColor: 'amber',
    technology: 'CI/CD / AWS',
    status: 'Resolved',
    symptoms: 'Merge to main failed during deploy step: "sts:AssumeRoleWithWebIdentity: Not authorized to perform sts:AssumeRoleWithWebIdentity".',
    skills: ['GitHub Actions', 'AWS IAM', 'OIDC', 'Security'],
    difficulty: 'Intermediate',
    timeElapsed: 'Resolved 2h ago',
    timeline: [
      { time: '08:00:10', message: 'Pull request #314 merged into main branch', status: 'info' },
      { time: '08:01:25', message: 'Workflow step "Configure AWS Credentials" invoked', status: 'info' },
      { time: '08:01:30', message: 'AWS STS error: Subject claim mismatch on OIDC token', status: 'error' },
      { time: '08:12:00', message: 'SRE updated IAM Trust Policy sub condition for repo/environment', status: 'info' },
      { time: '08:14:10', message: 'Pipeline re-run passed successfully', status: 'success' },
    ],
    logs: [
      { timestamp: '08:01:29.412', level: 'INFO', source: 'github-runner', message: 'Requesting GitHub OIDC Token for audience: sts.amazonaws.com...' },
      { timestamp: '08:01:30.187', level: 'ERROR', source: 'aws-actions/configure-aws-credentials', message: 'Error: Could not assume role with OIDC: An error occurred (AccessDenied) when calling the AssumeRoleWithWebIdentity operation: Not authorized to perform sts:AssumeRoleWithWebIdentity' },
    ],
    metrics: [
      {
        label: 'Pipeline Build Success Rate (%)',
        points: [
          { time: '07:30', value: 100 },
          { time: '08:00', value: 0 },
          { time: '08:15', value: 100 },
        ],
      },
    ],
    aiInvestigation: {
      possibleRootCause: 'The IAM role trust policy had a strict StringEquals condition matching repo:org/repo:ref:refs/heads/master, but the branch was renamed to refs/heads/main.',
      evidence: [
        'GitHub Actions OIDC subject claim was "repo:cloudforge/web-app:ref:refs/heads/main".',
        'IAM trust policy expected "repo:cloudforge/web-app:ref:refs/heads/master".',
      ],
      confidence: 96,
      recommendedInvestigation: [
        'Inspect aws iam get-role --role-name GitHubActionsDeployRole trust relationship policy document.',
      ],
      suggestedRemediation: 'Update the IAM trust policy "token.actions.githubusercontent.com:sub" value to match refs/heads/main.',
      remediationCommand: 'aws iam update-assume-role-policy --role-name GitHubActionsDeployRole --policy-document file://trust-policy.json',
    },
  },
  {
    id: 'inc-0045',
    incidentId: 'INC-0045',
    title: 'Argo CD OutOfSync: Cluster Resource Drift Detected',
    severity: 'P3 - Medium',
    severityColor: 'blue',
    technology: 'GitOps / Argo CD',
    status: 'Active',
    symptoms: 'Application payment-service in cluster prod-us-east-1 shows OutOfSync and Degraded status. Mutation webhook injected extra sidecar annotations.',
    skills: ['GitOps', 'Argo CD', 'Kustomize', 'Admission Webhooks'],
    difficulty: 'Intermediate',
    timeElapsed: '1h 10m active',
    timeline: [
      { time: '11:00:00', message: 'Argo CD reconciliation cycle triggered', status: 'info' },
      { time: '11:00:05', message: 'Diff detected between Git SHA 8f3a9b and live cluster state', status: 'warning' },
      { time: '11:00:10', message: 'Self-heal blocked due to ignoredDifferences configuration', status: 'warning' },
    ],
    logs: [
      { timestamp: '11:00:05.102', level: 'WARN', source: 'argocd-application-controller', message: 'Comparing app payment-service: 1 resource difference detected in Deployment/payment-service' },
      { timestamp: '11:00:05.110', level: 'INFO', source: 'argocd-diff', message: 'Live: annotations["vault.hashicorp.com/agent-inject"]: "true" | Target: null' },
    ],
    metrics: [
      {
        label: 'Cluster Sync Status',
        points: [
          { time: '10:30', value: 1 },
          { time: '11:00', value: 0 },
        ],
      },
    ],
    aiInvestigation: {
      possibleRootCause: 'The HashiCorp Vault mutating admission webhook injects annotations and an initContainer at runtime, causing Argo CD to constantly flag drift against the raw Git manifest.',
      evidence: [
        'Diff inspector isolates "vault.hashicorp.com/agent-inject" present on live cluster but missing in Git repository.',
      ],
      confidence: 95,
      recommendedInvestigation: [
        'Check Argo CD Application spec for ignoreDifferences blocks targeting the Vault agent annotations.',
      ],
      suggestedRemediation: 'Add ignoreDifferences for the Vault mutating annotations in the Argo CD Application manifest.',
      remediationPatch: `spec:
  ignoreDifferences:
  - group: apps
    kind: Deployment
    jsonPointers:
    - /spec/template/metadata/annotations/vault.hashicorp.com~1agent-inject`,
    },
  },
  {
    id: 'inc-0046',
    incidentId: 'INC-0046',
    title: 'AWS IAM AccessDenied on S3 Bucket Replication',
    severity: 'P3 - Medium',
    severityColor: 'blue',
    technology: 'AWS / IAM',
    status: 'Active',
    symptoms: 'Cross-region bucket replication from us-east-1 to eu-central-1 failing with ReplicationStatus: FAILED for customer data objects.',
    skills: ['AWS IAM', 'S3', 'KMS', 'Replication'],
    difficulty: 'Intermediate',
    timeElapsed: '3h active',
    timeline: [
      { time: '07:30:00', message: 'S3 Cross-Region Replication rule enabled on bucket logs-archive-prod', status: 'info' },
      { time: '07:35:10', message: 'Replication metrics show 100% failure rate for KMS-encrypted objects', status: 'error' },
    ],
    logs: [
      { timestamp: '07:35:10.890', level: 'ERROR', source: 's3-replication', message: 'AccessDenied: The replication role does not have permission to decrypt with source KMS key arn:aws:kms:us-east-1:123456789012:key/mrk-8492a' },
    ],
    metrics: [
      {
        label: 'Replication Failure Rate (%)',
        points: [
          { time: '07:30', value: 0 },
          { time: '07:35', value: 100 },
          { time: '08:00', value: 100 },
        ],
      },
    ],
    aiInvestigation: {
      possibleRootCause: 'Objects in the source S3 bucket are encrypted with AWS KMS customer-managed key (CMK). The IAM replication role lacks kms:Decrypt permissions on the source key and kms:Encrypt on the destination key.',
      evidence: [
        'CloudTrail event shows kms:Decrypt returned AccessDenied for role s3-replication-role-prod.',
      ],
      confidence: 97,
      recommendedInvestigation: [
        'Review the IAM policy attached to the S3 replication role and KMS key policy for key/mrk-8492a.',
      ],
      suggestedRemediation: 'Add kms:Decrypt permission to the S3 replication IAM role policy for the source KMS key.',
    },
  },
  {
    id: 'inc-0047',
    incidentId: 'INC-0047',
    title: 'Critical Container Vulnerability Detected (CVE-2024-21626)',
    severity: 'P1 - Critical',
    severityColor: 'rose',
    technology: 'Docker / Trivy',
    status: 'Resolved',
    symptoms: 'Trivy scheduled security scan identified runc container escape vulnerability (Leaky Vessels) in base image node:18-bullseye.',
    skills: ['DevSecOps', 'Trivy', 'Container Security', 'CVE Patching'],
    difficulty: 'Beginner',
    timeElapsed: 'Resolved 1d ago',
    timeline: [
      { time: '03:00:00', message: 'Nightly Trivy vulnerability scan triggered in GitHub Actions', status: 'info' },
      { time: '03:01:45', message: 'Vulnerability CVE-2024-21626 (CVSS 8.6 Critical) flagged in runc < 1.1.12', status: 'error' },
      { time: '03:05:00', message: 'Automated PR generated bumping base image to node:20-alpine3.19', status: 'info' },
      { time: '03:15:20', message: 'PR merged and new image deployed to production', status: 'success' },
    ],
    logs: [
      { timestamp: '03:01:44.201', level: 'FATAL', source: 'trivy-scanner', message: 'CVE-2024-21626 (CRITICAL) - runc: container breakout vulnerability via working directory file descriptor leak' },
    ],
    metrics: [
      {
        label: 'Critical Vulnerabilities Count',
        points: [
          { time: '03:00', value: 1 },
          { time: '03:15', value: 0 },
        ],
      },
    ],
    aiInvestigation: {
      possibleRootCause: 'The base image node:18-bullseye bundles an unpatched version of the runc container runtime containing a known file descriptor leak.',
      evidence: [
        'Trivy package inspection confirmed runc package version 1.1.5+ds1-1+deb11u1.',
      ],
      confidence: 100,
      recommendedInvestigation: [
        'Verify running nodes have updated host runc packages and rebuild container image on patched base OS.',
      ],
      suggestedRemediation: 'Upgrade base image to node:20-bookworm-slim or node:20-alpine which includes runc >= 1.1.12.',
    },
  },
]
