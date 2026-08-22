<script setup>
import { usePlaza } from '../../composables/usePlaza.js'
import bg from '../../assets/plaza/center.png'

// S1 Town Square center (delta §2) — the resting point: promise,
// grounding, belonging, two doors. Both doors lead to the east wing.
const { goTo } = usePlaza()
</script>

<template>
  <section class="zone zone-center" :style="{ '--bg': `url(${bg})` }">
    <div class="zone-copy">
      <p class="eyebrow">A HADORA EXPERIENCE</p>
      <h1 class="headline">A new AI event for people who want to shape what comes next.</h1>
      <p class="support">
        ATHA brings together curious people, real business challenges, emerging AI
        capabilities and deep thinking to explore what becomes possible in a new era of AI.
      </p>
      <p class="connection">The most important thing we bring together is people.</p>
      <p class="connection-sub">
        Students, business leaders, AI practitioners, researchers, founders and curious
        minds come together to explore a future that is still being defined.
      </p>
      <p class="event-info">ATHA 001 · WARWICK BUSINESS SCHOOL · FORMING</p>
      <div class="cta-row">
        <button type="button" class="plaza-btn solid" @click="goTo('east')">
          Join as a Student
        </button>
        <button type="button" class="plaza-btn" @click="goTo('east')">
          Bring a Challenge
        </button>
      </div>
    </div>
  </section>
</template>

<style scoped>
.zone-copy {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 0 8vw;
  gap: 12px;
  background: radial-gradient(58% 52% at 50% 50%, rgba(233, 226, 212, 0.66), transparent 78%);
}
.eyebrow {
  font-size: 12px;
  letter-spacing: 0.34em;
  color: rgba(43, 38, 34, 0.62);
  margin: 0;
}
.headline {
  max-width: 26ch;
  font-size: clamp(26px, 3.8vw, 48px);
  font-weight: 300;
  letter-spacing: -0.01em;
  color: #241f1b;
  margin: 0;
  text-shadow: 0 1px 0 rgba(255, 251, 240, 0.6);
}
.support {
  max-width: 58ch;
  color: rgba(36, 31, 27, 0.85);
  font-size: clamp(14px, 1.4vw, 16px);
  line-height: 1.6;
  margin: 0;
}
.connection {
  margin: 10px 0 0;
  font-size: clamp(13px, 1.3vw, 16px);
  letter-spacing: 0.22em;
  text-transform: uppercase;
  color: #241f1b;
}
.connection-sub {
  max-width: 56ch;
  margin: 0;
  color: rgba(36, 31, 27, 0.78);
  font-size: clamp(13px, 1.25vw, 15px);
  line-height: 1.55;
}
.event-info {
  margin: 8px 0 0;
  font-size: 12px;
  letter-spacing: 0.26em;
  color: rgba(43, 38, 34, 0.62);
}
.cta-row {
  display: flex;
  gap: 14px;
  flex-wrap: wrap;
  justify-content: center;
  margin-top: 10px;
}
</style>
