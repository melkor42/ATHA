<script setup>
import { usePlaza } from '../composables/usePlaza.js'

// The light veins are the primary navigation affordance (spec §2):
// a radial blossom at the center plus one wavy vein per direction.
// Purely visual, painted above the zone photos but below all content
// (stacking: zone bg z0 < veins z1 < content z2).
const { pulse, slowVeins, reduced } = usePlaza()

const PETAL = 'M1500 1500 C1620 1418 1768 1438 1792 1500 C1768 1562 1620 1582 1500 1500'
const PETALS = [0, 45, 90, 135, 180, 225, 270, 315]

const VEINS = [
  { zone: 'north', color: 'cyan', d: 'M1500 1300 C1420 1110 1580 940 1500 720 C1470 630 1500 560 1500 520' },
  { zone: 'east', color: 'amber', d: 'M1700 1500 C1880 1420 2060 1580 2280 1500 C2370 1470 2440 1500 2480 1500' },
  { zone: 'south', color: 'cyan', d: 'M1500 1700 C1580 1890 1420 2060 1500 2280 C1530 2370 1500 2440 1500 2480' },
  { zone: 'west', color: 'amber', d: 'M1300 1500 C1120 1580 940 1420 720 1500 C630 1530 560 1500 520 1500' }
]
</script>

<template>
  <svg class="veins" viewBox="0 0 3000 3000" preserveAspectRatio="none">
    <g class="blossom" :class="{ still: reduced }" transform="translate(1500 1500) scale(0.6) translate(-1500 -1500)">
      <path
        v-for="a in PETALS"
        :key="a"
        :d="PETAL"
        :transform="`rotate(${a} 1500 1500)`"
        class="vein-base petal"
        :class="a % 90 === 0 ? 'cyan' : 'amber'"
        vector-effect="non-scaling-stroke"
      />
    </g>
    <g
      v-for="v in VEINS"
      :key="v.zone"
      class="vein"
      :class="[v.color, { on: pulse === v.zone, slow: slowVeins, still: reduced }]"
    >
      <path :d="v.d" class="vein-base" vector-effect="non-scaling-stroke" />
      <path :d="v.d" class="vein-flow" vector-effect="non-scaling-stroke" />
    </g>
  </svg>
</template>

<style scoped>
.veins {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 1;
}
.vein-base {
  fill: none;
  stroke-width: 2px;
  opacity: 0.3;
}
.petal { stroke-width: 2px; opacity: 0.28; }
.cyan .vein-base, .vein-base.cyan, .cyan.petal { stroke: #1899ad; }
.amber .vein-base, .vein-base.amber, .amber.petal { stroke: #d98a2e; }
.vein-flow {
  fill: none;
  stroke-width: 3px;
  stroke-linecap: round;
  stroke-dasharray: 18 640;
  animation: vein-flow 5.2s linear infinite;
  filter: drop-shadow(0 0 6px currentColor);
}
.cyan .vein-flow { stroke: #35cfe3; color: #1899ad; }
.amber .vein-flow { stroke: #f2a94e; color: #d98a2e; }
.vein.slow .vein-flow { animation-duration: 11s; }
.vein.on .vein-base { opacity: 0.55; stroke-width: 3.5px; }
.vein.on .vein-flow { animation-duration: 2.6s; stroke-width: 4px; }
.vein.still .vein-flow, .blossom.still .vein-base { animation: none; }
.vein.still .vein-flow { opacity: 0.5; stroke-dasharray: none; }
@keyframes vein-flow {
  to { stroke-dashoffset: -658; }
}
</style>
