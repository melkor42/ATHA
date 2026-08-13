<script setup>
import { computed } from 'vue'
import UiRenderer from './UiRenderer.vue'

const props = defineProps({ node: { type: Object, required: true } })
const children = computed(() =>
  Array.isArray(props.node?.children) ? props.node.children : []
)
</script>

<template>
  <div class="card text-block">
    <h3 v-if="node.title">{{ node.title }}</h3>
    <p v-if="node.text">{{ node.text }}</p>
    <UiRenderer
      v-for="(child, i) in children"
      :key="i"
      :node="child"
      class="child"
    />
  </div>
</template>
