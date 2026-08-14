<script setup>
import { computed, ref, watch } from 'vue'
import Theater from './components/Theater.vue'
import WowPage from './components/WowPage.vue'
import { ACCENT_HUES, DEFAULT_HUES } from './theme.js'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/experience'
// wake ping: spin up a sleeping hosted backend while the user types
const HEALTH_URL = API_URL.replace(/\/api\/experience$/, '/health')
function wakeBackend() {
  try { fetch(HEALTH_URL, { method: 'GET' }).catch(() => {}) } catch { /* swallow */ }
}

// dev-only mock mode: ?fixture=miriam|jonas|david|tobias renders a
// hand-written ExperienceSchema without the backend.
const fixtureName = new URLSearchParams(window.location.search).get('fixture')

const phase = ref('onboarding') // onboarding | composing | ready | error
// fire one cheap /health ping each time the onboarding phase mounts — a
// sleeping Render backend wakes during the typing, no retries
watch(phase, (v) => { if (v === 'onboarding') wakeBackend() }, { immediate: true })
const input = ref('')
const schema = ref(null)
const persona = ref(null)
const errorMsg = ref('')
const theaterDone = ref(false)
const dataReady = ref(false)
const revealed = ref(false) // WowPage mounted — theater now plays its exit

const STEPS = [
  'persona: reading you',
  'traversal: querying the network',
  'compose: ranking signals',
  'grounding: verifying entity ids'
]

const waiting = computed(() => phase.value === 'composing' && theaterDone.value && !dataReady.value)

// substrate pulse palette follows the persona's ColorToken
const theaterHues = computed(() => ACCENT_HUES[persona.value?.accent_color] ?? DEFAULT_HUES)

function maybeReveal() {
  if (phase.value === 'composing' && theaterDone.value && dataReady.value) {
    phase.value = 'ready'
    // small beat so the WowPage entrance overlaps the graph dissolve
    setTimeout(() => { revealed.value = true }, 250)
  }
}

async function loadFixture(name) {
  const mods = import.meta.glob('./fixtures/*.json', { eager: true })
  const mod = mods[`./fixtures/${name}.json`]
  if (!mod) throw new Error(`unknown fixture: ${name}`)
  // small delay so the theater is visible in mock mode too
  await new Promise((r) => setTimeout(r, 1600))
  return mod.default ?? mod
}

async function start() {
  const text = input.value.trim()
  if (!text || phase.value === 'composing') return
  phase.value = 'composing'
  theaterDone.value = false
  dataReady.value = false
  revealed.value = false
  schema.value = null
  errorMsg.value = ''

  const request = fixtureName
    ? loadFixture(fixtureName)
    // no client timeout on purpose — the backend can take 20-60s
    : fetch(API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text })
      }).then((r) => {
        if (!r.ok) throw new Error(`backend responded HTTP ${r.status}`)
        return r.json()
      })

  try {
    const payload = await request
    // backend contract: {persona, experience, allowed_ids};
    // fixtures use the same envelope (or a bare ExperienceSchema)
    if (payload && payload.experience) {
      schema.value = payload.experience
      persona.value = payload.persona ?? null
    } else {
      schema.value = payload
      persona.value = null
    }
    dataReady.value = true
    maybeReveal()
  } catch (e) {
    errorMsg.value = e?.message || String(e)
    phase.value = 'error'
  }
}

function restart() {
  phase.value = 'onboarding'
  schema.value = null
  persona.value = null
  input.value = ''
  errorMsg.value = ''
}
</script>

<template>
  <header class="shell">
    <h1>SIGNAL · <span class="grad">the depth that makes it viable</span></h1>
    <p v-if="phase === 'onboarding'" class="hint">
      Tell me about you — one sentence is enough. The network composes your page.
    </p>
    <p v-else-if="fixtureName" class="hint">
      dev mock mode · fixture: {{ fixtureName }} · <a href="#" @click.prevent="restart">reset</a>
    </p>
  </header>

  <section v-if="phase === 'onboarding'" class="onboarding">
    <textarea
      v-model="input"
      rows="4"
      placeholder="Tell me about you — who you are, what you're looking for…"
      @keydown.ctrl.enter="start"
      @keydown.meta.enter="start"
    ></textarea>
    <button class="pill solid" type="button" :disabled="!input.trim()" @click="start">
      Compose my page
    </button>
  </section>

  <template v-if="phase === 'composing' || phase === 'ready'">
    <p v-if="waiting" class="waiting">still composing — the network goes deep, give it a moment…</p>
    <WowPage v-if="revealed && schema" :schema="schema" :persona="persona" @restart="restart" />
    <Theater
      :steps="STEPS"
      :active="!revealed"
      :exiting="revealed"
      :dim="0.16"
      :hues="theaterHues"
      @done="theaterDone = true; maybeReveal()"
    />
  </template>

  <section v-if="phase === 'error'" class="error">
    <p>The page could not be composed: {{ errorMsg }}</p>
    <button class="pill" type="button" @click="restart">Try again</button>
  </section>
</template>
