<script setup>
import { computed } from 'vue'

const props = defineProps({ node: { type: Object, required: true } })
const facts = computed(() => (Array.isArray(props.node.facts) ? props.node.facts : []))
// A confirmed fact needs no pill — the pill marks what is not yet settled (§6).
const isOpen = (status) => status === 'proposed' || status === 'open'
</script>

<template>
  <section class="atom fact-list">
    <span class="rule" aria-hidden="true"></span>
    <h3 v-if="node.title" class="u-wipe">{{ node.title }}</h3>
    <p v-if="node.text" class="u-fade" style="--d: 260ms">{{ node.text }}</p>
    <dl>
      <div v-for="(f, i) in facts" :key="i" class="row u-fade" :style="{ '--d': 340 + i * 110 + 'ms' }">
        <dt class="label">{{ f.label }}</dt>
        <dd>
          <span class="value">{{ f.value }}</span>
          <span v-if="isOpen(f.status)" class="pill">{{ f.status }}</span>
        </dd>
      </div>
    </dl>
  </section>
</template>

<style scoped>
.fact-list { display: flex; flex-direction: column; gap: 16px; }
.fact-list h3 { font-size: clamp(22px, 2.8vw, 28px); }
.fact-list > p { font-size: 15px; line-height: 1.46; opacity: 0.75; max-width: 58ch; }
dl { margin: 0; display: flex; flex-direction: column; }
.row {
  display: grid;
  grid-template-columns: minmax(120px, 22%) 1fr;
  gap: 20px;
  padding: 13px 0;
  border-top: 1px solid var(--rule);
}
.row:last-child { border-bottom: 1px solid var(--rule); }
dd {
  margin: 0;
  display: flex;
  align-items: baseline;
  gap: 12px;
  flex-wrap: wrap;
}
.value {
  font-family: var(--f-display);
  font-variation-settings: "opsz" 144;
  font-weight: 400;
  font-size: 17px;
  letter-spacing: -0.018em;
  line-height: 1.28;
}
.pill {
  font-family: var(--f-mono);
  text-transform: uppercase;
  letter-spacing: 0.13em;
  font-size: 10px;
  color: var(--ferrous);
  border: 1px solid var(--ferrous);
  padding: 2px 7px;
}
@media (max-width: 560px) {
  .row { grid-template-columns: 1fr; gap: 4px; }
}
</style>
