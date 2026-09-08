<script setup>
import { onMounted, onUnmounted, ref } from 'vue'
import DotField from './DotField.vue'
import { SLOGANS, ARRIVAL_KEY } from '../slogans.js'
import { arrived } from '../composables/useArrival.js'

const STEP = 2400
const HOLD = 3200
const OUT = 420
const index = ref(0)
let timer = 0

function span(i) {
  return i === SLOGANS.length - 1 ? HOLD : STEP
}

function finish() {
  try {
    sessionStorage.setItem(ARRIVAL_KEY, '1')
  } catch (e) {
    /* storage unavailable */
  }
  arrived.value = true
}

function advance() {
  if (index.value >= SLOGANS.length - 1) {
    finish()
    return
  }
  index.value += 1
  timer = setTimeout(advance, span(index.value))
}

function skip() {
  clearTimeout(timer)
  finish()
}

onMounted(() => {
  window.addEventListener('keydown', skip)
  timer = setTimeout(advance, span(index.value))
})

onUnmounted(() => {
  clearTimeout(timer)
  window.removeEventListener('keydown', skip)
})
</script>

<template>
  <div class="arrival" @click="skip">
    <span class="arrival-field" aria-hidden="true"><DotField :opacity="0.5" /></span>
    <p
      :key="index"
      class="slogan"
      :style="{ '--out': span(index) - OUT + 'ms' }"
    >{{ SLOGANS[index] }}</p>
  </div>
</template>

<style scoped>
.arrival {
  position: fixed;
  inset: 0;
  z-index: 60;
  background: var(--ground);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 var(--bar-gutter);
}
.arrival-field {
  position: absolute;
  inset: 0;
  overflow: hidden;
}
/* Each line rises, is read, and leaves before the next arrives — the exit is
   what gives the sequence its weight, a cut would read as a slideshow. */
.slogan {
  position: relative;
  max-width: 24ch;
  text-align: center;
  font-family: var(--f-display);
  font-variation-settings: "opsz" 144;
  font-weight: 300;
  font-size: clamp(24px, 4vw, 44px);
  line-height: 1.15;
  letter-spacing: -0.024em;
  color: var(--ink);
  animation:
    slogan-in 760ms var(--ease) both,
    slogan-out 420ms var(--ease) var(--out, 1980ms) both;
}
@keyframes slogan-in {
  from { opacity: 0; transform: translateY(10px); }
  to   { opacity: 1; transform: none; }
}
@keyframes slogan-out {
  from { opacity: 1; }
  to   { opacity: 0; }
}
</style>
