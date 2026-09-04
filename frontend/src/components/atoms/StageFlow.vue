<script setup>
import { computed } from 'vue'

const props = defineProps({ node: { type: Object, required: true } })
const stages = computed(() => (Array.isArray(props.node.stages) ? props.node.stages : []))
</script>

<template>
  <section class="atom stage-flow">
    <span class="rule" aria-hidden="true"></span>
    <h3 v-if="node.title" class="u-wipe">{{ node.title }}</h3>
    <p v-if="node.text" class="u-fade" style="--d: 260ms">{{ node.text }}</p>
    <ol v-if="stages.length">
      <svg class="spine" viewBox="0 0 1 1" preserveAspectRatio="none" aria-hidden="true">
        <line x1="0.5" y1="0" x2="0.5" y2="1" pathLength="1" vector-effect="non-scaling-stroke" class="u-draw" style="--d: 380ms" />
      </svg>
      <li v-for="(s, i) in stages" :key="i" class="stage u-fade" :style="{ '--d': 420 + i * 90 + 'ms' }">
        <span class="num">{{ String(i + 1).padStart(2, '0') }}</span>
        <div class="body">
          <h4>{{ s.name }}</h4>
          <p v-if="s.description">{{ s.description }}</p>
        </div>
      </li>
    </ol>
  </section>
</template>

<style scoped>
.stage-flow { display: flex; flex-direction: column; gap: 16px; }
.stage-flow h3 { font-size: clamp(22px, 2.8vw, 28px); }
.stage-flow > p { font-size: 15px; line-height: 1.46; opacity: 0.75; max-width: 58ch; }
ol {
  position: relative;
  margin: 0;
  padding: 0;
  list-style: none;
  display: flex;
  flex-direction: column;
}
.spine {
  position: absolute;
  left: 13px;
  top: 10px;
  bottom: 10px;
  width: 1px;
  height: auto;
}
.spine line { stroke: var(--rule); stroke-width: 1; opacity: 0.85; }
.stage {
  display: grid;
  grid-template-columns: 28px 1fr;
  gap: 16px;
  align-items: start;
  padding: 9px 0;
}
.num {
  font-family: var(--f-mono);
  font-size: 10px;
  letter-spacing: 0.1em;
  color: var(--ink);
  opacity: 0.45;
  padding-top: 5px;
  text-align: center;
}
.body h4 {
  margin: 0;
  font-family: var(--f-display);
  font-variation-settings: "opsz" 144;
  font-weight: 400;
  font-size: 18px;
  letter-spacing: -0.02em;
  line-height: 1.2;
}
.body p {
  margin-top: 4px;
  font-size: 15px;
  line-height: 1.44;
  opacity: 0.72;
  max-width: 56ch;
}
</style>
