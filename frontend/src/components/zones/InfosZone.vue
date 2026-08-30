<script setup>
import bg from '../../assets/plaza/west.jpg'
import SevenDirections from './SevenDirections.vue'

// S4 West — the quiet wing (spec §3): calm, bright, maximum readability.
// The wing's knowledge content lives in SevenDirections (approved copy
// only; unconfirmed facts carry their status per the brief's content rules).
</script>

<template>
  <section class="zone zone-west" :style="{ '--bg': `url(${bg})` }">
    <div class="west-copy">
      <p class="eyebrow">WISDOM</p>
      <h2 class="wing-title">The quiet wing</h2>
      <SevenDirections />
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
  gap: 14px;
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
</style>
