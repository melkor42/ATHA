<script setup>
import { computed, ref } from 'vue'

const mode = ref(document.documentElement.dataset.mode || 'day')
const target = computed(() => (mode.value === 'night' ? 'Day' : 'Night'))

function toggle() {
  const next = mode.value === 'night' ? 'day' : 'night'
  mode.value = next
  document.documentElement.dataset.mode = next
  try {
    localStorage.setItem('atha-mode', next)
  } catch (e) {
    /* storage unavailable */
  }
}
</script>

<template>
  <button type="button" class="mode-toggle" @click="toggle">{{ target }}</button>
</template>

<style scoped>
.mode-toggle {
  font-family: var(--f-mono);
  text-transform: uppercase;
  letter-spacing: 0.13em;
  font-size: 10.5px;
  color: var(--on-deep);
  opacity: 0.62;
  border-bottom: 1px solid currentColor;
  padding-bottom: 3px;
  transition: opacity 240ms var(--ease);
}
.mode-toggle:hover { opacity: 1; }
</style>
