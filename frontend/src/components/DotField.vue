<script setup>
import { computed } from 'vue'

// The signature mark (brand §7): a regular grid of paper dots on deep navy,
// growing slightly toward one edge, cut by a diagonal seam of signal-blue
// dots. Deterministic — no randomness, so it renders identically every time.

const props = defineProps({
  cols: { type: Number, default: 48 },
  rows: { type: Number, default: 15 },
  opacity: { type: Number, default: 0.45 }
})

const CW = 1000
const CH = 300

const dots = computed(() => {
  const out = []
  const cw = CW / props.cols
  const ch = CH / props.rows
  for (let i = 0; i < props.cols; i++) {
    for (let j = 0; j < props.rows; j++) {
      const gx = (i + 0.5) / props.cols
      const gy = (j + 0.5) / props.rows
      // distance from the anti-diagonal seam
      const d = Math.abs(gy - (1 - gx))
      const near = d < 0.055
      const fall = 1 - d / 0.055
      out.push({
        x: (i + 0.5) * cw,
        y: (j + 0.5) * ch,
        r: near ? 1.5 + fall * 1.1 : 0.9 + gx * 1.1,
        fill: near ? 'var(--signal)' : 'var(--on-deep)',
        o: near ? 0.55 + fall * 0.4 : 0.06 + gx * 0.16
      })
    }
  }
  return out
})
</script>

<template>
  <svg
    class="dot-field"
    :style="{ opacity }"
    :viewBox="`0 0 ${CW} ${CH}`"
    preserveAspectRatio="xMidYMid slice"
    aria-hidden="true"
  >
    <circle
      v-for="(p, i) in dots"
      :key="i"
      :cx="p.x"
      :cy="p.y"
      :r="p.r"
      :fill="p.fill"
      :opacity="p.o"
    />
  </svg>
</template>

<style scoped>
.dot-field {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}
</style>
