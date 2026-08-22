import { ref } from 'vue'
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

const selections = ref({
  role: null,
  topics: [],
  style: 'organic' // organic preselected — the dusk wing's home register
})

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
  say(
    'Two models are out in the network now, retrieving and composing your page. ' +
      'That takes about a minute — wander, and I will have it ready when you are back.',
    9000
  )
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
    state.value = 'ready'
    say('I composed this from who you told me you are. Poke me if you want to wander.')
    revealStagger() // soft panel assembly, one breath apart
  } catch (e) {
    errorMsg.value = e?.message || String(e)
    state.value = 'error'
    say('The corner could not compose this time — the night side stays patient.')
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
}

export function useCompose() {
  return { state, schema, persona, errorMsg, revealed, selections, compose, restart, fixtureName }
}
