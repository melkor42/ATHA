<script setup>
import { computed, inject } from 'vue'

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

const score = computed(() =>
  typeof entity.value.score === 'number'
    ? Math.max(0, Math.min(100, entity.value.score))
    : null
)
const topics = computed(() => {
  const t = entity.value.topics
  return Array.isArray(t) ? t.join(', ') : t || ''
})
// Contact pill: explicit node button label, else entity contact, else default
const contactLabel = computed(() =>
  props.node?.button?.label || entity.value.contact || 'Contact'
)
</script>

<template>
  <div class="card signal-card">
    <div class="k">SignalCard</div>
    <h3>{{ entity.name ?? node.title ?? '' }}</h3>
    <p v-if="entity.school">{{ entity.school }}</p>
    <div v-if="score !== null" class="score"><i :style="{ width: score + '%' }"></i></div>
    <div v-if="score !== null || topics" class="row">
      <span v-if="score !== null" class="num">match <b>{{ score }}</b></span>
      <span v-if="topics">{{ topics }}</span>
    </div>
    <button class="cta solid" type="button">{{ contactLabel }}</button>
  </div>
</template>
