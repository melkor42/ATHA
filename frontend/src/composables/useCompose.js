import { computed, ref } from 'vue'
import {
  Q_ROLE, ROLE_WHY, INTENTS, EXPLORE_OPTION, Q_INTENT,
  FACETS, Q_FREE, FREE_SKIP
} from '../interview.js'

// Chat-centred compose engine — module singleton so the conversation and the
// composed page survive every remount of the shell.
//
// The interview is the conversation: the agent asks role, intent and facet as
// questions, and only the answers to those travel to the stateless backend as
// role/intent/facet/free_text. "Memory" is visitor_state, derived from how many
// answers the visitor already has.

const API_URL = import.meta.env.VITE_API_URL
  || (import.meta.env.DEV ? 'http://localhost:8000/api/experience' : '/api/experience')
const LEAD_URL = API_URL.replace(/\/experience$/, '/lead')
const fixtureName = new URLSearchParams(window.location.search).get('fixture')

// Brand voice (§2): declarative, short, no hype. The introduction states what
// the agent is; its first question is the role choice the interview opens with.
export const GREETING =
  'I am the ATHA agent. I read the ATHA knowledge graph and compose the answer ' +
  'that matters for you now.'

// First-time visitors are never faced with an empty input. These carry the
// conversation when there is no interview to run: fixture mode, and a first
// compose that failed before a role was chosen.
const STARTERS = [
  { label: 'What actually happens across the experience?', intent: 'talent-happens', kind: 'follow' },
  { label: 'Would I fit a team like this?', intent: 'talent-fit', kind: 'follow' },
  { label: 'What do I take away from it?', intent: 'talent-takeaway', kind: 'follow' }
]

// Persistent CTA (§ brand: one ask per surface), per role. The subject is the
// approved running case used since the register zone.
export const APPLY_HREF =
  'mailto:hello@onemundi.one?subject=ATHA%20001%20%E2%80%94%20Talent%20Application'
export const APPLY_LABEL = 'Apply as talent'
const BUSINESS_CTA = {
  label: 'Schedule a call',
  href: 'mailto:hello@onemundi.one?subject=ATHA%20001%20%E2%80%94%20Schedule%20a%20call'
}
const WARWICK_CTA = {
  label: 'Talk education & research',
  href: 'mailto:hello@onemundi.one?subject=ATHA%20001%20%E2%80%94%20Education%20%26%20Research'
}

// MMC Delta — the synergy-matching app for the MBA teams. Separate host,
// IP-only, so it always opens in a new tab. Shown as the contextual CTA for
// team-shaped moments.
export const MMC_DELTA_HREF = 'http://92.5.120.120/how'
const TEAM_INTENTS = new Set(['talent-fit'])

const COMPOSING_LINE = 'Retrieving and composing. A few seconds.'
// Versioned on purpose. A v2 log was written while suggestion chips never
// carried their catalog id to the backend, so the pages it restores were
// composed from role|state alone and read as identical no matter what was
// asked. Bumping the key drops those stale logs; the version jump is the
// mechanism that starts every visitor on a clean, question-specific
// conversation.
const LOG_KEY = 'athaChatLog.v3'

function freshInterview() {
  return { stage: fixtureName ? 'done' : 'role', role: null, intent: null, facet: null }
}

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

function persist(messages, schema, suggestions, turns, interview, lead) {
  try {
    localStorage.setItem(LOG_KEY, JSON.stringify({
      messages, schema, suggestions, turns, interview, lead
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
const interview = ref(
  saved?.interview && ['role', 'intent', 'facet', 'freetext', 'done'].includes(saved.interview.stage)
    ? { ...freshInterview(), ...saved.interview }
    : freshInterview())
const lead = ref(saved?.lead ?? null) // null | captured | sent

const hasResult = computed(() => schema.value !== null)
const phase = computed(() => (hasResult.value ? 'reading' : 'landing'))
const busy = computed(() => status.value === 'composing')
const lastAnswer = computed(() => [...messages.value].reverse().find((m) => m.from === 'atha' && m.answer))

const currentCta = computed(() => {
  const role = interview.value.role
  if (role === 'business') return BUSINESS_CTA
  if (role === 'warwick') return WARWICK_CTA
  return { label: APPLY_LABEL, href: APPLY_HREF }
})

// Suggestion chips: the interview's current stage before the first answer, the
// catalog's follow-up questions after it. Each follow chip keeps its catalog id
// so a click composes that exact question (D1); suggestions whose text has
// already been sent are filtered out, so a question is never offered twice.
const chips = computed(() => {
  const stage = interview.value.stage
  if (stage === 'role') return []
  if (schema.value) {
    const sent = new Set(messages.value.filter((m) => m.from === 'you').map((m) => m.text))
    return suggestions.value
      .filter((s) => !sent.has(s.text))
      .map((s) => ({ label: s.text, id: s.id, kind: 'follow' }))
  }
  if (stage === 'intent') return [...INTENTS[interview.value.role], { ...EXPLORE_OPTION, kind: 'intent' }]
  if (stage === 'facet') return FACETS[interview.value.role].options.map((o) => ({ ...o, kind: 'facet' }))
  if (stage === 'freetext') return [{ ...FREE_SKIP, kind: 'skip' }]
  return STARTERS
})

// While the gate is open the role card is the only way forward: the composer
// stays visible but muted and disabled, because a typed question cannot be
// composed for a seat nobody has named yet.
const roleGate = computed(() =>
  !fixtureName && interview.value.stage === 'role' && schema.value === null)

// Exactly one contextual CTA below the persistent ask. It points at whatever
// the answer actually contains, or at MMC Delta for team-shaped questions.
const contextualCta = computed(() => {
  const sections = schema.value?.sections ?? []
  if ((lastAnswer.value && TEAM_INTENTS.has(lastAnswer.value.intent))
    || (interview.value.role === 'student' && interview.value.facet)) {
    return {
      label: 'How the matching works on MMC Delta',
      href: MMC_DELTA_HREF,
      external: true
    }
  }
  const kinds = {
    StageFlow: 'See how the experience runs',
    FactList: 'What is settled, and what is still open',
    PartnerLayers: 'See who stands behind ATHA'
  }
  for (const order of ['StageFlow', 'FactList', 'PartnerLayers']) {
    const i = sections.findIndex((s) => s.component === order)
    if (i >= 0) return { label: kinds[order], href: `#section-${i}`, external: false }
  }
  return null
})

// The email summary is a personal extra, not a step in the question→answer
// rhythm: it surfaces beside "Apply as talent" only once the visitor has seen
// real composed content (two answers), and withdraws once requested (D4).
const summaryCtaVisible = computed(() =>
  !fixtureName && lead.value === null && turns.value >= 2)

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

// An interview chip or typed line asks by intent/facet/free_text anchors; a
// clicked catalog question travels as anchor_qid, which the skeleton boosts
// above every other catalog anchor so the page is specific to that question.
// The backend plan is deterministic for catalog anchors, vector search for free
// text.
async function ask({ label, intent = null, facet = null, free_text = null, anchor_qid = null }) {
  if (busy.value || !label) return
  const text = label.trim()
  if (!text) return
  messages.value = [...messages.value, { from: 'you', text }]
  status.value = 'composing'
  const body = {
    role: interview.value.role || 'student', topics: [], visitor_state: stateForTurn(turns.value)
  }
  if (intent) body.intent = intent
  if (facet) body.facet = facet
  if (free_text) body.free_text = free_text
  if (anchor_qid) body.anchor_qid = anchor_qid
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
    const leadSection = schema.value?.sections?.[0]
    messages.value = [...messages.value, {
      from: 'atha',
      answer: true,
      intent: intent || null,
      title: leadSection?.title ?? 'Here is what the graph holds.',
      text: leadSection?.text ?? 'The answer is open in the page beside this conversation.'
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
    persist(messages.value, schema.value, suggestions.value, turns.value, interview.value, lead.value)
  }
}

// The interview runs as spoken question lines; each pick records the answer and
// the agent asks the next step. A typed line ends it and composes immediately.
function pick(chip) {
  if (busy.value) return
  const iv = interview.value
  if (iv.stage === 'done') {
    ask({ label: chip.label, intent: chip.intent ?? null, anchor_qid: chip.id ?? null })
    return
  }
  if (iv.stage === 'freetext') {
    // the skip composes from the answers alone; only a typed line is free text
    interview.value = { ...iv, stage: 'done' }
    ask({ label: chip.label, intent: iv.intent, facet: iv.facet })
    return
  }
  messages.value = [...messages.value, { from: 'you', text: chip.label }]
  if (iv.stage === 'role') {
    interview.value = { ...iv, role: chip.role, intent: null, facet: null, stage: 'done' }
  } else if (iv.stage === 'intent') {
    interview.value = { ...iv, intent: chip.intent, stage: 'facet' }
    messages.value = [...messages.value, { from: 'atha', text: FACETS[iv.role].question }]
  } else if (iv.stage === 'facet') {
    interview.value = chip.intent
      ? { ...iv, intent: chip.intent, facet: null, stage: 'freetext' }
      : { ...iv, facet: chip.facet, stage: 'freetext' }
    messages.value = [...messages.value, { from: 'atha', text: Q_FREE }]
  }
  persist(messages.value, schema.value, suggestions.value, turns.value, interview.value, lead.value)
}

// Typed text during the interview is the free-text answer that ends it; once
// the conversation is past the interview it is simply a follow-up question.
function submitTyped(text) {
  const iv = interview.value
  if (!schema.value && iv.stage !== 'done') {
    interview.value = { ...iv, stage: 'done' }
    ask({ label: text, intent: iv.intent, facet: iv.facet, free_text: text })
    return
  }
  ask({ label: text, free_text: text })
}

function settleGreeting() {
  if (!greetingLive.value) return
  greetingLive.value = false
  if (!fixtureName && interview.value.stage === 'role'
    && !messages.value.some((m) => m.text === Q_ROLE)) {
    messages.value = [...messages.value, { from: 'atha', kind: 'role-ask', text: Q_ROLE, why: ROLE_WHY }]
  }
  persist(messages.value, schema.value, suggestions.value, turns.value, interview.value, lead.value)
}

const emailDraft = ref('')
const leadBusy = ref(false)

async function submitLead(email) {
  const value = (email || '').trim()
  if (!value || leadBusy.value) return
  const iv = interview.value
  leadBusy.value = true
  let emailed = false
  let ok = false
  const sections = (schema.value?.sections ?? []).slice(0, 10).map((s) => ({
    title: (s.title || '').slice(0, 80),
    text: (s.text || '').slice(0, 500),
    component: (s.component || 'Statement').slice(0, 20)
  }))
  try {
    const res = await fetch(LEAD_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email: value,
        role: iv.role || 'student',
        intent: iv.intent,
        facet: iv.facet,
        sections
      })
    })
    if (res.ok) {
      const json = await res.json()
      emailed = !!json.emailed
      ok = true
      lead.value = emailed ? 'sent' : 'captured'
    }
  } catch (e) {
    console.error('[atha:lead] failed', e)
  }
  if (ok) {
    interview.value = { ...iv, stage: 'done' }
    emailDraft.value = ''
    messages.value = [...messages.value, {
      from: 'atha',
      text: emailed
        ? `Done — the summary is on its way to ${value}.`
        : `Saved — we will follow up at ${value}.`
    }]
  } else {
    // the form stays open: a refused request is not a refusal by the visitor
    messages.value = [...messages.value, {
      from: 'atha',
      error: true,
      text: 'That address did not go through. Try once more.'
    }]
  }
  leadBusy.value = false
  persist(messages.value, schema.value, suggestions.value, turns.value, interview.value, lead.value)
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
  interview.value = freshInterview()
  lead.value = null
  emailDraft.value = ''
  persist(messages.value, schema.value, suggestions.value, turns.value, interview.value, lead.value)
  window.scrollTo({ top: 0, behavior: 'auto' })
}

// The opening line counts as spoken the moment it has been delivered — persist
// it then, so a reload never re-types a greeting the visitor has already read.
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
    roleGate,
    greetingLive,
    settleGreeting,
    contextualCta,
    summaryCtaVisible,
    currentCta,
    interview,
    lead,
    emailDraft,
    leadBusy,
    revealed,
    turns,
    fixtureName,
    pick,
    submitTyped,
    submitLead,
    restart,
    composingLine: COMPOSING_LINE
  }
}
