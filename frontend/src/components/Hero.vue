<template>
  <div class="hero">
    <div class="hero-inner">
      <p class="label mono eyebrow u-fade" style="--d: 60ms">WBS × OneMundi</p>
      <span class="seam" aria-hidden="true"></span>
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
   element to a 0fr grid row, and a box's own padding cannot be sized away.
   Its height is the token the landing fold subtracts, so the fixed paddings sum
   inside it (160 = 6 + 16 + 14 + 2 + 18 + 78 + 26) instead of drifting with vh. */
.hero-inner {
  min-height: var(--claim-h);
  padding: 6px var(--bar-gutter) 26px;
}
.eyebrow { color: var(--paper); opacity: 0.62; }
.seam {
  display: block;
  width: 32px;
  height: 2px;
  background: var(--signal);
  margin: 14px 0 18px;
}
h1 {
  font-size: clamp(24px, 3.2vw, 36px);
  line-height: 1.08;
  letter-spacing: -0.022em;
  max-width: 30ch;
}
</style>
