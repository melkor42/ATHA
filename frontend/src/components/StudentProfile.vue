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
const children = computed(() =>
  Array.isArray(props.node?.children) ? props.node.children : []
)
</script>

<template>
  <div class="card student-profile">
    <div class="k">StudentProfile</div>
    <h3>{{ entity.name ?? node.title ?? '' }}</h3>
    <p v-if="entity.role" class="role">{{ entity.role }}</p>
    <p v-if="entity.story" class="story">{{ entity.story }}</p>
    <UiRenderer
      v-for="(child, i) in children"
      :key="i"
      :node="child"
      class="child"
    />
  </div>
</template>
