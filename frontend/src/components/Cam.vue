<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { usePlaza } from '../composables/usePlaza.js'

// CAM — the camera companion (spec §4): small rounded organic camera
// creature, lens = eye, antenna with warm light point. Fully procedural
// SVG so the lens can track the cursor continuously.
const props = defineProps({
  line: { type: String, default: '' },
  zone: { type: String, default: 'center' },
  prominent: { type: Boolean, default: false },
  rolling: { type: Boolean, default: false }
})

const { reduced } = usePlaza()

// lens follows the cursor with a curious lerp + slight body tilt
const pupilX = ref(0)
const pupilY = ref(0)
const tilt = ref(0)
let tx = 0
let ty = 0
let raf = 0

function onMove(e) {
  const nx = (e.clientX / window.innerWidth) * 2 - 1
  const ny = (e.clientY / window.innerHeight) * 2 - 1
  tx = nx * 7
  ty = ny * 6
}

function loop() {
  pupilX.value += (tx - pupilX.value) * 0.08
  pupilY.value += (ty - pupilY.value) * 0.08
  tilt.value += (tx * 0.7 - tilt.value) * 0.06
  raf = requestAnimationFrame(loop)
}

onMounted(() => {
  window.addEventListener('mousemove', onMove)
  raf = requestAnimationFrame(loop)
})
onBeforeUnmount(() => {
  window.removeEventListener('mousemove', onMove)
  cancelAnimationFrame(raf)
})

// poke curiosity: clicking CAM cycles a few atmospheric lines per zone
// (no program facts — CAM stays a companion, not a brochure)
const EXTRA = {
  center: [
    'Four paths, one plaza. Where shall we drift?',
    'I blink, therefore I am.',
    'The veins remember every visitor.'
  ],
  north: [
    'The night side composes; I just watch.',
    'Panels breathe while you wait — no spinners here.'
  ],
  south: ['Stories grow slower than pages.', 'Take the long way down sometime.'],
  west: ['Facts are the quietest light.', 'Clarity before atmosphere — always.'],
  east: ['Two doors, both warm.', 'Challenges and talent: same light, different angle.']
}
const poke = ref(null)
const pokeIdx = ref(-1)
const happy = ref(false)
let happyTimer = 0

function onPoke() {
  const pool = EXTRA[props.zone] ?? []
  if (!pool.length) return
  pokeIdx.value = (pokeIdx.value + 1) % pool.length
  poke.value = pool[pokeIdx.value]
  happy.value = true
  clearTimeout(happyTimer)
  happyTimer = setTimeout(() => (happy.value = false), 700)
}
watch([() => props.line, () => props.zone], () => {
  poke.value = null
  pokeIdx.value = -1
})

const activeLine = computed(() => poke.value ?? props.line)

// typewriter voice: CAM writes his lines, antenna pulses while talking
const shown = ref('')
const talking = ref(false)
let typeTimer = 0
let talkTimer = 0
watch(
  activeLine,
  (v) => {
    clearInterval(typeTimer)
    clearTimeout(talkTimer)
    if (!v) {
      shown.value = ''
      talking.value = false
      return
    }
    talking.value = true
    if (reduced.value) {
      shown.value = v
      talkTimer = setTimeout(() => (talking.value = false), 1600)
      return
    }
    shown.value = ''
    let i = 0
    typeTimer = setInterval(() => {
      i += 1
      shown.value = v.slice(0, i)
      if (i >= v.length) {
        clearInterval(typeTimer)
        talkTimer = setTimeout(() => (talking.value = false), 1600)
      }
    }, 18)
  },
  { immediate: true }
)
onBeforeUnmount(() => {
  clearInterval(typeTimer)
  clearTimeout(talkTimer)
  clearTimeout(happyTimer)
})

// small pop whenever a new line starts
const popKey = ref(0)
watch(activeLine, (v) => {
  if (v) popKey.value++
})
</script>

<template>
  <div class="cam" :class="{ prominent, rolling }" @click="onPoke" title="poke CAM">
    <div v-if="shown" class="cam-bubble" :class="{ talking }">
      {{ shown }}<span v-if="talking && !reduced" class="caret"></span>
    </div>
    <div class="cam-pop" :key="popKey" :class="{ happy }">
      <svg class="cam-body" :class="{ still: reduced }" viewBox="0 0 160 150" aria-label="CAM, your plaza companion">
        <defs>
          <linearGradient id="cam-shell" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stop-color="#f1e9d8" />
            <stop offset="70%" stop-color="#e3d7c0" />
            <stop offset="100%" stop-color="#d3c5aa" />
          </linearGradient>
          <radialGradient id="cam-glass" cx="38%" cy="35%" r="80%">
            <stop offset="0%" stop-color="#2e6d78" />
            <stop offset="55%" stop-color="#173a41" />
            <stop offset="100%" stop-color="#0c2126" />
          </radialGradient>
        </defs>
        <ellipse class="ground" cx="80" cy="143" rx="46" ry="6" />
        <g class="rig" :style="{ transform: `rotate(${tilt}deg)` }">
          <!-- antenna -->
          <path d="M80 42 C80 30 86 26 86 18" class="ant" />
          <circle cx="86" cy="14" r="5" class="tip" :class="{ talking }" />
          <!-- ears -->
          <rect x="16" y="72" width="12" height="26" rx="6" class="shell-dim" />
          <rect x="132" y="72" width="12" height="26" rx="6" class="shell-dim" />
          <!-- body -->
          <rect x="26" y="40" width="108" height="86" rx="40" fill="url(#cam-shell)" class="shell" />
          <!-- lens housing + glass -->
          <circle cx="80" cy="83" r="32" class="housing" />
          <circle cx="80" cy="83" r="24" class="ring" />
          <circle cx="80" cy="83" r="18" fill="url(#cam-glass)" />
          <!-- pupil tracks the cursor -->
          <g :transform="`translate(${pupilX} ${pupilY})`">
            <circle cx="80" cy="83" r="8" class="pupil" />
            <circle cx="77" cy="80" r="2.6" class="glint" />
          </g>
          <!-- eyelid blink -->
          <circle cx="80" cy="83" r="18.6" class="lid" />
          <!-- wheels -->
          <circle cx="56" cy="130" r="7" class="wheel" :class="{ rolling }" />
          <circle cx="104" cy="130" r="7" class="wheel" :class="{ rolling }" />
        </g>
      </svg>
    </div>
  </div>
</template>

<style scoped>
.cam {
  position: fixed;
  right: 26px;
  bottom: 20px;
  width: 118px;
  z-index: 45;
  transition: transform 0.9s cubic-bezier(0.22, 1, 0.36, 1);
  transform-origin: bottom right;
  cursor: pointer;
}
.cam.prominent { transform: scale(1.32) translate(-10px, -10px); }
.cam.rolling { animation: cam-roll 1.6s cubic-bezier(0.22, 1, 0.36, 1) both; }
@keyframes cam-roll {
  from { transform: translateX(45vw); }
  to { transform: translateX(0); }
}

.cam-bubble {
  position: absolute;
  bottom: calc(100% + 10px);
  right: 8px;
  width: 230px;
  padding: 12px 16px;
  background: rgba(248, 244, 236, 0.93);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 251, 240, 0.7);
  border-radius: 26px 22px 6px 24px;
  color: #2b2622;
  font-size: 13.5px;
  line-height: 1.45;
  box-shadow: 0 10px 30px rgba(20, 30, 35, 0.2);
  animation: bubble-in 0.5s cubic-bezier(0.22, 1, 0.36, 1);
}
.cam-bubble.talking { animation: bubble-in 0.5s cubic-bezier(0.22, 1, 0.36, 1), bubble-talk 1.1s ease-in-out infinite; }
@keyframes bubble-in {
  from { opacity: 0; transform: translateY(8px) scale(0.92); }
}
@keyframes bubble-talk {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.015); }
}
.caret {
  display: inline-block;
  width: 2px;
  height: 0.9em;
  margin-left: 2px;
  vertical-align: text-bottom;
  background: #2b8fa3;
  animation: caret-blink 0.8s steps(1) infinite;
}
@keyframes caret-blink {
  50% { opacity: 0; }
}

.cam-pop { transform-origin: bottom right; }
.cam-pop.happy { animation: cam-happy 0.65s cubic-bezier(0.3, 0.8, 0.4, 1); }
@keyframes cam-happy {
  0% { transform: scale(1); }
  30% { transform: scale(1.06, 0.94) translateY(2px); }
  60% { transform: scale(0.97, 1.05) translateY(-5px); }
  100% { transform: scale(1); }
}

.cam-body { width: 100%; display: block; overflow: visible; animation: cam-bob 5.5s ease-in-out infinite; }
.cam-body.still { animation: none; }
@keyframes cam-bob {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-3px); }
}
.rig {
  transform-box: view-box;
  transform-origin: 80px 90px;
  transition: transform 0.2s ease-out;
}
.ground { fill: rgba(40, 35, 28, 0.22); }
.shell { stroke: rgba(105, 90, 70, 0.55); stroke-width: 1.5; }
.shell-dim { fill: #cbbda2; }
.housing { fill: #241f1b; }
.ring { fill: #3a332c; }
.pupil { fill: #05080a; }
.glint { fill: #d9fbff; opacity: 0.9; }
.ant { fill: none; stroke: #a3967f; stroke-width: 3; stroke-linecap: round; }
.tip { fill: #f2b361; }
.tip.talking { animation: tip-pulse 0.7s ease-in-out infinite; }
@keyframes tip-pulse {
  0%, 100% { opacity: 0.55; }
  50% { opacity: 1; filter: drop-shadow(0 0 6px #f2b361); }
}
.lid {
  fill: #241f1b;
  transform: scaleY(0);
  transform-origin: 80px 83px;
  transform-box: view-box;
  animation: blink 4.6s infinite;
}
@keyframes blink {
  0%, 91%, 97%, 100% { transform: scaleY(0); }
  94% { transform: scaleY(1); }
}
.wheel { fill: #2b2622; }
.wheel.rolling { animation: wheel-spin 0.5s linear infinite; }
@keyframes wheel-spin {
  to { transform: rotate(360deg); }
}
</style>
