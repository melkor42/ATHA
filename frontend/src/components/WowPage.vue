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
// precomputed aura literals per ColorToken — ambient glow behind the page
// (harmonize with --primary/--accent-tok/--success/--warning, no color-mix)
const ACCENT_AURA = {
  primary: 'rgba(110, 160, 214, 0.10)',
  accent: 'rgba(201, 140, 158, 0.10)',
  success: 'rgba(150, 178, 112, 0.10)',
  warning: 'rgba(224, 162, 78, 0.10)'
}
const DEFAULT_AURA = 'rgba(230, 190, 112, 0.10)'

const spectrum = computed(() => (SPECTRA.has(props.schema?.spectrum) ? props.schema.spectrum : 'terra'))
const mode = computed(() => (MODES.has(props.schema?.mode) ? props.schema.mode : 'none'))
// persona signature: tone sets the ambient breathing tempo
const breathe = computed(() => {
  const tone = (props.persona?.tone || '').toLowerCase()
  if (tone.includes('calm') || tone.includes('warm')) return TEMPO.calm
  if (tone.includes('direct')) return TEMPO.direct
  if (tone.includes('playful')) return TEMPO.playful
  return TEMPO.default
})
// accent comes from the persona's ColorToken (backend); fixtures may
// carry it directly on the schema as a fallback
const accent = computed(() =>
  ACCENTS[props.persona?.accent_color] ?? ACCENTS[props.schema?.accent] ?? 'var(--accent-tok)'
)
const aura = computed(() =>
  ACCENT_AURA[props.persona?.accent_color] ?? ACCENT_AURA[props.schema?.accent] ?? DEFAULT_AURA
)
// the ambient layers live on body::before/body::after — outside this
// component's cascade — so persona tint and tempo are mirrored onto the root
watch(aura, (v) => document.documentElement.style.setProperty('--aura', v), { immediate: true })
watch(breathe, (v) => document.documentElement.style.setProperty('--breathe-dur', v), { immediate: true })
onBeforeUnmount(() => {
  document.documentElement.style.removeProperty('--aura')
  document.documentElement.style.removeProperty('--breathe-dur')
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
  <div class="wow-page" :class="['spectrum-' + spectrum, mode !== 'none' ? 'mode-' + mode : '', layout]" :style="{ '--accent': accent, '--breathe-dur': breathe }">
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
