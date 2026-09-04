<script setup>
import { ref } from 'vue'
import Hero from './components/Hero.vue'
import ChatPanel from './components/ChatPanel.vue'
import ResultPane from './components/ResultPane.vue'
import BrandSections from './components/BrandSections.vue'
import ClosingBand from './components/ClosingBand.vue'
import { useCompose, APPLY_HREF, APPLY_LABEL } from './composables/useCompose.js'

// Two surfaces, one conversation. Landing is a deep hero with the chat centred
// beneath it; the first composed answer turns the page into a reading layout —
// the answer carries the column, the agent keeps talking on the right.
const { phase, hasResult, restart } = useCompose()
const menuOpen = ref(false)

const NAV = [
  { label: 'The programme', href: '#programme' },
  { label: 'The five lenses', href: '#lenses' },
  { label: 'Who stands behind ATHA', href: '#who' }
]

function go(href) {
  menuOpen.value = false
  document.querySelector(href)?.scrollIntoView({ behavior: 'smooth', block: 'start' })
}
</script>

<template>
  <div class="app">
    <header class="chrome" :class="phase">
      <div class="chrome-inner">
        <div class="brand">
          <button
            v-if="hasResult"
            class="menu-toggle"
            type="button"
            :aria-expanded="menuOpen"
            aria-label="Menu"
            @click="menuOpen = !menuOpen"
          >
            <span class="bar"></span><span class="bar"></span>
          </button>
          <span class="wordmark">ATHA</span>
        </div>
        <div v-if="hasResult" class="chrome-actions">
          <a class="mini-apply" :href="APPLY_HREF">{{ APPLY_LABEL }}</a>
        </div>
      </div>
      <nav v-if="menuOpen" class="menu">
        <button v-for="n in NAV" :key="n.href" type="button" class="menu-link" @click="go(n.href)">
          {{ n.label }}
        </button>
        <span class="rule"></span>
        <button type="button" class="menu-link reset" @click="menuOpen = false; restart()">
          New conversation
        </button>
      </nav>
    </header>

    <main class="wrap" :class="phase">
      <div class="fold">
        <Hero v-if="!hasResult" />
        <section class="stage" :class="phase">
          <ResultPane v-if="hasResult" />
          <ChatPanel />
        </section>
      </div>
      <div class="brand-sections">
        <BrandSections />
      </div>
    </main>

    <ClosingBand />
  </div>
</template>

<style scoped>
.chrome {
  position: relative;
  z-index: 30;
}
.chrome.reading {
  position: sticky;
  top: 0;
  background: var(--paper);
  border-bottom: 1px solid var(--rule);
}
.chrome.landing {
  position: absolute;
  inset: 0 0 auto;
  color: var(--paper);
}
.chrome-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  padding: 16px clamp(22px, 5vw, 64px);
}
.brand { display: flex; align-items: center; gap: 14px; }
.wordmark {
  font-family: var(--f-display);
  font-variation-settings: "opsz" 144;
  font-weight: 400;
  font-size: 20px;
  letter-spacing: 0.06em;
}
.chrome.landing .wordmark { color: var(--paper); }
.chrome.reading .wordmark { color: var(--ink); }
.menu-toggle {
  display: flex;
  flex-direction: column;
  gap: 4px;
  width: 22px;
  padding: 5px 0;
}
.menu-toggle .bar { display: block; height: 1px; background: var(--ink); opacity: 0.8; }
.mini-apply {
  font-family: var(--f-mono);
  text-transform: uppercase;
  letter-spacing: 0.13em;
  font-size: 10.5px;
  color: var(--ink);
  opacity: 0.7;
  text-decoration: none;
  border-bottom: 1px solid var(--rule);
  padding-bottom: 3px;
  transition: opacity 240ms var(--ease);
}
.mini-apply:hover { opacity: 1; }

.menu {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: var(--paper);
  border-bottom: 1px solid var(--ink);
  padding: 8px clamp(22px, 5vw, 64px) 22px;
  display: flex;
  flex-direction: column;
}
.menu-link {
  text-align: left;
  font-family: var(--f-display);
  font-variation-settings: "opsz" 144;
  font-weight: 300;
  font-size: clamp(22px, 3.4vw, 30px);
  letter-spacing: -0.024em;
  color: var(--ink);
  padding: 10px 0;
  border-top: 1px solid transparent;
  transition: padding-left 240ms var(--ease);
}
.menu-link:hover { padding-left: 8px; }
.menu .rule { margin: 6px 0; }
.menu-link.reset { font-family: var(--f-body); font-size: 14px; letter-spacing: 0; opacity: 0.6; }

.wrap { display: flex; flex-direction: column; }
.fold { display: flex; flex-direction: column; }
/* the landing is one composition: band on top, agent in the rest of the fold */
.wrap.landing .fold { min-height: 100vh; min-height: 100svh; }
.stage { padding: clamp(34px, 6vh, 64px) clamp(22px, 5vw, 64px) 0; }
.stage.landing {
  flex: 1;
  display: flex;
  padding-top: clamp(24px, 3.6vh, 40px);
  padding-bottom: clamp(16px, 2.6vh, 26px);
}
.stage.reading {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 430px;
  gap: clamp(40px, 6vw, 96px);
  align-items: start;
  padding-bottom: clamp(40px, 7vh, 80px);
}
.stage.reading :deep(.chat.reading) {
  position: sticky;
  top: 76px;
  max-height: calc(100vh - 100px);
}
.brand-sections { padding: 0 clamp(22px, 5vw, 64px); margin-top: clamp(48px, 9vh, 104px); }

@media (max-width: 980px) {
  .stage.reading { grid-template-columns: 1fr; }
  .stage.reading :deep(.chat.reading) { position: static; max-height: none; }
}
</style>
