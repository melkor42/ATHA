<script setup>
import { computed, inject } from 'vue'

// NetworkGraph — frontend-derived organic panel (decision: backend contract
// stays at five components). Draws the entities map of the current
// ExperienceSchema as a luminous node graph: persons cyan, enterprises
// amber, events warm white; edges from shared topics or event membership.
const entities = inject('entities', computed(() => ({})))

const TYPE_COLOR = { person: '#7fe3f0', enterprise: '#f2b361', event: '#f1ede6' }

const nodes = computed(() => {
  const list = Object.entries(entities.value ?? {})
  const cx = 400
  const cy = 220
  return list.map(([id, e], i) => {
    const angle = i * 2.39996 // golden angle — organic, never gridlike
    const r = 110 + (i % 3) * 52
    return {
      id,
      name: e.name ?? id,
      type: e.type ?? 'person',
      topics: e.topics ?? [],
      x: cx + Math.cos(angle) * r * 1.4,
      y: cy + Math.sin(angle) * r * 0.72
    }
  })
})

const edges = computed(() => {
  const out = []
  const ns = nodes.value
  for (let i = 0; i < ns.length; i++) {
    for (let j = i + 1; j < ns.length; j++) {
      const a = ns[i]
      const b = ns[j]
      const shared = a.topics.some((t) => b.topics.includes(t))
      const eventLink = a.type === 'event' || b.type === 'event'
      if (shared || eventLink) out.push({ a, b, warm: shared })
    }
  }
  return out
})

function edgeD(e) {
  const mx = (e.a.x + e.b.x) / 2
  const my = (e.a.y + e.b.y) / 2
  const dx = e.b.x - e.a.x
  const dy = e.b.y - e.a.y
  const len = Math.hypot(dx, dy) || 1
  // bow the curve perpendicular for an organic, vein-like arc
  const k = 0.18
  return `M${e.a.x} ${e.a.y} Q${mx - (dy / len) * len * k} ${my + (dx / len) * len * k} ${e.b.x} ${e.b.y}`
}
</script>

<template>
  <svg class="network-graph" viewBox="0 0 800 440" role="img" aria-label="Your network graph">
    <path
      v-for="(e, i) in edges"
      :key="'e' + i"
      :d="edgeD(e)"
      class="edge"
      :class="{ warm: e.warm }"
    />
    <g v-for="(n, i) in nodes" :key="n.id" class="node" :style="{ animationDelay: i * 0.7 + 's' }">
      <circle :cx="n.x" :cy="n.y" r="10" class="halo" :style="{ stroke: TYPE_COLOR[n.type] }" />
      <circle :cx="n.x" :cy="n.y" r="4.5" :style="{ fill: TYPE_COLOR[n.type] }" />
      <text :x="n.x" :y="n.y + 26" class="label">{{ n.name }}</text>
    </g>
  </svg>
</template>

<style scoped>
.network-graph {
  width: 100%;
  height: auto;
  display: block;
}
.edge {
  fill: none;
  stroke: rgba(127, 227, 240, 0.4);
  stroke-width: 1.6;
  stroke-linecap: round;
}
.edge.warm { stroke: rgba(242, 179, 97, 0.45); }
.halo {
  fill: none;
  stroke-width: 1.4;
  opacity: 0.5;
  filter: drop-shadow(0 0 6px currentColor);
}
.label {
  fill: rgba(241, 237, 230, 0.82);
  font-size: 12px;
  text-anchor: middle;
  letter-spacing: 0.04em;
}
.node { animation: node-float 9s ease-in-out infinite alternate; }
@keyframes node-float {
  from { transform: translateY(0); }
  to { transform: translateY(-7px); }
}
</style>
