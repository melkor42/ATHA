<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { usePlaza, ZONE_POS } from '../composables/usePlaza.js'
import { useGate, Q1, Q2 } from '../composables/useGate.js'
import { SESSION_KEYS } from '../config.js'
import VeinsOverlay from './VeinsOverlay.vue'
import Compass from './Compass.vue'
import Cam from './Cam.vue'
import ArrivalOverlay from './ArrivalOverlay.vue'
import CenterZone from './zones/CenterZone.vue'
import StoryGateZone from './zones/StoryGateZone.vue'
import AiCornerZone from './zones/AiCornerZone.vue'
import InfosZone from './zones/InfosZone.vue'
import RegisterZone from './zones/RegisterZone.vue'
import WisdomCornerZone from './zones/WisdomCornerZone.vue'

// The Town Square shell (spec §2): one place, six zones, a soft camera.
// Wheel/touch/keys/veins/compass all resolve to goTo(); from a wing, any
// direction first steps back onto the center — spatially honest.
const { current, traveling, reduced, travelMs, goTo, setPulse, setTravelMs, note } = usePlaza()
const { step, seen, route, visibleQ1, start, answer1, answer2, finish } = useGate()

const arrived = ref(
  typeof sessionStorage !== 'undefined' &&
    sessionStorage.getItem(SESSION_KEYS.arrival) === '1'
)

// CAM context lines, one sentence per zone (spec §4)
const LINES = {
  center: 'Welcome to the plaza. Four paths, four intentions — I walk with you.',
  north: 'The night side of the plaza: everything here is composed live, for you.',
  west: 'The quiet wing. Facts, bright and clear — no decoration.',
  east: 'Where you join: bring a challenge, or bring your talent.',
  south: 'The story of Atha grows as you walk down.',
  wisdom: 'The still corner: how Atha works, and what makes a decision good.'
}
// CAM asks the gate questions himself, in any zone (spec §4)
const camLine = computed(() => {
  if (!arrived.value) return ''
  if (note.value) return note.value
  if (step.value === 'q1') return Q1.question
  if (step.value === 'q2') return Q2.question
  if (step.value === 'closing' && route.value) {
    return `Your way into Atha begins here. The ${route.value.zone} path is lit for you.`
  }
  return LINES[current.value]
})
const camProminent = computed(() => ['q1', 'q2', 'closing'].includes(step.value))
const gateOptions = computed(() => {
  if (step.value === 'q1') return visibleQ1.value
  if (step.value === 'q2') return Q2.options
  return []
})
function onAnswer1(id) {
  answer1(id)
}
// answering Q2: CAM names the lit path, then walks you there once said
let pendingRoute = null
function onAnswer2(id) {
  answer2(id)
  pendingRoute = route.value?.zone ?? null
}
function onCamSaid() {
  if (step.value === 'closing' && pendingRoute) {
    const target = pendingRoute
    pendingRoute = null
    finish()
    goTo(target)
  }
}

// first arrival: once the welcome overlay closes, CAM starts asking
watch(
  arrived,
  (v) => {
    if (v && !seen.value && step.value === 'idle') start()
  },
  { immediate: true }
)

// the closing pulse: CAM's recommendation lights the matching vein (spec §4)
watch(step, (s) => {
  if (s === 'closing' && route.value) setPulse(route.value.zone)
})

const cam = computed(() => {
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
    @wheel.passive="onWheel"
    @touchstart.passive="onTouchStart"
    @touchend.passive="onTouchEnd"
  >
    <div class="plaza-world" :style="{ transform: cam, transitionDuration: travelMs + 'ms' }">
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
        <div class="tile" :style="{ '--tx': 2, '--ty': 2 }"><WisdomCornerZone /></div>
        <VeinsOverlay />
      </div>
    </div>

    <button type="button" class="essentials-pill" @click="goTo('west')">Essentials</button>
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

    <Compass />
    <Cam
      :line="camLine"
      :zone="current"
      :prominent="camProminent"
      :rolling="!arrived"
      :options="gateOptions"
      @answer="step === 'q1' ? onAnswer1($event) : onAnswer2($event)"
      @said="onCamSaid"
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
.plaza-zoom.dip {
  animation: cam-dip both;
  animation-timing-function: cubic-bezier(0.3, 0.8, 0.4, 1);
}
@keyframes cam-dip {
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

.essentials-pill,
.travel-pill {
  position: fixed;
  top: 18px;
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
.essentials-pill { left: 20px; }
.travel-pill {
  left: 138px;
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
.essentials-pill:hover { background: rgba(250, 247, 240, 0.85); transform: translateY(-1px); }
</style>
