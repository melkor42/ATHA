<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { SESSION_KEYS } from '../config.js'
import { usePlaza } from '../composables/usePlaza.js'

// S0 Arrival (delta §1): a serif poem over a near-black void while the
// plaza sits faintly behind and flies in. Four statements fade in one by
// one (~1s each) and stay, composing the full picture in ~4s. Once per
// session, skippable.
const emit = defineEmits(['done'])
const { reduced } = usePlaza()
const leaving = ref(false)
let timer = 0

// last statement lands at ~3.9s; hold a breath, then reveal
const HOLD_MS = 4000

function finish() {
  if (leaving.value) return
  leaving.value = true
  try { sessionStorage.setItem(SESSION_KEYS.arrival, '1') } catch { /* private mode */ }
  // hand over mid-fade so the plaza brightens underneath — no hard cut
  setTimeout(() => emit('done'), reduced.value ? 0 : 300)
}

onMounted(() => {
  if (reduced.value) {
    finish()
    return
  }
  timer = setTimeout(finish, HOLD_MS)
})
onBeforeUnmount(() => clearTimeout(timer))
</script>

<template>
  <div class="arrival" :class="{ leaving }" @click="finish">
    <div class="veil"></div>
    <div class="stars" aria-hidden="true"></div>
    <div class="statements">
      <p class="st st1">A new era is here.</p>
      <p class="st st2">The playbook doesn&rsquo;t exist <em>yet</em>.</p>
      <p class="st st3">So we come <em>together</em> to figure it out.</p>
      <p class="st st4">
        <span class="eyebrow">Welcome to</span>
        ATHA.
      </p>
    </div>
    <button type="button" class="skip" @click.stop="finish">skip</button>
  </div>
</template>

<style scoped>
.arrival {
  position: fixed;
  inset: 0;
  z-index: 60;
  overflow: hidden;
  background: #0d0b09;
  transition: opacity 0.5s ease;
  cursor: pointer;
}
.arrival.leaving { opacity: 0; pointer-events: none; }

/* deep warm veil — the plaza stays a faint presence behind the void */
.veil {
  position: absolute;
  inset: 0;
  background:
    radial-gradient(64% 42% at 50% 110%, rgba(200, 155, 60, 0.10), transparent 70%),
    rgba(13, 11, 9, 0.88);
}

/* sparse star specks, like dust in a dark room */
.stars {
  position: absolute;
  inset: 0;
  opacity: 0.55;
  background-image:
    radial-gradient(1px 1px at 12% 24%, rgba(240, 232, 216, 0.5), transparent 55%),
    radial-gradient(1px 1px at 68% 12%, rgba(240, 232, 216, 0.35), transparent 55%),
    radial-gradient(1.5px 1.5px at 84% 62%, rgba(240, 232, 216, 0.4), transparent 55%),
    radial-gradient(1px 1px at 32% 78%, rgba(240, 232, 216, 0.3), transparent 55%),
    radial-gradient(1px 1px at 52% 44%, rgba(240, 232, 216, 0.25), transparent 55%),
    radial-gradient(1.5px 1.5px at 8% 58%, rgba(240, 232, 216, 0.3), transparent 55%);
}

/* the four statements compose one picture, like the inspiration */
.statements {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: clamp(26px, 7vh, 72px);
  padding: 10vh 12vw 12vh;
}
.st {
  margin: 0;
  max-width: 30ch;
  font-family: 'Cormorant Garamond', Georgia, serif;
  font-size: clamp(24px, 3.6vw, 42px);
  font-weight: 500;
  line-height: 1.3;
  color: #ede4d3;
  opacity: 0;
  animation: st-in 0.8s cubic-bezier(0.22, 1, 0.36, 1) both;
}
.st em {
  font-style: italic;
  color: #c89b3c;
}
.st1 { align-self: flex-start; animation-delay: 0.2s; }
.st2 { align-self: flex-end; text-align: right; animation-delay: 1.15s; }
.st3 { align-self: flex-start; animation-delay: 2.1s; }
.st4 {
  align-self: center;
  text-align: center;
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-width: none;
  animation-delay: 3.05s;
}
.st4 .eyebrow {
  font-family: var(--font-ui);
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.5em;
  text-transform: uppercase;
  color: rgba(237, 228, 211, 0.55);
}

/* fade in closer: rise slightly and settle toward the reader, then stay */
@keyframes st-in {
  from { opacity: 0; transform: translateY(20px) scale(1.03); }
  to { opacity: 1; transform: none; }
}

.skip {
  position: absolute;
  top: 20px;
  right: 22px;
  border: none;
  background: transparent;
  color: rgba(240, 232, 216, 0.45);
  font-size: 11px;
  letter-spacing: 0.28em;
  text-transform: uppercase;
  padding: 8px 10px;
  cursor: pointer;
  transition: color 0.3s ease;
}
.skip:hover { color: rgba(240, 232, 216, 0.85); }

@media (prefers-reduced-motion: reduce) {
  .st { animation: none; opacity: 1; }
}
</style>
