"""
Database Seed Module for CloudForge Core Curriculum.

Populates PostgreSQL with 9 production-grade Cloud, DevOps, Kubernetes, DevSecOps,
IaC, GitOps, Observability, AI, and Security courses, modules, lessons, and resources.

Can be run via: `python -m app.db.seed`
"""

import asyncio
from datetime import datetime, timezone
from typing import Any, Dict, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.core.logging import logger
from app.db.seed_projects_data import PROJECTS_DATA
from app.models.certification import (
    Certification,
    CertificationLevel,
    CertificationTraining,
    PracticeQuestion,
    UserCertificationEnrollment,
)
from app.models.course import (
    Course,
    CourseModule,
    Lesson,
    LessonResource,
)
from app.models.project import (
    Project,
    ProjectCourse,
    ProjectEnrollmentStatus,
    ProjectResource,
    ProjectSkill,
    ProjectStep,
    ProjectStepProgress,
    StepProgressStatus,
    UserProjectEnrollment,
)
from app.models.skill import Skill
from app.models.user import User

COURSES_DATA: List[Dict[str, Any]] = [
    {
        "slug": "cloud-computing-foundations",
        "title": "Cloud Computing Foundations",
        "category": "Cloud",
        "difficulty": "Beginner",
        "duration_minutes": 480,
        "thumbnail_url": "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=800&auto=format&fit=crop&q=80",
        "description": "Understand cloud computing fundamentals, service models, regions, availability zones, compute, storage, networking, identity and cloud security.",
        "long_description": "A comprehensive, engineering-first introduction to modern multi-cloud architectures. Learn how AWS, Azure, and Google Cloud organize hyperscale infrastructure, design resilient VPC networks, structure object storage, and configure secure IAM policies according to the Well-Architected Framework.",
        "technologies": [
            "AWS",
            "Azure",
            "Cloud Fundamentals",
            "VPC",
            "IAM",
            "S3",
            "FinOps",
        ],
        "learning_outcomes": [
            "Deconstruct IaaS, PaaS, SaaS across major hyperscalers",
            "Design fault-tolerant architectures across Availability Zones and Regions",
            "Architect highly available VPCs with public/private subnets and NAT gateways",
            "Configure principle-of-least-privilege IAM roles and access policies",
            "Optimize multi-tier cloud spend with FinOps cost allocation tags",
        ],
        "instructor_name": "Elena Rostova",
        "instructor_role": "Principal Cloud Architect, ex-AWS",
        "instructor_avatar": "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=150&auto=format&fit=crop&q=80",
        "modules": [
            {
                "module_number": "01",
                "title": "Cloud Fundamentals & Service Models",
                "description": "Evolution of distributed computing and service models.",
                "lessons": [
                    {
                        "title": "Evolution of Distributed Systems & Cloud",
                        "slug": "evolution-distributed-systems",
                        "lesson_type": "theory",
                        "estimated_minutes": 10,
                        "content": "### Learning Objectives\n- Trace the evolution from physical bare-metal to modern cloud computing.\n- Understand multitenancy and virtualization primitives.\n\n### Concept Explanation\nCloud computing transforms capital expenditure (CapEx) into variable operational expenditure (OpEx). Hyperscalers pool physical compute, storage, and networking resources across data centers.\n\n### Key Takeaways\n- Elasticity allows dynamic scale on demand.\n- Economies of scale drive down infrastructure cost.",
                    },
                    {
                        "title": "Shared Responsibility Model Deep-Dive",
                        "slug": "shared-responsibility-model",
                        "lesson_type": "theory",
                        "estimated_minutes": 15,
                        "content": "### Learning Objectives\n- Demarcate customer vs cloud provider security boundaries across IaaS, PaaS, and SaaS.\n\n### Concept Explanation\nIn IaaS, the provider manages the hardware, hypervisor, and physical facilities. The customer owns OS patching, networking rules, data encryption, and identity configuration.\n\n### Common Mistakes\n- Assuming the cloud provider automatically backups and protects application data.",
                    },
                ],
            },
            {
                "module_number": "02",
                "title": "Regions & Availability Zones",
                "description": "Global infrastructure resilience patterns.",
                "lessons": [
                    {
                        "title": "Hyperscaler Global Backbone Architecture",
                        "slug": "global-backbone",
                        "lesson_type": "theory",
                        "estimated_minutes": 12,
                        "content": "Learn how high-speed fiber ring backbones interconnect Availability Zones.",
                    }
                ],
            },
            {
                "module_number": "03",
                "title": "Compute",
                "description": "Virtual instances, containers, and serverless.",
                "lessons": [
                    {
                        "title": "Virtualization & Hypervisor Mechanics",
                        "slug": "virtualization-mechanics",
                        "lesson_type": "theory",
                        "estimated_minutes": 14,
                        "content": "KVM, Nitro, and modern hypervisors.",
                    }
                ],
            },
            {
                "module_number": "04",
                "title": "Storage",
                "description": "Block, file, and object storage semantics.",
                "lessons": [
                    {
                        "title": "S3 & Object Storage Consistency Models",
                        "slug": "s3-consistency",
                        "lesson_type": "theory",
                        "estimated_minutes": 14,
                        "content": "Strong read-after-write consistency in modern object stores.",
                    }
                ],
            },
            {
                "module_number": "05",
                "title": "Networking",
                "description": "VPCs, CIDRs, subnets, route tables, and gateways.",
                "lessons": [
                    {
                        "title": "CIDR Blocks & Route Tables",
                        "slug": "cidr-routing",
                        "lesson_type": "hands-on",
                        "estimated_minutes": 18,
                        "content": "Designing IP address space for enterprise cloud infrastructure.",
                    }
                ],
            },
            {
                "module_number": "06",
                "title": "Identity & Access",
                "description": "IAM policies, RBAC, and federated SSO.",
                "lessons": [
                    {
                        "title": "Principle of Least Privilege in IAM",
                        "slug": "least-privilege-iam",
                        "lesson_type": "theory",
                        "estimated_minutes": 15,
                        "content": "Crafting granular JSON IAM policies.",
                    }
                ],
            },
            {
                "module_number": "07",
                "title": "Cloud Security",
                "description": "Encryption at rest, in transit, and KMS.",
                "lessons": [
                    {
                        "title": "KMS Envelope Encryption",
                        "slug": "kms-envelope-encryption",
                        "lesson_type": "theory",
                        "estimated_minutes": 15,
                        "content": "Customer Master Keys (CMKs) and data key generation.",
                    }
                ],
            },
            {
                "module_number": "08",
                "title": "Cost Management",
                "description": "FinOps, reservation strategies, and tagging.",
                "lessons": [
                    {
                        "title": "Cloud Cost Allocation & FinOps Framework",
                        "slug": "finops-framework",
                        "lesson_type": "theory",
                        "estimated_minutes": 12,
                        "content": "Cost center attribution and savings plans.",
                    }
                ],
            },
            {
                "module_number": "09",
                "title": "Hands-on Architecture",
                "description": "Designing multi-tier resilient architectures.",
                "lessons": [
                    {
                        "title": "3-Tier Resilient Web Architecture",
                        "slug": "3-tier-architecture",
                        "lesson_type": "hands-on",
                        "estimated_minutes": 25,
                        "content": "Deploying web, application, and database tiers across multiple AZs.",
                    }
                ],
            },
            {
                "module_number": "10",
                "title": "Final Assessment",
                "description": "Capstone assessment and certification prep.",
                "lessons": [
                    {
                        "title": "Cloud Architecture Comprehensive Exam",
                        "slug": "cloud-architecture-exam",
                        "lesson_type": "quiz",
                        "estimated_minutes": 30,
                        "content": "Test your mastery of cloud computing fundamentals.",
                    }
                ],
            },
        ],
    },
    {
        "slug": "devops-engineering-foundations",
        "title": "DevOps Engineering Foundations",
        "category": "DevOps",
        "difficulty": "Beginner to Intermediate",
        "duration_minutes": 720,
        "thumbnail_url": "https://images.unsplash.com/photo-1618401471353-b98aedd04e11?w=800&auto=format&fit=crop&q=80",
        "description": "Master core Linux commands, Git workflows, CI/CD automation, Docker containerization, IaC, and monitoring pipelines.",
        "long_description": "Bridge the gap between development and operations. Learn how modern tech companies ship reliable software with automated test pipelines, trunk-based Git, Docker container builds, and infrastructure telemetry.",
        "technologies": [
            "Linux",
            "Git",
            "GitHub Actions",
            "Docker",
            "CI/CD",
            "Prometheus",
            "Bash",
        ],
        "learning_outcomes": [
            "Master Linux system internals, process management, and shell scripting",
            "Implement trunk-based development with semantic versioning",
            "Build automated CI/CD pipelines with GitHub Actions",
            "Containerize microservices with multi-stage Dockerfiles",
            "Configure centralized logging and metrics collection",
        ],
        "instructor_name": "Marcus Vance",
        "instructor_role": "Staff SRE, ex-GitLab",
        "instructor_avatar": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&auto=format&fit=crop&q=80",
        "modules": [
            {
                "module_number": "01",
                "title": "Linux Fundamentals",
                "description": "Linux kernel, systemd, networking tools.",
                "lessons": [
                    {
                        "title": "Linux Processes, Signals & Systemd",
                        "slug": "linux-processes",
                        "lesson_type": "hands-on",
                        "estimated_minutes": 15,
                        "content": "Process lifecycle, SIGTERM vs SIGKILL, and systemd units.",
                    }
                ],
            },
            {
                "module_number": "02",
                "title": "Git",
                "description": "Git internals, rebasing, bisecting.",
                "lessons": [
                    {
                        "title": "Git DAG Internals & Interactive Rebase",
                        "slug": "git-internals",
                        "lesson_type": "hands-on",
                        "estimated_minutes": 15,
                        "content": "Understanding commits as immutable snapshot nodes in a Directed Acyclic Graph.",
                    }
                ],
            },
            {
                "module_number": "03",
                "title": "GitHub",
                "description": "Branch protection, PR reviews, codeowners.",
                "lessons": [
                    {
                        "title": "Branch Protection & PR Workflows",
                        "slug": "github-workflows",
                        "lesson_type": "theory",
                        "estimated_minutes": 10,
                        "content": "Setting up status checks and CODEOWNERS.",
                    }
                ],
            },
            {
                "module_number": "04",
                "title": "CI/CD",
                "description": "Continuous integration and deployment pipelines.",
                "lessons": [
                    {
                        "title": "Designing Deterministic CI Pipelines",
                        "slug": "ci-pipelines",
                        "lesson_type": "hands-on",
                        "estimated_minutes": 20,
                        "content": "Caching dependencies and parallelizing test stages.",
                    }
                ],
            },
            {
                "module_number": "05",
                "title": "Docker",
                "description": "Container runtimes, namespaces, multi-stage builds.",
                "lessons": [
                    {
                        "title": "Multi-Stage Dockerfile Optimization",
                        "slug": "docker-multistage",
                        "lesson_type": "hands-on",
                        "estimated_minutes": 20,
                        "content": "Shrinking container images from 1GB to 25MB.",
                    }
                ],
            },
            {
                "module_number": "06",
                "title": "Container Registries",
                "description": "Artifact repositories, OCI standards, image signing.",
                "lessons": [
                    {
                        "title": "OCI Registries & Image Vulnerability Scanning",
                        "slug": "oci-registries",
                        "lesson_type": "theory",
                        "estimated_minutes": 12,
                        "content": "Trivy scans and container registry webhooks.",
                    }
                ],
            },
            {
                "module_number": "07",
                "title": "Infrastructure as Code",
                "description": "Declarative vs imperative infrastructure.",
                "lessons": [
                    {
                        "title": "Declarative Infrastructure Principles",
                        "slug": "iac-principles",
                        "lesson_type": "theory",
                        "estimated_minutes": 15,
                        "content": "Idempotency and drift detection.",
                    }
                ],
            },
            {
                "module_number": "08",
                "title": "Configuration Management",
                "description": "Ansible and configuration drift elimination.",
                "lessons": [
                    {
                        "title": "Idempotent Server Provisioning with Ansible",
                        "slug": "ansible-provisioning",
                        "lesson_type": "hands-on",
                        "estimated_minutes": 18,
                        "content": "Playbooks and Jinja2 templates.",
                    }
                ],
            },
            {
                "module_number": "09",
                "title": "Kubernetes Introduction",
                "description": "Container orchestration fundamentals.",
                "lessons": [
                    {
                        "title": "Why Orchestration Matters",
                        "slug": "why-orchestration",
                        "lesson_type": "theory",
                        "estimated_minutes": 15,
                        "content": "Scheduling, reconciliation loops, and self-healing.",
                    }
                ],
            },
            {
                "module_number": "10",
                "title": "Monitoring",
                "description": "Metrics aggregation and golden signals.",
                "lessons": [
                    {
                        "title": "The Four Golden Signals of Monitoring",
                        "slug": "four-golden-signals",
                        "lesson_type": "theory",
                        "estimated_minutes": 14,
                        "content": "Latency, Traffic, Errors, and Saturation.",
                    }
                ],
            },
            {
                "module_number": "11",
                "title": "Logging",
                "description": "Structured logging and log aggregators.",
                "lessons": [
                    {
                        "title": "Log Aggregation & Fluent Bit",
                        "slug": "log-aggregation",
                        "lesson_type": "hands-on",
                        "estimated_minutes": 16,
                        "content": "Parsing JSON logs and streaming to storage.",
                    }
                ],
            },
            {
                "module_number": "12",
                "title": "DevOps Best Practices",
                "description": "Incident postmortems and blameless culture.",
                "lessons": [
                    {
                        "title": "Blameless Post-Mortem Engineering",
                        "slug": "blameless-postmortems",
                        "lesson_type": "theory",
                        "estimated_minutes": 15,
                        "content": "Creating high-trust learning organizations.",
                    }
                ],
            },
        ],
    },
    {
        "slug": "kubernetes-engineering",
        "title": "Kubernetes Engineering",
        "category": "Kubernetes",
        "difficulty": "Intermediate",
        "duration_minutes": 1080,
        "thumbnail_url": "https://images.unsplash.com/photo-1667372393119-3d4c48d07fc9?w=800&auto=format&fit=crop&q=80",
        "description": "Deep-dive Kubernetes architecture, Deployments, Services, Ingress, RBAC, Network Policies, Helm, and production break-fix patterns.",
        "long_description": "Become an expert in managing enterprise Kubernetes clusters. Learn how kube-apiserver, etcd, kube-scheduler, and kubelet coordinate distributed state, write production YAML manifests, implement zero-downtime rollouts, and troubleshoot CrashLoopBackOff and OOMKilled incidents.",
        "technologies": [
            "Kubernetes",
            "Docker",
            "Helm",
            "kubectl",
            "Envoy",
            "etcd",
            "Calico",
        ],
        "learning_outcomes": [
            "Deconstruct Kubernetes control plane and node agent internal components",
            "Write robust declarative manifests for Deployments, StatefulSets, and DaemonSets",
            "Configure ClusterIP, NodePort, LoadBalancer Services and Ingress Controllers",
            "Enforce least-privilege cluster security with RBAC Roles and RoleBindings",
            "Debug live container lifecycle crashes, DNS failures, and scheduling deadlocks",
        ],
        "instructor_name": "Devin Thorne",
        "instructor_role": "Kubernetes Maintainer & CNCF Ambassador",
        "instructor_avatar": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&auto=format&fit=crop&q=80",
        "modules": [
            {
                "module_number": "01",
                "title": "Kubernetes Architecture",
                "description": "Control plane components, etcd, API machinery.",
                "lessons": [
                    {
                        "title": "Control Plane Internals: kube-apiserver & etcd",
                        "slug": "control-plane-internals",
                        "lesson_type": "theory",
                        "estimated_minutes": 15,
                        "content": "### Learning Objectives\n- Understand how the API server serves as the single source of truth.\n- Learn how etcd maintains distributed consensus with Raft.\n\n### Concept Explanation\nThe Kubernetes control plane maintains the desired state of the cluster. When you submit a manifest, `kube-apiserver` validates it, persists it to `etcd`, and informs controllers via watch streams.\n\n### Key Takeaways\n- Only `kube-apiserver` talks directly to `etcd`.\n- Controllers run continuous reconciliation loops.",
                    }
                ],
            },
            {
                "module_number": "02",
                "title": "Pods",
                "description": "Pod lifecycle, pause containers, multi-container patterns.",
                "lessons": [
                    {
                        "title": "Pod Lifecycle & Init Containers",
                        "slug": "pod-lifecycle",
                        "lesson_type": "hands-on",
                        "estimated_minutes": 15,
                        "content": "Sidecars, Ambassadors, and Init container sequencing.",
                    }
                ],
            },
            {
                "module_number": "03",
                "title": "Deployments",
                "description": "Rolling updates, rollbacks, and ReplicaSets.",
                "lessons": [
                    {
                        "title": "Zero-Downtime Rolling Updates & MaxSurge",
                        "slug": "rolling-updates",
                        "lesson_type": "hands-on",
                        "estimated_minutes": 18,
                        "content": "Tuning maxUnavailable and maxSurge parameters.",
                    }
                ],
            },
            {
                "module_number": "04",
                "title": "Services",
                "description": "ClusterIP, NodePort, LoadBalancer, and kube-proxy.",
                "lessons": [
                    {
                        "title": "Understanding ClusterIP",
                        "slug": "understanding-clusterip",
                        "lesson_type": "hands-on",
                        "estimated_minutes": 15,
                        "content": "### Learning Objectives\n- Understand internal service discovery and virtual IPs.\n- Learn how iptables/IPVS routes traffic to healthy Pod endpoints.\n\n### Concept Explanation\nA `ClusterIP` service exposes Pods on an internal IP address reachable only within the cluster.\n\n### Example YAML\n```yaml\napiVersion: v1\nkind: Service\nmetadata:\n  name: cloudforge-api\nspec:\n  selector:\n    app: cloudforge-api\n  ports:\n    - port: 80\n      targetPort: 8000\n  type: ClusterIP\n```\n\n### Common Mistakes\n- Mismatching the `spec.selector` labels with the target Pod labels.",
                    }
                ],
            },
            {
                "module_number": "05",
                "title": "ConfigMaps",
                "description": "Decoupling configuration from container images.",
                "lessons": [
                    {
                        "title": "Dynamic Configuration with ConfigMaps",
                        "slug": "configmaps-volumes",
                        "lesson_type": "hands-on",
                        "estimated_minutes": 12,
                        "content": "Mounting ConfigMaps as environment variables and volume files.",
                    }
                ],
            },
            {
                "module_number": "06",
                "title": "Secrets",
                "description": "Base64 encoding vs envelope encryption with KMS.",
                "lessons": [
                    {
                        "title": "Secret Management & External Secrets Operator",
                        "slug": "secret-management",
                        "lesson_type": "hands-on",
                        "estimated_minutes": 16,
                        "content": "Syncing secrets from AWS Secrets Manager / Vault.",
                    }
                ],
            },
            {
                "module_number": "07",
                "title": "Ingress",
                "description": "Ingress controllers, TLS termination, path routing.",
                "lessons": [
                    {
                        "title": "NGINX Ingress Controller & Let's Encrypt TLS",
                        "slug": "ingress-tls",
                        "lesson_type": "hands-on",
                        "estimated_minutes": 20,
                        "content": "Path routing and cert-manager integration.",
                    }
                ],
            },
            {
                "module_number": "08",
                "title": "Health Probes",
                "description": "Liveness, readiness, and startup probes.",
                "lessons": [
                    {
                        "title": "Tuning Liveness & Readiness Probes",
                        "slug": "health-probes",
                        "lesson_type": "hands-on",
                        "estimated_minutes": 15,
                        "content": "Avoiding premature pod restarts during traffic spikes.",
                    }
                ],
            },
            {
                "module_number": "09",
                "title": "Resource Management",
                "description": "CPU/Memory requests, limits, QoS classes.",
                "lessons": [
                    {
                        "title": "Guaranteed vs Burstable QoS Classes",
                        "slug": "qos-classes",
                        "lesson_type": "theory",
                        "estimated_minutes": 15,
                        "content": "OOMKiller priorities and CFS CPU throttling.",
                    }
                ],
            },
            {
                "module_number": "10",
                "title": "RBAC",
                "description": "ServiceAccounts, Roles, and RoleBindings.",
                "lessons": [
                    {
                        "title": "Enforcing Least-Privilege with RBAC",
                        "slug": "k8s-rbac",
                        "lesson_type": "hands-on",
                        "estimated_minutes": 18,
                        "content": "Creating granular ClusterRoles for CI/CD runners.",
                    }
                ],
            },
            {
                "module_number": "11",
                "title": "Network Policies",
                "description": "Calico, Cilium, egress and ingress isolation.",
                "lessons": [
                    {
                        "title": "Zero-Trust Microsegmentation with NetworkPolicies",
                        "slug": "network-policies",
                        "lesson_type": "hands-on",
                        "estimated_minutes": 20,
                        "content": "Default-deny ingress rules and namespace selectors.",
                    }
                ],
            },
            {
                "module_number": "12",
                "title": "Helm",
                "description": "Package management, templates, values overrides.",
                "lessons": [
                    {
                        "title": "Authoring Enterprise Helm Charts",
                        "slug": "helm-charts",
                        "lesson_type": "hands-on",
                        "estimated_minutes": 22,
                        "content": "Dry-run rendering, subcharts, and release management.",
                    }
                ],
            },
            {
                "module_number": "13",
                "title": "Troubleshooting",
                "description": "CrashLoopBackOff, ImagePullBackOff, Evictions.",
                "lessons": [
                    {
                        "title": "Diagnostic Workflow for CrashLoopBackOff",
                        "slug": "troubleshoot-crashloop",
                        "lesson_type": "hands-on",
                        "estimated_minutes": 25,
                        "content": "Using kubectl describe, logs -p, and ephemeral debug containers.",
                    }
                ],
            },
            {
                "module_number": "14",
                "title": "Production Patterns",
                "description": "Topology spread constraints, PDBs, HPA.",
                "lessons": [
                    {
                        "title": "High Availability with PodDisruptionBudgets & HPA",
                        "slug": "production-patterns",
                        "lesson_type": "hands-on",
                        "estimated_minutes": 20,
                        "content": "Autoscaling with Custom Metrics API.",
                    }
                ],
            },
        ],
    },
    {
        "slug": "devsecops-engineering",
        "title": "DevSecOps Engineering",
        "category": "DevSecOps",
        "difficulty": "Intermediate",
        "duration_minutes": 660,
        "thumbnail_url": "https://images.unsplash.com/photo-1563986768609-322da13575f3?w=800&auto=format&fit=crop&q=80",
        "description": "Shift security left. Automate SAST, secret detection, container image scanning, SBOM generation, and admission control.",
        "long_description": "Integrate automated security gates into every phase of your software supply chain. Learn to enforce policy-as-code with OPA Gatekeeper, sign container images with Cosign, and generate machine-readable Software Bill of Materials (SBOMs).",
        "technologies": [
            "Trivy",
            "Cosign",
            "Kyverno",
            "OPA Gatekeeper",
            "SonarQube",
            "Syft",
            "Gitleaks",
        ],
        "learning_outcomes": [
            "Implement automated secret scanning in Git pre-commit hooks and CI pipelines",
            "Scan dependencies for CVEs and generate SPDX / CycloneDX SBOMs",
            "Sign and verify container image provenance with Sigstore Cosign",
            "Enforce Kubernetes runtime security policies with Kyverno and OPA",
            "Build automated security gates that fail builds on critical vulnerabilities",
        ],
        "instructor_name": "Nadia Chen",
        "instructor_role": "Head of Security Architecture, CloudForge",
        "instructor_avatar": "https://images.unsplash.com/photo-1580489944761-15a19d654956?w=150&auto=format&fit=crop&q=80",
        "modules": [
            {
                "module_number": "01",
                "title": "DevSecOps Fundamentals",
                "description": "Shifting security left.",
                "lessons": [
                    {
                        "title": "Security in the CI/CD Pipeline",
                        "slug": "security-cicd",
                        "lesson_type": "theory",
                        "estimated_minutes": 15,
                        "content": "Continuous security verification.",
                    }
                ],
            },
            {
                "module_number": "02",
                "title": "Secure Git",
                "description": "Preventing credentials in source code.",
                "lessons": [
                    {
                        "title": "Gitleaks Pre-Commit Hooks",
                        "slug": "gitleaks-precommit",
                        "lesson_type": "hands-on",
                        "estimated_minutes": 15,
                        "content": "Detecting API keys before they hit GitHub.",
                    }
                ],
            },
            {
                "module_number": "03",
                "title": "Secret Management",
                "description": "HashiCorp Vault & AWS Secrets Manager.",
                "lessons": [
                    {
                        "title": "Dynamic Secrets with HashiCorp Vault",
                        "slug": "vault-dynamic-secrets",
                        "lesson_type": "hands-on",
                        "estimated_minutes": 20,
                        "content": "Short-lived database credentials.",
                    }
                ],
            },
            {
                "module_number": "04",
                "title": "SAST",
                "description": "Static Application Security Testing.",
                "lessons": [
                    {
                        "title": "Static Code Analysis with Semgrep",
                        "slug": "sast-semgrep",
                        "lesson_type": "hands-on",
                        "estimated_minutes": 18,
                        "content": "Writing custom SAST rules for security anti-patterns.",
                    }
                ],
            },
            {
                "module_number": "05",
                "title": "Dependency Security",
                "description": "Software composition analysis (SCA).",
                "lessons": [
                    {
                        "title": "SCA & Automated Dependabot Remediation",
                        "slug": "dependency-sca",
                        "lesson_type": "theory",
                        "estimated_minutes": 14,
                        "content": "Patching transitive vulnerabilities.",
                    }
                ],
            },
            {
                "module_number": "06",
                "title": "Container Security",
                "description": "Rootless containers, distroless images.",
                "lessons": [
                    {
                        "title": "Distroless & Non-Root Containerization",
                        "slug": "distroless-containers",
                        "lesson_type": "hands-on",
                        "estimated_minutes": 18,
                        "content": "Reducing attack surface to bare binaries.",
                    }
                ],
            },
            {
                "module_number": "07",
                "title": "Image Scanning",
                "description": "Trivy, Clair, and vulnerability databases.",
                "lessons": [
                    {
                        "title": "Automated Trivy Vulnerability Gates",
                        "slug": "trivy-scanning",
                        "lesson_type": "hands-on",
                        "estimated_minutes": 16,
                        "content": "Failing CI builds on CVSS > 7.0.",
                    }
                ],
            },
            {
                "module_number": "08",
                "title": "SBOM",
                "description": "Software Bill of Materials standards.",
                "lessons": [
                    {
                        "title": "Generating SBOMs with Syft & Grype",
                        "slug": "sbom-generation",
                        "lesson_type": "hands-on",
                        "estimated_minutes": 15,
                        "content": "CycloneDX formatting for supply chain audits.",
                    }
                ],
            },
            {
                "module_number": "09",
                "title": "Security Gates",
                "description": "Automated policy gates in GitHub Actions.",
                "lessons": [
                    {
                        "title": "Building Branch Protection Security Gates",
                        "slug": "branch-security-gates",
                        "lesson_type": "hands-on",
                        "estimated_minutes": 15,
                        "content": "Integrating security test results into pull requests.",
                    }
                ],
            },
            {
                "module_number": "10",
                "title": "Kubernetes Security",
                "description": "Kyverno, OPA Gatekeeper, admission control.",
                "lessons": [
                    {
                        "title": "Enforcing Pod Security Standards with Kyverno",
                        "slug": "kyverno-pss",
                        "lesson_type": "hands-on",
                        "estimated_minutes": 22,
                        "content": "Restricted Pod Security Standard policies.",
                    }
                ],
            },
            {
                "module_number": "11",
                "title": "Security Monitoring",
                "description": "Falco runtime threat detection.",
                "lessons": [
                    {
                        "title": "Runtime Kernel Threat Detection with Falco",
                        "slug": "falco-runtime",
                        "lesson_type": "hands-on",
                        "estimated_minutes": 20,
                        "content": "Detecting privilege escalation and unauthorized shell spawns.",
                    }
                ],
            },
        ],
    },
    {
        "slug": "infrastructure-as-code-with-terraform",
        "title": "Infrastructure as Code with Terraform",
        "category": "Infrastructure as Code",
        "difficulty": "Intermediate",
        "duration_minutes": 780,
        "thumbnail_url": "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=800&auto=format&fit=crop&q=80",
        "description": "Master HashiCorp Terraform from syntax fundamentals to reusable modules, remote state locking, Terragrunt, and multi-cloud provisioning.",
        "long_description": "Write clean, modular, production-ready HashiCorp Configuration Language (HCL). Learn how Terraform constructs dependency graphs, manages remote state in S3 with DynamoDB locking, handles drift, and integrates with CI/CD runners.",
        "technologies": [
            "Terraform",
            "HCL",
            "AWS",
            "Terragrunt",
            "tflint",
            "S3",
            "DynamoDB",
        ],
        "learning_outcomes": [
            "Write modular HCL code utilizing variables, outputs, and local values",
            "Manage remote backend state with S3 bucket encryption and DynamoDB locking",
            "Author reusable, versioned Terraform modules for VPC and compute layers",
            "Safely import existing cloud resources and resolve state drift",
            "Implement automated Terraform plan/apply workflows in CI/CD pipelines",
        ],
        "instructor_name": "Vikram Sethi",
        "instructor_role": "Principal DevOps Architect & HashiCorp Ambassador",
        "instructor_avatar": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=150&auto=format&fit=crop&q=80",
        "modules": [
            {
                "module_number": "01",
                "title": "IaC Fundamentals",
                "description": "Declarative syntax, state files, providers.",
                "lessons": [
                    {
                        "title": "Terraform Core Architecture & State Model",
                        "slug": "terraform-core",
                        "lesson_type": "theory",
                        "estimated_minutes": 15,
                        "content": "Understanding the state file as the ledger of real-world infrastructure.",
                    }
                ],
            },
            {
                "module_number": "02",
                "title": "Terraform Installation",
                "description": "CLI setup, tfswitch, tenv.",
                "lessons": [
                    {
                        "title": "Managing Terraform Versions with tenv",
                        "slug": "tenv-setup",
                        "lesson_type": "hands-on",
                        "estimated_minutes": 10,
                        "content": "Switching between Terraform and OpenTofu.",
                    }
                ],
            },
            {
                "module_number": "03",
                "title": "Providers",
                "description": "Configuring AWS, Azure, and Google Cloud providers.",
                "lessons": [
                    {
                        "title": "Provider Authentication & AssumeRole",
                        "slug": "provider-assumerole",
                        "lesson_type": "hands-on",
                        "estimated_minutes": 15,
                        "content": "Configuring multi-account AWS provider credentials.",
                    }
                ],
            },
            {
                "module_number": "04",
                "title": "Resources",
                "description": "Resource blocks, dependencies, lifecycle rules.",
                "lessons": [
                    {
                        "title": "Lifecycle Meta-Arguments: prevent_destroy & create_before_destroy",
                        "slug": "resource-lifecycles",
                        "lesson_type": "hands-on",
                        "estimated_minutes": 18,
                        "content": "Protecting critical production databases.",
                    }
                ],
            },
            {
                "module_number": "05",
                "title": "Variables",
                "description": "Input validation, type constraints, variable precedence.",
                "lessons": [
                    {
                        "title": "Custom Variable Validation Rules",
                        "slug": "variable-validation",
                        "lesson_type": "hands-on",
                        "estimated_minutes": 14,
                        "content": "Enforcing naming conventions with regex validators.",
                    }
                ],
            },
            {
                "module_number": "06",
                "title": "Outputs",
                "description": "Sensitive outputs, querying module outputs.",
                "lessons": [
                    {
                        "title": "Exporting Sensitive Connection Strings",
                        "slug": "sensitive-outputs",
                        "lesson_type": "theory",
                        "estimated_minutes": 12,
                        "content": "Preventing password leakage in CLI logs.",
                    }
                ],
            },
            {
                "module_number": "07",
                "title": "State",
                "description": "State manipulation, terraform state mv, rm.",
                "lessons": [
                    {
                        "title": "Refactoring Code with moved Blocks & state mv",
                        "slug": "refactoring-state",
                        "lesson_type": "hands-on",
                        "estimated_minutes": 20,
                        "content": "Refactoring without destroying live resources.",
                    }
                ],
            },
            {
                "module_number": "08",
                "title": "Modules",
                "description": "Authoring published and local modules.",
                "lessons": [
                    {
                        "title": "Building a Production-Grade VPC Module",
                        "slug": "building-vpc-module",
                        "lesson_type": "hands-on",
                        "estimated_minutes": 25,
                        "content": "Dynamic subnets with cidrsubnet functions.",
                    }
                ],
            },
            {
                "module_number": "09",
                "title": "Remote State",
                "description": "S3 backend, DynamoDB state locking.",
                "lessons": [
                    {
                        "title": "Locking Remote State with DynamoDB",
                        "slug": "s3-dynamodb-backend",
                        "lesson_type": "hands-on",
                        "estimated_minutes": 18,
                        "content": "Preventing concurrent write corruption.",
                    }
                ],
            },
            {
                "module_number": "10",
                "title": "AWS Infrastructure",
                "description": "Deploying ECS, ALB, and RDS clusters.",
                "lessons": [
                    {
                        "title": "Provisioning Multi-AZ ECS Fargate Clusters",
                        "slug": "ecs-fargate-terraform",
                        "lesson_type": "hands-on",
                        "estimated_minutes": 30,
                        "content": "Full stack application deployment.",
                    }
                ],
            },
            {
                "module_number": "11",
                "title": "Terraform CI/CD",
                "description": "Atlantis, GitHub Actions, Terraform Cloud.",
                "lessons": [
                    {
                        "title": "Pull-Request Plan Automation with Atlantis",
                        "slug": "atlantis-automation",
                        "lesson_type": "hands-on",
                        "estimated_minutes": 20,
                        "content": "Running terraform plan on PR comments.",
                    }
                ],
            },
            {
                "module_number": "12",
                "title": "Infrastructure Troubleshooting",
                "description": "Debugging cycle errors and drift.",
                "lessons": [
                    {
                        "title": "Resolving Dependency Cycle Deadlocks",
                        "slug": "dependency-cycles",
                        "lesson_type": "hands-on",
                        "estimated_minutes": 18,
                        "content": "Decoupling circular dependencies.",
                    }
                ],
            },
        ],
    },
    {
        "slug": "gitops-with-argo-cd",
        "title": "GitOps with Argo CD",
        "category": "DevOps",
        "difficulty": "Intermediate",
        "duration_minutes": 600,
        "thumbnail_url": "https://images.unsplash.com/photo-1556075798-4825dfaaf498?w=800&auto=format&fit=crop&q=80",
        "description": "Implement declarative Kubernetes deployments using Argo CD. Master ApplicationSets, sync waves, drift reconciliation, and progressive rollouts.",
        "long_description": "Git is your single source of truth for infrastructure and applications. Learn how Argo CD reconciles live cluster state with Git repositories, automates multi-environment deployments via ApplicationSets, and executes progressive canary releases.",
        "technologies": [
            "Argo CD",
            "GitOps",
            "Kubernetes",
            "Kustomize",
            "Helm",
            "Argo Rollouts",
        ],
        "learning_outcomes": [
            "Deconstruct the GitOps operating model and reconciliation architecture",
            "Install, secure, and configure Argo CD with SSO and RBAC",
            "Deploy multi-tenant clusters using Argo CD ApplicationSets",
            "Control deployment ordering with Sync Waves and Resource Hooks",
            "Execute automated canary deployments with Argo Rollouts and Prometheus metrics",
        ],
        "instructor_name": "Siddharth Rao",
        "instructor_role": "Principal SRE, GitOps Working Group",
        "instructor_avatar": "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=150&auto=format&fit=crop&q=80",
        "modules": [
            {
                "module_number": "01",
                "title": "GitOps Fundamentals",
                "description": "Core GitOps principles.",
                "lessons": [
                    {
                        "title": "The Four Principles of OpenGitOps",
                        "slug": "opengitops-principles",
                        "lesson_type": "theory",
                        "estimated_minutes": 12,
                        "content": "Declarative, versioned, pulled automatically, continuously reconciled.",
                    }
                ],
            },
            {
                "module_number": "02",
                "title": "Desired State",
                "description": "Kustomize overlays and environment structuring.",
                "lessons": [
                    {
                        "title": "Structuring Base & Overlays with Kustomize",
                        "slug": "kustomize-overlays",
                        "lesson_type": "hands-on",
                        "estimated_minutes": 16,
                        "content": "DRY multi-cluster manifest repositories.",
                    }
                ],
            },
            {
                "module_number": "03",
                "title": "Argo CD",
                "description": "Architecture, reposerver, dex SSO.",
                "lessons": [
                    {
                        "title": "Argo CD Controller Internals",
                        "slug": "argocd-internals",
                        "lesson_type": "theory",
                        "estimated_minutes": 15,
                        "content": "How the repo-server and application controller interact.",
                    }
                ],
            },
            {
                "module_number": "04",
                "title": "Applications",
                "description": "Application CRD, project isolation.",
                "lessons": [
                    {
                        "title": "Writing Declarative Argo CD Application CRDs",
                        "slug": "application-crds",
                        "lesson_type": "hands-on",
                        "estimated_minutes": 18,
                        "content": "Targeting remote clusters and namespaces.",
                    }
                ],
            },
            {
                "module_number": "05",
                "title": "Sync",
                "description": "Automated sync policies, self-heal, prune.",
                "lessons": [
                    {
                        "title": "Configuring Self-Healing & Automated Prune",
                        "slug": "sync-policies",
                        "lesson_type": "hands-on",
                        "estimated_minutes": 15,
                        "content": "Preventing manual cluster modifications from sticking.",
                    }
                ],
            },
            {
                "module_number": "06",
                "title": "Health",
                "description": "Custom resource health assessment with Lua.",
                "lessons": [
                    {
                        "title": "Authoring Custom Lua Health Checks",
                        "slug": "lua-health-checks",
                        "lesson_type": "hands-on",
                        "estimated_minutes": 18,
                        "content": "Reporting health status for proprietary CRDs.",
                    }
                ],
            },
            {
                "module_number": "07",
                "title": "Drift Detection",
                "description": "Monitoring and alerting on configuration drift.",
                "lessons": [
                    {
                        "title": "Automated Slack Alerts on Cluster Drift",
                        "slug": "drift-alerting",
                        "lesson_type": "hands-on",
                        "estimated_minutes": 15,
                        "content": "Argo CD notifications controller configuration.",
                    }
                ],
            },
            {
                "module_number": "08",
                "title": "Rollbacks",
                "description": "Instant rollbacks and disaster recovery.",
                "lessons": [
                    {
                        "title": "Git-Driven Rollbacks vs Argo CD History",
                        "slug": "gitops-rollbacks",
                        "lesson_type": "theory",
                        "estimated_minutes": 14,
                        "content": "Why git revert is always preferred over manual UI rollback.",
                    }
                ],
            },
            {
                "module_number": "09",
                "title": "Multi-environment GitOps",
                "description": "ApplicationSets for multi-cluster scaling.",
                "lessons": [
                    {
                        "title": "Scaling Hundreds of Clusters with ApplicationSets",
                        "slug": "applicationsets",
                        "lesson_type": "hands-on",
                        "estimated_minutes": 25,
                        "content": "Matrix generators and cluster list generators.",
                    }
                ],
            },
            {
                "module_number": "10",
                "title": "Production Patterns",
                "description": "Sync waves and database migration hooks.",
                "lessons": [
                    {
                        "title": "Sequencing DB Migrations with Sync Waves",
                        "slug": "sync-waves",
                        "lesson_type": "hands-on",
                        "estimated_minutes": 20,
                        "content": "Running pre-sync Kubernetes jobs before rolling deployments.",
                    }
                ],
            },
        ],
    },
    {
        "slug": "observability-engineering",
        "title": "Observability Engineering",
        "category": "Observability",
        "difficulty": "Intermediate",
        "duration_minutes": 720,
        "thumbnail_url": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=800&auto=format&fit=crop&q=80",
        "description": "Master metrics, structured logs, and distributed traces. Build enterprise observability with Prometheus, Grafana, Loki, Tempo, and OpenTelemetry.",
        "long_description": "Transform unreadable logs into actionable insights. Learn how to instrument microservices with OpenTelemetry, collect high-cardinality Prometheus metrics, query Loki logs with LogQL, trace requests with Tempo, and define business SLOs.",
        "technologies": [
            "Prometheus",
            "Grafana",
            "OpenTelemetry",
            "Loki",
            "Tempo",
            "PromQL",
            "LogQL",
        ],
        "learning_outcomes": [
            "Deconstruct the three pillars: Metrics, Structured Logs, and Distributed Tracing",
            "Write advanced PromQL queries and alert rules for error budgets",
            "Auto-instrument polyglot microservices using OpenTelemetry Collector",
            "Design actionable Grafana dashboards with dynamic drill-down variables",
            "Calculate Service Level Objectives (SLOs) and Error Budget burn rates",
        ],
        "instructor_name": "Maya Lin",
        "instructor_role": "Principal Observability Engineer, ex-Grafana",
        "instructor_avatar": "https://images.unsplash.com/photo-1573497019940-1c28c88b4f3e?w=150&auto=format&fit=crop&q=80",
        "modules": [
            {
                "module_number": "01",
                "title": "Observability Fundamentals",
                "description": "Why monitoring is not observability.",
                "lessons": [
                    {
                        "title": "The Three Pillars & High Cardinality",
                        "slug": "three-pillars",
                        "lesson_type": "theory",
                        "estimated_minutes": 15,
                        "content": "Understanding why traditional monitoring fails in distributed systems.",
                    }
                ],
            },
            {
                "module_number": "02",
                "title": "Metrics",
                "description": "Counters, Gauges, Histograms, Summaries.",
                "lessons": [
                    {
                        "title": "Metric Types & Memory Footprints",
                        "slug": "metric-types",
                        "lesson_type": "theory",
                        "estimated_minutes": 14,
                        "content": "Why histograms are essential for p99 latency measurement.",
                    }
                ],
            },
            {
                "module_number": "03",
                "title": "Logs",
                "description": "Structured logging, correlation IDs, JSON formatting.",
                "lessons": [
                    {
                        "title": "Injecting Trace IDs into JSON Logs",
                        "slug": "log-trace-correlation",
                        "lesson_type": "hands-on",
                        "estimated_minutes": 16,
                        "content": "Enabling 1-click jump from log lines to distributed trace spans.",
                    }
                ],
            },
            {
                "module_number": "04",
                "title": "Traces",
                "description": "Spans, context propagation, baggage.",
                "lessons": [
                    {
                        "title": "W3C TraceContext & Context Propagation",
                        "slug": "w3c-tracecontext",
                        "lesson_type": "theory",
                        "estimated_minutes": 15,
                        "content": "Passing traceparent headers across HTTP and gRPC boundaries.",
                    }
                ],
            },
            {
                "module_number": "05",
                "title": "Prometheus",
                "description": "PromQL, rate, histogram_quantile, recording rules.",
                "lessons": [
                    {
                        "title": "Mastering PromQL: rate vs irate & histogram_quantile",
                        "slug": "promql-deepdive",
                        "lesson_type": "hands-on",
                        "estimated_minutes": 22,
                        "content": "Computing reliable 5-minute request rates.",
                    }
                ],
            },
            {
                "module_number": "06",
                "title": "Grafana",
                "description": "Dashboards, panels, dynamic variables, alerting.",
                "lessons": [
                    {
                        "title": "Building Executive & Engineering Grafana Dashboards",
                        "slug": "grafana-dashboards",
                        "lesson_type": "hands-on",
                        "estimated_minutes": 25,
                        "content": "Template variables and threshold overrides.",
                    }
                ],
            },
            {
                "module_number": "07",
                "title": "Loki",
                "description": "LogQL, label indexing, chunk storage.",
                "lessons": [
                    {
                        "title": "LogQL Queries & Metric Generation from Logs",
                        "slug": "logql-queries",
                        "lesson_type": "hands-on",
                        "estimated_minutes": 18,
                        "content": "Counting 500 errors dynamically without Prometheus.",
                    }
                ],
            },
            {
                "module_number": "08",
                "title": "Tempo",
                "description": "Object storage tracing at petabyte scale.",
                "lessons": [
                    {
                        "title": "Distributed Tracing Storage with Grafana Tempo",
                        "slug": "tempo-storage",
                        "lesson_type": "theory",
                        "estimated_minutes": 15,
                        "content": "Storing traces in S3 with zero indexing costs.",
                    }
                ],
            },
            {
                "module_number": "09",
                "title": "OpenTelemetry",
                "description": "OTel Collector, processors, exporters.",
                "lessons": [
                    {
                        "title": "Deploying the OpenTelemetry Collector DaemonSet",
                        "slug": "otel-collector",
                        "lesson_type": "hands-on",
                        "estimated_minutes": 24,
                        "content": "Filtering PII data in collector batch processors.",
                    }
                ],
            },
            {
                "module_number": "10",
                "title": "Alerting",
                "description": "Prometheus Alertmanager, inhibition, routing.",
                "lessons": [
                    {
                        "title": "Multi-Tier Alertmanager Routing & Deduplication",
                        "slug": "alertmanager-routing",
                        "lesson_type": "hands-on",
                        "estimated_minutes": 18,
                        "content": "Routing high-severity pages to PagerDuty.",
                    }
                ],
            },
            {
                "module_number": "11",
                "title": "SLOs",
                "description": "SLIs, SLOs, Error Budgets, and Burn Rates.",
                "lessons": [
                    {
                        "title": "Calculating Multi-Window Multi-Burn-Rate Alerts",
                        "slug": "slo-burn-rates",
                        "lesson_type": "theory",
                        "estimated_minutes": 20,
                        "content": "Alerting based on 14-day error budget depletion rate.",
                    }
                ],
            },
            {
                "module_number": "12",
                "title": "Incident Response",
                "description": "On-call triage and war room navigation.",
                "lessons": [
                    {
                        "title": "Triaging Live Latency Spikes with Telemetry",
                        "slug": "triage-latency",
                        "lesson_type": "hands-on",
                        "estimated_minutes": 25,
                        "content": "Identifying downstream database locks using trace flamegraphs.",
                    }
                ],
            },
        ],
    },
    {
        "slug": "ai-for-cloud-devops",
        "title": "AI for Cloud & DevOps",
        "category": "AI",
        "difficulty": "Intermediate",
        "duration_minutes": 660,
        "thumbnail_url": "https://images.unsplash.com/photo-1677442136019-21780ecad995?w=800&auto=format&fit=crop&q=80",
        "description": "Supercharge engineering workflows with LLMs. Build AI root cause diagnostic engines, automated remediation agents, and DevOps copilots.",
        "long_description": "Integrate Large Language Models directly into your cloud operations. Learn prompt engineering for code synthesis, Retrieval Augmented Generation (RAG) on engineering runbooks, autonomous debugging agents, and AI-assisted CI/CD failure analysis.",
        "technologies": [
            "Python",
            "FastAPI",
            "OpenAI",
            "LangChain",
            "Vector DBs",
            "RAG",
            "Kubernetes",
        ],
        "learning_outcomes": [
            "Deconstruct LLM inference mechanics, token budgets, and embeddings",
            "Build Retrieval-Augmented Generation (RAG) pipelines over runbooks and architecture RFCs",
            "Develop autonomous root-cause diagnostic engines for CI/CD failure logs",
            "Synthesize automated Git patch diffs and pull requests with AI agents",
            "Enforce security boundaries, guardrails, and human-in-the-loop approval gates",
        ],
        "instructor_name": "Aria Stark",
        "instructor_role": "Lead AI Systems Engineer, CloudForge",
        "instructor_avatar": "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=150&auto=format&fit=crop&q=80",
        "modules": [
            {
                "module_number": "01",
                "title": "AI for Engineering",
                "description": "Landscape of AI in SRE and DevOps.",
                "lessons": [
                    {
                        "title": "How Generative AI Augments Cloud Operations",
                        "slug": "genai-operations",
                        "lesson_type": "theory",
                        "estimated_minutes": 15,
                        "content": "Moving from reactive alerts to contextual synthesis.",
                    }
                ],
            },
            {
                "module_number": "02",
                "title": "LLM Fundamentals",
                "description": "Tokens, temperature, context windows.",
                "lessons": [
                    {
                        "title": "Understanding Tokenization & Context Windows",
                        "slug": "tokenization-context",
                        "lesson_type": "theory",
                        "estimated_minutes": 14,
                        "content": "Managing context boundaries when feeding logs into LLMs.",
                    }
                ],
            },
            {
                "module_number": "03",
                "title": "Prompt Engineering",
                "description": "Few-shot prompting, structured outputs.",
                "lessons": [
                    {
                        "title": "Structured JSON Extraction with System Prompts",
                        "slug": "structured-prompts",
                        "lesson_type": "hands-on",
                        "estimated_minutes": 18,
                        "content": "Forcing LLMs to return strict Pydantic schemas.",
                    }
                ],
            },
            {
                "module_number": "04",
                "title": "RAG",
                "description": "Vector databases, chunking, embeddings.",
                "lessons": [
                    {
                        "title": "Building a Runbook Vector Search with pgvector",
                        "slug": "pgvector-rag",
                        "lesson_type": "hands-on",
                        "estimated_minutes": 22,
                        "content": "Retrieving relevant incident runbooks using cosine similarity.",
                    }
                ],
            },
            {
                "module_number": "05",
                "title": "AI-assisted CI/CD",
                "description": "Automated build failure triage.",
                "lessons": [
                    {
                        "title": "Automated CI/CD Log Parsing & Diff Synthesis",
                        "slug": "cicd-log-synthesis",
                        "lesson_type": "hands-on",
                        "estimated_minutes": 20,
                        "content": "Parsing compiler traces and proposing git diff fixes.",
                    }
                ],
            },
            {
                "module_number": "06",
                "title": "AI Log Analysis",
                "description": "Semantic log grouping and anomaly detection.",
                "lessons": [
                    {
                        "title": "Clustering High-Volume Error Logs Semantically",
                        "slug": "log-clustering",
                        "lesson_type": "hands-on",
                        "estimated_minutes": 18,
                        "content": "Reducing 50,000 error lines to 3 root-cause clusters.",
                    }
                ],
            },
            {
                "module_number": "07",
                "title": "AI Incident Investigation",
                "description": "Cross-telemetry synthesis.",
                "lessons": [
                    {
                        "title": "Correlating Metrics, Logs, and Traces with AI",
                        "slug": "cross-telemetry-ai",
                        "lesson_type": "hands-on",
                        "estimated_minutes": 25,
                        "content": "Synthesizing full Root Cause Analysis reports in 30 seconds.",
                    }
                ],
            },
            {
                "module_number": "08",
                "title": "AI Documentation",
                "description": "Generating architecture docs and diagrams.",
                "lessons": [
                    {
                        "title": "Auto-Generating Architecture RFCs from Terraform Code",
                        "slug": "auto-rfcs",
                        "lesson_type": "hands-on",
                        "estimated_minutes": 16,
                        "content": "Extracting resources and outputting Mermaid diagrams.",
                    }
                ],
            },
            {
                "module_number": "09",
                "title": "AI Agents",
                "description": "Tool use, ReAct frameworks, LangGraph.",
                "lessons": [
                    {
                        "title": "Building a Kubernetes Diagnostic Agent with Tool Calling",
                        "slug": "k8s-agent-tool-calling",
                        "lesson_type": "hands-on",
                        "estimated_minutes": 26,
                        "content": "Giving the LLM read-only kubectl access.",
                    }
                ],
            },
            {
                "module_number": "10",
                "title": "Human-in-the-loop Automation",
                "description": "Safety boundaries and approval workflows.",
                "lessons": [
                    {
                        "title": "Designing Safe Approval Gates for AI Remediations",
                        "slug": "approval-gates",
                        "lesson_type": "theory",
                        "estimated_minutes": 15,
                        "content": "Ensuring no destructive changes occur without human signoff.",
                    }
                ],
            },
            {
                "module_number": "11",
                "title": "AI Security",
                "description": "Prompt injection, data privacy, guardrails.",
                "lessons": [
                    {
                        "title": "Defending Against Indirect Prompt Injection in Logs",
                        "slug": "prompt-injection-defense",
                        "lesson_type": "theory",
                        "estimated_minutes": 18,
                        "content": "Sanitizing untrusted log input before LLM ingestion.",
                    }
                ],
            },
            {
                "module_number": "12",
                "title": "Building DevOps Copilots",
                "description": "End-to-end full stack copilot project.",
                "lessons": [
                    {
                        "title": "Assembling the CloudForge Floating Copilot",
                        "slug": "cloudforge-copilot",
                        "lesson_type": "hands-on",
                        "estimated_minutes": 30,
                        "content": "Connecting frontend chat UI to streaming FastAPI endpoints.",
                    }
                ],
            },
        ],
    },
    {
        "slug": "cloud-security-fundamentals",
        "title": "Cloud Security Fundamentals",
        "category": "Security",
        "difficulty": "Beginner to Intermediate",
        "duration_minutes": 540,
        "thumbnail_url": "https://images.unsplash.com/photo-1510511459019-5dda7724fd87?w=800&auto=format&fit=crop&q=80",
        "description": "Establish a bulletproof security baseline across cloud infrastructure. Master IAM, zero-trust network boundaries, KMS encryption, and audit logging.",
        "long_description": "Security is not an afterthought. Learn how to secure multi-account AWS and cloud topologies according to CIS Benchmarks, implement zero-trust network boundaries, configure envelope encryption with KMS, and monitor CloudTrail audit logs for anomalous activity.",
        "technologies": [
            "AWS",
            "IAM",
            "KMS",
            "CloudTrail",
            "GuardDuty",
            "Zero Trust",
            "CIS Benchmarks",
        ],
        "learning_outcomes": [
            "Implement multi-account AWS Organization security architecture",
            "Design zero-trust network boundaries with security groups and microsegmentation",
            "Enforce encryption at rest and in transit across S3, EBS, and RDS using KMS",
            "Monitor CloudTrail audit streams for privilege escalation with Amazon GuardDuty",
            "Audit infrastructure compliance against CIS Cloud Security Benchmarks",
        ],
        "instructor_name": "Marcus Vance",
        "instructor_role": "Staff SRE & Security Architect",
        "instructor_avatar": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&auto=format&fit=crop&q=80",
        "modules": [
            {
                "module_number": "01",
                "title": "Security Fundamentals",
                "description": "CIA triad and threat modeling in the cloud.",
                "lessons": [
                    {
                        "title": "Cloud Threat Modeling & Attack Vectors",
                        "slug": "cloud-threat-modeling",
                        "lesson_type": "theory",
                        "estimated_minutes": 15,
                        "content": "Identifying external and insider threat actors.",
                    }
                ],
            },
            {
                "module_number": "02",
                "title": "IAM",
                "description": "Service Control Policies, permissions boundaries.",
                "lessons": [
                    {
                        "title": "AWS Organizations & Service Control Policies (SCPs)",
                        "slug": "scps-iam",
                        "lesson_type": "hands-on",
                        "estimated_minutes": 18,
                        "content": "Enforcing guardrails that even account root users cannot bypass.",
                    }
                ],
            },
            {
                "module_number": "03",
                "title": "Network Security",
                "description": "Private subnets, VPC peering, Transit Gateways.",
                "lessons": [
                    {
                        "title": "Zero-Trust VPC Network Architecture",
                        "slug": "zero-trust-vpc",
                        "lesson_type": "hands-on",
                        "estimated_minutes": 20,
                        "content": "Eliminating public IPs on backend application and database tiers.",
                    }
                ],
            },
            {
                "module_number": "04",
                "title": "Encryption",
                "description": "KMS, TLS 1.3, client-side encryption.",
                "lessons": [
                    {
                        "title": "KMS Customer Managed Keys & Key Rotation",
                        "slug": "kms-key-rotation",
                        "lesson_type": "hands-on",
                        "estimated_minutes": 15,
                        "content": "Automating annual cryptographic key rotation.",
                    }
                ],
            },
            {
                "module_number": "05",
                "title": "Secrets",
                "description": "Secrets Manager and rotation lambdas.",
                "lessons": [
                    {
                        "title": "Automated Database Password Rotation",
                        "slug": "automated-secret-rotation",
                        "lesson_type": "hands-on",
                        "estimated_minutes": 20,
                        "content": "Using AWS Secrets Manager with RDS rotation Lambdas.",
                    }
                ],
            },
            {
                "module_number": "06",
                "title": "Logging",
                "description": "CloudTrail, VPC Flow Logs, S3 Access Logs.",
                "lessons": [
                    {
                        "title": "Enabling Immutable CloudTrail Multi-Region Logs",
                        "slug": "immutable-cloudtrail",
                        "lesson_type": "hands-on",
                        "estimated_minutes": 16,
                        "content": "Log file integrity validation.",
                    }
                ],
            },
            {
                "module_number": "07",
                "title": "Monitoring",
                "description": "GuardDuty, Security Hub, AWS Config.",
                "lessons": [
                    {
                        "title": "Threat Detection with Amazon GuardDuty",
                        "slug": "guardduty-detection",
                        "lesson_type": "theory",
                        "estimated_minutes": 15,
                        "content": "Detecting cryptocurrency mining and compromised IAM keys.",
                    }
                ],
            },
            {
                "module_number": "08",
                "title": "Least Privilege",
                "description": "IAM Access Analyzer and credential cleanup.",
                "lessons": [
                    {
                        "title": "Pruning Unused IAM Permissions with Access Analyzer",
                        "slug": "access-analyzer",
                        "lesson_type": "hands-on",
                        "estimated_minutes": 16,
                        "content": "Automated permission reduction.",
                    }
                ],
            },
            {
                "module_number": "09",
                "title": "Cloud Security Architecture",
                "description": "CIS Benchmarks and compliance reporting.",
                "lessons": [
                    {
                        "title": "Automated CIS Benchmark Compliance Auditing",
                        "slug": "cis-benchmarks",
                        "lesson_type": "hands-on",
                        "estimated_minutes": 22,
                        "content": "Running Prowler scans against multi-account infrastructure.",
                    }
                ],
            },
        ],
    },
]


async def seed_courses(db: AsyncSession) -> None:
    """Seed courses, modules, lessons, and resources if not present."""
    logger.info("Starting Core Curriculum database seeding...")

    for c_data in COURSES_DATA:
        existing = await db.execute(select(Course).where(Course.slug == c_data["slug"]))
        course = existing.scalars().first()

        if not course:
            course = Course(
                slug=c_data["slug"],
                title=c_data["title"],
                category=c_data["category"],
                difficulty=c_data["difficulty"],
                duration_minutes=c_data["duration_minutes"],
                thumbnail_url=c_data["thumbnail_url"],
                description=c_data["description"],
                long_description=c_data.get("long_description"),
                technologies=c_data.get("technologies", []),
                learning_outcomes=c_data.get("learning_outcomes", []),
                instructor_name=c_data.get("instructor_name"),
                instructor_role=c_data.get("instructor_role"),
                instructor_avatar=c_data.get("instructor_avatar"),
                instructor_verified=True,
                published=True,
            )
            db.add(course)
            await db.flush()  # populate course.id

            logger.info(f"Created course: {course.title} ({course.slug})")

            # Seed Modules and Lessons
            for mod_idx, m_data in enumerate(c_data.get("modules", [])):
                module = CourseModule(
                    course_id=course.id,
                    module_number=m_data.get("module_number", f"{mod_idx + 1:02d}"),
                    title=m_data["title"],
                    description=m_data.get("description"),
                    order_index=mod_idx,
                    published=True,
                )
                db.add(module)
                await db.flush()

                for les_idx, l_data in enumerate(m_data.get("lessons", [])):
                    lesson = Lesson(
                        module_id=module.id,
                        title=l_data["title"],
                        slug=l_data["slug"],
                        description=l_data.get("description", l_data["title"]),
                        content=l_data.get(
                            "content",
                            f"# {l_data['title']}\n\nLesson content placeholder.",
                        ),
                        lesson_type=l_data.get("lesson_type", "theory"),
                        estimated_minutes=l_data.get("estimated_minutes", 15),
                        order_index=les_idx,
                        published=True,
                    )
                    db.add(lesson)
                    await db.flush()

                    # Add Sample Lesson Resource
                    resource = LessonResource(
                        lesson_id=lesson.id,
                        title=f"{l_data['title']} Reference & Manifests",
                        resource_type="github",
                        url=f"https://github.com/cloudforge-learning/{c_data['slug']}",
                        description=f"Official companion repository and code samples for {l_data['title']}",
                        order_index=0,
                    )
                    db.add(resource)

    await db.commit()
    logger.info("Core Curriculum database seeding complete!")


async def seed_demo_student_progress(db: AsyncSession):
    """
    Seed realistic, deterministic learning progress for a standard demo student.
    Provides:
    - 3 Enrolled courses (DevOps Foundations [completed], Kubernetes Engineering [in progress], DevSecOps [started])
    - LessonProgress records for completed and in-progress lessons
    - Distinct LearningActivity records spanning 12 continuous days to produce a real 12-day streak
    - ~38.5 hours of calculated study time
    """
    from datetime import timedelta

    from app.core.security import get_password_hash
    from app.models.course import CourseEnrollment, EnrollmentStatus
    from app.models.progress import (
        ActivityType,
        LearningActivity,
        LessonProgress,
        LessonProgressStatus,
    )
    from app.models.user import User, UserRole

    logger.info("Seeding demo student progress...")

    # 1. Ensure Demo Student Exists
    result = await db.execute(select(User).where(User.email == "student@cloudforge.io"))
    student = result.scalars().first()

    if not student:
        student = User(
            email="student@cloudforge.io",
            hashed_password=get_password_hash("Student123!"),
            name="Alex Mercer",
            role=UserRole.STUDENT.value,
            is_active=True,
            is_verified=True,
            learning_goal="DevOps",
            avatar_url="https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&auto=format&fit=crop&q=80",
            terminal_theme="cloudforge-dark",
            terminal_font_size=14,
            email_notifications=True,
        )
        db.add(student)
        await db.flush()
        logger.info(f"Created demo student: {student.email} ({student.id})")

    # 2. Get Courses
    courses_res = await db.execute(select(Course))
    courses = {c.slug: c for c in courses_res.scalars().all()}

    now = datetime.now(timezone.utc)

    # A. Enroll in DevOps Engineering Foundations (COMPLETED COURSE)
    devops_course = courses.get("devops-engineering-foundations")
    if devops_course:
        enr_res = await db.execute(
            select(CourseEnrollment).where(
                CourseEnrollment.user_id == student.id,
                CourseEnrollment.course_id == devops_course.id,
            )
        )
        devops_enr = enr_res.scalars().first()
        if not devops_enr:
            devops_enr = CourseEnrollment(
                user_id=student.id,
                course_id=devops_course.id,
                status=EnrollmentStatus.COMPLETED.value,
                enrolled_at=now - timedelta(days=20),
                completed_at=now - timedelta(days=5),
            )
            db.add(devops_enr)
            await db.flush()

        # Complete all lessons in DevOps Foundations (~24 hours = 86400s)
        for mod in devops_course.modules or []:
            for les in mod.lessons or []:
                prog_res = await db.execute(
                    select(LessonProgress).where(
                        LessonProgress.user_id == student.id,
                        LessonProgress.lesson_id == les.id,
                    )
                )
                if not prog_res.scalars().first():
                    db.add(
                        LessonProgress(
                            user_id=student.id,
                            lesson_id=les.id,
                            status=LessonProgressStatus.COMPLETED.value,
                            started_at=now - timedelta(days=18),
                            completed_at=now - timedelta(days=6),
                            time_spent_seconds=7200,
                            last_accessed_at=now - timedelta(days=6),
                        )
                    )

    # B. Enroll in Kubernetes Engineering (IN PROGRESS - 68%)
    k8s_course = courses.get("kubernetes-engineering")
    if k8s_course:
        enr_res = await db.execute(
            select(CourseEnrollment).where(
                CourseEnrollment.user_id == student.id,
                CourseEnrollment.course_id == k8s_course.id,
            )
        )
        k8s_enr = enr_res.scalars().first()
        if not k8s_enr:
            k8s_enr = CourseEnrollment(
                user_id=student.id,
                course_id=k8s_course.id,
                status=EnrollmentStatus.ACTIVE.value,
                enrolled_at=now - timedelta(days=12),
            )
            db.add(k8s_enr)
            await db.flush()

        # Mark first 4 modules completed, 5th in progress (~12 hours = 43200s)
        for mod_idx, mod in enumerate(k8s_course.modules or []):
            for les_idx, les in enumerate(mod.lessons or []):
                prog_res = await db.execute(
                    select(LessonProgress).where(
                        LessonProgress.user_id == student.id,
                        LessonProgress.lesson_id == les.id,
                    )
                )
                if not prog_res.scalars().first():
                    if mod_idx < 4:
                        db.add(
                            LessonProgress(
                                user_id=student.id,
                                lesson_id=les.id,
                                status=LessonProgressStatus.COMPLETED.value,
                                started_at=now - timedelta(days=10 - mod_idx),
                                completed_at=now - timedelta(days=10 - mod_idx),
                                time_spent_seconds=5400,
                                last_accessed_at=now - timedelta(days=10 - mod_idx),
                            )
                        )
                    elif mod_idx == 4 and les_idx == 0:
                        db.add(
                            LessonProgress(
                                user_id=student.id,
                                lesson_id=les.id,
                                status=LessonProgressStatus.IN_PROGRESS.value,
                                started_at=now - timedelta(hours=2),
                                time_spent_seconds=1800,
                                last_accessed_at=now - timedelta(minutes=15),
                            )
                        )

    # C. Enroll in DevSecOps Engineering (STARTED)
    sec_course = courses.get("devsecops-engineering")
    if sec_course:
        enr_res = await db.execute(
            select(CourseEnrollment).where(
                CourseEnrollment.user_id == student.id,
                CourseEnrollment.course_id == sec_course.id,
            )
        )
        if not enr_res.scalars().first():
            db.add(
                CourseEnrollment(
                    user_id=student.id,
                    course_id=sec_course.id,
                    status=EnrollmentStatus.ACTIVE.value,
                    enrolled_at=now - timedelta(days=3),
                )
            )

    # 3. Seed 12 Days of Continuous Learning Activities for Streak
    # From day 11 ago up to today (0 ago)
    for day_offset in range(11, -1, -1):
        activity_time = now - timedelta(days=day_offset, hours=2)
        # Check if activity exists on this date
        start_of_day = activity_time.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)

        act_res = await db.execute(
            select(LearningActivity).where(
                LearningActivity.user_id == student.id,
                LearningActivity.created_at >= start_of_day,
                LearningActivity.created_at < end_of_day,
            )
        )
        if not act_res.scalars().first():
            act = LearningActivity(
                user_id=student.id,
                activity_type=ActivityType.LESSON_COMPLETED.value
                if day_offset > 0
                else ActivityType.LESSON_STARTED.value,
                course_id=k8s_course.id if k8s_course else None,
                duration_seconds=3600,
                activity_metadata={"seeded": True, "day_offset": day_offset},
                created_at=activity_time,
            )
            db.add(act)

    await db.commit()
    logger.info("Demo student progress seeding complete!")


async def seed_skills_and_roadmaps(db: AsyncSession):
    """
    Seed 16 technical skills, course-skill associations, and 4 comprehensive career roadmaps.
    """
    from app.models.roadmap import (
        Roadmap,
        RoadmapStep,
        RoadmapStepType,
        UserRoadmapProgress,
    )
    from app.models.skill import CourseSkill, Skill
    from app.models.user import User

    logger.info("Starting Skills & Career Roadmaps seeding...")

    # 1. Fetch Courses mapping
    courses_res = await db.execute(select(Course))
    courses = {c.slug: c for c in courses_res.scalars().all()}

    # 2. Seed Skills Definition
    SKILLS_DATA = [
        {
            "slug": "linux",
            "name": "Linux & Systems Administration",
            "category": "DevOps",
            "target_level": 4,
            "trend": "+4%",
            "description": "Filesystem hierarchy, POSIX standards, process diagnostics, systemd, and Bash scripting.",
        },
        {
            "slug": "git",
            "name": "Git & Version Control",
            "category": "DevOps",
            "target_level": 4,
            "trend": "+12%",
            "description": "Trunk-based development, interactive rebase, branch protection rules, and commit hygiene.",
        },
        {
            "slug": "docker",
            "name": "Docker & Containerization",
            "category": "DevOps",
            "target_level": 4,
            "trend": "+8%",
            "description": "Linux namespaces, cgroups, multi-stage builds, rootless containers, and container networking.",
        },
        {
            "slug": "kubernetes",
            "name": "Kubernetes Orchestration",
            "category": "Kubernetes",
            "target_level": 4,
            "trend": "+12%",
            "description": "Control plane machinery, Deployments, Services, Ingress, RBAC, NetworkPolicies, and CrashLoopBackOff debugging.",
        },
        {
            "slug": "terraform",
            "name": "Terraform & IaC",
            "category": "Cloud",
            "target_level": 4,
            "trend": "+4%",
            "description": "Declarative HCL syntax, remote S3 state locking, reusable modules, and multi-cloud provisioning.",
        },
        {
            "slug": "aws",
            "name": "AWS Cloud Architecture",
            "category": "Cloud",
            "target_level": 4,
            "trend": "+8%",
            "description": "Multi-AZ VPC networks, EC2/EKS compute, S3 storage, IAM least-privilege, and Well-Architected Framework.",
        },
        {
            "slug": "azure",
            "name": "Microsoft Azure Architecture",
            "category": "Cloud",
            "target_level": 3,
            "trend": "+5%",
            "description": "VNets, Azure Kubernetes Service (AKS), Entra ID, and Azure Resource Manager (ARM).",
        },
        {
            "slug": "cicd",
            "name": "CI/CD Automation",
            "category": "DevOps",
            "target_level": 4,
            "trend": "+12%",
            "description": "GitHub Actions deterministic workflows, automated test runners, artifact promotion, and security verification.",
        },
        {
            "slug": "devsecops",
            "name": "DevSecOps & Security Automation",
            "category": "DevSecOps",
            "target_level": 4,
            "trend": "+8%",
            "description": "Shift-left security, secret scanning with Gitleaks, SAST with Semgrep, and Trivy image scanning.",
        },
        {
            "slug": "cloud-security",
            "name": "Cloud Security & IAM",
            "category": "Security",
            "target_level": 4,
            "trend": "+6%",
            "description": "KMS envelope encryption, least privilege IAM policies, zero-trust microsegmentation, and CIS benchmarks.",
        },
        {
            "slug": "observability",
            "name": "Observability & Telemetry",
            "category": "Observability",
            "target_level": 4,
            "trend": "+4%",
            "description": "Prometheus PromQL metrics, Grafana dashboards, Loki structured logging, OpenTelemetry tracing, and SLO burn rates.",
        },
        {
            "slug": "ai-devops",
            "name": "AI for Cloud & DevOps",
            "category": "AI",
            "target_level": 4,
            "trend": "+12%",
            "description": "LLM prompt engineering, runbook RAG with vector search, automated CI/CD failure analysis, and autonomous SRE copilots.",
        },
        {
            "slug": "python",
            "name": "Python for Platform Engineering",
            "category": "Programming",
            "target_level": 4,
            "trend": "+7%",
            "description": "AsyncIO concurrency, Pydantic data validation, FastAPI microservices, and boto3 cloud automation.",
        },
        {
            "slug": "networking",
            "name": "Networking & VPC Architecture",
            "category": "Infrastructure",
            "target_level": 4,
            "trend": "+5%",
            "description": "OSI stack, TCP/IP, DNS, CIDR address calculation, routing tables, and load balancing.",
        },
        {
            "slug": "gitops",
            "name": "GitOps & Continuous Delivery",
            "category": "DevOps",
            "target_level": 4,
            "trend": "+10%",
            "description": "Declarative Git-driven Kubernetes reconciliation, Argo CD ApplicationSets, and progressive canary rollouts.",
        },
        {
            "slug": "helm",
            "name": "Helm Package Management",
            "category": "Kubernetes",
            "target_level": 4,
            "trend": "+6%",
            "description": "Authoring enterprise Helm charts, values overlays, template functions, and release lifecycle hooks.",
        },
    ]

    skills_map = {}
    for s_data in SKILLS_DATA:
        s_res = await db.execute(select(Skill).where(Skill.slug == s_data["slug"]))
        skill = s_res.scalars().first()
        if not skill:
            skill = Skill(
                slug=s_data["slug"],
                name=s_data["name"],
                category=s_data["category"],
                target_level=s_data["target_level"],
                trend=s_data["trend"],
                description=s_data["description"],
            )
            db.add(skill)
            await db.flush()
        skills_map[s_data["slug"]] = skill

    # 3. Associate Courses to Skills
    COURSE_SKILL_MAPPINGS = {
        "cloud-computing-foundations": ["aws", "azure", "networking", "cloud-security"],
        "devops-engineering-foundations": ["linux", "git", "docker", "cicd"],
        "kubernetes-engineering": ["kubernetes", "docker", "helm", "networking"],
        "devsecops-engineering": ["devsecops", "cloud-security", "cicd"],
        "infrastructure-as-code-with-terraform": ["terraform", "aws"],
        "gitops-with-argo-cd": ["gitops", "kubernetes", "cicd"],
        "observability-engineering": ["observability"],
        "ai-for-cloud-devops": ["ai-devops", "python"],
    }

    for c_slug, skill_slugs in COURSE_SKILL_MAPPINGS.items():
        course = courses.get(c_slug)
        if course:
            for s_slug in skill_slugs:
                skill = skills_map.get(s_slug)
                if skill:
                    cs_res = await db.execute(
                        select(CourseSkill).where(
                            CourseSkill.course_id == course.id,
                            CourseSkill.skill_id == skill.id,
                        )
                    )
                    if not cs_res.scalars().first():
                        db.add(
                            CourseSkill(
                                course_id=course.id, skill_id=skill.id, weight=1.0
                            )
                        )

    # 4. Seed Career Roadmaps
    ROADMAPS_DATA: List[Dict[str, Any]] = [
        {
            "slug": "cloud-engineer",
            "title": "Cloud Engineer Roadmap",
            "category": "Cloud",
            "difficulty": "Beginner to Intermediate",
            "duration_label": "4-6 months",
            "skills_count": 18,
            "projects_count": 4,
            "description": "Master hyperscale infrastructure, VPC networking, security posture, and Infrastructure as Code to architect production workloads on AWS and Azure.",
            "certifications_targeted": [
                "AWS Certified Cloud Practitioner",
                "Microsoft Azure Fundamentals AZ-900",
            ],
            "steps": [
                {
                    "title": "Linux Fundamentals",
                    "step_type": "course",
                    "course_slug": "devops-engineering-foundations",
                    "skill_slug": "linux",
                    "estimated_hours": "25h",
                    "skills": ["Linux", "Bash", "SSH"],
                    "description": "Filesystem hierarchy, process management, shell scripting, and remote SSH administration.",
                },
                {
                    "title": "Networking Fundamentals",
                    "step_type": "skill",
                    "skill_slug": "networking",
                    "estimated_hours": "30h",
                    "skills": ["DNS", "Subnetting", "TCP/IP"],
                    "description": "OSI model, TCP/IP, DNS, CIDR subnetting, routing tables, and firewalls.",
                },
                {
                    "title": "Cloud Computing Foundations",
                    "step_type": "course",
                    "course_slug": "cloud-computing-foundations",
                    "skill_slug": "aws",
                    "estimated_hours": "35h",
                    "skills": ["Cloud Architecture", "High Availability"],
                    "description": "Shared responsibility, regions, availability zones, compute, object storage, and service models.",
                },
                {
                    "title": "AWS / Azure Architecture",
                    "step_type": "skill",
                    "skill_slug": "aws",
                    "estimated_hours": "50h",
                    "skills": ["AWS EC2", "AWS VPC", "Azure VMs"],
                    "description": "Core compute (EC2/VMs), networking (VPC/VNet), serverless (Lambda/Functions), and managed DBs.",
                },
                {
                    "title": "Identity & Access Management (IAM)",
                    "step_type": "skill",
                    "skill_slug": "cloud-security",
                    "estimated_hours": "25h",
                    "skills": ["IAM", "RBAC", "STS"],
                    "description": "Least-privilege policies, roles, cross-account STS tokens, OIDC federation, and security baselines.",
                },
                {
                    "title": "Terraform & IaC",
                    "step_type": "course",
                    "course_slug": "infrastructure-as-code-with-terraform",
                    "skill_slug": "terraform",
                    "estimated_hours": "40h",
                    "skills": ["Terraform", "HCL", "IaC"],
                    "description": "Declarative infrastructure, state management, remote backends, and reusable infrastructure modules.",
                },
                {
                    "title": "Cloud Security & Governance",
                    "step_type": "skill",
                    "skill_slug": "cloud-security",
                    "estimated_hours": "30h",
                    "skills": ["KMS", "WAF", "CloudTrail"],
                    "description": "KMS key rotation, VPC flow logs, GuardDuty threat detection, and automated compliance policies.",
                },
                {
                    "title": "Capstone: Resilient Multi-Tier Infrastructure",
                    "step_type": "milestone",
                    "estimated_hours": "35h",
                    "skills": ["Architecture Design", "Disaster Recovery"],
                    "description": "Architect and deploy an enterprise multi-AZ cloud application stack with automated failover.",
                },
            ],
        },
        {
            "slug": "devops-engineer",
            "title": "DevOps Engineer Roadmap",
            "category": "DevOps",
            "difficulty": "Intermediate",
            "duration_label": "6-8 months",
            "skills_count": 24,
            "projects_count": 6,
            "description": "The industry-standard path to becoming a high-impact DevOps & Site Reliability Engineer. From container runtimes to Kubernetes, GitOps, and production observability.",
            "certifications_targeted": [
                "Kubernetes Fundamentals",
                "DevOps Foundations",
            ],
            "steps": [
                {
                    "title": "Linux & Shell Scripting",
                    "step_type": "course",
                    "course_slug": "devops-engineering-foundations",
                    "skill_slug": "linux",
                    "estimated_hours": "30h",
                    "skills": ["Linux", "Bash", "Systemd"],
                    "description": "POSIX standards, memory/CPU diagnostic commands, systemd, and automated Bash scripts.",
                },
                {
                    "title": "Git & Version Control",
                    "step_type": "skill",
                    "skill_slug": "git",
                    "estimated_hours": "20h",
                    "skills": ["Git", "GitHub", "CI Hooks"],
                    "description": "Trunk-based development, interactive rebase, branch protection, and commit signing.",
                },
                {
                    "title": "Docker & Containers",
                    "step_type": "skill",
                    "skill_slug": "docker",
                    "estimated_hours": "35h",
                    "skills": ["Docker", "OCI", "Compose"],
                    "description": "Namespaces, cgroups, multi-stage builds, rootless security, and container networking.",
                },
                {
                    "title": "CI/CD Automation",
                    "step_type": "skill",
                    "skill_slug": "cicd",
                    "estimated_hours": "40h",
                    "skills": ["GitHub Actions", "Pipelines", "Release"],
                    "description": "GitHub Actions, automated test suites, artifact promotion, and ephemeral test environments.",
                },
                {
                    "title": "Kubernetes Orchestration",
                    "step_type": "course",
                    "course_slug": "kubernetes-engineering",
                    "skill_slug": "kubernetes",
                    "estimated_hours": "55h",
                    "skills": ["Kubernetes", "kubectl", "CNI"],
                    "description": "Pods, Deployments, Services, Ingress, scheduling, and pod lifecycle debugging.",
                },
                {
                    "title": "Helm Package Management",
                    "step_type": "skill",
                    "skill_slug": "helm",
                    "estimated_hours": "20h",
                    "skills": ["Helm", "Package Management"],
                    "description": "Modular charts, templates, subcharts, dynamic values, and release management.",
                },
                {
                    "title": "GitOps with Argo CD",
                    "step_type": "course",
                    "course_slug": "gitops-with-argo-cd",
                    "skill_slug": "gitops",
                    "estimated_hours": "30h",
                    "skills": ["Argo CD", "GitOps", "Canary"],
                    "description": "Declarative cluster synchronization, automated reconciliation, and canary rollouts with Argo Rollouts.",
                },
                {
                    "title": "Observability & SRE",
                    "step_type": "course",
                    "course_slug": "observability-engineering",
                    "skill_slug": "observability",
                    "estimated_hours": "45h",
                    "skills": ["Prometheus", "Grafana", "OTel"],
                    "description": "Prometheus metrics, Grafana dashboards, Loki logging, OpenTelemetry tracing, and SLO management.",
                },
                {
                    "title": "Cloud Infrastructure with Terraform",
                    "step_type": "course",
                    "course_slug": "infrastructure-as-code-with-terraform",
                    "skill_slug": "terraform",
                    "estimated_hours": "40h",
                    "skills": ["AWS EKS", "Terraform", "VPC"],
                    "description": "Provisioning managed Kubernetes (EKS/AKS) and supporting services using Terraform.",
                },
                {
                    "title": "Production Capstone: Zero-Downtime SaaS Platform",
                    "step_type": "milestone",
                    "estimated_hours": "50h",
                    "skills": ["SRE", "Production Readiness"],
                    "description": "End-to-end GitOps delivery of a microservice architecture with auto-scaling and self-healing.",
                },
            ],
        },
        {
            "slug": "devsecops-engineer",
            "title": "DevSecOps Engineer Roadmap",
            "category": "DevSecOps",
            "difficulty": "Intermediate",
            "duration_label": "4-6 months",
            "skills_count": 19,
            "projects_count": 4,
            "description": "Embed automated security into every phase of the CI/CD pipeline: static analysis, secret detection, container image signing, and Kubernetes admission controllers.",
            "certifications_targeted": [
                "DevSecOps Practitioner",
                "Kubernetes Security",
            ],
            "steps": [
                {
                    "title": "Linux Security Baselines",
                    "step_type": "skill",
                    "skill_slug": "linux",
                    "estimated_hours": "25h",
                    "skills": ["Linux", "SELinux", "Hardening"],
                    "description": "File permissions, POSIX capabilities, SELinux/AppArmor, and kernel hardening.",
                },
                {
                    "title": "Secure Git & Pre-commit Hooks",
                    "step_type": "skill",
                    "skill_slug": "git",
                    "estimated_hours": "20h",
                    "skills": ["Gitleaks", "GPG", "Git Hygiene"],
                    "description": "Detecting secrets before commit using Gitleaks, signed GPG commits, and CODEOWNERS.",
                },
                {
                    "title": "Secure CI/CD Pipelines",
                    "step_type": "skill",
                    "skill_slug": "cicd",
                    "estimated_hours": "35h",
                    "skills": ["CI Security", "OIDC", "Hardening"],
                    "description": "Hardened GitHub Actions runners, OIDC short-lived credentials, and pipeline tamper-resistance.",
                },
                {
                    "title": "Static Application Security (SAST)",
                    "step_type": "skill",
                    "skill_slug": "devsecops",
                    "estimated_hours": "30h",
                    "skills": ["Semgrep", "SonarQube", "SAST"],
                    "description": "Writing Semgrep custom rules, integrating SonarQube quality gates, and automated code review.",
                },
                {
                    "title": "Dependency Security & SBOM",
                    "step_type": "skill",
                    "skill_slug": "devsecops",
                    "estimated_hours": "25h",
                    "skills": ["Syft", "SBOM", "Snyk"],
                    "description": "Software supply chain auditing, Dependabot, and generating signed CycloneDX SBOMs with Syft.",
                },
                {
                    "title": "Container Security & Scanning",
                    "step_type": "skill",
                    "skill_slug": "devsecops",
                    "estimated_hours": "35h",
                    "skills": ["Trivy", "Cosign", "Image Hardening"],
                    "description": "Scanning base images with Trivy, distroless runtimes, and signing images with Cosign / Sigstore.",
                },
                {
                    "title": "DevSecOps Engineering Masterclass",
                    "step_type": "course",
                    "course_slug": "devsecops-engineering",
                    "skill_slug": "devsecops",
                    "estimated_hours": "40h",
                    "skills": ["Kyverno", "NetworkPolicies", "RBAC"],
                    "description": "Pod Security Standards, Calico NetworkPolicies, and validating admission controllers with Kyverno.",
                },
                {
                    "title": "DevSecOps Capstone Pipeline Project",
                    "step_type": "milestone",
                    "estimated_hours": "35h",
                    "skills": ["GuardDuty", "SecurityHub", "CIS"],
                    "description": "Zero-trust IAM boundaries, CloudTrail anomaly detection, and automated CIS benchmarks.",
                },
            ],
        },
        {
            "slug": "ai-devops-engineer",
            "title": "AI + DevOps Engineer Roadmap",
            "category": "AI Engineering",
            "difficulty": "Intermediate to Advanced",
            "duration_label": "5-7 months",
            "skills_count": 22,
            "projects_count": 5,
            "description": "Pioneer the future of intelligent infrastructure operations. Build autonomous AI agents for incident diagnosis, automated code remediation, and RAG-powered SRE runbooks.",
            "certifications_targeted": [
                "AI-900 Azure AI Fundamentals",
                "AI for Cloud & DevOps Certified",
            ],
            "steps": [
                {
                    "title": "Python for Platform Engineering",
                    "step_type": "skill",
                    "skill_slug": "python",
                    "estimated_hours": "35h",
                    "skills": ["Python", "AsyncIO", "Boto3"],
                    "description": "AsyncIO, typing, httpx, interacting with cloud SDKs (boto3, kubernetes-client), and CLI tools.",
                },
                {
                    "title": "Cloud & Kubernetes Foundations",
                    "step_type": "course",
                    "course_slug": "kubernetes-engineering",
                    "skill_slug": "kubernetes",
                    "estimated_hours": "40h",
                    "skills": ["Kubernetes", "Prometheus", "APIs"],
                    "description": "Understanding cluster APIs, metrics endpoints, logs streams, and deployment mechanics.",
                },
                {
                    "title": "DevOps & Pipeline Automation",
                    "step_type": "skill",
                    "skill_slug": "cicd",
                    "estimated_hours": "30h",
                    "skills": ["Webhooks", "Pipelines", "Alerts"],
                    "description": "Designing webhooks, GitHub Actions events, and PagerDuty alert integrations.",
                },
                {
                    "title": "LLM Foundations & Prompt Engineering",
                    "step_type": "skill",
                    "skill_slug": "ai-devops",
                    "estimated_hours": "30h",
                    "skills": ["Prompt Engineering", "Structured JSON"],
                    "description": "Few-shot prompting, JSON mode enforcement, token management, and structured schema outputs.",
                },
                {
                    "title": "RAG for Infrastructure Runbooks",
                    "step_type": "course",
                    "course_slug": "ai-for-cloud-devops",
                    "skill_slug": "ai-devops",
                    "estimated_hours": "45h",
                    "skills": ["RAG", "Vector DB", "Embeddings"],
                    "description": "Vector embeddings, chunking strategies, pgvector, and semantic search over internal architecture docs.",
                },
                {
                    "title": "AI-Powered CI/CD Failure Triage",
                    "step_type": "skill",
                    "skill_slug": "ai-devops",
                    "estimated_hours": "35h",
                    "skills": ["Log Analysis", "CI Triage"],
                    "description": "Automated log parser extracting build failures, identifying root cause, and recommending fixes.",
                },
                {
                    "title": "AI Incident Investigation & Telemetry",
                    "step_type": "skill",
                    "skill_slug": "ai-devops",
                    "estimated_hours": "45h",
                    "skills": ["Telemetry AI", "Root Cause Analysis"],
                    "description": "Synthesizing Prometheus alerts, Jaeger distributed traces, and pod logs into root-cause hypotheses.",
                },
                {
                    "title": "Autonomous SRE Agents with Human-in-the-Loop",
                    "step_type": "milestone",
                    "estimated_hours": "50h",
                    "skills": ["AI Agents", "MCP", "Human-in-the-loop"],
                    "description": "Building tool-calling agents using Model Context Protocol (MCP) with approval gates for production changes.",
                },
            ],
        },
    ]

    for r_data in ROADMAPS_DATA:
        r_res = await db.execute(select(Roadmap).where(Roadmap.slug == r_data["slug"]))
        roadmap = r_res.scalars().first()

        if not roadmap:
            roadmap = Roadmap(
                slug=r_data["slug"],
                title=r_data["title"],
                category=r_data["category"],
                difficulty=r_data["difficulty"],
                duration_label=r_data["duration_label"],
                skills_count=r_data["skills_count"],
                projects_count=r_data["projects_count"],
                description=r_data["description"],
                certifications_targeted=r_data["certifications_targeted"],
                published=True,
            )
            db.add(roadmap)
            await db.flush()

            steps: List[Dict[str, Any]] = r_data.get("steps", [])
            for step_idx, s_info in enumerate(steps):
                step_course_slug = s_info.get("course_slug")
                target_course = courses.get(str(step_course_slug)) if step_course_slug else None
                step_skill_slug = s_info.get("skill_slug")
                target_skill = skills_map.get(str(step_skill_slug)) if step_skill_slug else None

                step = RoadmapStep(
                    roadmap_id=roadmap.id,
                    title=s_info["title"],
                    description=s_info.get("description"),
                    step_type=s_info.get("step_type", RoadmapStepType.COURSE.value),
                    order_index=step_idx,
                    required=True,
                    estimated_hours=s_info.get("estimated_hours", "25h"),
                    skills_covered=s_info.get("skills", []),
                    course_id=target_course.id if target_course else None,
                    skill_id=target_skill.id if target_skill else None,
                )
                db.add(step)

    # 5. Enroll Demo Student in DevOps Engineer Roadmap
    student_res = await db.execute(
        select(User).where(User.email == "student@cloudforge.io")
    )
    student = student_res.scalars().first()
    if student:
        devops_rm_res = await db.execute(
            select(Roadmap).where(Roadmap.slug == "devops-engineer")
        )
        devops_rm = devops_rm_res.scalars().first()
        if devops_rm:
            ur_res = await db.execute(
                select(UserRoadmapProgress).where(
                    UserRoadmapProgress.user_id == student.id,
                    UserRoadmapProgress.roadmap_id == devops_rm.id,
                )
            )
            if not ur_res.scalars().first():
                db.add(
                    UserRoadmapProgress(
                        user_id=student.id,
                        roadmap_id=devops_rm.id,
                        status="in_progress",
                    )
                )

    await db.commit()
    logger.info("Skills & Career Roadmaps seeding complete!")


CERTIFICATIONS_DATA: List[Dict[str, Any]] = [
    {
        "code": "CLF-C02",
        "slug": "aws-certified-cloud-practitioner-clf-c02",
        "name": "AWS Certified Cloud Practitioner",
        "vendor": "AWS",
        "description": "Validate foundational understanding of AWS Cloud concepts, security, architecture, pricing, and support ecosystem.",
        "level": "foundational",
        "category": "Cloud",
        "is_official_certification": True,
        "official_url": "https://aws.amazon.com/certification/certified-cloud-practitioner/",
        "exam_duration_minutes": 90,
        "total_exam_questions": 65,
        "passing_score_percentage": 70,
        "icon_name": "aws",
        "domains": [
            {
                "domain_name": "Cloud Concepts",
                "weight_percentage": 24,
                "question_count": 16,
            },
            {
                "domain_name": "Security and Compliance",
                "weight_percentage": 30,
                "question_count": 20,
            },
            {
                "domain_name": "Cloud Technology and Services",
                "weight_percentage": 34,
                "question_count": 22,
            },
            {
                "domain_name": "Billing, Pricing, and Support",
                "weight_percentage": 12,
                "question_count": 7,
            },
        ],
        "training": {
            "title": "AWS Cloud Practitioner Preparation Program",
            "slug": "aws-cloud-practitioner-prep",
            "description": "Comprehensive prep track covering core AWS architectural best practices, global infrastructure, IAM, and FinOps pricing models.",
            "level": "foundational",
            "estimated_hours": 20,
            "course_slug": "cloud-computing-foundations",
        },
        "questions": [
            {
                "question_text": "Under the AWS Shared Responsibility Model, which security task is the exclusive responsibility of AWS?",
                "question_type": "single_choice",
                "options": [
                    "Configuring IAM user password policies",
                    "Patching guest operating system on EC2 instances",
                    "Physical security and facility access at AWS data centers",
                    "Encrypting client-side application data",
                ],
                "correct_option": 2,
                "explanation": "AWS manages security OF the cloud, which includes physical data center security, hardware maintenance, and hypervisors. Customers manage security IN the cloud (IAM, OS patching, data encryption).",
                "topic": "Security and Compliance",
                "difficulty": "easy",
                "points": 10,
            },
            {
                "question_text": "Which AWS Well-Architected Framework pillar emphasizes avoiding single points of failure and automatically recovering from disruptions?",
                "question_type": "single_choice",
                "options": [
                    "Performance Efficiency",
                    "Cost Optimization",
                    "Reliability",
                    "Operational Excellence",
                ],
                "correct_option": 2,
                "explanation": "The Reliability pillar focuses on ensuring a workload performs its intended function correctly and consistently, including distributed system design and automated fault recovery.",
                "topic": "Cloud Concepts",
                "difficulty": "easy",
                "points": 10,
            },
            {
                "question_text": "An organization wants to decouple asynchronous microservices using a fully managed message queuing service. Which AWS service should they choose?",
                "question_type": "single_choice",
                "options": [
                    "Amazon SNS",
                    "Amazon SQS",
                    "Amazon Kinesis Data Streams",
                    "Amazon EventBridge",
                ],
                "correct_option": 1,
                "explanation": "Amazon Simple Queue Service (SQS) is a fully managed message queuing service that enables decoupling and scaling of microservices and distributed systems.",
                "topic": "Cloud Technology and Services",
                "difficulty": "medium",
                "points": 10,
            },
            {
                "question_text": "Which AWS pricing model provides the highest discount (up to 90%) for fault-tolerant workloads that can tolerate unexpected interruptions?",
                "question_type": "single_choice",
                "options": [
                    "On-Demand Instances",
                    "Savings Plans",
                    "Reserved Instances",
                    "Spot Instances",
                ],
                "correct_option": 3,
                "explanation": "Amazon EC2 Spot Instances offer up to a 90% discount compared to On-Demand prices by utilizing spare EC2 compute capacity, but can be reclaimed by AWS with a 2-minute notice.",
                "topic": "Billing, Pricing, and Support",
                "difficulty": "medium",
                "points": 10,
            },
            {
                "question_text": "Which AWS service provides consolidated billing, centralized policy enforcement (SCPs), and hierarchical management across multiple AWS accounts?",
                "question_type": "single_choice",
                "options": [
                    "AWS Identity and Access Management (IAM)",
                    "AWS Organizations",
                    "AWS Control Tower",
                    "AWS Resource Access Manager (RAM)",
                ],
                "correct_option": 1,
                "explanation": "AWS Organizations allows centralized management and governance across multiple AWS accounts with Service Control Policies (SCPs) and consolidated billing.",
                "topic": "Security and Compliance",
                "difficulty": "medium",
                "points": 10,
            },
        ],
    },
    {
        "code": "AZ-900",
        "slug": "microsoft-azure-fundamentals-az-900",
        "name": "Microsoft Azure Fundamentals",
        "vendor": "Microsoft",
        "description": "Demonstrate foundational knowledge of cloud concepts, core Azure architectural components, compute, networking, security, and governance.",
        "level": "foundational",
        "category": "Cloud",
        "is_official_certification": True,
        "official_url": "https://learn.microsoft.com/en-us/credentials/certifications/azure-fundamentals/",
        "exam_duration_minutes": 60,
        "total_exam_questions": 45,
        "passing_score_percentage": 70,
        "icon_name": "azure",
        "domains": [
            {
                "domain_name": "Describe Cloud Concepts",
                "weight_percentage": 30,
                "question_count": 14,
            },
            {
                "domain_name": "Describe Azure Architecture and Services",
                "weight_percentage": 35,
                "question_count": 16,
            },
            {
                "domain_name": "Describe Azure Management and Governance",
                "weight_percentage": 35,
                "question_count": 15,
            },
        ],
        "training": {
            "title": "Microsoft Azure Fundamentals Training Program",
            "slug": "azure-fundamentals-prep",
            "description": "Master Azure Resource Manager (ARM), Virtual Networks, Entra ID authentication, Cost Management, and Azure Policy.",
            "level": "foundational",
            "estimated_hours": 15,
            "course_slug": "cloud-computing-foundations",
        },
        "questions": [
            {
                "question_text": "What is the primary benefit of deploying resources across multiple Azure Availability Zones?",
                "question_type": "single_choice",
                "options": [
                    "Lower network latency to on-premises data centers",
                    "Protection against physical datacenter failures within the same region",
                    "Automatic zero-cost data replication across continents",
                    "Automatic generation of ARM templates",
                ],
                "correct_option": 1,
                "explanation": "Azure Availability Zones are physically separate locations within an Azure region, each with independent power, cooling, and networking, providing high availability against local failures.",
                "topic": "Describe Azure Architecture and Services",
                "difficulty": "easy",
                "points": 10,
            },
            {
                "question_text": "Which Azure identity service is used for centralized single sign-on (SSO), multifactor authentication (MFA), and role-based access management?",
                "question_type": "single_choice",
                "options": [
                    "Microsoft Entra ID (formerly Azure AD)",
                    "Azure Key Vault",
                    "Azure Active Directory Domain Services (AAD DS)",
                    "Azure Bastion",
                ],
                "correct_option": 0,
                "explanation": "Microsoft Entra ID (formerly Azure Active Directory) is Microsoft's multi-tenant, cloud-based identity and access management service.",
                "topic": "Describe Azure Management and Governance",
                "difficulty": "easy",
                "points": 10,
            },
            {
                "question_text": "An enterprise needs to enforce a corporate rule that virtual machines can only be deployed in the 'East US' and 'West US' regions. Which Azure feature should be used?",
                "question_type": "single_choice",
                "options": [
                    "Azure Blueprints",
                    "Azure Policy",
                    "Azure Monitor",
                    "Role-Based Access Control (RBAC)",
                ],
                "correct_option": 1,
                "explanation": "Azure Policy enables organizations to define and enforce rules (such as allowed location policies) across resource groups and subscriptions.",
                "topic": "Describe Azure Management and Governance",
                "difficulty": "medium",
                "points": 10,
            },
            {
                "question_text": "Which cloud computing model provides the customer with the highest degree of management control over the operating system and networking configuration?",
                "question_type": "single_choice",
                "options": [
                    "Software as a Service (SaaS)",
                    "Platform as a Service (PaaS)",
                    "Infrastructure as a Service (IaaS)",
                    "Function as a Service (FaaS)",
                ],
                "correct_option": 2,
                "explanation": "In Infrastructure as a Service (IaaS), customers retain complete administrative control over virtual machines, OS configuration, runtime software, and network firewall rules.",
                "topic": "Describe Cloud Concepts",
                "difficulty": "easy",
                "points": 10,
            },
        ],
    },
    {
        "code": "AI-900",
        "slug": "microsoft-azure-ai-fundamentals-ai-900",
        "name": "Microsoft Azure AI Fundamentals",
        "vendor": "Microsoft",
        "description": "Demonstrate foundational knowledge of machine learning concepts, computer vision, natural language processing, and Azure OpenAI conversational solutions.",
        "level": "foundational",
        "category": "AI",
        "is_official_certification": True,
        "official_url": "https://learn.microsoft.com/en-us/credentials/certifications/azure-ai-fundamentals/",
        "exam_duration_minutes": 60,
        "total_exam_questions": 45,
        "passing_score_percentage": 70,
        "icon_name": "azure",
        "domains": [
            {
                "domain_name": "Describe AI Workloads and Considerations",
                "weight_percentage": 20,
                "question_count": 9,
            },
            {
                "domain_name": "Describe Fundamental Principles of Machine Learning",
                "weight_percentage": 25,
                "question_count": 11,
            },
            {
                "domain_name": "Describe Features of Computer Vision Workloads",
                "weight_percentage": 20,
                "question_count": 9,
            },
            {
                "domain_name": "Describe Features of NLP and Generative AI",
                "weight_percentage": 35,
                "question_count": 16,
            },
        ],
        "training": {
            "title": "Azure AI Fundamentals Training Program",
            "slug": "azure-ai-fundamentals-prep",
            "description": "Learn responsible AI governance, classification, regression, computer vision models, Azure OpenAI studio, and prompt design.",
            "level": "foundational",
            "estimated_hours": 18,
            "course_slug": "ai-for-cloud-devops",
        },
        "questions": [
            {
                "question_text": "Which principle of Responsible AI ensures that AI algorithms do not discriminate based on race, gender, or demographic background?",
                "question_type": "single_choice",
                "options": [
                    "Fairness",
                    "Reliability and Safety",
                    "Transparency",
                    "Accountability",
                ],
                "correct_option": 0,
                "explanation": "The Microsoft Responsible AI principle of Fairness requires that AI systems treat all people impartially and avoid bias.",
                "topic": "Describe AI Workloads and Considerations",
                "difficulty": "easy",
                "points": 10,
            },
            {
                "question_text": "You need to predict the exact continuous selling price of a cloud VM based on historical CPU, memory, and disk usage metrics. What type of machine learning model should you build?",
                "question_type": "single_choice",
                "options": [
                    "Binary Classification",
                    "Regression",
                    "Clustering",
                    "Anomaly Detection",
                ],
                "correct_option": 1,
                "explanation": "Regression algorithms predict continuous numerical output values (like prices or temperatures) based on input feature correlations.",
                "topic": "Describe Fundamental Principles of Machine Learning",
                "difficulty": "medium",
                "points": 10,
            },
            {
                "question_text": "Which Azure AI service enables developers to deploy enterprise GPT-4 models, configure system prompts, and index enterprise data for RAG solutions?",
                "question_type": "single_choice",
                "options": [
                    "Azure Computer Vision",
                    "Azure OpenAI Service",
                    "Azure Translator",
                    "Azure Form Recognizer",
                ],
                "correct_option": 1,
                "explanation": "Azure OpenAI Service provides REST API access to OpenAI's advanced language models including GPT-4 and embeddings, with enterprise security and responsible AI filters.",
                "topic": "Describe Features of NLP and Generative AI",
                "difficulty": "easy",
                "points": 10,
            },
        ],
    },
    {
        "code": "CF-AWS-FOUND",
        "slug": "aws-cloud-computing-foundations",
        "name": "AWS Cloud Computing Foundations",
        "vendor": "CloudForge",
        "description": "A comprehensive CloudForge engineering track covering AWS compute primitives, VPC routing topologies, IAM security policies, and fault-tolerant architecture.",
        "level": "foundational",
        "category": "Cloud",
        "is_official_certification": False,
        "exam_duration_minutes": 45,
        "total_exam_questions": 30,
        "passing_score_percentage": 75,
        "icon_name": "aws",
        "domains": [
            {
                "domain_name": "VPC & Subnet Topologies",
                "weight_percentage": 30,
                "question_count": 9,
            },
            {
                "domain_name": "Compute & Autoscaling",
                "weight_percentage": 30,
                "question_count": 9,
            },
            {
                "domain_name": "IAM & Least Privilege",
                "weight_percentage": 25,
                "question_count": 8,
            },
            {
                "domain_name": "Storage & Databases",
                "weight_percentage": 15,
                "question_count": 4,
            },
        ],
        "training": {
            "title": "CloudForge AWS Cloud Foundations Track",
            "slug": "cf-aws-cloud-foundations-track",
            "description": "Build real multi-tier cloud infrastructure with secure VPCs, public/private subnets, NAT gateways, and IAM policy enforcement.",
            "level": "foundational",
            "estimated_hours": 16,
            "course_slug": "cloud-computing-foundations",
        },
        "questions": [
            {
                "question_text": "In a 3-tier AWS VPC architecture, where should the backend database instances (RDS) be placed for optimal security?",
                "question_type": "single_choice",
                "options": [
                    "In public subnets with direct Internet Gateways",
                    "In isolated private subnets with no direct internet ingress route",
                    "In the default VPC public subnet",
                    "Attached directly to the NAT Gateway",
                ],
                "correct_option": 1,
                "explanation": "Database tiers must be placed in isolated private subnets without public IPs and with route tables that do not route traffic to the Internet Gateway.",
                "topic": "VPC & Subnet Topologies",
                "difficulty": "medium",
                "points": 10,
            },
            {
                "question_text": "What is the primary difference between a Security Group and a Network Access Control List (NACL) in AWS VPC?",
                "question_type": "single_choice",
                "options": [
                    "Security Groups are stateless at subnet level; NACLs are stateful at instance level",
                    "Security Groups operate at the instance level and are stateful; NACLs operate at the subnet level and are stateless",
                    "Security Groups only support DENY rules; NACLs only support ALLOW rules",
                    "NACLs cannot filter outbound traffic",
                ],
                "correct_option": 1,
                "explanation": "Security Groups are stateful firewalls attached to ENIs/instances. NACLs are stateless packet filters applied at the subnet boundary.",
                "topic": "VPC & Subnet Topologies",
                "difficulty": "medium",
                "points": 10,
            },
            {
                "question_text": "Which AWS IAM component allows EC2 instances or Lambda functions to securely obtain temporary credentials without hardcoding access keys in source code?",
                "question_type": "single_choice",
                "options": [
                    "IAM User Access Keys",
                    "IAM Roles attached via Instance Profile",
                    "IAM Group Policies",
                    "Root account credentials",
                ],
                "correct_option": 1,
                "explanation": "IAM Roles provide temporary credentials generated via AWS Security Token Service (STS) and attached to compute resources through Instance Profiles.",
                "topic": "IAM & Least Privilege",
                "difficulty": "easy",
                "points": 10,
            },
        ],
    },
    {
        "code": "CF-K8S-FOUND",
        "slug": "kubernetes-fundamentals",
        "name": "Kubernetes Fundamentals",
        "vendor": "CloudForge",
        "description": "CloudForge engineering certification covering Kubernetes cluster architecture, Pod lifecycle, Deployments, Services, RBAC, and Helm packaging.",
        "level": "intermediate",
        "category": "Kubernetes",
        "is_official_certification": False,
        "exam_duration_minutes": 60,
        "total_exam_questions": 40,
        "passing_score_percentage": 75,
        "icon_name": "kubernetes",
        "domains": [
            {
                "domain_name": "Control Plane & Cluster Architecture",
                "weight_percentage": 25,
                "question_count": 10,
            },
            {
                "domain_name": "Workload Management & Deployments",
                "weight_percentage": 30,
                "question_count": 12,
            },
            {
                "domain_name": "Services & Networking",
                "weight_percentage": 25,
                "question_count": 10,
            },
            {
                "domain_name": "RBAC & Cluster Security",
                "weight_percentage": 20,
                "question_count": 8,
            },
        ],
        "training": {
            "title": "CloudForge Kubernetes Core Engineering Track",
            "slug": "cf-k8s-core-engineering-track",
            "description": "Hands-on mastery of Kubernetes manifests, zero-downtime rolling updates, Ingress controllers, and least-privilege RBAC.",
            "level": "intermediate",
            "estimated_hours": 25,
            "course_slug": "kubernetes-engineering",
        },
        "questions": [
            {
                "question_text": "Which Kubernetes control plane component is the ONLY one that reads from and writes to the etcd key-value store?",
                "question_type": "single_choice",
                "options": [
                    "kube-scheduler",
                    "kube-controller-manager",
                    "kube-apiserver",
                    "kubelet",
                ],
                "correct_option": 2,
                "explanation": "The kube-apiserver acts as the single point of entry and the sole component that directly interfaces with etcd to persist cluster state.",
                "topic": "Control Plane & Cluster Architecture",
                "difficulty": "easy",
                "points": 10,
            },
            {
                "question_text": "What happens when a Pod's liveness probe consistently fails?",
                "question_type": "single_choice",
                "options": [
                    "The Pod is removed from Service endpoints but continues running",
                    "The kubelet restarts the failing container according to its restartPolicy",
                    "The kube-scheduler reschedules the Pod to a different node immediately",
                    "The node is marked NotReady by the controller manager",
                ],
                "correct_option": 1,
                "explanation": "When a liveness probe fails, kubelet kills the container and initiates a restart according to the Pod's restartPolicy. (Readiness probe failure removes it from endpoints).",
                "topic": "Workload Management & Deployments",
                "difficulty": "medium",
                "points": 10,
            },
            {
                "question_text": "Which Kubernetes Service type creates a dedicated external cloud load balancer and automatically routes traffic to NodePorts?",
                "question_type": "single_choice",
                "options": ["ClusterIP", "NodePort", "LoadBalancer", "ExternalName"],
                "correct_option": 2,
                "explanation": "A LoadBalancer Service provisions an external cloud load balancer (e.g. AWS NLB/ALB) and directs external traffic to the assigned NodePorts across the cluster.",
                "topic": "Services & Networking",
                "difficulty": "easy",
                "points": 10,
            },
            {
                "question_text": "Which Kubernetes RBAC object binds a ClusterRole to a specific user ONLY within a single designated namespace?",
                "question_type": "single_choice",
                "options": [
                    "ClusterRoleBinding",
                    "RoleBinding",
                    "ServiceAccount",
                    "NamespaceBinding",
                ],
                "correct_option": 1,
                "explanation": "A RoleBinding can reference a ClusterRole to grant its defined permissions within the RoleBinding's specific namespace without granting cluster-wide access.",
                "topic": "RBAC & Cluster Security",
                "difficulty": "medium",
                "points": 10,
            },
        ],
    },
    {
        "code": "CF-DEVOPS-FOUND",
        "slug": "devops-foundations",
        "name": "DevOps Foundations",
        "vendor": "CloudForge",
        "description": "CloudForge engineering program covering trunk-based Git, Docker containerization, CI/CD pipelines, and Infrastructure as Code.",
        "level": "foundational",
        "category": "DevOps",
        "is_official_certification": False,
        "exam_duration_minutes": 45,
        "total_exam_questions": 30,
        "passing_score_percentage": 75,
        "icon_name": "devops",
        "domains": [
            {
                "domain_name": "Git & Trunk-Based Development",
                "weight_percentage": 25,
                "question_count": 8,
            },
            {
                "domain_name": "CI/CD Automation Pipelines",
                "weight_percentage": 30,
                "question_count": 9,
            },
            {
                "domain_name": "Docker & Multi-Stage Builds",
                "weight_percentage": 25,
                "question_count": 8,
            },
            {
                "domain_name": "Telemetry & Observability",
                "weight_percentage": 20,
                "question_count": 5,
            },
        ],
        "training": {
            "title": "CloudForge DevOps Engineering Track",
            "slug": "cf-devops-engineering-track",
            "description": "Master automated GitHub Actions pipelines, multi-stage Docker build caching, semantic versioning, and Prometheus metrics collection.",
            "level": "foundational",
            "estimated_hours": 20,
            "course_slug": "devops-engineering-foundations",
        },
        "questions": [
            {
                "question_text": "What is the primary advantage of multi-stage Docker builds?",
                "question_type": "single_choice",
                "options": [
                    "Allows running multiple containers inside a single Pod",
                    "Separates build-time dependencies from the final minimal runtime image",
                    "Automatically scans images for CVE vulnerabilities",
                    "Enables Docker to run without root daemon privileges",
                ],
                "correct_option": 1,
                "explanation": "Multi-stage builds allow using bulky compilers/SDKs in early stages and copying only the compiled artifacts into a lightweight distroless/alpine final image.",
                "topic": "Docker & Multi-Stage Builds",
                "difficulty": "easy",
                "points": 10,
            },
            {
                "question_text": "In CI/CD pipeline design, what is the key characteristic of an idempotent deployment step?",
                "question_type": "single_choice",
                "options": [
                    "It executes faster than 10 seconds",
                    "Executing the step multiple times with the same input produces the exact same system state without unintended side-effects",
                    "It automatically rolls back on network timeouts",
                    "It requires manual human approval before execution",
                ],
                "correct_option": 1,
                "explanation": "Idempotency ensures that running an operation repeatedly results in the same desired state, preventing configuration drift or duplicate resources.",
                "topic": "CI/CD Automation Pipelines",
                "difficulty": "medium",
                "points": 10,
            },
            {
                "question_text": "Which of the following represents the Four Golden Signals of distributed systems monitoring?",
                "question_type": "single_choice",
                "options": [
                    "CPU, Memory, Disk, Network",
                    "Latency, Traffic, Errors, Saturation",
                    "Availability, Scalability, Resiliency, Security",
                    "SAST, DAST, SCA, SBOM",
                ],
                "correct_option": 1,
                "explanation": "Google's SRE book defines the Four Golden Signals as Latency (time taken), Traffic (demand/throughput), Errors (failure rate), and Saturation (resource utilization headroom).",
                "topic": "Telemetry & Observability",
                "difficulty": "easy",
                "points": 10,
            },
        ],
    },
]


async def seed_certifications_and_exams(db: AsyncSession) -> None:
    """Seed the 6 core certifications, training programs, and practice questions."""
    logger.info("Seeding Certifications, Trainings, and Practice Questions...")

    # Load all existing courses for mapping
    courses_res = await db.execute(select(Course))
    courses_map = {c.slug: c for c in courses_res.scalars().all()}

    for cert_data in CERTIFICATIONS_DATA:
        # Check or create certification
        res = await db.execute(
            select(Certification).where(Certification.slug == cert_data["slug"])
        )
        cert = res.scalars().first()

        level_enum = CertificationLevel(cert_data["level"])

        if not cert:
            cert = Certification(
                code=cert_data["code"],
                slug=cert_data["slug"],
                name=cert_data["name"],
                vendor=cert_data["vendor"],
                description=cert_data["description"],
                level=level_enum,
                category=cert_data["category"],
                is_official_certification=cert_data["is_official_certification"],
                official_url=cert_data.get("official_url"),
                exam_duration_minutes=cert_data["exam_duration_minutes"],
                total_exam_questions=cert_data["total_exam_questions"],
                passing_score_percentage=cert_data["passing_score_percentage"],
                icon_name=cert_data.get("icon_name"),
                domains=cert_data.get("domains", []),
                is_published=True,
            )
            db.add(cert)
            await db.flush()
            logger.info(f"Created Certification: {cert.name}")

        # Check or create training
        t_data = cert_data.get("training")
        training = None
        if t_data:
            t_res = await db.execute(
                select(CertificationTraining).where(
                    CertificationTraining.slug == t_data["slug"]
                )
            )
            training = t_res.scalars().first()
            linked_course = courses_map.get(t_data.get("course_slug"))

            if not training:
                training = CertificationTraining(
                    certification_id=cert.id,
                    title=t_data["title"],
                    slug=t_data["slug"],
                    description=t_data["description"],
                    level=CertificationLevel(t_data["level"]),
                    estimated_hours=t_data["estimated_hours"],
                    course_id=linked_course.id if linked_course else None,
                    is_published=True,
                )
                db.add(training)
                await db.flush()
                logger.info(f"Created Training Program: {training.title}")

        # Check or create practice questions
        for q_data in cert_data.get("questions", []):
            q_res = await db.execute(
                select(PracticeQuestion).where(
                    PracticeQuestion.certification_id == cert.id,
                    PracticeQuestion.question_text == q_data["question_text"],
                )
            )
            if not q_res.scalars().first():
                question = PracticeQuestion(
                    certification_id=cert.id,
                    training_id=training.id if t_data and training else None,
                    question_text=q_data["question_text"],
                    question_type=q_data.get("question_type", "single_choice"),
                    options=q_data["options"],
                    correct_option=q_data["correct_option"],
                    explanation=q_data["explanation"],
                    topic=q_data.get("topic"),
                    difficulty=q_data.get("difficulty", "medium"),
                    points=q_data.get("points", 10),
                    is_published=True,
                )
                db.add(question)

    # 4. Enroll Demo Student in AWS Cloud Practitioner
    student_res = await db.execute(
        select(User).where(User.email == "student@cloudforge.io")
    )
    student = student_res.scalars().first()
    if student:
        t_res = await db.execute(
            select(CertificationTraining).where(
                CertificationTraining.slug == "aws-cloud-practitioner-prep"
            )
        )
        aws_training = t_res.scalars().first()
        if aws_training:
            enr_res = await db.execute(
                select(UserCertificationEnrollment).where(
                    UserCertificationEnrollment.user_id == student.id,
                    UserCertificationEnrollment.training_id == aws_training.id,
                )
            )
            if not enr_res.scalars().first():
                db.add(
                    UserCertificationEnrollment(
                        user_id=student.id,
                        certification_id=aws_training.certification_id,
                        training_id=aws_training.id,
                        status="in_progress",
                    )
                )

    await db.commit()
    logger.info("Certifications, Trainings & Practice Questions seeding complete!")


async def seed_projects(db: AsyncSession):
    """Seed the 8 practical DevOps engineering projects, steps, resources, and connections."""
    logger.info("Seeding practical DevOps engineering projects...")

    courses_res = await db.execute(select(Course))
    courses_map = {c.slug: c for c in courses_res.scalars().all()}

    skills_res = await db.execute(select(Skill))
    skills_map = {s.slug: s for s in skills_res.scalars().all()}

    now = datetime.now(timezone.utc)

    for p_data in PROJECTS_DATA:
        p_res = await db.execute(select(Project).where(Project.slug == p_data["slug"]))
        project = p_res.scalars().first()

        if not project:
            project = Project(
                title=p_data["title"],
                slug=p_data["slug"],
                short_description=p_data["short_description"],
                description=p_data["description"],
                difficulty=p_data["difficulty"],
                estimated_hours=p_data["estimated_hours"],
                status=p_data["status"],
                featured=p_data["featured"],
                technologies=p_data["technologies"],
                deliverables=p_data["deliverables"],
                architecture_overview=p_data["architecture_overview"],
                prerequisites=p_data["prerequisites"],
                learning_objectives=p_data["learning_objectives"],
                repository_url=p_data["repository_url"],
                documentation_url=p_data["documentation_url"],
            )
            db.add(project)
            await db.flush()
            logger.info(f"Created Project: {project.title}")

            # Add Project Steps
            for s_data in p_data.get("steps", []):
                step = ProjectStep(
                    project_id=project.id,
                    step_order=s_data["step_order"],
                    step_type=s_data["step_type"],
                    title=s_data["title"],
                    description=s_data.get("description"),
                    instructions=s_data.get("instructions"),
                    command=s_data.get("command"),
                    expected_outcome=s_data.get("expected_outcome"),
                    is_required=s_data.get("is_required", True),
                )
                db.add(step)

            # Add Project Resources
            for r_data in p_data.get("resources", []):
                resource = ProjectResource(
                    project_id=project.id,
                    title=r_data["title"],
                    resource_type=r_data["resource_type"],
                    url=r_data["url"],
                    description=r_data.get("description"),
                    display_order=r_data.get("display_order", 0),
                )
                db.add(resource)

            # Link Courses
            for c_slug in p_data.get("course_slugs", []):
                course = courses_map.get(c_slug)
                if course:
                    db.add(ProjectCourse(project_id=project.id, course_id=course.id))

            # Link Skills
            for s_slug in p_data.get("skill_slugs", []):
                skill = skills_map.get(s_slug)
                if skill:
                    db.add(ProjectSkill(project_id=project.id, skill_id=skill.id))

    # Enroll demo student in Kubernetes Production Deployment & CloudForge CI/CD Pipeline
    student_res = await db.execute(
        select(User).where(User.email == "student@cloudforge.io")
    )
    student = student_res.scalars().first()

    if student:
        # Project 1: Kubernetes Production Deployment (In Progress)
        k8s_proj_res = await db.execute(
            select(Project).where(Project.slug == "kubernetes-production-deployment")
        )
        k8s_proj = k8s_proj_res.scalars().first()
        if k8s_proj:
            enr_res = await db.execute(
                select(UserProjectEnrollment).where(
                    UserProjectEnrollment.user_id == student.id,
                    UserProjectEnrollment.project_id == k8s_proj.id,
                )
            )
            if not enr_res.scalars().first():
                db.add(
                    UserProjectEnrollment(
                        user_id=student.id,
                        project_id=k8s_proj.id,
                        status=ProjectEnrollmentStatus.IN_PROGRESS.value,
                        started_at=now,
                        last_activity_at=now,
                    )
                )
                # Mark first 6 steps as completed
                steps_res = await db.execute(
                    select(ProjectStep)
                    .where(ProjectStep.project_id == k8s_proj.id)
                    .order_by(ProjectStep.step_order.asc())
                )
                k8s_steps = list(steps_res.scalars().all())
                for idx, step in enumerate(k8s_steps):
                    if idx < 6:
                        db.add(
                            ProjectStepProgress(
                                user_id=student.id,
                                project_step_id=step.id,
                                status=StepProgressStatus.COMPLETED.value,
                                started_at=now,
                                completed_at=now,
                                notes="Completed in local kind cluster environment.",
                            )
                        )
                    elif idx == 6:
                        db.add(
                            ProjectStepProgress(
                                user_id=student.id,
                                project_step_id=step.id,
                                status=StepProgressStatus.IN_PROGRESS.value,
                                started_at=now,
                                notes="Currently investigating CrashLoopBackOff.",
                            )
                        )

        # Project 2: CloudForge CI/CD Pipeline (Completed)
        cicd_proj_res = await db.execute(
            select(Project).where(Project.slug == "cloudforge-cicd-pipeline")
        )
        cicd_proj = cicd_proj_res.scalars().first()
        if cicd_proj:
            enr_res = await db.execute(
                select(UserProjectEnrollment).where(
                    UserProjectEnrollment.user_id == student.id,
                    UserProjectEnrollment.project_id == cicd_proj.id,
                )
            )
            if not enr_res.scalars().first():
                db.add(
                    UserProjectEnrollment(
                        user_id=student.id,
                        project_id=cicd_proj.id,
                        status=ProjectEnrollmentStatus.COMPLETED.value,
                        started_at=now,
                        completed_at=now,
                        last_activity_at=now,
                    )
                )
                steps_res = await db.execute(
                    select(ProjectStep)
                    .where(ProjectStep.project_id == cicd_proj.id)
                    .order_by(ProjectStep.step_order.asc())
                )
                for step in steps_res.scalars().all():
                    db.add(
                        ProjectStepProgress(
                            user_id=student.id,
                            project_step_id=step.id,
                            status=StepProgressStatus.COMPLETED.value,
                            started_at=now,
                            completed_at=now,
                            notes="Verified with GitHub Actions matrix execution.",
                        )
                    )

    await db.commit()
    logger.info("Projects seeding complete!")


async def main():
    """CLI execution entrypoint."""
    async with AsyncSessionLocal() as session:
        await seed_courses(session)
        await seed_demo_student_progress(session)
        await seed_skills_and_roadmaps(session)
        await seed_certifications_and_exams(session)
        await seed_projects(session)


if __name__ == "__main__":
    asyncio.run(main())
