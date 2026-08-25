import { ref, computed } from 'vue'
import { LIFECYCLE, SESSION_KEYS } from '../config.js'

// Copy is EXACT per spec §5 — do not reword.
export const Q1 = {
  question: 'How are you meeting Atha today?',
  options: [
    { id: 'first', label: 'I am discovering Atha for the first time' },
    { id: 'deciding', label: 'I am deciding whether to attend' },
    { id: 'preparing', label: 'I am preparing to come' },
    // only visible/active AFTER the event (spec §5/§6)
    { id: 'experienced', label: 'I have already experienced Atha', afterOnly: true }
  ]
}

export const Q2 = {
  question: 'What would be most helpful now?',
  options: [
    { id: 'understand', label: 'Help me understand what Atha is' },
    { id: 'essential', label: 'Show me the essential details' },
    { id: 'atmosphere', label: 'Guide me into the atmosphere' },
    { id: 'explore', label: 'Let me explore in my own way' }
  ]
}

// Q2 answer → recommended direction (spec §4)
export const ROUTE = {
  understand: { zone: 'west', slow: false },
  essential: { zone: 'south', slow: false },
  atmosphere: { zone: 'north', slow: true },
  // routeless by spec: explore closes the gate without a lit path
  explore: { zone: null, slow: false }
}

const step = ref('idle') // idle | q1 | q2 | closing | done
const a1 = ref(null)
const a2 = ref(null)
// module-level so Plaza (who asks) and the gate zone (who renders
// welcome-back) share one visitor state
const seen = ref(
  typeof sessionStorage !== 'undefined' &&
    sessionStorage.getItem(SESSION_KEYS.entrance) === '1'
)

export function useGate() {
  const visibleQ1 = computed(() =>
    Q1.options.filter((o) => !o.afterOnly || LIFECYCLE === 'AFTER')
  )

  const route = computed(() => ROUTE[a2.value] ?? null)

  // the gate answers double as the compose prompt for the AI Corner
  const promptText = computed(() => {
    const l1 = Q1.options.find((o) => o.id === a1.value)?.label
    const l2 = Q2.options.find((o) => o.id === a2.value)?.label
    if (!l1 || !l2) return ''
    return `${l1}. ${l2}.`
  })

  function start() {
    step.value = 'q1'
  }

  function answer1(id) {
    console.info('[atha:gate] Q1 answered', { answer: id })
    a1.value = id
    step.value = 'q2'
    // canonical session keys per docs/atha-context-brief.md
    try { sessionStorage.setItem('athaVisitorState', id) } catch { /* private mode */ }
  }

  function answer2(id) {
    console.info('[atha:gate] Q2 answered', { answer: id, route: ROUTE[id]?.zone ?? null })
    a2.value = id
    // a routeless answer (explore) skips the closing step entirely:
    // no lit path, no closing line, no travel — the gate simply closes
    step.value = ROUTE[id]?.zone ? 'closing' : 'done'
    seen.value = true
    try {
      sessionStorage.setItem('athaExplorationMode', id)
      sessionStorage.setItem('athaEntryRoute', ROUTE[id]?.zone ?? '')
      sessionStorage.setItem(SESSION_KEYS.entrance, '1')
    } catch { /* private mode */ }
  }

  function changeRoute() {
    a1.value = null
    a2.value = null
    step.value = 'q1'
  }

  function finish() {
    console.info('[atha:gate] gate complete')
    step.value = 'done'
  }

  return { step, a1, a2, seen, visibleQ1, route, promptText, start, answer1, answer2, changeRoute, finish }
}
