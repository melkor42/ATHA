export const ROLES = [
  {
    role: 'student',
    title: 'Talent',
    text: 'Join an MBA team and work a live company case.',
    label: 'Talent'
  },
  {
    role: 'business',
    title: 'Enterprise',
    text: 'You bring a challenge and have it defended by an MBA team.',
    label: 'Enterprise'
  },
  {
    role: 'warwick',
    title: 'Warwick',
    text: 'Education and research — the academic partner of ATHA.',
    label: 'Warwick'
  }
]

export const Q_ROLE = 'What role would fit you most?'

export const ROLE_WHY =
  'The experience looks different from each seat. I write for the one that matters to you.'

export const INTENTS = {
  student: [
    { intent: 'talent-fit', label: "Whether I'd fit a team" },
    { intent: 'talent-happens', label: 'What actually happens' },
    { intent: 'talent-judged', label: 'How the work is judged' },
    { intent: 'talent-takeaway', label: 'What I take away' }
  ],
  business: [
    { intent: 'biz-receive', label: 'What we receive as a partner' },
    { intent: 'biz-evaluated', label: 'How our challenge is evaluated' },
    { intent: 'biz-afterwards', label: 'What happens afterwards' },
    { intent: 'biz-ip', label: 'IP & confidentiality' }
  ],
  warwick: [
    { intent: 'wbs-education', label: 'How ATHA serves education' },
    { intent: 'wbs-role', label: "WBS's role" },
    { intent: 'wbs-research', label: 'The research ambition' }
  ]
}

export const EXPLORE_OPTION = { intent: 'explore', label: 'Just looking around' }

export const Q_INTENT = 'What do you most want to know right now?'

export const FACETS = {
  student: {
    question: 'Which role in a team would fit you best?',
    options: [
      { facet: 'func-domain-expert', label: 'A · Domain Expert' },
      { facet: 'func-ai-workflow-lead', label: 'B · AI Workflow Lead' },
      { facet: 'func-responsible-ai-risk', label: 'C · Responsible AI & Risk Lead' },
      { facet: 'func-business-viability-coordinator', label: 'D · Business Viability & Coordinator' },
      { facet: 'func-pitch-design-lead', label: 'E · Pitch & Design Lead' },
      { facet: null, label: 'Not sure yet — show me the mix' }
    ]
  },
  business: {
    question: 'What matters most to you as a partner?',
    options: [
      { facet: 'value-experience', label: 'Experience' },
      { facet: 'value-perspective', label: 'Perspective' },
      { facet: 'value-decision', label: 'Decision' },
      { facet: 'value-belonging', label: 'Belonging' },
      { facet: 'value-continuity', label: 'Continuity' },
      { facet: null, intent: 'biz-evaluated', label: 'How our challenge would be evaluated' }
    ]
  },
  warwick: {
    question: 'Where is your focus?',
    options: [
      { facet: 'cluster-education', label: 'Education — developing AI-native changemakers' },
      { facet: 'cluster-research', label: 'Research — evidence for healthier innovation' },
      { facet: 'cluster-institutional', label: 'Institutional — WBS’s role & the network' }
    ]
  }
}

export const Q_FREE = 'Anything else you want to know?'

export const FREE_SKIP = { label: 'Just show me what matters most.' }
