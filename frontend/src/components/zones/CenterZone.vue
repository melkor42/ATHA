<script setup>
import { usePlaza } from '../../composables/usePlaza.js'
import bg from '../../assets/plaza/center.png'

// S1 Town Square center (spec §3) — the resting point; copy exact per §5.
const { goTo } = usePlaza()
</script>

<template>
  <section class="zone zone-center" :style="{ '--bg': `url(${bg})` }">
    <div class="zone-copy">
      <p class="eyebrow">A HADORA EXPERIENCE</p>
      <h1 class="headline">Meet Signal from where you are.</h1>
      <p class="support">The new edge isn&rsquo;t AI &mdash; it&rsquo;s the depth that makes it viable.</p>
      <div class="cta-row">
        <button type="button" class="plaza-btn solid" @click="goTo('south')">
          Choose your way into Signal
        </button>
        <button type="button" class="plaza-btn" @click="goTo('north')">
          Explore Signal freely
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
  gap: 14px;
  background: radial-gradient(58% 52% at 50% 50%, rgba(233, 226, 212, 0.66), transparent 78%);
}
.eyebrow {
  font-size: 12px;
  letter-spacing: 0.34em;
  color: rgba(43, 38, 34, 0.62);
  margin: 0;
}
.headline {
  font-size: clamp(30px, 4.6vw, 58px);
  font-weight: 300;
  letter-spacing: -0.01em;
  color: #241f1b;
  margin: 0;
  text-shadow: 0 1px 0 rgba(255, 251, 240, 0.6);
}
.support {
  max-width: 52ch;
  color: rgba(36, 31, 27, 0.85);
  font-size: 16px;
  line-height: 1.6;
  margin: 0;
}
.cta-row {
  display: flex;
  gap: 14px;
  flex-wrap: wrap;
  justify-content: center;
  margin-top: 10px;
}
</style>
