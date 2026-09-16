import type { NotificationItem } from '../types'

export const NOTIFICATIONS: NotificationItem[] = [
  {
    id: 'notif-1',
    title: 'Course In Progress',
    description: 'Your Kubernetes Engineering course is 68% complete. Resume: "ClusterIP vs NodePort".',
    timeAgo: '20m ago',
    read: false,
    type: 'course',
    link: '/learn/kubernetes-engineering/k8s-402',
  },
  {
    id: 'notif-2',
    title: 'Curriculum Update',
    description: 'New DevSecOps module available: "Container & Dependency Security with Trivy".',
    timeAgo: '2h ago',
    read: false,
    type: 'course',
    link: '/courses/devsecops-engineering',
  },
  {
    id: 'notif-3',
    title: 'Certification Prep Ready',
    description: 'Your AWS Cloud Practitioner (CLF-C02) mock exam score has been evaluated (84% score).',
    timeAgo: '1d ago',
    read: true,
    type: 'cert',
    link: '/certifications/aws-certified-cloud-practitioner',
  },
  {
    id: 'notif-4',
    title: 'Achievement Unlocked',
    description: 'You earned the Docker Explorer achievement (+400 XP)!',
    timeAgo: '3d ago',
    read: true,
    type: 'achievement',
    link: '/achievements',
  },
  {
    id: 'notif-5',
    title: 'New Incident Simulation',
    description: 'INC-0042 (502 Bad Gateway) has been assigned to the active troubleshooting queue.',
    timeAgo: '5d ago',
    read: true,
    type: 'incident',
    link: '/troubleshooting/inc-0042',
  },
]
