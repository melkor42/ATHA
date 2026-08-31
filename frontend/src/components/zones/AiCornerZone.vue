<script setup>
import { computed, onBeforeUnmount, provide, ref, watch } from 'vue'
import UiRenderer from '../UiRenderer.vue'
import Theater from '../Theater.vue'
import { useCompose, ROLES, STYLES, INTENTS, FACETS } from '../../composables/useCompose.js'
import { ACCENT_HUES, DEFAULT_HUES } from '../../theme.js'
import bg from '../../assets/plaza/north.jpg'

// S3 North — AI Corner (spec §3): the plaza's composed-live zone. Everything
// here is composed live from the existing backend. The ritual is a short
// interview — role, intent, facet, free text, style — asked sequentially by
// Boris himself (useCompose step machine); the zone shows a compact summary of
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
const intentLabel = computed(() => {
  const id = selections.value.intent
  if (!id) return 'Looking around'
  return (INTENTS[selections.value.role] ?? []).find((o) => o.id === id)?.label ?? '—'
})
const facetLabel = computed(() => {
  const id = selections.value.facet
  if (!id) return 'Open mix'
  return (FACETS[selections.value.role] ?? []).find((o) => o.id === id)?.label ?? '—'
})
const freeTextLabel = computed(() => selections.value.freeText ?? '')
const styleLabel = computed(
  () => STYLES.find((s) => s.id === selections.value.style)?.label ?? ''
)

// the echo: the composed page says back what the visitor stated — their role,
// straight from their own selection; nothing invented
const echoLine = computed(() => {
  const role = ROLES[selections.value.role]?.label
  return role ? `For you — ${role}` : ''
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
              @click="reopen('intent')"
            ><span class="sum-k">intent</span><span class="sum-v">{{ intentLabel }}</span></button>
            <button
              type="button"
              class="sum-chip"
              :class="{ filled: !!selections.role }"
              @click="reopen('facet')"
            ><span class="sum-k">facet</span><span class="sum-v">{{ facetLabel }}</span></button>
            <button
              v-if="freeTextLabel"
              type="button"
              class="sum-chip filled"
              @click="reopen('freetext')"
            ><span class="sum-k">asked</span><span class="sum-v">{{ freeTextLabel }}</span></button>
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
  scrollbar-color: rgba(107, 128, 76, 0.4) transparent;
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
  color: rgba(76, 90, 62, 0.78);
  margin: 0;
}
.wing-title {
  font-weight: 300;
  font-size: clamp(24px, 3vw, 40px);
  color: #241f1b;
  margin: 0 0 4px;
  text-shadow: 0 1px 0 rgba(255, 251, 240, 0.6);
}

/* CAM's explanation of what happens here — frosted paper like the rest
   of the plaza's day material, dark ink over the photo */
.cam-intro {
  width: min(720px, 94%);
  margin: 0;
  background: rgba(250, 247, 240, 0.78);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(120, 105, 85, 0.35);
  border-radius: 22px;
  padding: 28px 36px;
  color: rgba(43, 38, 34, 0.8);
  font-size: 14px;
  line-height: 1.65;
  letter-spacing: 0.02em;
  text-align: center;
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
  background: rgba(250, 247, 240, 0.66);
  border: 1px solid rgba(120, 105, 85, 0.3);
  border-radius: 9px;
  padding: 8px 14px;
  color: rgba(43, 38, 34, 0.72);
  font-family: var(--font-ui);
  font-size: 13px;
  letter-spacing: 0.01em;
  cursor: pointer;
  transition: border-color 0.35s var(--ease), color 0.35s var(--ease),
    background 0.35s var(--ease);
}
.sum-k {
  color: rgba(76, 90, 62, 0.75);
  font-size: 10px;
  font-weight: 600;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}
.sum-chip:hover { border-color: rgba(107, 128, 76, 0.55); }
.sum-chip.filled {
  color: #2b2622;
  border-color: rgba(107, 128, 76, 0.5);
  background: rgba(244, 236, 214, 0.9);
}

/* the canvas — flex-grows to claim the rest of the zone; its min-height
   stays stable across the loading→ready swap so nothing collapses */
.canvas-frame {
  position: relative;
  width: min(1240px, 97%);
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
  background: rgba(250, 247, 240, 0.85);
  border: 1px solid rgba(180, 90, 60, 0.4);
  border-radius: 28px 32px 30px 26px;
  padding: 22px 26px;
  color: #2b2622;
  display: flex;
  flex-direction: column;
  gap: 12px;
  align-items: flex-start;
}

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
.panel.on {
  opacity: 1;
  transform: none;
  filter: blur(0);
}

/* the composed canvas: spectrum × mode own the card styling now — the
   selected style restyles this wing's canvas and nothing else.
   The sheet ground (paper vs. night) is decided in style.css — light
   modes read warm paper, retro/steampunk keep their dark material. */
.composed {
  width: 100%;
  display: grid;
  grid-template-columns: 1fr 1fr;
  align-items: start;
  gap: 16px;
  background-image: var(--bg-tint, none);
  border: 1px solid rgba(241, 237, 230, 0.09);
  border-radius: 22px;
  padding: clamp(20px, 3vw, 32px);
}

/* echo and restart span the full sheet width */
.composed .echo,
.composed .link-btn { grid-column: 1 / -1; }
.composed .link-btn { justify-self: center; }

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
  /* token colors: readable on the paper sheet AND the night sheet
     (retro/steampunk), since both tokens flip with the ground */
  color: var(--muted);
  font: inherit;
  font-size: 13px;
  letter-spacing: 0.06em;
  cursor: pointer;
  transition: color 0.35s var(--ease);
}
.link-btn:hover { color: var(--text); }

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
  .composed { padding: 18px 14px; border-radius: 18px; grid-template-columns: 1fr; }
}
@media (max-width: 600px) {
  .wing-title { font-size: 22px; }
  .cam-intro { font-size: 13px; }
  .sum-chip { font-size: 12px; padding: 7px 11px; }
}
</style>
