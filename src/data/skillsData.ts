import type { Skill } from '../types'

export const SKILLS: Skill[] = [
  {
    id: 'git',
    name: 'Git & Version Control',
    category: 'DevOps',
    proficiency: 85,
    targetLevel: 'Advanced',
    levelLabel: 'Advanced',
    trend: '+12%',
    relatedCourses: [
      { id: 'devops-engineering-foundations', title: 'DevOps Engineering Foundations' },
    ],
    relatedProjects: [
      { id: 'cloudforge-cicd-pipeline', title: 'CloudForge CI/CD Pipeline' },
      { id: 'gitops-delivery-platform', title: 'GitOps Delivery Platform' },
    ],
  },
  {
    id: 'docker',
    name: 'Docker & Containerization',
    category: 'DevOps',
    proficiency: 78,
    targetLevel: 'Intermediate',
    levelLabel: 'Intermediate',
    trend: '+8%',
    relatedCourses: [
      { id: 'devops-engineering-foundations', title: 'DevOps Engineering Foundations' },
      { id: 'kubernetes-engineering', title: 'Kubernetes Engineering' },
    ],
    relatedProjects: [
      { id: 'containerized-web-platform', title: 'Containerized Web Platform' },
      { id: 'secure-container-platform', title: 'Secure Container Platform' },
    ],
  },
  {
    id: 'cicd',
    name: 'CI/CD Automation',
    category: 'DevOps',
    proficiency: 74,
    targetLevel: 'Intermediate',
    levelLabel: 'Intermediate',
    trend: '+12%',
    relatedCourses: [
      { id: 'devops-engineering-foundations', title: 'DevOps Engineering Foundations' },
      { id: 'devsecops-engineering', title: 'DevSecOps Engineering' },
    ],
    relatedProjects: [
      { id: 'cloudforge-cicd-pipeline', title: 'CloudForge CI/CD Pipeline' },
    ],
  },
  {
    id: 'linux',
    name: 'Linux & Systems Administration',
    category: 'DevOps',
    proficiency: 72,
    targetLevel: 'Intermediate',
    levelLabel: 'Intermediate',
    trend: '+4%',
    relatedCourses: [
      { id: 'devops-engineering-foundations', title: 'DevOps Engineering Foundations' },
      { id: 'cloud-computing-foundations', title: 'Cloud Computing Foundations' },
    ],
    relatedProjects: [
      { id: 'terraform-aws-infrastructure', title: 'Terraform AWS Infrastructure' },
    ],
  },
  {
    id: 'aws',
    name: 'AWS Cloud Architecture',
    category: 'Cloud',
    proficiency: 67,
    targetLevel: 'Intermediate',
    levelLabel: 'Intermediate',
    trend: '+8%',
    relatedCourses: [
      { id: 'cloud-computing-foundations', title: 'Cloud Computing Foundations' },
      { id: 'cloud-security-fundamentals', title: 'Cloud Security Fundamentals' },
    ],
    relatedProjects: [
      { id: 'terraform-aws-infrastructure', title: 'Terraform AWS Infrastructure' },
    ],
  },
  {
    id: 'kubernetes',
    name: 'Kubernetes Orchestration',
    category: 'Kubernetes',
    proficiency: 61,
    targetLevel: 'Intermediate',
    levelLabel: 'Intermediate',
    trend: '+12%',
    relatedCourses: [
      { id: 'kubernetes-engineering', title: 'Kubernetes Engineering' },
      { id: 'gitops-with-argo-cd', title: 'GitOps with Argo CD' },
    ],
    relatedProjects: [
      { id: 'kubernetes-production-deployment', title: 'Kubernetes Production Deployment' },
    ],
  },
  {
    id: 'terraform',
    name: 'Terraform & IaC',
    category: 'Cloud',
    proficiency: 54,
    targetLevel: 'Beginner+',
    levelLabel: 'Beginner+',
    trend: '+4%',
    relatedCourses: [
      { id: 'infrastructure-as-code-terraform', title: 'Infrastructure as Code with Terraform' },
    ],
    relatedProjects: [
      { id: 'terraform-aws-infrastructure', title: 'Terraform AWS Infrastructure' },
    ],
  },
  {
    id: 'devsecops',
    name: 'DevSecOps & Security Automation',
    category: 'DevSecOps',
    proficiency: 48,
    targetLevel: 'Beginner',
    levelLabel: 'Beginner',
    trend: '+8%',
    relatedCourses: [
      { id: 'devsecops-engineering', title: 'DevSecOps Engineering' },
      { id: 'cloud-security-fundamentals', title: 'Cloud Security Fundamentals' },
    ],
    relatedProjects: [
      { id: 'devsecops-pipeline', title: 'DevSecOps Pipeline' },
    ],
  },
  {
    id: 'observability',
    name: 'Observability & Telemetry',
    category: 'Observability',
    proficiency: 42,
    targetLevel: 'Beginner',
    levelLabel: 'Beginner',
    trend: '+4%',
    relatedCourses: [
      { id: 'observability-engineering', title: 'Observability Engineering' },
    ],
    relatedProjects: [
      { id: 'observability-platform', title: 'Observability Stack' },
    ],
  },
  {
    id: 'ai-devops',
    name: 'AI for Cloud & DevOps',
    category: 'AI',
    proficiency: 35,
    targetLevel: 'Beginner',
    levelLabel: 'Beginner',
    trend: '+12%',
    relatedCourses: [
      { id: 'ai-for-cloud-devops', title: 'AI for Cloud & DevOps' },
    ],
    relatedProjects: [
      { id: 'ai-incident-intelligence-platform', title: 'AI Incident Intelligence Platform' },
    ],
  },
]
