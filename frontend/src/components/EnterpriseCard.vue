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
const seeks = computed(() => {
  // EntityPayload: enterprises carry their SEEKS_EXPERTISE topics
  const s = entity.value.seeks ?? entity.value.topics
  return Array.isArray(s) ? s.join(', ') : s || ''
})
// metadata completeness: explicit field if present, else counted from
// the EntityPayload fields the backend hydrates
const metadata = computed(() => {
  if (entity.value.metadata) return entity.value.metadata
  const fields = ['sector', 'size', 'hq', 'contact', 'topics']
  const filled = fields.filter((f) => {
    const v = entity.value[f]
    return Array.isArray(v) ? v.length > 0 : Boolean(v)
  }).length
  return fields.length ? `${Math.round((filled / fields.length) * 100)}%` : ''
})
</script>

<template>
  <div class="card enterprise-card">
    <div class="k">EnterpriseCard</div>
    <h3>{{ entity.name ?? node.title ?? '' }}</h3>
    <div class="meta">
      <div v-if="entity.sector" class="row"><span>sector</span><b>{{ entity.sector }}</b></div>
      <div v-if="entity.size" class="row"><span>size</span><b>{{ entity.size }}</b></div>
      <div v-if="entity.hq" class="row"><span>hq</span><b>{{ entity.hq }}</b></div>
      <div v-if="metadata" class="row"><span>metadata</span><b>{{ metadata }}</b></div>
    </div>
    <div v-if="seeks" class="row seeks"><span>seeks</span><b>{{ seeks }}</b></div>
  </div>
</template>
