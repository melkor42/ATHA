<script setup>
import bg from '../../assets/plaza/west.png'

// S4 West — Essential Infos (spec §3): calm, bright, maximum readability.
// Values from docs/signal-context-brief.md (approved copy only);
// unconfirmed facts carry their status per the brief's content rules.
const FACTS = [
  ['Format', 'The AI-Native Viability Sprint — 48 hours. Not a hackathon · Not a conference · Something new.'],
  ['When', 'Q4 2026 · exact dates: Open'],
  ['Where', 'Warwick Business School × OneMundi'],
  ['Access', '[PLACEHOLDER] · Open'],
  ['Contact', 'hello@onemundi.one']
]
</script>

<template>
  <section class="zone zone-west" :style="{ '--bg': `url(${bg})` }">
    <div class="west-copy">
      <p class="eyebrow">ESSENTIALS</p>
      <h2 class="wing-title">The quiet wing</h2>
      <dl class="tablets">
        <div v-for="[k, v] in FACTS" :key="k" class="tablet">
          <dt>{{ k }}</dt>
          <dd>{{ v }}</dd>
        </div>
      </dl>
    </div>
  </section>
</template>

<style scoped>
.west-copy {
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
  color: rgba(43, 38, 34, 0.6);
  margin: 0;
}
.wing-title {
  font-weight: 300;
  font-size: clamp(24px, 3vw, 40px);
  color: #241f1b;
  margin: 0;
}
.tablets {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 14px;
  width: min(880px, 92%);
  margin: 0;
}
.tablet {
  background: rgba(250, 247, 240, 0.93);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 251, 240, 0.9);
  border-radius: 22px 26px 24px 20px;
  padding: 16px 20px;
  box-shadow: 0 10px 30px rgba(30, 40, 45, 0.14);
}
.tablet dt {
  font-size: 11.5px;
  letter-spacing: 0.22em;
  color: rgba(43, 38, 34, 0.55);
  text-transform: uppercase;
}
.tablet dd {
  margin: 6px 0 0;
  color: #241f1b;
  font-size: 16px;
  line-height: 1.5;
}
</style>
