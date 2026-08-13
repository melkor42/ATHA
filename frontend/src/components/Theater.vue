<script setup>
import { onMounted, onBeforeUnmount, ref, watch } from 'vue'

const props = defineProps({
  steps: { type: Array, required: true },
  cadence: { type: Number, default: 350 }, // prototype cadence
  active: { type: Boolean, default: true } // animate only while composing
})
const emit = defineEmits(['done'])

const on = ref(0)
const canvas = ref(null)
let raf = 0, running = false, dpr = 1

// brand support palette — the pulse travels through the identity
const HUES = ['#D8A24C', '#CF7053', '#9A7FC8', '#5E92C4', '#8FA96E', '#BD8794']

let seed = 7
const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647

let nodes = [], edges = [], adj = [], pulse = null
let neurons = [], spark = null

function build(w, h) {
  // left half: the network graph
  const gw = w * 0.52
  nodes = Array.from({ length: 12 }, () => ({
    x: 20 + rnd() * (gw - 40), y: 16 + rnd() * (h - 32), r: 2 + rnd() * 2, lit: 0
  }))
  adj = nodes.map(() => [])
  edges = []
  nodes.forEach((n, i) => {
    const near = nodes
      .map((m, j) => [i === j ? 1e9 : (n.x - m.x) ** 2 + (n.y - m.y) ** 2, j])
      .sort((a, b) => a[0] - b[0])
    near.slice(0, 3).forEach(([, j]) => {
      if (!adj[i].includes(j)) { adj[i].push(j); adj[j].push(i); edges.push([i, j]) }
    })
  })
  pulse = { from: 0, to: adj[0][0] ?? 1, t: 0 }
  // right half: the neural strip
  const layers = [4, 6, 6, 3]
  const x0 = w * 0.62, x1 = w - 24
  neurons = layers.map((c, li) => Array.from({ length: c }, (_, ni) => ({
    x: x0 + (x1 - x0) * (li / (layers.length - 1)),
    y: h / 2 + (ni - (c - 1) / 2) * ((h - 44) / Math.max(c - 1, 1)),
    lit: 0
  })))
  spark = { li: 0, from: 0, to: 2, t: 0 }
}

function draw(ctx, w, h, time) {
  ctx.clearRect(0, 0, w, h)
  // graph edges + nodes
  ctx.strokeStyle = 'rgba(241,237,230,0.12)'; ctx.lineWidth = 1
  edges.forEach(([a, b]) => { ctx.beginPath(); ctx.moveTo(nodes[a].x, nodes[a].y); ctx.lineTo(nodes[b].x, nodes[b].y); ctx.stroke() })
  nodes.forEach((n, i) => {
    n.lit = Math.max(0, n.lit - 0.008)
    ctx.beginPath(); ctx.arc(n.x, n.y, n.r + n.lit * 2.5, 0, 7)
    ctx.fillStyle = n.lit > 0.02 ? HUES[i % HUES.length] : 'rgba(241,237,230,0.30)'
    ctx.globalAlpha = 0.35 + n.lit * 0.65; ctx.fill(); ctx.globalAlpha = 1
  })
  // the pulse: one node to the next
  pulse.t += 0.016
  if (pulse.t >= 1) {
    nodes[pulse.to].lit = 1
    const nexts = adj[pulse.to].filter(j => j !== pulse.from)
    const to = nexts.length ? nexts[Math.floor(rnd() * nexts.length)] : (adj[pulse.to][0] ?? pulse.from)
    pulse = { from: pulse.to, to, t: 0 }
  }
  {
    const a = nodes[pulse.from], b = nodes[pulse.to]
    const x = a.x + (b.x - a.x) * pulse.t, y = a.y + (b.y - a.y) * pulse.t
    const col = HUES[Math.floor(time / 2400) % HUES.length]
    const g = ctx.createRadialGradient(x, y, 0, x, y, 14)
    g.addColorStop(0, col); g.addColorStop(1, 'rgba(0,0,0,0)')
    ctx.fillStyle = g; ctx.beginPath(); ctx.arc(x, y, 14, 0, 7); ctx.fill()
    ctx.fillStyle = '#F1EDE6'; ctx.beginPath(); ctx.arc(x, y, 1.6, 0, 7); ctx.fill()
  }
  // neural links + neurons
  ctx.strokeStyle = 'rgba(241,237,230,0.07)'
  for (let li = 0; li < neurons.length - 1; li++)
    neurons[li].forEach(a => neurons[li + 1].forEach(b => { ctx.beginPath(); ctx.moveTo(a.x, a.y); ctx.lineTo(b.x, b.y); ctx.stroke() }))
  neurons.forEach((layer, li) => layer.forEach(n => {
    n.lit = Math.max(0, n.lit - 0.02)
    ctx.beginPath(); ctx.arc(n.x, n.y, 2.5 + n.lit * 2, 0, 7)
    ctx.fillStyle = n.lit > 0.02 ? HUES[(li + 1) % HUES.length] : 'rgba(241,237,230,0.18)'
    ctx.globalAlpha = 0.3 + n.lit * 0.7; ctx.fill(); ctx.globalAlpha = 1
  }))
  // the spark: layer to layer
  spark.t += 0.028
  if (spark.t >= 1) {
    neurons[spark.li + 1][spark.to].lit = 1
    spark = spark.li + 2 < neurons.length
      ? { li: spark.li + 1, from: spark.to, to: Math.floor(rnd() * neurons[spark.li + 2].length), t: 0 }
      : { li: 0, from: Math.floor(rnd() * neurons[0].length), to: Math.floor(rnd() * neurons[1].length), t: 0 }
  } else {
    const a = neurons[spark.li][spark.from], b = neurons[spark.li + 1][spark.to]
    ctx.fillStyle = HUES[(spark.li + 2) % HUES.length]
    ctx.beginPath(); ctx.arc(a.x + (b.x - a.x) * spark.t, a.y + (b.y - a.y) * spark.t, 2, 0, 7); ctx.fill()
  }
}

function loop(time) {
  if (!running) return
  const cv = canvas.value
  if (cv) draw(cv.getContext('2d'), cv.width / dpr, cv.height / dpr, time)
  raf = requestAnimationFrame(loop)
}

function start() {
  const cv = canvas.value
  if (!cv || running) return
  dpr = window.devicePixelRatio || 1
  const w = cv.clientWidth, h = cv.clientHeight
  cv.width = w * dpr; cv.height = h * dpr
  cv.getContext('2d').scale(dpr, dpr)
  build(w, h)
  running = true
  raf = requestAnimationFrame(loop)
}
function stop() { running = false; cancelAnimationFrame(raf) }

watch(() => props.active, v => (v ? start() : stop()))

onMounted(() => {
  props.steps.forEach((_, i) => {
    setTimeout(() => {
      on.value = i + 1
      if (i === props.steps.length - 1) setTimeout(() => emit('done'), 400)
    }, props.cadence * i + 150)
  })
  if (props.active) start()
})
onBeforeUnmount(stop)
</script>

<template>
  <div class="theater" aria-live="polite">
    <span v-for="(s, i) in steps" :key="i" class="step" :class="{ on: i < on }">{{ s }}</span>
    <canvas v-show="active" ref="canvas" class="pulse-canvas"></canvas>
  </div>
</template>

<style scoped>
.pulse-canvas { width: 100%; height: 170px; margin-top: 14px; display: block; }
</style>
