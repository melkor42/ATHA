<script setup>
import { computed, nextTick, onMounted, provide, ref } from 'vue'
import UiRenderer from './UiRenderer.vue'

const props = defineProps({
  schema: { type: Object, required: true },
  persona: { type: Object, default: null }
})
const emit = defineEmits(['restart'])

// allowlists — the LLM only ever picks enum values (ticket 07)
const THEMES = new Set(['boardroom', 'festival', 'garden', 'ledger'])
const ACCENTS = {
  primary: 'var(--primary)',
  accent: 'var(--accent-tok)',
  success: 'var(--success)',
  warning: 'var(--warning)'
}

const theme = computed(() => (THEMES.has(props.schema?.theme) ? props.schema.theme : 'boardroom'))
// accent comes from the persona's ColorToken (backend); fixtures may
// carry it directly on the schema as a fallback
const accent = computed(() =>
  ACCENTS[props.persona?.accent_color] ?? ACCENTS[props.schema?.accent] ?? 'var(--accent-tok)'
)
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
  <div class="wow-page" :class="['theme-' + theme, layout]" :style="{ '--accent': accent }">
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
