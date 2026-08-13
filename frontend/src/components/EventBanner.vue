<script setup>
import { computed, inject } from 'vue'
import UiRenderer from './UiRenderer.vue'

const props = defineProps({ node: { type: Object, required: true } })

const entities = inject('entities', null)
// real contract: entity_ids (list); entity_id tolerated for fixtures
const entityId = computed(() => {
  const ids = props.node?.entity_ids
  return (Array.isArray(ids) ? ids[0] : null) ?? props.node?.entity_id ?? null
})
const entity = computed(() =>
  entities ? entities.value?.[entityId.value] ?? {} : {}
)

// "when" line: node.when takes precedence, else entity date · location
const when = computed(() =>
  props.node?.when ||
  [entity.value.date, entity.value.location].filter(Boolean).join(' · ')
)
const children = computed(() =>
  Array.isArray(props.node?.children) ? props.node.children : []
)
</script>

<template>
  <div class="card banner">
    <div v-if="when" class="when">{{ when }}</div>
    <h3>{{ node.title ?? entity.name ?? '' }}</h3>
    <p v-if="node.text">{{ node.text }}</p>
    <UiRenderer
      v-for="(child, i) in children"
      :key="i"
      :node="child"
      class="child"
    />
  </div>
</template>
