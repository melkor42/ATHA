<script setup>
import { computed } from 'vue'
import UiRenderer from './UiRenderer.vue'
import { useCompose } from '../composables/useCompose.js'

const { schema, revealed } = useCompose()
const sections = computed(() =>
  Array.isArray(schema.value?.sections) ? schema.value.sections : []
)
</script>

<template>
  <section v-if="sections.length" class="result">
    <p class="label result-label">Answer</p>
    <div
      v-for="(s, i) in sections"
      :id="`section-${i}`"
      :key="i"
      class="section"
      :class="{ shown: i < revealed }"
    >
      <UiRenderer :node="s" />
    </div>
    <p class="label grounding">Composed from the ATHA knowledge graph</p>
  </section>
</template>

<style scoped>
.result {
  display: flex;
  flex-direction: column;
  gap: 44px;
  scroll-margin-top: 88px;
}
.result-label { opacity: 0.4; }
.section {
  opacity: 0;
  transform: translateY(10px);
  transition: opacity 600ms var(--ease), transform 600ms var(--ease);
  scroll-margin-top: 96px;
}
.section.shown { opacity: 1; transform: none; }
.grounding { margin-top: -12px; opacity: 0.35; }
</style>
