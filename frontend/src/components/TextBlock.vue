<script setup>
import { computed } from 'vue'
import UiRenderer from './UiRenderer.vue'

// Silent fallback: any component type the registry does not know still renders
// its copy as plain text rather than breaking the page.
const props = defineProps({ node: { type: Object, required: true } })
const children = computed(() =>
  Array.isArray(props.node?.children) ? props.node.children : []
)
</script>

<template>
  <section class="atom text-block">
    <span class="rule" aria-hidden="true"></span>
    <h3 v-if="node.title">{{ node.title }}</h3>
    <p v-if="node.text">{{ node.text }}</p>
    <UiRenderer
      v-for="(child, i) in children"
      :key="i"
      :node="child"
      class="child"
    />
  </section>
</template>

<style scoped>
.text-block { display: flex; flex-direction: column; gap: 14px; }
.text-block h3 { font-size: clamp(22px, 2.8vw, 28px); }
.text-block p { font-size: 16px; line-height: 1.48; opacity: 0.82; max-width: 62ch; }
</style>
