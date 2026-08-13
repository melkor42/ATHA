<script setup>
import { computed, onMounted, onBeforeUnmount, ref, watch } from 'vue'
import { DEFAULT_HUES } from '../theme.js'

const props = defineProps({
  steps: { type: Array, required: true },
  cadence: { type: Number, default: 350 }, // prototype cadence
  active: { type: Boolean, default: true }, // animate only while composing
  exiting: { type: Boolean, default: false }, // exit choreography toward the reveal
  dim: { type: Number, default: 0 }, // residual fade level — > 0 keeps the field alive as substrate
  hues: { type: Array, default: () => DEFAULT_HUES } // persona-tinted pulse palette
})
const emit = defineEmits(['done'])

const on = ref(0)
const canvas = ref(null)
let raf = 0, running = false, lastDraw = 0
// dpr capped at 1 — the loop now lives forever and glow-based visuals are
// indistinguishable at dpr 1
const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches

// after reveal with dim > 0 the stage becomes a faint substrate below the content
const substrate = computed(() => props.exiting && props.dim > 0)

let seed = 7
const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647

let nodes = [], edges = []
let pulses = []
let litEdges = new Map() // "a-b" -> { heat, hue }

function build(w, h) {
  const count = Math.round((w * h) / 16000)
  const n = Math.max(30, Math.min(90, count))
  nodes = Array.from({ length: n }, () => ({
    x: 16 + rnd() * (w - 32), y: 16 + rnd() * (h - 32), r: 1.8 + rnd() * 2.4, lit: 0
  }))
  const adj = nodes.map(() => [])
  edges = []
  nodes.forEach((node, i) => {
    node.adj = adj[i]
    const near = nodes
      .map((m, j) => [i === j ? 1e9 : (node.x - m.x) ** 2 + (node.y - m.y) ** 2, j])
      .sort((a, b) => a[0] - b[0])
    near.slice(0, 3).forEach(([, j]) => {
      if (!adj[i].includes(j)) { adj[i].push(j); adj[j].push(i); edges.push([i, j]) }
    })
  })
  pulses = Array.from({ length: Math.max(3, Math.round(n / 16)) }, () =>
    ({ from: 0, to: nodes[0].adj[0] ?? 1, t: rnd() }))
}

function spawnPulse() {
  // occasional extra pulse keeps the field alive — a tad more flashy
  if (pulses.length < 9 && rnd() < 0.35) {
    const start = Math.floor(rnd() * nodes.length)
    const ns = nodes[start]
    pulses.push({ from: start, to: ns.adj[Math.floor(rnd() * ns.adj.length)] ?? 0, t: 0 })
  }
}

function draw(ctx, w, h, time, fade) {
  ctx.clearRect(0, 0, w, h)
  // base edges
  ctx.strokeStyle = `rgba(241,237,230,${0.07 * fade})`; ctx.lineWidth = 1
  edges.forEach(([a, b]) => {
    ctx.beginPath(); ctx.moveTo(nodes[a].x, nodes[a].y); ctx.lineTo(nodes[b].x, nodes[b].y); ctx.stroke()
  })
  // lit edges decay — the wake of each pulse
  litEdges.forEach((e, key) => {
    e.heat -= 0.014
    if (e.heat <= 0) { litEdges.delete(key); return }
    const [a, b] = key.split('-').map(Number)
    ctx.strokeStyle = e.hue
    ctx.globalAlpha = e.heat * 0.55 * fade
    ctx.lineWidth = 1 + e.heat
    ctx.beginPath(); ctx.moveTo(nodes[a].x, nodes[a].y); ctx.lineTo(nodes[b].x, nodes[b].y); ctx.stroke()
    ctx.globalAlpha = 1
  })
  // nodes
  nodes.forEach((n, i) => {
    n.lit = Math.max(0, n.lit - 0.01)
    const hue = props.hues[i % props.hues.length]
    // halo on lit nodes
    if (n.lit > 0.02) {
      const g = ctx.createRadialGradient(n.x, n.y, 0, n.x, n.y, n.r * 6)
      g.addColorStop(0, hue); g.addColorStop(1, 'rgba(0,0,0,0)')
      ctx.globalAlpha = n.lit * 0.35 * fade
      ctx.fillStyle = g; ctx.beginPath(); ctx.arc(n.x, n.y, n.r * 6, 0, 7); ctx.fill()
      ctx.globalAlpha = 1
    }
    ctx.beginPath(); ctx.arc(n.x, n.y, n.r + n.lit * 2.5, 0, 7)
    ctx.fillStyle = n.lit > 0.02 ? hue : `rgba(241,237,230,${0.28 * fade})`
    ctx.globalAlpha = (0.35 + n.lit * 0.65) * fade; ctx.fill(); ctx.globalAlpha = 1
  })
  // pulses — the traveling tick, multiple at once
  pulses.forEach(p => {
    p.t += 0.018
    if (p.t >= 1) {
      const arrived = nodes[p.to]
      arrived.lit = 1
      const key = p.from < p.to ? `${p.from}-${p.to}` : `${p.to}-${p.from}`
      litEdges.set(key, { heat: 1, hue: props.hues[Math.floor(time / 1800 + p.from) % props.hues.length] })
      spawnPulse()
      const nexts = arrived.adj.filter(j => j !== p.from)
      const to = nexts.length ? nexts[Math.floor(rnd() * nexts.length)] : (arrived.adj[0] ?? p.from)
      Object.assign(p, { from: p.to, to, t: 0 })
    }
    const a = nodes[p.from], b = nodes[p.to]
    const x = a.x + (b.x - a.x) * p.t, y = a.y + (b.y - a.y) * p.t
    const col = props.hues[Math.floor(time / 1800 + p.from) % props.hues.length]
    const g = ctx.createRadialGradient(x, y, 0, x, y, 16)
    g.addColorStop(0, col); g.addColorStop(1, 'rgba(0,0,0,0)')
    ctx.globalAlpha = fade
    ctx.fillStyle = g; ctx.beginPath(); ctx.arc(x, y, 16, 0, 7); ctx.fill()
    // bright core with a thin white ring — the flashy bit
    ctx.fillStyle = '#EFFFFC'; ctx.beginPath(); ctx.arc(x, y, 2, 0, 7); ctx.fill()
    ctx.strokeStyle = 'rgba(255,255,255,0.5)'; ctx.lineWidth = 0.8
    ctx.beginPath(); ctx.arc(x, y, 4 + Math.sin(time / 120 + p.from) * 1.2, 0, 7); ctx.stroke()
    ctx.globalAlpha = 1
  })
}

function loop(time) {
  if (!running) return
  const cv = canvas.value
  // substrate mode throttles to ~15 fps; loading stays full rate
  if (!substrate.value || time - lastDraw >= 66) {
    lastDraw = time
    if (cv) {
      // exit choreography: ease the field down to substrate level (or out entirely)
      const target = props.exiting ? props.dim : 1
      fade.value += (target - fade.value) * 0.08
      draw(cv.getContext('2d'), cv.width, cv.height, time, fade.value)
      if (props.exiting && props.dim === 0 && fade.value < 0.02) { stop(); return }
    }
  }
  raf = requestAnimationFrame(loop)
}

const fade = ref(1)

// one static frame, never an rAF loop (prefers-reduced-motion)
function paintStatic(alpha) {
  const cv = canvas.value
  if (!cv) return
  const w = cv.clientWidth, h = cv.clientHeight
  cv.width = w; cv.height = h
  if (!nodes.length) build(w, h)
  draw(cv.getContext('2d'), w, h, 1200, alpha)
}

function start() {
  const cv = canvas.value
  if (!cv || running) return
  const w = cv.clientWidth, h = cv.clientHeight
  cv.width = w; cv.height = h
  build(w, h)
  fade.value = 1
  if (reducedMotion) { draw(cv.getContext('2d'), w, h, 1200, 1); return }
  running = true
  lastDraw = 0
  raf = requestAnimationFrame(loop)
}
function stop() { running = false; cancelAnimationFrame(raf); raf = 0 }

// pause rAF while the tab is hidden — the substrate loop lives forever
function onVisibility() {
  if (document.hidden) { cancelAnimationFrame(raf); raf = 0 }
  else if (running && !raf) raf = requestAnimationFrame(loop)
}

watch(() => props.active, v => {
  if (v) start()
  else if (!props.exiting) stop() // exiting keeps the loop alive for the dissolve/substrate
})
watch(() => props.exiting, v => {
  if (!v) return
  if (reducedMotion) { paintStatic(props.dim); return } // one static faint frame
  if (!running) start() // safety: never exit from a frozen canvas
})

onMounted(() => {
  document.addEventListener('visibilitychange', onVisibility)
  props.steps.forEach((_, i) => {
    setTimeout(() => {
      on.value = i + 1
      if (i === props.steps.length - 1) setTimeout(() => emit('done'), 400)
    }, props.cadence * i + 150)
  })
  if (props.active) start()
})
onBeforeUnmount(() => {
  document.removeEventListener('visibilitychange', onVisibility)
  stop()
})
</script>

<template>
  <div class="theater-stage" :class="{ exiting, substrate }">
    <canvas ref="canvas" class="pulse-canvas"></canvas>
    <div class="theater-steps" aria-live="polite">
      <span v-for="(s, i) in steps" :key="i" class="step" :class="{ on: i < on }">{{ s }}</span>
    </div>
  </div>
</template>

<style scoped>
.theater-stage {
  position: fixed;
  inset: 0;
  z-index: 5;
  background: var(--bg);
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  transition: opacity 0.8s var(--ease), visibility 0.8s;
}
.theater-stage.exiting:not(.substrate) { opacity: 0; visibility: hidden; pointer-events: none; }
/* substrate mode: faint living field below the content */
.theater-stage.substrate { z-index: 0; background: transparent; pointer-events: none; }
.theater-stage.substrate .theater-steps { display: none; }
.pulse-canvas { position: absolute; inset: 0; width: 100%; height: 100%; display: block; }
.theater-steps {
  position: relative;
  z-index: 1;
  display: flex;
  flex-wrap: wrap;
  gap: 18px;
  justify-content: center;
  padding: 0 32px 40px;
}
.step {
  color: var(--subtle);
  font: 500 12px var(--font-mono);
  opacity: 0;
  transform: translateY(6px);
  transition: all 0.5s var(--ease);
  white-space: nowrap;
}
.step.on { opacity: 1; transform: none; color: var(--muted); }
.step.on::before { content: "✓ "; color: var(--success); }
</style>
