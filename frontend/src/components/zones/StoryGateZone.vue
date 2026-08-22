<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { useGate } from '../../composables/useGate.js'
import bg from '../../assets/plaza/south.png'

// S2 South — Story & Entrance-Gate (spec §3).
// (a) five phases revealed on scroll like growing light;
// (b) the gate questions themselves are asked by CAM in his bubble,
//     anywhere in the plaza — the zone only keeps the welcome-back card.
const gate = useGate()
const { seen, route, changeRoute } = gate

// Phase lines carry only approved brief copy (docs/atha-context-brief.md) —
// no invented program details. The seven-stage ATHA rhythm; the length
// of each stage is a decision, and the gaps between them are designed too.
const PHASES = [
  { n: '01', title: 'Arrive & Settle', line: 'People are met rather than processed. The room is made, not booked.' },
  { n: '02', title: 'Open & Sense', line: 'The question is opened before it is attacked — presented as it actually sits, with what was tried and what is feared.' },
  { n: '03', title: 'Connect', line: 'Teams form across disciplines, around the question — not around a single skill.' },
  { n: '04', title: 'Create', line: 'The longest stage: investigation with AI as a working partner, never accepted blindly.' },
  { n: '05', title: 'Discern', line: 'Given more room than any stage except the work itself — evidence, consequences, uncertainty, trade-offs.' },
  { n: '06', title: 'Celebrate', line: 'Recognition is shared, not ranked. Different forms of excellence — no overall winner.' },
  { n: '07', title: 'Integrate & Return', line: 'Leave with something integrated. The relationships carry into the next edition.' }
]

const scroller = ref(null)
const revealed = ref(new Set())

let obs = null
onMounted(() => {
  // observes every .phase regardless of count; one-shot unobserve per reveal
  obs = new IntersectionObserver(
    (entries) => {
      for (const en of entries) {
        if (!en.isIntersecting) continue
        const i = Number(en.target.dataset.i)
        if (!revealed.value.has(i)) {
          revealed.value.add(i)
          revealed.value = new Set(revealed.value) // retrigger reactivity
        }
        obs.unobserve(en.target)
      }
    },
    { root: scroller.value, threshold: 0.35 }
  )
  scroller.value.querySelectorAll('.phase').forEach((el) => obs.observe(el))
})
onBeforeUnmount(() => obs?.disconnect())
</script>

<template>
  <section class="zone zone-south scrollable" ref="scroller" :style="{ '--bg': `url(${bg})` }">
    <div class="story" :class="{ slow: route?.slow }">
      <article
        v-for="(p, i) in PHASES"
        :key="p.n"
        :data-i="i"
        class="phase"
        :class="{ on: revealed.has(i) }"
      >
        <span class="phase-n">{{ p.n }}</span>
        <h3>{{ p.title }}</h3>
        <p>{{ p.line }}</p>
      </article>
    </div>

    <div class="gate">
      <!-- returning visitor: route change reopens CAM's questions (§6) -->
      <div v-if="seen" class="gate-card welcome-back">
        <h3>Welcome back — your route is set.</h3>
        <button type="button" class="plaza-btn" @click="changeRoute()">
          Change your route
        </button>
      </div>
      <p v-else class="gate-hint">CAM walks with you — he will ask how to guide you.</p>
    </div>
  </section>
</template>

<style scoped>
.zone-south {
  overflow-y: auto;
  scrollbar-width: thin;
  scrollbar-color: rgba(120, 105, 85, 0.4) transparent;
}
.story {
  position: relative;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 9vh;
  padding: 14vh 8vw 10vh;
}
.phase {
  max-width: 460px;
  text-align: center;
  opacity: 0;
  transform: translateY(26px) scale(0.96);
  filter: blur(6px);
  transition:
    opacity 1.1s cubic-bezier(0.22, 1, 0.36, 1),
    transform 1.1s cubic-bezier(0.22, 1, 0.36, 1),
    filter 1.1s cubic-bezier(0.22, 1, 0.36, 1);
}
.story.slow .phase { transition-duration: 2.2s; }
.phase.on {
  opacity: 1;
  transform: none;
  filter: blur(0);
}
.phase-n {
  font-size: 12px;
  letter-spacing: 0.3em;
  color: rgba(47, 143, 163, 0.75);
}
.phase h3 {
  margin: 6px 0 8px;
  font-weight: 300;
  font-size: 26px;
  color: #241f1b;
  text-shadow: 0 1px 0 rgba(255, 251, 240, 0.65);
}
.phase p {
  margin: 0;
  color: rgba(36, 31, 27, 0.88);
  font-size: 15.5px;
  line-height: 1.6;
  text-shadow: 0 1px 0 rgba(255, 251, 240, 0.55);
}

.gate {
  position: relative;
  min-height: 88vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 8vh 6vw 16vh;
}
.gate-card {
  width: min(560px, 92%);
  display: flex;
  flex-direction: column;
  gap: 12px;
  background: rgba(250, 247, 240, 0.94);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 251, 240, 0.95);
  border-radius: 34px 38px 34px 30px;
  padding: 28px 30px;
  box-shadow: 0 16px 44px rgba(30, 40, 45, 0.16), inset 0 0 30px rgba(255, 214, 150, 0.14);
  animation: gate-in 0.8s cubic-bezier(0.22, 1, 0.36, 1);
}
@keyframes gate-in {
  from { opacity: 0; transform: translateY(18px) scale(0.97); }
}
.gate-card h3 {
  margin: 0 0 6px;
  font-weight: 300;
  font-size: 22px;
  color: #241f1b;
}
.gate-hint {
  color: rgba(43, 38, 34, 0.55);
  font-size: 13px;
  letter-spacing: 0.08em;
}
</style>
