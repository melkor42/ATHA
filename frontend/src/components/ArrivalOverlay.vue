<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { SESSION_KEYS } from '../config.js'
import { usePlaza } from '../composables/usePlaza.js'

// S0 Arrival (spec §3): mist clears, veins ignite radially from the center,
// CAM rolls in. Once per session, ~2s, skippable. No terminal, no boot lines.
const emit = defineEmits(['done'])
const { reduced } = usePlaza()
const leaving = ref(false)
let timer = 0

function finish() {
  if (leaving.value) return
  leaving.value = true
  try { sessionStorage.setItem(SESSION_KEYS.arrival, '1') } catch { /* private mode */ }
  setTimeout(() => emit('done'), reduced.value ? 0 : 650)
}

onMounted(() => {
  if (reduced.value) {
    finish()
    return
  }
  timer = setTimeout(finish, 2200)
})
onBeforeUnmount(() => clearTimeout(timer))
</script>

<template>
  <div class="arrival" :class="{ leaving }">
    <div class="mist m1"></div>
    <div class="mist m2"></div>
    <svg class="ignite" viewBox="0 0 200 200" aria-hidden="true">
      <g v-for="a in [0, 45, 90, 135, 180, 225, 270, 315]" :key="a" :transform="`rotate(${a} 100 100)`">
        <path d="M100 100 C116 88 134 92 138 100 C134 108 116 112 100 100" class="spark" :class="a % 90 === 0 ? 'cyan' : 'amber'" />
      </g>
    </svg>
    <button type="button" class="skip" @click="finish">skip</button>
  </div>
</template>

<style scoped>
.arrival {
  position: fixed;
  inset: 0;
  z-index: 60;
  background: linear-gradient(180deg, rgba(38, 84, 92, 0.55), rgba(240, 234, 222, 0.9));
  transition: opacity 0.65s ease;
  overflow: hidden;
}
.arrival.leaving { opacity: 0; pointer-events: none; }
.mist {
  position: absolute;
  inset: -20%;
  background:
    radial-gradient(42% 34% at 30% 60%, rgba(248, 244, 236, 0.95), transparent 70%),
    radial-gradient(50% 40% at 70% 45%, rgba(233, 240, 238, 0.9), transparent 70%);
  filter: blur(30px);
  animation: mist-clear 2.1s ease-out forwards;
}
.mist.m2 { animation-delay: 0.25s; transform: scale(1.2); }
@keyframes mist-clear {
  to { opacity: 0; transform: scale(1.35); }
}
.ignite {
  position: absolute;
  left: 50%;
  top: 50%;
  width: min(58vmin, 520px);
  transform: translate(-50%, -50%);
  mix-blend-mode: screen;
}
.spark {
  fill: none;
  stroke-width: 2.4;
  stroke-linecap: round;
  stroke-dasharray: 120;
  stroke-dashoffset: 120;
  animation: spark-draw 1.5s cubic-bezier(0.3, 0.8, 0.4, 1) forwards;
}
.spark.cyan { stroke: #7fe3f0; }
.spark.amber { stroke: #f2b361; }
@keyframes spark-draw {
  60% { opacity: 1; }
  to { stroke-dashoffset: 0; opacity: 0.85; }
}
.skip {
  position: absolute;
  top: 18px;
  right: 20px;
  border: none;
  background: rgba(248, 244, 236, 0.6);
  backdrop-filter: blur(8px);
  color: #4c443c;
  font-size: 12px;
  letter-spacing: 0.08em;
  padding: 8px 16px;
  border-radius: 999px;
  cursor: pointer;
}
</style>
