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
    <nav class="signpost" aria-label="Plaza directions">
      <button type="button" class="arm-north" @click="goTo('north')">↑ AI Compose</button>
      <button type="button" class="arm-east" @click="goTo('east')">Events →</button>
      <button type="button" class="arm-south" @click="goTo('south')">↓ Explore</button>
      <button type="button" class="arm-west" @click="goTo('west')">← Wisdom</button>
    </nav>
  </section>
</template>

<style scoped>
/* white readability halo behind the copy column: sits at z0 so the
   veins blossom (VeinsOverlay z1, painted above the tiles) stays
   visible ABOVE it, while the copy (.zone > * z2) stays above both —
   paint order: halo < flower < text */
.zone-center::before {
  content: '';
  position: absolute;
  left: 50%;
  top: 50%;
  /* the drawn ring around the copy is the veins blossom (VeinsOverlay
     .blossom): petal tips sit at 292 SVG units * 0.6 scale = 175.2 units,
     and the 3000-unit viewBox spans 300vw/300vh (10 units = 1vw/1vh), so
     the ring's box is 35.04vw x 35.04vh on the tile center. The halo sits
     ~3% inside that box so the fade completes just before the ring edge
     and nothing washes outside the circle anymore. */
  /* size is owner-dialed live via --halo-size (tune bar, default 66): the
     raw number scales 1:1 into vw/vh so the halo stays a circle in viewport
     terms at any dial */
  width: calc(var(--halo-size, 66) * 1vw);
  height: calc(var(--halo-size, 66) * 1vh);
  transform: translate(-50%, -50%);
  /* holds its strength across the text area, fades only near the rim;
     core alpha is owner-dialed via --halo-alpha (tune bar, 100% default) */
  background: radial-gradient(closest-side,
    rgba(255, 255, 255, var(--halo-alpha, 1)) 0%,
    rgba(255, 255, 255, var(--halo-alpha, 1)) 55%,
    rgba(255, 255, 255, 0) 100%);
  pointer-events: none;
  z-index: 0;
}
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
.signpost {
  position: absolute;
  inset: 0;
  pointer-events: none;
  z-index: 3;
}
.signpost button {
  pointer-events: auto;
  position: absolute;
  /* z0 owns a stacking context so the halo (::before z-1) paints
     behind the label text but never escapes under the tile background */
  z-index: 0;
  background: none;
  border: none;
  cursor: pointer;
  padding: 12px 22px;
  font-family: ui-monospace, 'Cascadia Mono', Menlo, Consolas, monospace;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.26em;
  text-transform: uppercase;
  color: rgba(43, 38, 34, 0.9);
  text-shadow: 0 1px 0 rgba(255, 251, 240, 0.65);
  opacity: 0.75;
  transition: opacity 0.3s ease;
}
/* the halo rests visible and fades away on hover/focus so the label
   alone points the way — transitions stay opacity-only, per the
   signpost's discreet contract */
.signpost button::before {
  content: '';
  position: absolute;
  /* tucks the halo behind the button's own text node (see z-index: 0 above) */
  z-index: -1;
  inset: -18px -36px;
  background: radial-gradient(closest-side, rgba(255, 255, 255, 0.7), rgba(255, 255, 255, 0) 100%);
  opacity: 1;
  transition: opacity 0.3s ease;
  /* breathing pulse so the arm reads as alive/clickable; hover
     kills the animation so its opacity: 0 fade-out wins (below) */
  animation: signpost-breathe 2.5s ease-in-out infinite alternate;
  pointer-events: none;
}
@keyframes signpost-breathe {
  /* var() resolves per element: the tune bar's --signpost-pulse sets the
     dark end of the breath, so the slider dials the pulse depth live */
  from { opacity: var(--signpost-pulse, 0); }
  to { opacity: 1; }
}
.signpost button:hover,
.signpost button:focus-visible {
  opacity: 1;
  color: rgba(43, 38, 34, 0.9);
}
.signpost button:hover::before,
.signpost button:focus-visible::before {
  animation: none;
  opacity: 0;
}
@media (prefers-reduced-motion: reduce) {
  .signpost button::before { animation: none; }
}
/* 14px inset compensates the 12px halo padding, so the labels sit at the
   same visual position as before the aura was added */
.signpost .arm-north { top: 14px; left: 50%; transform: translateX(-50%); padding-top: 0; }
.signpost .arm-east { right: 14px; top: 50%; transform: translateY(-50%); padding-right: 0; }
.signpost .arm-south { bottom: 14px; left: 50%; transform: translateX(-50%); padding-bottom: 0; }
.signpost .arm-west { left: 14px; top: 50%; transform: translateY(-50%); padding-left: 0; }
</style>
