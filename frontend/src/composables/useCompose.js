import { computed, ref } from 'vue'

// Chat-centred compose engine — module singleton so the conversation and the
// composed page survive every remount of the shell.
//
// The visitor never picks a role, a facet or a style any more: role is pinned
// to 'student', and everything else is a question in the chat. The backend
// stays stateless — the conversation lives here and in localStorage, and the
// only thing that travels as "memory" is visitor_state, derived from how many
// answers the visitor already has.

const API_URL = import.meta.env.VITE_API_URL
  || (import.meta.env.DEV ? 'http://localhost:8001/api/experience' : '/api/experience')
const fixtureName = new URLSearchParams(window.location.search).get('fixture')

export const ROLE = 'student'

// Brand voice (§2): declarative, short, no hype. The agent opens with a
// question, because a question is what an agent does first.
export const GREETING =
  'I am the ATHA agent. I read the ATHA knowledge graph and compose the answer ' +
  'that matters for you now. What do you want to know about the three days?'

// First-time visitors are never faced with an empty input.
export const STARTERS = [
  { label: 'What actually happens across the three days?', intent: 'talent-happens' },
  { label: 'Would I fit a team like this?', intent: 'talent-fit' },
  { label: 'What do I take away from it?', intent: 'talent-takeaway' }
]

// Persistent CTA (§ brand: one ask per surface). The subject is the approved
// running case used since the register zone.
export const APPLY_HREF =
  'mailto:hello@onemundi.one?subject=ATHA%20001%20%E2%80%94%20Talent%20Application'
export const APPLY_LABEL = 'Apply as talent'

// MMC Delta — the synergy-matching app for the MBA teams. Separate host,
// IP-only, so it always opens in a new tab. Placement of this CTA is still
// being decided with Manuel; it hangs off team-shaped questions for now.
export const MMC_DELTA_HREF = 'http://92.5.120.120/'
const TEAM_INTENTS = new Set(['talent-fit'])

const COMPOSING_LINE = 'Retrieving and composing. A few seconds.'
const LOG_KEY = 'athaChatLog'

// discovering → deciding → preparing: the ranking context the copywriter uses.
function stateForTurn(turns) {
  if (turns <= 0) return 'discovering'
  if (turns < 3) return 'deciding'
  return 'preparing'
}

function loadSession() {
  try {
    const raw = localStorage.getItem(LOG_KEY)
    const parsed = raw ? JSON.parse(raw) : null
    return parsed && Array.isArray(parsed.messages) ? parsed : null
  } catch {
    return null // private mode / storage unavailable
  }
}

function persist(messages, schema, suggestions, turns) {
  try {
    localStorage.setItem(LOG_KEY, JSON.stringify({
      messages, schema, suggestions, turns
    }))
  } catch {
    /* non-fatal: the conversation simply does not survive a reload */
  }
}

const saved = loadSession()

const messages = ref(saved?.messages ?? [{ from: 'atha', text: GREETING }])
const schema = ref(saved?.schema ?? null)
const suggestions = ref(saved?.suggestions ?? [])
const turns = ref(saved?.turns ?? 0)
const status = ref('idle') // idle | composing | ready | error
const revealed = ref(schema.value ? (schema.value.sections?.length ?? 0) : 0)
// True only while a brand-new greeting has never been seen: restored sessions
// are already-read conversations, and the agent does not repeat itself.
const greetingLive = ref(saved === null)

const hasResult = computed(() => schema.value !== null)
const phase = computed(() => (hasResult.value ? 'reading' : 'landing'))
const busy = computed(() => status.value === 'composing')
const lastAnswer = computed(() => [...messages.value].reverse().find((m) => m.from === 'atha' && m.answer))

// Suggestion chips: the static starters before the first answer, the
// catalog's follow-up questions after it.
const chips = computed(() => {
  if (turns.value === 0) return STARTERS.map((s) => ({ ...s, kind: 'starter' }))
  return suggestions.value.map((s) => ({ label: s.text, intent: null, kind: 'follow' }))
})

// Exactly one contextual CTA below the persistent ask. It points at whatever
// the answer actually contains, or at MMC Delta for team-shaped questions.
const contextualCta = computed(() => {
  const sections = schema.value?.sections ?? []
  if (lastAnswer.value && TEAM_INTENTS.has(lastAnswer.value.intent)) {
    return {
      label: 'Match your team on MMC Delta',
      href: MMC_DELTA_HREF,
      external: true
    }
  }
  const kinds = {
    StageFlow: 'See how the three days run',
    FactList: 'What is settled, and what is still open',
    PartnerLayers: 'See who stands behind ATHA'
  }
  for (const order of ['StageFlow', 'FactList', 'PartnerLayers']) {
    const i = sections.findIndex((s) => s.component === order)
    if (i >= 0) return { label: kinds[order], href: `#section-${i}`, external: false }
  }
  return null
})

async function loadFixture() {
  const mods = import.meta.glob('../fixtures/*.json', { eager: true })
  const mod = mods[`../fixtures/${fixtureName}.json`]
  if (!mod) throw new Error(`unknown fixture: ${fixtureName}`)
  // one full beat, so the composing field is legible in demo mode too
  await new Promise((r) => setTimeout(r, 2400))
  const payload = mod.default ?? mod
  return { ...payload, experience: payload.experience ?? payload }
}

async function requestPayload(body) {
  const t0 = performance.now()
  const res = await fetch(API_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
  })
  const ms = Math.round(performance.now() - t0)
  console.info('[atha:compose] response', { status: res.status, ms })
  if (!res.ok) throw new Error(`backend responded HTTP ${res.status}`)
  return res.json()
}

async function revealStagger() {
  const count = schema.value?.sections?.length ?? 0
  for (let i = revealed.value; i < count; i++) {
    await new Promise((r) => setTimeout(r, 340))
    revealed.value = i + 1
  }
}

// A starter chip asks by intent (deterministic anchors); typed text and
// follow-up chips ask by free_text (the vector search finds their answer).
async function ask({ label, intent = null }) {
  if (busy.value || !label) return
  const text = label.trim()
  if (!text) return
  messages.value = [...messages.value, { from: 'you', text }]
  status.value = 'composing'
  const body = { role: ROLE, topics: [], visitor_state: stateForTurn(turns.value) }
  if (intent) body.intent = intent
  else body.free_text = text
  console.info('[atha:compose] request', body)
  try {
    const payload = fixtureName
      ? await loadFixture()
      : await requestPayload(body)
    schema.value = payload.experience ?? null
    suggestions.value = Array.isArray(payload.suggestions) ? payload.suggestions : []
    turns.value += 1
    if (payload.degraded) {
      // loud on purpose: a paused Aura instance must not hide behind the page
      console.error('[atha:compose] degraded — ' + (payload.degraded_reason || 'no reason given'))
    }
    const lead = schema.value?.sections?.[0]
    messages.value = [...messages.value, {
      from: 'atha',
      answer: true,
      intent: intent || null,
      title: lead?.title ?? 'Here is what the graph holds.',
      text: lead?.text ?? 'The answer is open in the page beside this conversation.'
    }]
    status.value = 'ready'
    revealed.value = 0
    revealStagger()
  } catch (e) {
    console.error('[atha:compose] failed', e)
    status.value = 'error'
    messages.value = [...messages.value, {
      from: 'atha',
      error: true,
      text: 'That answer did not come. The graph is still there — ask again.'
    }]
  } finally {
    persist(messages.value, schema.value, suggestions.value, turns.value)
  }
}

function restart() {
  if (busy.value) return
  messages.value = [{ from: 'atha', text: GREETING }]
  greetingLive.value = true
  schema.value = null
  suggestions.value = []
  turns.value = 0
  revealed.value = 0
  status.value = 'idle'
  persist(messages.value, schema.value, suggestions.value, turns.value)
  window.scrollTo({ top: 0, behavior: 'auto' })
}

// The opening line counts as spoken the moment it has been delivered — persist
// it then, so a reload never re-types a greeting the visitor has already read.
function settleGreeting() {
  if (!greetingLive.value) return
  greetingLive.value = false
  persist(messages.value, schema.value, suggestions.value, turns.value)
}

export function useCompose() {
  return {
    phase,
    hasResult,
    status,
    busy,
    schema,
    suggestions,
    messages,
    chips,
    greetingLive,
    settleGreeting,
    contextualCta,
    revealed,
    turns,
    fixtureName,
    asking: ask,
    restart,
    composingLine: COMPOSING_LINE
  }
}
