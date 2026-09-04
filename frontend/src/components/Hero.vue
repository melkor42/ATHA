<script setup>
import DotField from './DotField.vue'
</script>

<template>
  <header class="hero deep">
    <DotField :opacity="0.32" />
    <div class="hero-inner">
      <div class="hero-title">
        <p class="label mono eyebrow u-fade" style="--d: 60ms">WBS × OneMundi</p>
        <span class="seam" aria-hidden="true"></span>
        <h1 class="u-wipe">
          Not an AI event. Not a hackathon.<br />
          A living laboratory for the AI-native era.
        </h1>
      </div>
      <p class="lede u-fade" style="--d: 560ms">
        Real companies bring real decisions. Executive MBA teams, specialists, mentors
        and researchers work them for three days. Every recommendation is defended in
        front of the company, and one owned decision leaves the room.
      </p>
    </div>
  </header>
</template>

<style scoped>
.hero {
  position: relative;
  overflow: hidden;
  /* top padding keeps the absolute chrome's wordmark clear of the eyebrow */
  padding: clamp(58px, 9vh, 76px) clamp(22px, 5vw, 64px) clamp(22px, 3.4vh, 38px);
}
.hero-inner {
  position: relative;
  max-width: 1080px;
  display: grid;
  gap: clamp(18px, 3vw, 44px);
}
.eyebrow { color: var(--paper); opacity: 0.5; }
.seam {
  display: block;
  width: 32px;
  height: 2px;
  background: var(--signal);
  margin: 18px 0 20px;
}
.hero h1 {
  font-size: clamp(24px, 3.2vw, 36px);
  line-height: 1.08;
  letter-spacing: -0.022em;
  max-width: 30ch;
}
.lede {
  margin-top: 18px;
  max-width: 56ch;
  font-size: clamp(15px, 1.4vw, 16px);
  line-height: 1.5;
  color: var(--paper);
  opacity: 0.6;
}
/* wide screens carry the headline and its explanation side by side */
@media (min-width: 1100px) {
  .hero-inner {
    max-width: 1280px;
    grid-template-columns: minmax(0, 1.25fr) minmax(0, 1fr);
    align-items: start;
  }
  /* the column bounds the measure; a ch-cap here would wrap the lede taller
     than the headline and give the compression back */
  .lede { margin-top: 22px; max-width: none; }
}
</style>
