<script setup>
import { computed, onBeforeUnmount, provide, ref, watch } from 'vue'
import UiRenderer from '../UiRenderer.vue'
import NetworkGraph from '../NetworkGraph.vue'
import Theater from '../Theater.vue'
import { useCompose, ROLES, STYLES } from '../../composables/useCompose.js'
import { ACCENT_HUES, DEFAULT_HUES } from '../../theme.js'
import bg from '../../assets/plaza/north.png'

// S3 North — AI Corner (spec §3): the plaza's composed-live zone. Everything
// here is composed live from the existing backend. The ritual is three
// questions from CAM — role, topics, style — asked sequentially by Boris
// himself (useCompose step machine); the zone shows a compact summary of
// the selections. Loading is the Theater field, never a spinner.

const {
  state,
  schema,
  persona,
  errorMsg,
  revealed,
  selections,
  compose,
  restart,
  reopen
} = useCompose()

provide('entities', computed(() => schema.value?.entities ?? {}))
const sections = computed(() => (Array.isArray(schema.value?.sections) ? schema.value.sections : []))

// allowlists — spectrum × mode drive the canvas restyle,
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

// compact selection summary — the picking itself happens with Boris
const roleLabel = computed(() => ROLES[selections.value.role]?.label ?? '')
const topicsLabel = computed(() =>
  selections.value.topics.length ? selections.value.topics.join(', ') : 'Boris chooses'
)
const styleLabel = computed(
  () => STYLES.find((s) => s.id === selections.value.style)?.label ?? ''
)

// the echo: the composed page says back what the visitor stated — role and
// topics only, straight from their own selections; nothing invented
const echoLine = computed(() => {
  const role = ROLES[selections.value.role]?.label
  if (!role) return ''
  const topics = selections.value.topics
  return topics.length
    ? `For you — coming as ${role}, curious about ${topics.join(', ')}`
    : `For you — coming as ${role}, with Boris choosing what fits`
})

// loading → ready choreography: the opaque dark Theater used to unmount in
// one frame while panels faded in from zero — a hard flicker. Now it stays
// mounted with exiting/dim and dissolves over ~0.8s WHILE the panels
// assemble beneath it; unmount only after the fade finishes.
const theaterExiting = ref(false)
let exitTimer = 0
watch(state, (s, prev) => {
  if (s === 'ready' && prev === 'loading') {
    theaterExiting.value = true
    clearTimeout(exitTimer)
    exitTimer = setTimeout(() => (theaterExiting.value = false), 850)
  }
})
onBeforeUnmount(() => clearTimeout(exitTimer))
</script>

<template>
  <section class="zone zone-north scrollable" :style="{ '--bg': `url(${bg})` }">
    <div class="north-copy">
      <p class="eyebrow">AI CORNER</p>
      <h2 class="wing-title">Composed live, for you</h2>

      <!-- the ritual now lives in Boris: the zone keeps a compact summary -->
      <template v-if="state === 'idle'">
        <p class="cam-intro">
          Here the network composes a page only for you. Tell me who you are
          and where you are coming from, pick what you would like to see and
          how it should feel — one model then retrieves the most fitting
          pieces of the network and builds your page in the style you chose.
          That takes only a few seconds.
        </p>

        <div class="select-summary">
          <div class="summary-chips">
            <button
              type="button"
              class="sum-chip"
              :class="{ filled: !!roleLabel }"
              @click="reopen('role')"
            ><span class="sum-k">role</span><span class="sum-v">{{ roleLabel || '—' }}</span></button>
            <button
              type="button"
              class="sum-chip"
              :class="{ filled: !!selections.role }"
              @click="reopen('topics')"
            ><span class="sum-k">topics</span><span class="sum-v">{{ topicsLabel }}</span></button>
            <button
              type="button"
              class="sum-chip"
              :class="{ filled: !!selections.role }"
              @click="reopen('style')"
            ><span class="sum-k">style</span><span class="sum-v">{{ styleLabel }}</span></button>
          </div>
        </div>
      </template>

      <!-- the canvas: theater while composing, result when ready; it
           flex-grows to claim the rest of the zone -->
      <div class="canvas-frame">
        <div
          v-if="state === 'loading' || theaterExiting"
          class="corner-theater"
          :class="{ leaving: theaterExiting }"
        >
          <Theater
            :steps="theaterSteps"
            :cadence="1600"
            :active="state === 'loading'"
            :exiting="theaterExiting"
            :dim="0"
            :hues="hues"
          />
          <p class="theater-note">the corner listens — and composes what fits you</p>
        </div>

        <div v-if="state === 'error'" class="error-card">
          <p>The corner could not compose: {{ errorMsg }}</p>
          <button type="button" class="plaza-btn" @click="compose()">Try again</button>
        </div>

        <template v-if="state === 'ready'">
          <div class="graph-panel on">
            <NetworkGraph />
          </div>
          <div
            class="composed"
            :class="['spectrum-' + spectrum, 'mode-' + mode]"
            :style="{ '--accent': accentVar }"
          >
            <p v-if="echoLine" class="echo">{{ echoLine }}</p>
            <UiRenderer
              v-for="(node, i) in sections"
              :key="i"
              :node="node"
              class="panel"
              :class="{ on: i < revealed }"
            />
            <button type="button" class="link-btn" @click="restart()">
              …or start again — choose another role
            </button>
          </div>
        </template>
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
.eyebrow {
  font-size: 12px;
  letter-spacing: 0.34em;
  color: rgba(174, 244, 252, 0.75);
  margin: 0;
  text-shadow: 0 1px 8px rgba(8, 16, 20, 0.55);
}
.wing-title {
  font-weight: 300;
  font-size: clamp(24px, 3vw, 40px);
  color: #f1ede6;
  margin: 0 0 4px;
  text-shadow: 0 0 24px rgba(127, 227, 240, 0.35);
}

/* CAM's explanation of what happens here — a dark card surface so the
   light text never washes out over the photo, in the wisdom-corner card
   language but in this wing's night material */
.cam-intro {
  width: min(720px, 94%);
  margin: 0;
  background: rgba(10, 18, 22, 0.85);
  border: 1px solid rgba(127, 227, 240, 0.16);
  border-radius: 22px;
  padding: 28px 36px;
  color: rgba(241, 237, 230, 0.72);
  font-size: 14px;
  line-height: 1.65;
  letter-spacing: 0.02em;
  text-align: center;
  text-shadow: 0 1px 8px rgba(8, 16, 20, 0.55);
}

/* the compact selection summary — mono chips, one glance at the choices */
.select-summary {
  width: min(720px, 94%);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 14px;
}
.summary-chips {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 8px;
}
.sum-chip {
  display: inline-flex;
  align-items: center;
  gap: 9px;
  background: rgba(14, 26, 30, 0.55);
  border: 1px solid rgba(241, 237, 230, 0.16);
  border-radius: 7px;
  padding: 7px 12px;
  color: rgba(241, 237, 230, 0.48);
  font-family: var(--font-mono);
  font-size: 11px;
  letter-spacing: 0.06em;
  cursor: pointer;
  transition: border-color 0.35s var(--ease), color 0.35s var(--ease),
    background 0.35s var(--ease);
}
.sum-k {
  color: rgba(174, 244, 252, 0.5);
  font-size: 9.5px;
  letter-spacing: 0.2em;
  text-transform: uppercase;
}
.sum-chip:hover { border-color: rgba(127, 227, 240, 0.55); }
.sum-chip.filled {
  color: #f1ede6;
  border-color: rgba(127, 227, 240, 0.45);
  background: rgba(32, 58, 66, 0.5);
}

/* the canvas — flex-grows to claim the rest of the zone; its min-height
   stays stable across the loading→ready swap so nothing collapses */
.canvas-frame {
  position: relative;
  width: min(1080px, 96%);
  flex: 1;
  min-height: clamp(240px, 52vh, 640px);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 18px;
}

/* the Theater scoped into the wing (it ships as a fixed full-viewport stage) */
.corner-theater {
  position: relative;
  width: 100%;
  height: clamp(240px, 52vh, 640px);
}
/* while dissolving over the freshly composed panels the theater floats
   above them instead of holding its own row of layout space */
.corner-theater.leaving {
  position: absolute;
  inset: 0;
  z-index: 3;
  height: auto;
  pointer-events: none;
}
.corner-theater.leaving .theater-note { opacity: 0; }
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
  transition: opacity 0.6s var(--ease);
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
   selected style restyles this wing's canvas and nothing else.
   The sheet carries its own full-height night background so the composed
   content never renders light-on-light over the day plaza below the fold. */
.composed {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 16px;
  background-color: #0b0a09;
  background-image: var(--bg-tint, none);
  border: 1px solid rgba(241, 237, 230, 0.09);
  border-radius: 22px;
  padding: clamp(20px, 3vw, 32px);
  /* label tokens lifted for ≥4.5:1 contrast on the dark sheet */
  --subtle: #948c80;
}

/* the echo line — mono eyebrow restating the visitor's own inputs */
.echo {
  margin: 0;
  font-family: var(--font-mono);
  font-size: 11px;
  font-weight: 500;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--s-dimtext, rgba(241, 237, 230, 0.72));
}

.link-btn {
  align-self: center;
  margin-top: 6px;
  background: none;
  border: none;
  padding: 6px 10px;
  color: rgba(241, 237, 230, 0.68);
  font: inherit;
  font-size: 13px;
  letter-spacing: 0.06em;
  cursor: pointer;
  transition: color 0.35s var(--ease);
}
.link-btn:hover { color: rgba(174, 244, 252, 0.9); }

/* narrow viewports: keep the composed page readable and non-overlapping;
   the desktop layout above stays untouched */
@media (max-width: 900px) {
  .north-copy {
    padding-left: 5vw;
    padding-right: 5vw;
    /* safe area below the fixed compass widget */
    padding-bottom: 120px;
  }
  .canvas-frame { width: 100%; min-height: 0; gap: 14px; }
  .graph-panel {
    --graph-h: clamp(200px, 40vh, 420px);
    padding: 10px;
    border-radius: 22px 24px 22px 20px;
  }
  .composed { padding: 18px 14px; border-radius: 18px; }
}
@media (max-width: 600px) {
  .wing-title { font-size: 22px; }
  .cam-intro { font-size: 13px; }
  .sum-chip { font-size: 10px; padding: 6px 9px; }
}
</style>
