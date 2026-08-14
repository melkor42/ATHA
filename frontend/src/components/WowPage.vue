<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, provide, ref, watch } from 'vue'
import UiRenderer from './UiRenderer.vue'
import { TEMPO } from '../theme.js'

const props = defineProps({
  schema: { type: Object, required: true },
  persona: { type: Object, default: null }
})
const emit = defineEmits(['restart'])

// allowlists — the LLM only ever picks enum values (Phase A axis grammar:
// Spectrum × StyleMode, contract shared with backend/ui_schema.py)
const SPECTRA = new Set(['mycelium', 'terra', 'aurora', 'neon', 'void'])
const MODES = new Set(['none', 'minimal', 'retro', 'organic', 'earth', 'steampunk'])
const ACCENTS = {
  primary: 'var(--primary)',
  accent: 'var(--accent-tok)',
  success: 'var(--success)',
  warning: 'var(--warning)'
}
// precomputed aura RGB triples per ColorToken — ambient glow behind the
// page (harmonize with --primary/--accent-tok/--success/--warning)
const ACCENT_AURA = {
  primary: '110, 160, 214',
  accent: '201, 140, 158',
  success: '150, 178, 112',
  warning: '224, 162, 78'
}
const DEFAULT_AURA = '230, 190, 112'

const spectrum = computed(() => (SPECTRA.has(props.schema?.spectrum) ? props.schema.spectrum : 'terra'))
const mode = computed(() => (MODES.has(props.schema?.mode) ? props.schema.mode : 'none'))
// per-mode ambient modulation, mirrored from prototypes/axis-preview.html.
// Merge rule — MODE WINS: the mode sets the field tier (breathing tempo,
// aura dim, grain); the persona tone fine-tunes the tempo only in mode-none.
const AMBIENT = {
  none: {},                                            // persona tone drives tempo
  minimal: { dur: '16s', paused: true, dim: 0.35, grain: 0.02 },
  retro: { dur: '10s' },
  organic: { dur: '20s' },
  earth: { dur: '22s', dim: 0.8, grain: 0.12 },
  steampunk: { dur: '13s' }
}
const amb = computed(() => AMBIENT[mode.value] ?? {})
// persona signature: tone sets the ambient breathing tempo (mode-none only)
const toneTempo = computed(() => {
  const tone = (props.persona?.tone || '').toLowerCase()
  if (tone.includes('calm') || tone.includes('warm')) return TEMPO.calm
  if (tone.includes('direct')) return TEMPO.direct
  if (tone.includes('playful')) return TEMPO.playful
  return TEMPO.default
})
const breathe = computed(() => amb.value.dur ?? toneTempo.value)
const breathePlay = computed(() => (amb.value.paused ? 'paused' : 'running'))
const grain = computed(() => String(amb.value.grain ?? 0.035))
// accent comes from the persona's ColorToken (backend); fixtures may
// carry it directly on the schema as a fallback
const accent = computed(() =>
  ACCENTS[props.persona?.accent_color] ?? ACCENTS[props.schema?.accent] ?? 'var(--accent-tok)'
)
// aura alpha is dimmed per mode (minimal whispers, earth settles)
const aura = computed(() => {
  const rgb =
    ACCENT_AURA[props.persona?.accent_color] ?? ACCENT_AURA[props.schema?.accent] ?? DEFAULT_AURA
  return `rgba(${rgb}, ${(0.1 * (amb.value.dim ?? 1)).toFixed(3)})`
})
// the ambient layers live on body::before/body::after — outside this
// component's cascade — so persona tint, tempo and mode atmosphere are
// mirrored onto the document root
watch(aura, (v) => document.documentElement.style.setProperty('--aura', v), { immediate: true })
watch(breathe, (v) => document.documentElement.style.setProperty('--breathe-dur', v), { immediate: true })
watch(breathePlay, (v) => document.documentElement.style.setProperty('--breathe-play', v), { immediate: true })
watch(grain, (v) => document.documentElement.style.setProperty('--grain-opacity', v), { immediate: true })
onBeforeUnmount(() => {
  document.documentElement.style.removeProperty('--aura')
  document.documentElement.style.removeProperty('--breathe-dur')
  document.documentElement.style.removeProperty('--breathe-play')
  document.documentElement.style.removeProperty('--grain-opacity')
})
const layout = computed(() => (props.schema?.layout === 'grid' ? 'grid' : 'single'))
const sections = computed(() =>
  Array.isArray(props.schema?.sections) ? props.schema.sections : []
)

// components resolve their data from the entities map by entity_id
provide('entities', computed(() => props.schema?.entities ?? {}))

// wide sections span both columns in grid layouts
function isWide(node) {
  return node?.component === 'TextBlock' || node?.component === 'EventBanner'
}

// sequential reveal, ~380ms stagger like the prototype
const revealed = ref(0)
onMounted(async () => {
  await nextTick()
  for (let i = 0; i < sections.value.length; i++) {
    await new Promise((r) => setTimeout(r, 380))
    revealed.value = i + 1
  }
})
</script>

<template>
  <div class="wow-page" :class="['spectrum-' + spectrum, 'mode-' + mode, layout]" :style="{ '--accent': accent, '--breathe-dur': breathe }">
    <UiRenderer
      v-for="(node, i) in sections"
      :key="i"
      :node="node"
      class="section"
      :class="{ on: i < revealed, wide: isWide(node) }"
    />
    <div class="again">
      <button class="pill" type="button" @click="emit('restart')">Compose another</button>
    </div>
  </div>
</template>
