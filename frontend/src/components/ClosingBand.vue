<script setup>
import DotField from './DotField.vue'
import { useCompose } from '../composables/useCompose.js'

const { currentCta } = useCompose()
</script>

<template>
  <footer class="closing deep">
    <DotField />
    <div class="closing-inner">
      <span class="seam" aria-hidden="true"></span>
      <p class="statement">A conference resets. A laboratory compounds.</p>
      <p class="sub">
        The temporary experience creates a permanent capability — on all five lenses,
        defended in the room, owned by a person.
      </p>
      <a class="ask" :href="currentCta.href">{{ currentCta.label }}<span class="arrow">→</span></a>
      <p class="label colophon">ATHA · OneMundi × WBS</p>
    </div>
  </footer>
</template>

<style scoped>
.closing {
  position: relative;
  overflow: hidden;
  margin-top: 120px;
  padding: clamp(56px, 10vh, 110px) clamp(22px, 5vw, 64px) clamp(40px, 6vh, 64px);
}
.closing-inner { position: relative; max-width: 1080px; }
.seam {
  display: block;
  width: 44px;
  height: 3px;
  background: var(--signal);
  margin-bottom: 26px;
}
.statement {
  font-family: var(--f-display);
  font-variation-settings: "opsz" 144;
  font-weight: 400;
  font-size: clamp(26px, 3.6vw, 40px);
  letter-spacing: -0.026em;
  line-height: 1.1;
  max-width: 24ch;
}
.sub {
  margin-top: 18px;
  max-width: 52ch;
  font-size: 16px;
  line-height: 1.5;
  color: var(--on-deep);
  opacity: 0.6;
}
.ask {
  margin-top: 34px;
  display: inline-flex;
  gap: 12px;
  align-items: baseline;
  color: var(--on-deep);
  text-decoration: none;
  font-size: 15px;
  font-weight: 600;
  border-bottom: 1px solid var(--signal);
  padding-bottom: 6px;
  transition: gap 240ms var(--ease);
}
.ask:hover { gap: 18px; }
.arrow { font-weight: 400; }
.colophon { color: var(--on-deep); opacity: 0.35; margin-top: 56px; }
</style>
