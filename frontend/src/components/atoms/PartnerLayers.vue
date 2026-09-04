<script setup>
import { computed } from 'vue'

const props = defineProps({ node: { type: Object, required: true } })
const layers = computed(() => (Array.isArray(props.node.layers) ? props.node.layers : []))
</script>

<template>
  <section class="atom partner-layers">
    <span class="rule" aria-hidden="true"></span>
    <h3 v-if="node.title" class="u-wipe">{{ node.title }}</h3>
    <p v-if="node.text" class="u-fade" style="--d: 260ms">{{ node.text }}</p>
    <ul v-if="layers.length">
      <li v-for="(l, i) in layers" :key="i" class="layer u-fade" :style="{ '--d': 360 + i * 130 + 'ms' }">
        <span class="ring">{{ i + 1 }}</span>
        <div class="content">
          <p class="label">{{ l.kind || 'Layer' }}</p>
          <h4>{{ l.name }}</h4>
          <p v-if="l.description" class="desc">{{ l.description }}</p>
        </div>
      </li>
    </ul>
  </section>
</template>

<style scoped>
.partner-layers { display: flex; flex-direction: column; gap: 16px; }
.partner-layers h3 { font-size: clamp(22px, 2.8vw, 28px); }
.partner-layers > p { font-size: 15px; line-height: 1.46; opacity: 0.75; max-width: 58ch; }
ul { margin: 0; padding: 0; list-style: none; }
.layer {
  display: grid;
  grid-template-columns: 28px 1fr;
  gap: 16px;
  align-items: start;
  padding: 13px 0;
  border-top: 1px solid var(--rule);
}
.layer:last-child { border-bottom: 1px solid var(--rule); }
.ring {
  display: grid;
  place-items: center;
  width: 26px;
  height: 26px;
  margin-top: 2px;
  border: 1px solid var(--slate);
  font-family: var(--f-mono);
  font-size: 10px;
  color: var(--slate);
}
.content h4 {
  margin: 2px 0 0;
  font-family: var(--f-display);
  font-variation-settings: "opsz" 144;
  font-weight: 400;
  font-size: 19px;
  letter-spacing: -0.02em;
  line-height: 1.2;
}
.desc {
  margin-top: 5px;
  font-size: 15px;
  line-height: 1.44;
  opacity: 0.72;
  max-width: 56ch;
}
</style>
