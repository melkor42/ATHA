<script setup>
import { usePlaza } from '../composables/usePlaza.js'

// Secondary navigation: a small organic compass (soft blob, no HUD grid).
const { current, goTo } = usePlaza()

const DOTS = [
  { zone: 'north', x: 50, y: 16 },
  { zone: 'west', x: 16, y: 50 },
  { zone: 'center', x: 50, y: 50 },
  { zone: 'east', x: 84, y: 50 },
  { zone: 'south', x: 50, y: 84 },
  { zone: 'wisdom', x: 84, y: 84 }
]
</script>

<template>
  <nav class="compass" aria-label="Plaza directions">
    <button
      v-for="d in DOTS"
      :key="d.zone"
      type="button"
      class="dot"
      :class="[d.zone, { here: current === d.zone }]"
      :style="{ left: d.x + '%', top: d.y + '%' }"
      :aria-label="d.zone"
      :title="d.zone"
      @click="goTo(d.zone)"
    ></button>
  </nav>
</template>

<style scoped>
.compass {
  position: fixed;
  left: 22px;
  bottom: 22px;
  width: 92px;
  height: 92px;
  border-radius: 58% 42% 55% 45% / 48% 55% 45% 52%;
  background: rgba(244, 239, 231, 0.55);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 251, 240, 0.65);
  box-shadow: 0 8px 28px rgba(20, 30, 35, 0.18), inset 0 0 18px rgba(255, 214, 150, 0.25);
  z-index: 40;
}
.dot {
  position: absolute;
  width: 16px;
  height: 16px;
  transform: translate(-50%, -50%);
  border: none;
  padding: 0;
  border-radius: 50% 46% 54% 50%;
  background: rgba(90, 110, 115, 0.4);
  cursor: pointer;
  transition: background 0.4s, box-shadow 0.4s, scale 0.4s;
}
.dot.center { background: rgba(90, 110, 115, 0.55); }
.dot:hover { background: #2f8fa3; }
.dot.here {
  background: #f2b361;
  box-shadow: 0 0 10px rgba(242, 179, 97, 0.8);
  scale: 1.25;
}
/* narrow viewports: the compass shrinks into the corner so it stops
   overlapping card content (zones carry matching bottom safe areas) */
@media (max-width: 900px) {
  .compass { width: 68px; height: 68px; left: 16px; bottom: 16px; }
  .dot { width: 13px; height: 13px; }
}
</style>
