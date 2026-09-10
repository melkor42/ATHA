<template>
  <div class="hero">
    <div class="hero-inner">
      <p class="label mono eyebrow u-fade" style="--d: 60ms">WBS × OneMundi</p>
      <h1 class="u-wipe">
        Not an AI event. Not a hackathon.<br />
        A living laboratory for the AI-native era.
      </h1>
    </div>
  </div>
</template>

<style scoped>
/* The claim is part of the band now: no ground, no texture, no top padding —
   the row above sets the measure and the header's crop decides how much shows.
   The padding lives one level in, on .hero-inner: the header collapses this
   element to a 0fr grid row, and a box's own padding cannot be sized away. */
.hero-inner {
  min-height: var(--claim-h);
  padding: 6px var(--bar-gutter) 26px;
}
.eyebrow { color: var(--on-deep); opacity: 0.62; }
h1 {
  margin-top: 14px;
  font-size: clamp(24px, 3.2vw, 36px);
  line-height: 1.08;
  letter-spacing: -0.022em;
  text-align: center;
}
</style>
