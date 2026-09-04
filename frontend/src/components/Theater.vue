<script setup>
import { onMounted, onBeforeUnmount, ref, watch } from 'vue'

// The network field, now a paper instrument: hairline slate edges, ink nodes,
// one ferrous accent travelling through them. It lives inline inside the chat
// panel while an answer is composing — never a fullscreen takeover.

const props = defineProps({
  steps: { type: Array, default: () => [] },
  cadence: { type: Number, default: 320 },
  active: { type: Boolean, default: true }
})
const emit = defineEmits(['done'])

const on = ref(0)
const canvas = ref(null)
const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches
let raf = 0, running = false

const EDGE = 'rgba(90,107,132,0.22)'      // slate hairline
const NODE = 'rgba(27,33,41,0.30)'        // ink, quiet
const LIT = 'rgba(27,33,41,0.85)'
const ACCENT = '#9B4324'                  // ferrous — the only accent on paper

let seed = 7
const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647

let nodes = [], edges = [], pulses = []
let litEdges = new Map() // "a-b" -> heat

function build(w, h) {
  const n = Math.max(18, Math.min(56, Math.round((w * h) / 7000)))
  nodes = Array.from({ length: n }, () => ({
    x: 12 + rnd() * (w - 24), y: 12 + rnd() * (h - 24), r: 1.2 + rnd() * 1.8, lit: 0
  }))
  const adj = nodes.map(() => [])
  edges = []
  nodes.forEach((node, i) => {
    node.adj = adj[i]
    const near = nodes
      .map((m, j) => [i === j ? 1e9 : (node.x - m.x) ** 2 + (node.y - m.y) ** 2, j])
      .sort((a, b) => a[0] - b[0])
    near.slice(0, 2).forEach(([, j]) => {
      if (!adj[i].includes(j)) { adj[i].push(j); adj[j].push(i); edges.push([i, j]) }
    })
  })
  pulses = Array.from({ length: Math.max(2, Math.round(n / 18)) }, () =>
    ({ from: 0, to: nodes[0].adj[0] ?? 1, t: rnd() }))
}

function spawnPulse() {
  if (pulses.length < 5 && rnd() < 0.3) {
    const start = Math.floor(rnd() * nodes.length)
    const ns = nodes[start]
    pulses.push({ from: start, to: ns.adj[Math.floor(rnd() * ns.adj.length)] ?? 0, t: 0 })
  }
}

function draw(ctx, w, h) {
  ctx.clearRect(0, 0, w, h)
  ctx.strokeStyle = EDGE; ctx.lineWidth = 1
  edges.forEach(([a, b]) => {
    ctx.beginPath(); ctx.moveTo(nodes[a].x, nodes[a].y); ctx.lineTo(nodes[b].x, nodes[b].y); ctx.stroke()
  })
  litEdges.forEach((e, key) => {
    e.heat -= 0.016
    if (e.heat <= 0) { litEdges.delete(key); return }
    const [a, b] = key.split('-').map(Number)
    ctx.strokeStyle = ACCENT
    ctx.globalAlpha = e.heat * 0.7
    ctx.lineWidth = 1
    ctx.beginPath(); ctx.moveTo(nodes[a].x, nodes[a].y); ctx.lineTo(nodes[b].x, nodes[b].y); ctx.stroke()
    ctx.globalAlpha = 1
  })
  nodes.forEach((n) => {
    n.lit = Math.max(0, n.lit - 0.012)
    if (n.lit > 0.02) {
      const g = ctx.createRadialGradient(n.x, n.y, 0, n.x, n.y, n.r * 5)
      g.addColorStop(0, ACCENT); g.addColorStop(1, 'rgba(155,67,36,0)')
      ctx.globalAlpha = n.lit * 0.22
      ctx.fillStyle = g; ctx.beginPath(); ctx.arc(n.x, n.y, n.r * 5, 0, 7); ctx.fill()
      ctx.globalAlpha = 1
    }
    ctx.beginPath(); ctx.arc(n.x, n.y, n.r + n.lit * 1.6, 0, 7)
    ctx.fillStyle = n.lit > 0.02 ? LIT : NODE
    ctx.fill()
  })
  pulses.forEach((p) => {
    p.t += 0.02
    if (p.t >= 1) {
      const arrived = nodes[p.to]
      arrived.lit = 1
      const key = p.from < p.to ? `${p.from}-${p.to}` : `${p.to}-${p.from}`
      litEdges.set(key, { heat: 1 })
      spawnPulse()
      const nexts = arrived.adj.filter((j) => j !== p.from)
      const to = nexts.length ? nexts[Math.floor(rnd() * nexts.length)] : (arrived.adj[0] ?? p.from)
      Object.assign(p, { from: p.to, to, t: 0 })
    }
    const a = nodes[p.from], b = nodes[p.to]
    const x = a.x + (b.x - a.x) * p.t, y = a.y + (b.y - a.y) * p.t
    ctx.fillStyle = ACCENT
    ctx.beginPath(); ctx.arc(x, y, 2.1, 0, 7); ctx.fill()
  })
}

function loop() {
  if (!running) return
  const cv = canvas.value
  if (cv) draw(cv.getContext('2d'), cv.width, cv.height)
  raf = requestAnimationFrame(loop)
}

function paint() {
  const cv = canvas.value
  if (!cv) return
  const w = cv.clientWidth, h = cv.clientHeight
  if (!w || !h) return
  cv.width = w; cv.height = h
  if (!nodes.length) build(w, h)
  draw(cv.getContext('2d'), w, h)
}

function start() {
  if (!canvas.value || running) return
  paint()
  if (reducedMotion) return
  running = true
  raf = requestAnimationFrame(loop)
}
function stop() { running = false; cancelAnimationFrame(raf); raf = 0 }

function onVisibility() {
  if (document.hidden) { cancelAnimationFrame(raf); raf = 0 }
  else if (running && !raf) raf = requestAnimationFrame(loop)
}

let resizeT = 0
function onResize() {
  clearTimeout(resizeT)
  resizeT = setTimeout(() => {
    const cv = canvas.value
    if (!cv) return
    const w = cv.clientWidth, h = cv.clientHeight
    if (w === cv.width && h === cv.height && nodes.length) return
    cv.width = w; cv.height = h
    build(w, h)
    paint()
  }, 200)
}

watch(() => props.active, (v) => { if (v) start(); else stop() })

const timers = []
onMounted(() => {
  document.addEventListener('visibilitychange', onVisibility)
  window.addEventListener('resize', onResize)
  if (props.steps.length) {
    props.steps.forEach((_, i) => {
      timers.push(setTimeout(() => {
        on.value = i + 1
        if (i === props.steps.length - 1) timers.push(setTimeout(() => emit('done'), 360))
      }, props.cadence * i + 140))
    })
  }
  if (props.active) start()
})
onBeforeUnmount(() => {
  document.removeEventListener('visibilitychange', onVisibility)
  window.removeEventListener('resize', onResize)
  clearTimeout(resizeT)
  timers.forEach(clearTimeout)
  stop()
})
</script>

<template>
  <div class="field" aria-hidden="true">
    <canvas ref="canvas" class="field-canvas"></canvas>
    <p v-if="steps.length" class="field-steps">
      <span v-for="(s, i) in steps" :key="i" :class="{ on: i < on }">{{ s }}</span>
    </p>
  </div>
</template>

<style scoped>
.field {
  position: relative;
  height: 128px;
  border-top: 1px solid var(--rule);
  border-bottom: 1px solid var(--rule);
  opacity: 0.9;
}
.field-canvas { position: absolute; inset: 0; width: 100%; height: 100%; display: block; }
.field-steps {
  position: absolute;
  left: 0; right: 0; bottom: 8px;
  display: flex;
  flex-wrap: wrap;
  gap: 14px;
  justify-content: center;
}
.field-steps span {
  font-family: var(--f-mono);
  text-transform: uppercase;
  letter-spacing: 0.13em;
  font-size: 10px;
  color: var(--ink);
  opacity: 0.3;
  transition: opacity 500ms var(--ease);
}
.field-steps span.on { opacity: 0.62; }
</style>
