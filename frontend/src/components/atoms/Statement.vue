<script setup>
defineProps({ node: { type: Object, required: true } })
</script>

<template>
  <section class="atom statement">
    <span class="rule" aria-hidden="true"></span>
    <h3 v-if="node.title" class="u-wipe">{{ node.title }}</h3>
    <p v-if="node.text" class="u-fade" style="--d: 320ms">{{ node.text }}</p>
  </section>
</template>

<style scoped>
.statement {
  display: flex;
  flex-direction: column;
  gap: 14px;
}
.statement h3 { font-size: clamp(24px, 3.4vw, 34px); }
.statement p {
  max-width: 62ch;
  font-size: 16px;
  line-height: 1.48;
  opacity: 0.82;
}
</style>
