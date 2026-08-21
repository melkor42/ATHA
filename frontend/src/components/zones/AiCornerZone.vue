<script setup>
import { computed, provide, ref, watch } from 'vue'
import UiRenderer from '../UiRenderer.vue'
import NetworkGraph from '../NetworkGraph.vue'
import { usePlaza } from '../../composables/usePlaza.js'
import { useGate } from '../../composables/useGate.js'
import bg from '../../assets/plaza/north.png'

// S3 North — AI Corner (spec §3): the only dusk-tonality zone. Everything
// here is composed live from the existing backend; the gate answers double
// as the compose prompt, with an optional free-text override. Loading is
// veins-slow + panels-breathe, never a spinner.
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/experience'
const fixtureName = new URLSearchParams(window.location.search).get('fixture')

const { current, slowVeins, say } = usePlaza()
const { promptText } = useGate()

const state = ref('idle') // idle | loading | ready | error
const schema = ref(null)
const persona = ref(null)
const errorMsg = ref('')
const freeText = ref('')
const revealed = ref(0)

provide('entities', computed(() => schema.value?.entities ?? {}))
const sections = computed(() => (Array.isArray(schema.value?.sections) ? schema.value.sections : []))

async function loadFixture() {
  const mods = import.meta.glob('../../fixtures/*.json', { eager: true })
  const mod = mods[`../../fixtures/${fixtureName}.json`]
  if (!mod) throw new Error(`unknown fixture: ${fixtureName}`)
  // small beat so the breathing panels are visible in mock mode too
  await new Promise((r) => setTimeout(r, 1200))
  return mod.default ?? mod
}

async function compose(custom) {
  if (state.value === 'loading') return
  state.value = 'loading'
  slowVeins.value = true
  errorMsg.value = ''
  revealed.value = 0
  const text =
    custom ||
    promptText.value ||
    'I am discovering Signal for the first time. Let me explore in my own way.'
  try {
    const payload = fixtureName
      ? await loadFixture()
      : await fetch(API_URL, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ text })
        }).then((r) => {
          if (!r.ok) throw new Error(`backend responded HTTP ${r.status}`)
          return r.json()
        })
    schema.value = payload?.experience ?? payload
    persona.value = payload?.persona ?? null
    state.value = 'ready'
    say('I composed this from what you told me. Poke me if you want to wander.')
    // panels assemble softly, one breath apart
    for (let i = 0; i < sections.value.length; i++) {
      await new Promise((r) => setTimeout(r, 380))
      revealed.value = i + 1
    }
  } catch (e) {
    errorMsg.value = e?.message || String(e)
    state.value = 'error'
  } finally {
    slowVeins.value = false
  }
}

// compose on first arrival in the north wing
watch(
  current,
  (z) => {
    if (z === 'north' && state.value === 'idle') compose()
  },
  { immediate: true }
)
</script>

<template>
  <section class="zone zone-north scrollable" :style="{ '--bg': `url(${bg})` }">
    <div class="north-copy">
      <p class="eyebrow">AI CORNER</p>
      <h2 class="wing-title">Composed live, for you</h2>

      <!-- loading: panels breathe light, no spinner (spec §3) -->
      <div v-if="state === 'loading'" class="breathing">
        <div v-for="n in 3" :key="n" class="breath-panel" :style="{ animationDelay: n * 0.45 + 's' }"></div>
        <p>the night side is listening…</p>
      </div>

      <div v-else-if="state === 'error'" class="error-card">
        <p>The corner could not compose: {{ errorMsg }}</p>
        <button type="button" class="plaza-btn" @click="compose(freeText.trim() || undefined)">
          Try again
        </button>
      </div>

      <template v-else-if="state === 'ready'">
        <div class="graph-panel on">
          <NetworkGraph />
        </div>
        <UiRenderer
          v-for="(node, i) in sections"
          :key="i"
          :node="node"
          class="panel"
          :class="{ on: i < revealed }"
        />
        <form class="compose-row" @submit.prevent="compose(freeText.trim() || undefined)">
          <input v-model="freeText" type="text" placeholder="…or tell CAM about you" />
          <button type="submit" class="plaza-btn solid">Compose</button>
        </form>
      </template>
    </div>
  </section>
</template>

<style scoped>
.zone-north {
  overflow-y: auto;
  scrollbar-width: thin;
  scrollbar-color: rgba(127, 227, 240, 0.35) transparent;
}
.north-copy {
  position: relative;
  min-height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 18px;
  padding: clamp(56px, 8vh, 110px) 6vw clamp(24px, 7vh, 96px);
}
/* the wing rarely gets the full design canvas: when the column is shorter
   than the space we have, auto margins center it in that space; when it is
   taller, they collapse to zero and the wing scrolls as before */
.north-copy > :first-child { margin-top: auto; }
.north-copy > :last-child { margin-bottom: auto; }
.eyebrow {
  font-size: 12px;
  letter-spacing: 0.34em;
  color: rgba(174, 244, 252, 0.75);
  margin: 0;
}
.wing-title {
  font-weight: 300;
  font-size: clamp(24px, 3vw, 40px);
  color: #f1ede6;
  margin: 0 0 12px;
  text-shadow: 0 0 24px rgba(127, 227, 240, 0.35);
}

/* breathing loading state */
.breathing {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 14px;
  width: min(720px, 94%);
}
.breath-panel {
  width: 100%;
  height: 84px;
  border-radius: 28px 32px 30px 26px;
  background: rgba(14, 26, 30, 0.68);
  border: 1px solid rgba(255, 214, 150, 0.18);
  animation: breathe-light 2.6s ease-in-out infinite;
}
@keyframes breathe-light {
  0%, 100% { box-shadow: inset 0 0 18px rgba(255, 190, 120, 0.08); opacity: 0.6; }
  50% { box-shadow: inset 0 0 42px rgba(255, 190, 120, 0.28); opacity: 1; }
}
.breathing p {
  color: rgba(241, 237, 230, 0.6);
  font-size: 13px;
  letter-spacing: 0.1em;
}

.error-card {
  background: rgba(14, 26, 30, 0.6);
  border: 1px solid rgba(255, 150, 120, 0.3);
  border-radius: 28px 32px 30px 26px;
  padding: 22px 26px;
  color: #f1ede6;
  display: flex;
  flex-direction: column;
  gap: 12px;
  align-items: flex-start;
}

.graph-panel,
.panel {
  width: min(720px, 94%);
  opacity: 0;
  transform: translateY(16px);
  filter: blur(5px);
  transition:
    opacity 0.9s cubic-bezier(0.22, 1, 0.36, 1),
    transform 0.9s cubic-bezier(0.22, 1, 0.36, 1),
    filter 0.9s cubic-bezier(0.22, 1, 0.36, 1);
}
.graph-panel.on,
.panel.on {
  opacity: 1;
  transform: none;
  filter: blur(0);
}
.graph-panel {
  /* the graph yields to the space we have instead of forcing its aspect */
  --graph-h: clamp(140px, 30vh, 396px);
  display: flex;
  align-items: center;
  background: rgba(14, 26, 30, 0.72);
  border: 1px solid rgba(127, 227, 240, 0.2);
  border-radius: 30px 34px 32px 28px;
  padding: 14px 18px;
  box-shadow: 0 12px 36px rgba(0, 0, 0, 0.35), inset 0 0 26px rgba(127, 227, 240, 0.08);
}

/* organic dusk restyle of the five registry components (scoped to this wing) */
.zone-north :deep(.card) {
  background: rgba(14, 26, 30, 0.8);
  border: 1px solid rgba(255, 214, 150, 0.22);
  border-radius: 26px 30px 28px 24px;
  backdrop-filter: blur(12px);
  box-shadow: 0 12px 36px rgba(0, 0, 0, 0.35), inset 0 0 26px rgba(255, 190, 120, 0.12);
  color: #f1ede6;
}
.zone-north :deep(.card .k) { color: rgba(174, 244, 252, 0.6); }
.zone-north :deep(.card .row span) { color: rgba(241, 237, 230, 0.55); }
.zone-north :deep(.card .row b) { color: #f1ede6; }

.compose-row {
  display: flex;
  gap: 10px;
  width: min(720px, 94%);
  margin-top: 8px;
}
.compose-row input {
  flex: 1;
  background: rgba(14, 26, 30, 0.78);
  border: 1px solid rgba(241, 237, 230, 0.25);
  border-radius: 999px;
  padding: 12px 20px;
  color: #f1ede6;
  font: inherit;
  font-size: 14px;
  outline: none;
}
.compose-row input:focus { border-color: rgba(127, 227, 240, 0.6); }
.compose-row input::placeholder { color: rgba(241, 237, 230, 0.45); }
</style>
