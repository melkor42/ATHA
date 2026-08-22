<script setup>
import { computed, provide } from 'vue'
import UiRenderer from '../UiRenderer.vue'
import NetworkGraph from '../NetworkGraph.vue'
import Theater from '../Theater.vue'
import { useCompose, ROLES, STYLES } from '../../composables/useCompose.js'
import { ACCENT_HUES, DEFAULT_HUES } from '../../theme.js'
import bg from '../../assets/plaza/north.png'

// S3 North — AI Corner (spec §3): the only dusk-tonality zone. Everything
// here is composed live from the existing backend. The ritual is three
// questions from CAM — role, topics, style — then the compose agent builds
// the page; the compose state lives in useCompose so the ~1-minute wait
// survives leaving the wing. Loading is the Theater field, never a spinner.

const { state, schema, persona, errorMsg, revealed, selections, compose, restart } = useCompose()

provide('entities', computed(() => schema.value?.entities ?? {}))
const sections = computed(() => (Array.isArray(schema.value?.sections) ? schema.value.sections : []))

// allowlists — mirror WowPage: spectrum × mode drive the canvas restyle,
// scoped to this wing only (the rest of the plaza stays untouched)
const SPECTRA = new Set(['mycelium', 'terra', 'aurora', 'neon', 'void'])
const MODES = new Set(['none', 'minimal', 'retro', 'organic', 'earth', 'steampunk'])
const spectrum = computed(() => (SPECTRA.has(schema.value?.spectrum) ? schema.value.spectrum : 'terra'))
const mode = computed(() => (MODES.has(schema.value?.mode) ? schema.value.mode : 'none'))

const ACCENTS = {
  primary: 'var(--primary)',
  accent: 'var(--accent-tok)',
  success: 'var(--success)',
  warning: 'var(--warning)'
}
const accentVar = computed(() => ACCENTS[persona.value?.accent_color] ?? 'var(--accent-tok)')

// Theater hues follow the selected role's accent family while composing
const ROLE_HUE = { student: 'accent', warwick: 'success', business: 'primary' }
const hues = computed(() => ACCENT_HUES[ROLE_HUE[selections.value.role]] ?? DEFAULT_HUES)

const theaterSteps = ['asking the network', 'retrieving your matches', 'composing your page']

function pickRole(id) {
  selections.value.role = id
  selections.value.topics = []
}

function toggleTopic(topic) {
  const t = selections.value.topics
  selections.value.topics = t.includes(topic) ? t.filter((x) => x !== topic) : [...t, topic]
}

function pickStyle(id) {
  selections.value.style = id
}
</script>

<template>
  <section class="zone zone-north scrollable" :style="{ '--bg': `url(${bg})` }">
    <div class="north-copy">
      <p class="eyebrow">AI CORNER</p>
      <h2 class="wing-title">Composed live, for you</h2>

      <!-- the ritual: three questions from CAM, one at a time -->
      <template v-if="state === 'idle'">
        <p class="cam-intro">
          Here the network composes a page only for you. Tell me who you are
          and where you are coming from, pick what you would like to see and
          how it should feel — two models then retrieve the most fitting
          pieces of the network and build your page in the style you chose.
          That takes about a minute.
        </p>

        <div class="step">
          <p class="step-q">Who are you coming as?</p>
          <div class="chip-row">
            <button
              v-for="(r, id) in ROLES"
              :key="id"
              type="button"
              class="pick-chip"
              :class="{ on: selections.role === id }"
              @click="pickRole(id)"
            >{{ r.label }}</button>
          </div>
        </div>

        <template v-if="selections.role">
          <div class="step">
            <p class="step-q">What would you like to see?</p>
            <div class="chip-row">
              <button
                v-for="t in ROLES[selections.role].topics"
                :key="t"
                type="button"
                class="pick-chip"
                :class="{ on: selections.topics.includes(t) }"
                @click="toggleTopic(t)"
              >{{ t }}</button>
            </div>
            <p class="step-hint">Pick as many as you like — pick none and I choose for you.</p>
          </div>

          <div class="step">
            <p class="step-q">How should it feel?</p>
            <div class="chip-row">
              <button
                v-for="s in STYLES"
                :key="s.id"
                type="button"
                class="pick-chip"
                :class="{ on: selections.style === s.id }"
                @click="pickStyle(s.id)"
              >{{ s.label }}</button>
            </div>
            <button type="button" class="plaza-btn solid compose-btn" @click="compose()">
              Compose my page
            </button>
          </div>
        </template>
      </template>

      <!-- the canvas: empty in idle, theater while composing, result when ready -->
      <div class="canvas-frame" :class="{ waiting: state === 'loading' }">
        <div v-if="state === 'loading'" class="corner-theater">
          <Theater :steps="theaterSteps" :cadence="14000" :active="true" :hues="hues" />
          <p class="theater-note">the night side is listening — wander, it will wait for you</p>
        </div>

        <div v-else-if="state === 'error'" class="error-card">
          <p>The corner could not compose: {{ errorMsg }}</p>
          <button type="button" class="plaza-btn" @click="compose()">Try again</button>
        </div>

        <template v-else-if="state === 'ready'">
          <div class="graph-panel on">
            <NetworkGraph />
          </div>
          <div
            class="composed"
            :class="['spectrum-' + spectrum, 'mode-' + mode]"
            :style="{ '--accent': accentVar }"
          >
            <UiRenderer
              v-for="(node, i) in sections"
              :key="i"
              :node="node"
              class="panel"
              :class="{ on: i < revealed }"
            />
          </div>
          <button type="button" class="link-btn" @click="restart()">
            …or start again — choose another role
          </button>
        </template>

        <div v-else class="empty-canvas">
          <p>your page will be composed here</p>
        </div>
      </div>
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
  padding: clamp(56px, 8vh, 110px) 4vw clamp(24px, 7vh, 96px);
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
  margin: 0 0 4px;
  text-shadow: 0 0 24px rgba(127, 227, 240, 0.35);
}

/* CAM's explanation of what happens here */
.cam-intro {
  width: min(720px, 94%);
  margin: 0;
  color: rgba(241, 237, 230, 0.72);
  font-size: 14px;
  line-height: 1.65;
  letter-spacing: 0.02em;
  text-align: center;
}

/* the three questions */
.step {
  width: min(720px, 94%);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}
.step-q {
  margin: 0;
  color: rgba(174, 244, 252, 0.85);
  font-size: 13px;
  letter-spacing: 0.14em;
}
.step-hint {
  margin: 0;
  color: rgba(241, 237, 230, 0.45);
  font-size: 12px;
  letter-spacing: 0.04em;
}
.chip-row {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 10px;
}
.pick-chip {
  background: rgba(14, 26, 30, 0.68);
  border: 1px solid rgba(241, 237, 230, 0.22);
  border-radius: 999px;
  padding: 10px 18px;
  color: #f1ede6;
  font: inherit;
  font-size: 14px;
  cursor: pointer;
  transition: border-color 0.35s var(--ease), background 0.35s var(--ease),
    box-shadow 0.35s var(--ease);
}
.pick-chip:hover { border-color: rgba(127, 227, 240, 0.5); }
.pick-chip.on {
  border-color: rgba(127, 227, 240, 0.75);
  background: rgba(32, 58, 66, 0.78);
  box-shadow: inset 0 0 18px rgba(127, 227, 240, 0.16);
}
.compose-btn { margin-top: 6px; }

/* the canvas — owns most of the zone's space */
.canvas-frame {
  position: relative;
  width: min(1080px, 96%);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 18px;
}
.canvas-frame.waiting { min-height: clamp(240px, 52vh, 640px); }
.empty-canvas {
  width: 100%;
  min-height: clamp(240px, 42vh, 480px);
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px dashed rgba(127, 227, 240, 0.18);
  border-radius: 30px 34px 32px 28px;
  background: rgba(14, 26, 30, 0.35);
}
.empty-canvas p {
  margin: 0;
  color: rgba(241, 237, 230, 0.32);
  font-size: 13px;
  letter-spacing: 0.18em;
}

/* the Theater scoped into the wing (it ships as a fixed full-viewport stage) */
.corner-theater {
  position: relative;
  width: 100%;
  height: clamp(240px, 52vh, 640px);
}
.corner-theater :deep(.theater-stage) {
  position: absolute;
  inset: 0;
  z-index: 1;
  background: rgba(10, 18, 22, 0.82);
  border: 1px solid rgba(127, 227, 240, 0.2);
  border-radius: 30px 34px 32px 28px;
  overflow: hidden;
}
.theater-note {
  position: absolute;
  left: 0;
  right: 0;
  top: 18px;
  z-index: 2;
  margin: 0;
  text-align: center;
  color: rgba(241, 237, 230, 0.6);
  font-size: 13px;
  letter-spacing: 0.1em;
}

.error-card {
  width: min(720px, 94%);
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
  width: 100%;
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
  --graph-h: clamp(240px, 52vh, 640px);
  display: flex;
  align-items: center;
  background: rgba(14, 26, 30, 0.72);
  border: 1px solid rgba(127, 227, 240, 0.2);
  border-radius: 30px 34px 32px 28px;
  padding: 14px 18px;
  box-shadow: 0 12px 36px rgba(0, 0, 0, 0.35), inset 0 0 26px rgba(127, 227, 240, 0.08);
}

/* the composed canvas: spectrum × mode own the card styling now — the
   selected style restyles this wing's canvas and nothing else */
.composed {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.link-btn {
  background: none;
  border: none;
  padding: 6px 10px;
  color: rgba(241, 237, 230, 0.5);
  font: inherit;
  font-size: 13px;
  letter-spacing: 0.06em;
  cursor: pointer;
  transition: color 0.35s var(--ease);
}
.link-btn:hover { color: rgba(174, 244, 252, 0.9); }
</style>
