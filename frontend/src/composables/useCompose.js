import { computed, ref, watch } from 'vue'
import { usePlaza } from './usePlaza.js'

// AI Corner compose state — lifted out of the zone (module-level singleton)
// so an honest ~1-minute compose survives the visitor leaving the north wing:
// they can wander, and the result waits for them. Mirrors the usePlaza /
// useGate pattern: one visitor, one shared state.

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/experience'
const fixtureName = new URLSearchParams(window.location.search).get('fixture')

// Step 1 — who are you coming as. Keys travel through the API as `role`.
export const ROLES = {
  student: {
    label: 'Student',
    topics: ['networking', 'mentoring', 'career development', 'events', 'entrepreneurship']
  },
  warwick: {
    label: 'University of Warwick',
    topics: ['mentoring', 'wellbeing', 'community', 'events', 'leadership']
  },
  business: {
    label: 'Business connection',
    topics: ['talent acquisition', 'consulting', 'fintech', 'sustainability', 'entrepreneurship']
  }
}

// Step 3 — how should it feel. 'surprise' sends no style: the compose agent's
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

const state = ref('idle') // idle | loading | ready | error
const schema = ref(null)
const persona = ref(null)
const errorMsg = ref('')
const revealed = ref(0) // staggered panel reveal, survives zone travel too

// Boris stays pinned to the composing line while the models are out
export const COMPOSING_LINE =
  'Two models are out in the network now, retrieving and composing your page. That takes about a minute — wander, and I will have it ready when you are back.'

// pickup notice: the compose finished while the visitor wandered elsewhere
const pickup = ref(false)
const { current: plazaZone } = usePlaza()
watch(plazaZone, (z) => {
  if (z === 'north') pickup.value = false
})

function clearPickup() {
  pickup.value = false
}

// owner decision: all moods visible at once — the style pick is low-stakes, no decision-load cap.

const selections = ref({
  role: null,
  topics: [],
  style: 'organic' // organic preselected — the AI Corner's home register
})

// Boris's sequential interview (spec: three questions, one after another,
// asked by the companion in the north wing). Lazy: starts on the first
// north visit of the session, pauses when the visitor wanders off (the
// plaza's line priority simply hides the branch) and resumes on return.
const step = ref('role') // role | topics | style | done
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
      return 'Who are you coming as?'
    case 'topics':
      return 'What would you like to see? Pick as many as you like — pick none and I choose.'
    case 'style':
      return 'How should it feel?'
    default:
      return ''
  }
})

const interviewOptions = computed(() => {
  if (step.value === 'role') {
    return Object.entries(ROLES).map(([id, r]) => ({
      id,
      label: r.label,
      selected: selections.value.role === id
    }))
  }
  if (step.value === 'topics') {
    const role = ROLES[selections.value.role]
    // one framed multi-select group (chip: true renders them as a wrapped
    // chip set, not competing full-width rows) + a single continue action
    const topics = (role?.topics ?? []).map((t) => ({
      id: t,
      label: t,
      selected: selections.value.topics.includes(t),
      chip: true
    }))
    return [...topics, { id: 'continue', label: 'continue →', action: true }]
  }
  if (step.value === 'style') {
    return STYLES.map((s) => ({ id: s.id, label: s.label, selected: selections.value.style === s.id, theme: s.id }))
  }
  return []
})

function answer(id) {
  if (!interviewStarted.value || step.value === 'done') return
  if (step.value === 'role') {
    if (selections.value.role !== id) selections.value.topics = [] // new role, new topic pool
    selections.value.role = id
    step.value = 'topics'
  } else if (step.value === 'topics') {
    if (id === 'continue') {
      step.value = 'style'
      return
    }
    const t = selections.value.topics
    selections.value.topics = t.includes(id) ? t.filter((x) => x !== id) : [...t, id]
  } else if (step.value === 'style') {
    selections.value.style = id
    step.value = 'done'
    // compose starts the moment the last answer lands — compose() itself
    // speaks the 'two models are out in the network' line
    compose()
  }
}

// a summary chip can pull the interview back to its question any time —
// even after 'done', so selections stay editable until compose starts
function reopen(s) {
  if (!interviewStarted.value) return
  if ((s === 'topics' || s === 'style') && !selections.value.role) return
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
  const { role, topics, style } = selections.value
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
      payload = await loadFixture()
    } else {
      const body = { role, topics }
      if (style && style !== 'surprise') body.style = style
      payload = await fetch(API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      }).then((r) => {
        if (!r.ok) throw new Error(`backend responded HTTP ${r.status}`)
        return r.json()
      })
    }
    schema.value = payload?.experience ?? payload
    persona.value = payload?.persona ?? null
    if (payload?.degraded) {
      // loud on purpose: a paused/deleted Aura instance must not hide
      // behind the quiet fallback page
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
  selections.value = { role: null, topics: [], style: 'organic' }
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
