<script setup>
import bg from '../../assets/plaza/east.png'

// S5 East — Anmeldung (spec §3): warm welcoming pole, two organic CTAs.
// Copy = the four-perspective deliverables (docs/atha-context-brief.md);
// entry points are the brief's approved mailto subjects.
const CARDS = [
  {
    cta: 'Bring a Challenge',
    line: 'Bring a real AI workflow. Get an evidence-grade verdict, modelled unit economics, first-look talent access.',
    href: 'mailto:hello@onemundi.one?subject=ATHA%20001%20%E2%80%94%20Enterprise%20Challenge'
  },
  {
    cta: 'Apply as Talent',
    line: 'Bring depth, judgment, context. Get proof of how you operate with AI — and a place in a compounding ecosystem.',
    href: 'mailto:hello@onemundi.one?subject=ATHA%20001%20%E2%80%94%20Talent%20Application'
  }
]
</script>

<template>
  <section class="zone zone-east" :style="{ '--bg': `url(${bg})` }">
    <div class="east-copy">
      <p class="eyebrow">JOIN</p>
      <h2 class="wing-title">Your way in</h2>
      <div class="east-cards">
        <article v-for="c in CARDS" :key="c.cta" class="east-card">
          <p class="line">{{ c.line }}</p>
          <a class="plaza-btn solid" :href="c.href">{{ c.cta }}</a>
        </article>
      </div>
    </div>
  </section>
</template>

<style scoped>
.east-copy {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 18px;
  padding: 6vh 8vw;
}
.eyebrow {
  font-size: 12px;
  letter-spacing: 0.34em;
  color: rgba(60, 40, 28, 0.6);
  margin: 0;
}
.wing-title {
  font-weight: 300;
  font-size: clamp(24px, 3vw, 40px);
  color: #2b2018;
  margin: 0;
}
.east-cards {
  display: flex;
  gap: 18px;
  flex-wrap: wrap;
  justify-content: center;
}
.east-card {
  width: min(320px, 84vw);
  display: flex;
  flex-direction: column;
  gap: 14px;
  align-items: flex-start;
  background: rgba(252, 244, 234, 0.92);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 240, 220, 0.9);
  border-radius: 30px 34px 30px 26px;
  padding: 22px 24px;
  box-shadow: 0 12px 34px rgba(70, 40, 20, 0.16), inset 0 0 24px rgba(255, 190, 120, 0.18);
}
.line {
  margin: 0;
  color: rgba(43, 31, 22, 0.9);
  font-size: 15.5px;
  line-height: 1.55;
}
</style>
