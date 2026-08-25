<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { usePlaza, ZONE_POS } from '../composables/usePlaza.js'
import { useGate, Q1, Q2 } from '../composables/useGate.js'
import { useCompose, COMPOSING_LINE } from '../composables/useCompose.js'
import { SESSION_KEYS } from '../config.js'
import VeinsOverlay from './VeinsOverlay.vue'
import Compass from './Compass.vue'
import Companion from './Companion.vue'
import ArrivalOverlay from './ArrivalOverlay.vue'
import CenterZone from './zones/CenterZone.vue'
import StoryGateZone from './zones/StoryGateZone.vue'
import AiCornerZone from './zones/AiCornerZone.vue'
import InfosZone from './zones/InfosZone.vue'
import RegisterZone from './zones/RegisterZone.vue'

// The Town Square shell (spec §2): one place, five zones, a soft camera.
// Wheel/touch/keys/veins/compass all resolve to goTo(); from a wing, any
// direction first steps back onto the center — spatially honest.
const { current, traveling, reduced, travelMs, goTo, setPulse, setTravelMs, veil, setVeil, borisOpacity, setBorisOpacity, haloOpacity, setHaloOpacity, haloSize, setHaloSize, signpostPulse, setSignpostPulse, note } = usePlaza()
const { step, seen, route, visibleQ1, start, answer1, answer2, finish } = useGate()
const {
  state: composeState,
  step: composeStep,
  interviewActive,
  interviewLine,
  interviewOptions,
  beginInterview,
  answer: composeAnswer,
  pickup,
  clearPickup
} = useCompose()

const arrived = ref(
  typeof sessionStorage !== 'undefined' &&
    sessionStorage.getItem(SESSION_KEYS.arrival) === '1'
)

// owner mode: the travel/veil tune sliders are debug controls, not visitor
// surface — read once from the URL (?tune), hidden by default
const tuneMode = new URLSearchParams(window.location.search).has('tune')

// Boris context lines, one sentence per zone (spec §4)
const LINES = {
  center: 'Welcome to the plaza. Four paths, four intentions — I walk with you.',
  north: 'The AI Corner: everything here is composed live, for you.',
  west: 'The quiet wing — seven directions on how Atha works, and what makes a decision good.',
  east: 'Where you join: bring a challenge, or bring your talent.',
  south: 'The story of Atha grows as you walk down.'
}
// Boris asks the gate questions himself, in any zone (spec §4)
const companionLine = computed(() => {
  if (!arrived.value) return ''
  if (note.value) return note.value
  // the compose pin: Boris holds the composing line until it is ready
  // (the interview is inactive while loading, so this keeps winning here)
  if (composeState.value === 'loading') return COMPOSING_LINE
  // the compose interview: at the AI Corner with compose idle, the
  // role/topics/style questions win over unanswered gate intro questions
  if (composeInterviewActive.value) return interviewLine.value
  if (step.value === 'q1') return Q1.question
  if (step.value === 'q2') return Q2.question
  if (step.value === 'closing' && route.value) {
    return `Your way into Atha begins here. The ${route.value.zone} path is lit for you.`
  }
  if (composeState.value === 'ready' && pickup.value && current.value !== 'north') {
    return 'Your compose is finished — shall I bring you to the AI Corner to show you the result?'
  }
  return LINES[current.value]
})
const composeInterviewActive = computed(
  () =>
    current.value === 'north' &&
    composeState.value === 'idle' &&
    interviewActive.value
)
const companionProminent = computed(
  () => ['q1', 'q2', 'closing'].includes(step.value) || composeInterviewActive.value
)
const gateOptions = computed(() => {
  // the compose interview's options win over the gate questions at north
  if (composeInterviewActive.value) return interviewOptions.value
  if (step.value === 'q1') return visibleQ1.value
  if (step.value === 'q2') return Q2.options
  // the pickup question waits until the travel note has cleared — mirroring
  // companionLine's note priority, so options never surface before the line
  if (note.value) return []
  if (composeState.value === 'ready' && pickup.value && current.value !== 'north') {
    return [
      { id: 'pickup-go', label: 'Yes — show me the result', action: true },
      { id: 'pickup-stay', label: 'Not yet' }
    ]
  }
  return []
})
function onAnswer1(id) {
  answer1(id)
}
// answering Q2: Boris names the lit path, then walks you there once said
let pendingRoute = null
function onAnswer2(id) {
  answer2(id)
  pendingRoute = route.value?.zone ?? null
}
function onCompanionSaid() {
  if (step.value === 'closing' && pendingRoute) {
    const target = pendingRoute
    pendingRoute = null
    finish()
    goTo(target)
  }
}

// answers reach the gate or the compose interview, depending on who asked
function onCompanionAnswer(id) {
  if (id === 'pickup-go') {
    // mid-travel clicks would clear the notice and no-op goTo() — ignore
    // them until the camera arrives so the offer stays answerable
    if (traveling.value) return
    clearPickup()
    goTo('north')
    return
  }
  if (id === 'pickup-stay') {
    clearPickup()
    return
  }
  // interview answers first — role ids must never fall through into
  // answer1() (they would be written to the athaVisitorState session key)
  if (composeInterviewActive.value) {
    composeAnswer(id)
    return
  }
  if (step.value === 'q1') {
    answer1(id)
    return
  }
  onAnswer2(id)
}

// the compose interview is lazy: it starts on the visitor's first north
// arrival of the session and pauses/resumes purely through line priority
watch([current, arrived], ([zone, here]) => {
  if (zone === 'north' && here) {
    beginInterview()
    clearPickup()
  }
}, { immediate: true })

// first arrival: once the welcome overlay closes, Boris starts asking
watch(
  arrived,
  (v) => {
    if (v && !seen.value && step.value === 'idle') start()
  },
  { immediate: true }
)

// the closing pulse: Boris's recommendation lights the matching vein (spec §4)
watch(step, (s) => {
  if (s === 'closing' && route.value) setPulse(route.value.zone)
})

// the plaza's travel camera: shifts the world so the current zone fills the view
const worldShift = computed(() => {
  const p = ZONE_POS[current.value]
  return `translate3d(${-p.x * 100}vw, ${-p.y * 100}vh, 0)`
})

function navTarget(dir) {
  return current.value === 'center' ? dir : 'center'
}

function onWheel(e) {
  if (!arrived.value || traveling.value) return
  const sc = e.target.closest('.scrollable')
  if (sc) {
    const atTop = sc.scrollTop <= 0
    const atBottom = sc.scrollTop + sc.clientHeight >= sc.scrollHeight - 1
    // inside a scrollable wing, native scroll wins until the boundary
    if (!(e.deltaY < 0 && atTop) && !(e.deltaY > 0 && atBottom)) return
  }
  const dir =
    Math.abs(e.deltaY) >= Math.abs(e.deltaX)
      ? e.deltaY > 0
        ? 'south'
        : 'north'
      : e.deltaX > 0
        ? 'east'
        : 'west'
  goTo(navTarget(dir))
}

function onKey(e) {
  if (!arrived.value || e.target.matches('input, textarea')) return
  const map = { ArrowUp: 'north', ArrowDown: 'south', ArrowLeft: 'west', ArrowRight: 'east' }
  const dir = map[e.key]
  if (!dir) return
  e.preventDefault()
  goTo(navTarget(dir))
}

// touch-pan in four directions (spec §8 mobile)
let touch = null
function onTouchStart(e) {
  touch = { x: e.touches[0].clientX, y: e.touches[0].clientY }
}
function onTouchEnd(e) {
  if (!touch || !arrived.value) return
  const from = touch
  touch = null
  if (e.target.closest('.scrollable')) return
  const dx = e.changedTouches[0].clientX - from.x
  const dy = e.changedTouches[0].clientY - from.y
  if (Math.max(Math.abs(dx), Math.abs(dy)) < 60) return
  const dir =
    Math.abs(dy) >= Math.abs(dx)
      ? dy > 0
        ? 'north'
        : 'south'
      : dx > 0
        ? 'west'
        : 'east'
  goTo(navTarget(dir))
}

onMounted(() => window.addEventListener('keydown', onKey))
onBeforeUnmount(() => window.removeEventListener('keydown', onKey))
</script>

<template>
  <div
    class="plaza"
    :class="{ reduced, arriving: !arrived }"
    :style="{ '--veil-strength': veil / 100, '--boris-alpha': borisOpacity / 100, '--halo-alpha': haloOpacity / 100, '--halo-size': haloSize, '--signpost-pulse': signpostPulse / 100 }"
    @wheel.passive="onWheel"
    @touchstart.passive="onTouchStart"
    @touchend.passive="onTouchEnd"
  >
    <div class="plaza-world" :style="{ transform: worldShift, transitionDuration: travelMs + 'ms' }">
      <div
        class="plaza-zoom"
        :class="{ dip: traveling && !reduced }"
        :style="{ animationDuration: travelMs + 'ms' }"
      >
        <div class="tile" :style="{ '--tx': 0, '--ty': 1 }"><InfosZone /></div>
        <div class="tile" :style="{ '--tx': 1, '--ty': 0 }"><AiCornerZone /></div>
        <div class="tile" :style="{ '--tx': 1, '--ty': 1 }"><CenterZone /></div>
        <div class="tile" :style="{ '--tx': 2, '--ty': 1 }"><RegisterZone /></div>
        <div class="tile" :style="{ '--tx': 1, '--ty': 2 }"><StoryGateZone /></div>
        <VeinsOverlay />
      </div>
    </div>

    <div v-if="tuneMode" class="pill-bar">
      <label class="travel-pill">
        <span>travel · {{ travelMs }}ms</span>
        <input
          type="range"
          min="100"
          max="1300"
          step="25"
          :value="travelMs"
          @input="setTravelMs(Number($event.target.value))"
        />
      </label>
      <label class="travel-pill veil-pill">
        <span>veil · {{ veil }}%</span>
        <input
          type="range"
          min="0"
          max="100"
          step="1"
          :value="veil"
          @input="setVeil(Number($event.target.value))"
        />
      </label>
      <label class="travel-pill boris-pill">
        <span>boris bubble · {{ borisOpacity }}%</span>
        <input
          type="range"
          min="0"
          max="100"
          step="1"
          :value="borisOpacity"
          @input="setBorisOpacity(Number($event.target.value))"
        />
      </label>
      <label class="travel-pill halo-pill">
        <span>center halo · {{ haloOpacity }}%</span>
        <input
          type="range"
          min="0"
          max="100"
          step="1"
          :value="haloOpacity"
          @input="setHaloOpacity(Number($event.target.value))"
        />
      </label>
      <label class="travel-pill halo-size-pill">
        <span>halo size · {{ haloSize }}</span>
        <input
          type="range"
          min="20"
          max="80"
          step="1"
          :value="haloSize"
          @input="setHaloSize(Number($event.target.value))"
        />
      </label>
      <label class="travel-pill pulse-pill">
        <span>signpost pulse · {{ signpostPulse }}%</span>
        <input
          type="range"
          min="0"
          max="100"
          step="1"
          :value="signpostPulse"
          @input="setSignpostPulse(Number($event.target.value))"
        />
      </label>
    </div>

    <Compass />
    <Companion
      name="Boris"
      :line="companionLine"
      :zone="current"
      :prominent="companionProminent"
      :locked="composeState === 'loading'"
      :rolling="!arrived"
      :options="gateOptions"
      @answer="onCompanionAnswer"
      @said="onCompanionSaid"
    />
    <ArrivalOverlay v-if="!arrived" @done="arrived = true" />
  </div>
</template>

<style scoped>
.plaza {
  position: fixed;
  inset: 0;
  overflow: hidden;
  background: #e9e2d4;
  transition: background-color 1.6s ease;
}
/* arrival (delta §1): the square sits in the same void as the overlay,
   then brightens into daylight as the veil lifts — no black/white cut */
.plaza.arriving { background: #0d0b09; }
.plaza.reduced { transition: none; }
.plaza-world {
  position: absolute;
  width: 300vw;
  height: 300vh;
  transition-property: transform;
  transition-timing-function: cubic-bezier(0.22, 1, 0.36, 1);
  will-change: transform;
}
.plaza-zoom {
  position: absolute;
  inset: 0;
}
/* fly-in (delta §1): while the arrival veil speaks, the square sits
   scaled up and dimmed; on reveal it settles down to full presence */
.plaza.arriving .plaza-zoom {
  transform: scale(1.07);
  opacity: 0.32;
}
.plaza-zoom {
  transition: transform 1.5s cubic-bezier(0.22, 1, 0.36, 1), opacity 1.3s ease;
}
.plaza.reduced .plaza-zoom { transition: none; }
/* the veil now lives inside each tile's own background (.zone's top
   background-image layer in style.css): it washes the artwork only,
   never the content — paint order per tile: photo < veil < content
   (.zone > * z2); veins z1 ride above the tiles, chrome stays
   outside the world entirely. */
/* travel camera dip (zoom breath while moving between zones) */
.plaza-zoom.dip {
  animation: travel-dip both;
  animation-timing-function: cubic-bezier(0.3, 0.8, 0.4, 1);
}
@keyframes travel-dip {
  0% { transform: scale(1); }
  45% { transform: scale(1.045); }
  100% { transform: scale(1); }
}
.tile {
  position: absolute;
  width: 100vw;
  height: 100vh;
  left: calc(var(--tx) * 100vw);
  top: calc(var(--ty) * 100vh);
}

/* one fixed flex row owns the top-right slot: pills flow inside it,
   so the gap (12px) holds at any label width — overlap is impossible.
   Top-right keeps the owner tools clear of centered zone headings. */
.pill-bar {
  position: fixed;
  top: 18px;
  right: 20px;
  z-index: 40;
  display: flex;
  align-items: center;
  gap: 12px;
}
.travel-pill {
  z-index: 40;
  border: 1px solid rgba(255, 251, 240, 0.7);
  background: rgba(244, 239, 231, 0.6);
  backdrop-filter: blur(10px);
  color: #3c352e;
  font: inherit;
  font-size: 12.5px;
  letter-spacing: 0.14em;
  padding: 9px 18px;
  border-radius: 999px;
  cursor: pointer;
  box-shadow: 0 8px 24px rgba(20, 30, 35, 0.16);
  transition: background 0.35s, transform 0.35s;
}
.travel-pill {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 14px;
  cursor: default;
  font-size: 11px;
  letter-spacing: 0.08em;
  opacity: 0.85;
}
.travel-pill span {
  font-family: ui-monospace, 'Cascadia Mono', Menlo, Consolas, monospace;
  font-size: 10.5px;
  letter-spacing: 0.06em;
  white-space: nowrap;
}
.travel-pill input[type='range'] {
  width: 96px;
  height: 14px;
  accent-color: #3c352e;
  cursor: pointer;
}
</style>
