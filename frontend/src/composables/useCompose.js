import { computed, ref, watch } from 'vue'
import { usePlaza } from './usePlaza.js'

// AI Corner compose state — lifted out of the zone (module-level singleton)
// so a fast single-model compose survives the visitor leaving the north wing:
// they can wander, and the result waits for them. Mirrors the usePlaza /
// useGate pattern: one visitor, one shared state.

// Single-service deploys (Koyeb Docker) serve SPA and API from one origin,
// so production defaults to the relative path; local dev talks to the
// uvicorn port unless VITE_API_URL overrides.
const API_URL = import.meta.env.VITE_API_URL
  || (import.meta.env.DEV ? 'http://localhost:8000/api/experience' : '/api/experience')
const fixtureName = new URLSearchParams(window.location.search).get('fixture')

// Step 1 — who are you coming as. Keys travel through the API as `role`.
export const ROLES = {
  student: { label: 'As talent — I want to join a team' },
  warwick: { label: 'From Warwick — education & research' },
  business: { label: 'As an enterprise — I want to bring a challenge' }
}

// Step 2 — intent: what do you most want to know right now? Ids must match
// backend skeleton.INTENTS (role-specific keys); the skip option sends no
// intent, which yields the identity bundle. Unknown ids are ignored by the
// backend, so drift degrades gracefully.
export const INTENTS = {
  student: [
    { id: 'talent-fit', label: 'Whether I\u2019d fit a team' },
    { id: 'talent-happens', label: 'What actually happens' },
    { id: 'talent-judged', label: 'How the work is judged' },
    { id: 'talent-takeaway', label: 'What I take away' }
  ],
  warwick: [
    { id: 'wbs-education', label: 'How ATHA serves education' },
    { id: 'wbs-role', label: 'WBS\u2019s role' },
    { id: 'wbs-research', label: 'The research ambition' }
  ],
  business: [
    { id: 'biz-receive', label: 'What we receive as a partner' },
    { id: 'biz-evaluated', label: 'How our challenge is evaluated' },
    { id: 'biz-afterwards', label: 'What happens afterwards' },
    { id: 'biz-ip', label: 'IP & confidentiality' }
  ]
}
export const INTENT_SKIP = { id: null, label: 'Just looking around' }

// Step 3 — facet: one role-specific narrowing question. Ids must match
// backend skeleton.known_facet_ids() (team functions / value forms / clusters).
export const FACETS = {
  student: [
    { id: 'func-domain-expert', label: 'Domain Expert — understanding the challenge' },
    { id: 'func-ai-workflow-lead', label: 'AI Workflow Lead — the technical approach' },
    { id: 'func-responsible-ai-risk', label: 'Responsible AI & Risk — governance and ethics' },
    { id: 'func-business-viability-coordinator', label: 'Business Viability — the business case' },
    { id: 'func-pitch-design-lead', label: 'Pitch & Design — communicating the decision' }
  ],
  warwick: [
    { id: 'cluster-education', label: 'Education — developing changemakers' },
    { id: 'cluster-research', label: 'Research — evidence for healthier innovation' },
    { id: 'cluster-institutional', label: 'Institutional — WBS\u2019s role and network' }
  ],
  business: [
    { id: 'value-experience', label: 'Experience — a different way of working' },
    { id: 'value-perspective', label: 'Perspective — seeing AI more fully' },
    { id: 'value-decision', label: 'Decision — a defensible verdict' },
    { id: 'value-belonging', label: 'Belonging — joining the community' },
    { id: 'value-continuity', label: 'Continuity — an ongoing relationship' }
  ]
}
export const FACET_SKIP = { id: null, label: 'Not sure yet — show me the mix' }

// Step 4 — free text: suggestion chips are real catalog questions; a chip click
// sends that question as free_text (the vector search finds its answer).
export const CHIPS = {
  student: [
    'How are teams formed?',
    'How is the teams\u2019 work judged?',
    'What happens during the experience?'
  ],
  warwick: [
    'How does ATHA serve education and research?',
    'What is Warwick Business School\u2019s role in ATHA?',
    'Why does ATHA exist — what makes it different?'
  ],
  business: [
    'How is confidentiality and IP handled?',
    'What happens after the experience?',
    'What do we need to bring as a partner?'
  ]
}
export const FREETEXT_SKIP_ID = 'freetext-skip'

// Step 5 — how should it feel. 'surprise' sends no style: the compose agent's
// temperament rule keeps the pages diverse. Everything else is enforced
// server-side (mode override), guaranteed.
export const STYLES = [
  { id: 'organic', label: 'Organic & alive' },
  { id: 'surprise', label: 'Surprise me' },
  { id: 'minimal', label: 'Clean & minimal' },
  { id: 'retro', label: 'Retro arcade' },
  { id: 'earth', label: 'Earth & craft' },
  { id: 'steampunk', label: 'Brass & steam' }
]

// The entrance gate (useGate.js answer1) stores its option id in
// sessionStorage['athaVisitorState']; 'first' means discovering. Map those ids
// onto the backend's visitor_state vocabulary so the compose call carries the
// journey state the visitor already stated at the gate.
const GATE_STATE = {
  first: 'discovering',
  deciding: 'deciding',
  preparing: 'preparing',
  experienced: 'experienced'
}

function gateVisitorState() {
  try {
    return GATE_STATE[sessionStorage.getItem('athaVisitorState') ?? ''] ?? null
  } catch {
    return null // private mode / storage unavailable
  }
}

const state = ref('idle') // idle | loading | ready | error
const schema = ref(null)
const persona = ref(null)
const errorMsg = ref('')
const revealed = ref(0) // staggered panel reveal, survives zone travel too

// Boris stays pinned to the composing line while the model is out
export const COMPOSING_LINE =
  'One model is out in the network now, retrieving and composing your page. A few heartbeats — stay close, it is already taking shape.'

// pickup notice: the compose finished while the visitor wandered elsewhere
const pickup = ref(false)
const { current: plazaZone } = usePlaza()
watch(plazaZone, (z) => {
  if (z === 'north') pickup.value = false
})

function clearPickup() {
  pickup.value = false
}

const selections = ref({
  role: null,
  intent: null,   // backend intent id or null (identity bundle)
  facet: null,    // backend facet id or null (no narrowing)
  freeText: null, // free-text question or null
  style: 'organic' // organic preselected — the AI Corner's home register
})

// Boris's sequential interview: role -> intent -> facet -> freetext -> style,
// asked by the companion in the north wing. Every step after role is skippable.
// Lazy: starts on the first north visit of the session, pauses when the visitor
// wanders off (the plaza's line priority simply hides the branch) and resumes
// on return.
const step = ref('role') // role | intent | facet | freetext | style | done
const interviewStarted = ref(false)

function beginInterview() {
  interviewStarted.value = true
}

const interviewActive = computed(
  () => interviewStarted.value && step.value !== 'done'
)

const interviewLine = computed(() => {
  switch (step.value) {
    case 'role':
      return 'How are you coming to ATHA?'
    case 'intent':
      return 'What do you most want to know right now?'
    case 'facet':
      return facetLine()
    case 'freetext':
      return 'Anything else you want to know? Pick a suggestion or type your own.'
    case 'style':
      return 'How should it feel?'
    default:
      return ''
  }
})

function facetLine() {
  switch (selections.value.role) {
    case 'student': return 'Which role in a team would fit you best?'
    case 'business': return 'What matters most to you as a partner?'
    case 'warwick': return 'Where is your focus?'
    default: return 'Anything you want to narrow down?'
  }
}

const interviewOptions = computed(() => {
  const role = selections.value.role
  if (step.value === 'role') {
    return Object.entries(ROLES).map(([id, r]) => ({
      id,
      label: r.label,
      selected: selections.value.role === id
    }))
  }
  if (step.value === 'intent') {
    const opts = (INTENTS[role] ?? []).map((o) => ({
      id: o.id,
      label: o.label,
      selected: selections.value.intent === o.id
    }))
    return [...opts, { id: 'intent-skip', label: INTENT_SKIP.label, selected: selections.value.intent === null }]
  }
  if (step.value === 'facet') {
    const opts = (FACETS[role] ?? []).map((o) => ({
      id: o.id,
      label: o.label,
      selected: selections.value.facet === o.id
    }))
    return [...opts, { id: 'facet-skip', label: FACET_SKIP.label, selected: selections.value.facet === null }]
  }
  if (step.value === 'freetext') {
    const chips = (CHIPS[role] ?? []).map((text) => ({
      id: text,       // chip id IS the question text -> becomes free_text
      label: text,
      chip: true
    }))
    return [
      ...chips,
      { input: true }, // renders the text field (Companion.vue)
      { id: FREETEXT_SKIP_ID, label: 'Just show me what matters most', action: true }
    ]
  }
  if (step.value === 'style') {
    return STYLES.map((s) => ({ id: s.id, label: s.label, selected: selections.value.style === s.id, theme: s.id }))
  }
  return []
})

function answer(id) {
  if (!interviewStarted.value || step.value === 'done') return
  if (step.value === 'role') {
    console.info('[atha:compose] role picked', { role: id })
    if (selections.value.role !== id) {
      // new role resets the narrowing answers
      selections.value.intent = null
      selections.value.facet = null
      selections.value.freeText = null
    }
    selections.value.role = id
    step.value = 'intent'
  } else if (step.value === 'intent') {
    selections.value.intent = id === 'intent-skip' ? null : id
    console.info('[atha:compose] intent picked', { intent: selections.value.intent })
    step.value = 'facet'
  } else if (step.value === 'facet') {
    selections.value.facet = id === 'facet-skip' ? null : id
    console.info('[atha:compose] facet picked', { facet: selections.value.facet })
    step.value = 'freetext'
  } else if (step.value === 'freetext') {
    selections.value.freeText = id === FREETEXT_SKIP_ID ? null : id
    console.info('[atha:compose] freetext set', { freeText: selections.value.freeText })
    step.value = 'style'
  } else if (step.value === 'style') {
    selections.value.style = id
    step.value = 'done'
    // compose starts the moment the last answer lands — compose() itself
    // speaks the 'one model is out in the network' line
    console.info('[atha:compose] style picked — compose triggered', { style: id })
    compose()
  }
}

// a summary chip can pull the interview back to its question any time —
// even after 'done', so selections stay editable until compose starts
function reopen(s) {
  if (!interviewStarted.value) return
  if (s !== 'role' && !selections.value.role) return
  step.value = s
}

async function loadFixture() {
  const mods = import.meta.glob('../fixtures/*.json', { eager: true })
  const mod = mods[`../fixtures/${fixtureName}.json`]
  if (!mod) throw new Error(`unknown fixture: ${fixtureName}`)
  // small beat so the theater field is visible in mock mode too
  await new Promise((r) => setTimeout(r, 2400))
  return mod.default ?? mod
}

async function revealStagger() {
  const count = Array.isArray(schema.value?.sections) ? schema.value.sections.length : 0
  for (let i = revealed.value; i < count; i++) {
    await new Promise((r) => setTimeout(r, 380))
    revealed.value = i + 1
  }
}

async function compose() {
  if (state.value === 'loading') return
  const { role, intent, facet, freeText, style } = selections.value
  if (!role) return
  state.value = 'loading'
  errorMsg.value = ''
  revealed.value = 0
  const { slowVeins, say } = usePlaza()
  slowVeins.value = true
  say(COMPOSING_LINE, 9000)
  try {
    let payload
    if (fixtureName) {
      console.info('[atha:compose] fixture branch', { fixture: fixtureName })
      payload = await loadFixture()
    } else {
      const body = { role, topics: [] }
      if (intent) body.intent = intent
      if (facet) body.facet = facet
      if (freeText) body.free_text = freeText
      if (style && style !== 'surprise') body.style = style
      const visitorState = gateVisitorState()
      if (visitorState) body.visitor_state = visitorState
      console.info('[atha:compose] request', body)
      const t0 = performance.now()
      payload = await fetch(API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      }).then((r) => {
        const ms = Math.round(performance.now() - t0)
        console.info('[atha:compose] response', { status: r.status, ms })
        if (!r.ok) throw new Error(`backend responded HTTP ${r.status}`)
        return r.json()
      })
    }
    schema.value = payload?.experience ?? payload
    persona.value = payload?.persona ?? null
    if (payload?.degraded) {
      // loud on purpose: a paused/deleted Aura instance must not hide
      // behind the quiet fallback page
      console.info('[atha:compose] degraded branch', { reason: payload?.degraded_reason || 'none' })
      console.error(
        '[AI Corner] compose degraded to the fallback page — Neo4j Aura is likely not connected.\n' +
          (payload?.degraded_reason || 'backend reported no reason')
      )
    }
    state.value = 'ready'
    pickup.value = plazaZone.value !== 'north'
    say('I composed this from who you told me you are. Poke me if you want to wander.')
    revealStagger() // soft panel assembly, one breath apart
  } catch (e) {
    console.error('[atha:compose] failed', e)
    errorMsg.value = e?.message || String(e)
    state.value = 'error'
    say('The corner could not compose this time — it stays patient.')
  } finally {
    slowVeins.value = false
  }
}

// discreet recompose: back to step 1, role first
function restart() {
  if (state.value === 'loading') return
  selections.value = { role: null, intent: null, facet: null, freeText: null, style: 'organic' }
  schema.value = null
  persona.value = null
  revealed.value = 0
  state.value = 'idle'
  step.value = 'role'
  pickup.value = false
}

export function useCompose() {
  return {
    state,
    schema,
    persona,
    errorMsg,
    revealed,
    selections,
    compose,
    restart,
    pickup,
    clearPickup,
    fixtureName,
    // the Boris interview
    step,
    interviewActive,
    interviewLine,
    interviewOptions,
    beginInterview,
    answer,
    reopen
  }
}
