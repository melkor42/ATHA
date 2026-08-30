<script setup>
import { usePlaza } from '../composables/usePlaza.js'

// Secondary navigation: a small organic compass (soft blob, no HUD grid).
const { current, goTo } = usePlaza()

const DOTS = [
  { zone: 'north', x: 50, y: 16, name: 'AI Compose' },
  { zone: 'west', x: 16, y: 50, name: 'Wisdom' },
  { zone: 'center', x: 50, y: 50, name: 'Center' },
  { zone: 'east', x: 84, y: 50, name: 'Events' },
  { zone: 'south', x: 50, y: 84, name: 'Explore' }
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
      :data-name="d.name"
      :aria-label="d.name"
      @click="goTo(d.zone)"
    ></button>
    <span class="compass-label" aria-hidden="true">Navigation</span>
  </nav>
</template>

<style scoped>
.compass {
  position: fixed;
  left: 22px;
  bottom: 22px;
  width: 101px;
  height: 101px;
  border-radius: 58% 42% 55% 45% / 48% 55% 45% 52%;
  background: rgba(244, 239, 231, 0.55);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 251, 240, 0.65);
  box-shadow: 0 8px 28px rgba(20, 30, 35, 0.18), inset 0 0 18px rgba(255, 214, 150, 0.25);
  z-index: 40;
}
.dot {
  position: absolute;
  width: 17.6px;
  height: 17.6px;
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
/* always-visible micro-caption: same voice as the center signpost arms */
.compass-label {
  position: absolute;
  top: calc(100% + 3px);
  left: 50%;
  transform: translateX(-50%);
  font-family: ui-monospace, 'Cascadia Mono', Menlo, Consolas, monospace;
  font-size: 10px;
  line-height: 1;
  letter-spacing: 0.26em;
  text-transform: uppercase;
  color: rgba(43, 38, 34, 0.72);
  text-shadow: 0 1px 0 rgba(255, 251, 240, 0.6);
  white-space: nowrap;
  pointer-events: none;
}
/* hover/focus corner names: signpost micro-style, opacity-only fade,
   never intercepting clicks; edge dots open inward so labels stay
   inside the viewport (west opens right, east opens left) */
.dot::after {
  content: attr(data-name);
  position: absolute;
  top: calc(100% + 7px);
  left: 50%;
  transform: translateX(-50%);
  padding: 3px 7px 3px 9px;
  font-family: ui-monospace, 'Cascadia Mono', Menlo, Consolas, monospace;
  font-size: 10px;
  line-height: 1;
  letter-spacing: 0.26em;
  text-transform: uppercase;
  color: rgba(43, 38, 34, 0.88);
  background: rgba(248, 244, 236, 0.92);
  border: 1px solid rgba(255, 251, 240, 0.7);
  border-radius: 4px;
  box-shadow: 0 4px 12px rgba(20, 30, 35, 0.14);
  white-space: nowrap;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.25s ease;
}
.dot:hover::after,
.dot:focus-visible::after { opacity: 1; }
.dot.west::after { left: -4px; transform: none; }
.dot.east::after { left: auto; right: -4px; transform: none; }
/* narrow viewports: the compass shrinks into the corner so it stops
   overlapping card content (zones carry matching bottom safe areas) */
@media (max-width: 900px) {
  .compass { width: 75px; height: 75px; left: 16px; bottom: 16px; }
  .dot { width: 14.3px; height: 14.3px; }
}
</style>
