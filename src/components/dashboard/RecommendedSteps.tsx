import { Link } from 'react-router-dom'
import { Card } from '../common/Card'
import { Server, Shield, Layers, Award, ArrowRight, Zap } from 'lucide-react'
import { Button } from '../common/Button'

export function RecommendedSteps() {
  const steps = [
    {
      title: 'Learn Kubernetes Services',
      category: 'Recommended Lesson',
      duration: '18m',
      desc: 'ClusterIP vs NodePort vs LoadBalancer traffic routing internals.',
      link: '/learn/kubernetes-engineering/k8s-402',
      icon: <Server className="w-4 h-4 text-cyan-400" />,
      actionLabel: 'Resume Lesson',
      color: 'cyan',
    },
    {
      title: 'Complete Docker Security Module',
      category: 'DevSecOps Skill',
      duration: '45m',
      desc: 'Audit OCI image layers with Trivy & enforce non-root runtime users.',
      link: '/courses/devsecops-engineering',
      icon: <Shield className="w-4 h-4 text-emerald-400" />,
      actionLabel: 'Start Module',
      color: 'emerald',
    },
    {
      title: 'Start Terraform AWS Project',
      category: 'Production Project',
      duration: '16h',
      desc: 'Provision multi-AZ VPC, EKS cluster, and DynamoDB remote state lock.',
      link: '/projects/terraform-aws-infrastructure',
      icon: <Layers className="w-4 h-4 text-purple-400" />,
      actionLabel: 'View Project',
      color: 'purple',
    },
    {
      title: 'Take AWS Cloud Practitioner Assessment',
      category: 'Mock Exam',
      duration: '65 Questions',
      desc: 'Full timed practice exam simulating the CLF-C02 exam domains.',
      link: '/certifications/aws-certified-cloud-practitioner',
      icon: <Award className="w-4 h-4 text-amber-400" />,
      actionLabel: 'Launch Exam',
      color: 'amber',
    },
  ]

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Zap className="w-4 h-4 text-amber-400" />
          <h3 className="text-base font-bold text-white">Recommended Next Steps</h3>
        </div>
        <span className="text-xs font-mono text-slate-400">Tailored to your goal: DevOps</span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {steps.map(step => (
          <Card key={step.title} className="p-5 flex flex-col justify-between hover:border-slate-700 transition-all group">
            <div>
              <div className="flex items-center justify-between mb-3">
                <div className="p-2 rounded-lg bg-slate-800 border border-slate-700/60">
                  {step.icon}
                </div>
                <span className="text-[10px] font-mono text-slate-400">{step.duration}</span>
              </div>
              <span className="text-[10px] font-mono uppercase tracking-wider text-slate-500">
                {step.category}
              </span>
              <h4 className="text-sm font-bold text-white group-hover:text-cyan-300 transition-colors mt-1">
                {step.title}
              </h4>
              <p className="text-xs text-slate-400 mt-1.5 leading-relaxed line-clamp-2">
                {step.desc}
              </p>
            </div>

            <div className="mt-5 pt-3 border-t border-slate-800">
              <Link to={step.link}>
                <Button variant="secondary" size="xs" className="w-full justify-between" iconRight={<ArrowRight className="w-3 h-3" />}>
                  {step.actionLabel}
                </Button>
              </Link>
            </div>
          </Card>
        ))}
      </div>
    </div>
  )
}
