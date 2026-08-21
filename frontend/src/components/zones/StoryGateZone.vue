<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { useGate, Q1, Q2 } from '../../composables/useGate.js'
import { usePlaza } from '../../composables/usePlaza.js'
import bg from '../../assets/plaza/south.png'

// S2 South — Story & Entrance-Gate (spec §3).
// (a) five phases revealed on scroll like growing light;
// (b) CAM asks Q1 then Q2 as soft organic cards, closing + route advice.
const { goTo } = usePlaza()
const gate = useGate()
const { step, seen, visibleQ1, route } = gate

// Phase lines carry only approved brief copy (docs/signal-context-brief.md) —
// no invented program details.
const PHASES = [
  { n: '01', title: 'Challenge', line: 'Real enterprise AI challenges enter the room, carried by the people who own them.' },
  { n: '02', title: 'Cohort', line: 'Talent gathers: depth, judgment, context. No spectators.' },
  { n: '03', title: '48 Hours', line: 'Five lenses — Desirability, Feasibility, Viability, Scalability, Responsibility. The deliverable is a board-ready verdict, not a demo.' },
  { n: '04', title: 'Experience', line: 'Wellbeing is infrastructure. Supported, not depleted.' },
  { n: '05', title: 'Signal', line: 'Everyone else resets. We compound.' }
]

const scroller = ref(null)
const gateEl = ref(null)
const revealed = ref(new Set())
const changing = ref(false)

let obs = null
onMounted(() => {
  obs = new IntersectionObserver(
    (entries) => {
      for (const en of entries) {
        if (!en.isIntersecting) continue
        const i = Number(en.target.dataset.i)
        if (!revealed.value.has(i)) {
          revealed.value.add(i)
          revealed.value = new Set(revealed.value) // retrigger reactivity
        }
        if (en.target.dataset.gate === '1' && step.value === 'idle') {
          if (seen.value && !changing.value) return // welcome-back renders instead
          gate.start()
        }
      }
    },
    { root: scroller.value, threshold: 0.35 }
  )
  scroller.value.querySelectorAll('.phase').forEach((el) => obs.observe(el))
  obs.observe(gateEl.value)
})
onBeforeUnmount(() => obs?.disconnect())

function follow() {
  if (!route.value) return
  const target = route.value.zone
  gate.finish()
  goTo(target)
}
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

    <div class="gate" ref="gateEl">
      <!-- first visit / changing route: CAM asks Q1 then Q2 -->
      <template v-if="!seen || changing">
        <div v-if="step === 'q1'" class="gate-card">
          <h3>{{ Q1.question }}</h3>
          <button
            v-for="o in visibleQ1"
            :key="o.id"
            type="button"
            class="answer-card"
            @click="gate.answer1(o.id)"
          >
            {{ o.label }}
          </button>
        </div>
        <div v-else-if="step === 'q2'" class="gate-card">
          <h3>{{ Q2.question }}</h3>
          <button
            v-for="o in Q2.options"
            :key="o.id"
            type="button"
            class="answer-card"
            @click="gate.answer2(o.id)"
          >
            {{ o.label }}
          </button>
        </div>
        <div v-else-if="step === 'closing'" class="gate-card closing">
          <h3>Your way into Signal begins here.</h3>
          <div class="cta-row">
            <button type="button" class="plaza-btn solid" @click="follow">
              Follow my light path
            </button>
            <button type="button" class="plaza-btn" @click="gate.changeRoute()">
              Change your route
            </button>
          </div>
        </div>
        <p v-else class="gate-hint">CAM is waiting below…</p>
      </template>

      <!-- returning visitor: gate skipped, route change stays visible (§6) -->
      <template v-else>
        <div class="gate-card welcome-back">
          <h3>Welcome back — your route is set.</h3>
          <button type="button" class="plaza-btn" @click="changing = true; gate.start()">
            Change your route
          </button>
        </div>
      </template>
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
.answer-card {
  text-align: left;
  border: 1px solid rgba(120, 105, 85, 0.25);
  background: rgba(255, 252, 246, 0.92);
  border-radius: 20px 24px 22px 18px;
  padding: 13px 18px;
  font-size: 15.5px;
  color: #2b2622;
  cursor: pointer;
  transition: background 0.35s, transform 0.35s, box-shadow 0.35s;
}
.answer-card:hover {
  background: rgba(127, 227, 240, 0.22);
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(47, 143, 163, 0.18);
}
.cta-row {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}
.gate-hint {
  color: rgba(43, 38, 34, 0.55);
  font-size: 13px;
  letter-spacing: 0.08em;
}
</style>
