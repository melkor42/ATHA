<script setup>
import { onMounted, onUnmounted, ref } from 'vue'
import Hero from './components/Hero.vue'
import DotField from './components/DotField.vue'
import ChatPanel from './components/ChatPanel.vue'
import ResultPane from './components/ResultPane.vue'
import BrandSections from './components/BrandSections.vue'
import EditionOverview from './components/EditionOverview.vue'
import ClosingBand from './components/ClosingBand.vue'
import ModeToggle from './components/ModeToggle.vue'
import ArrivalOverlay from './components/ArrivalOverlay.vue'
import { useCompose } from './composables/useCompose.js'
import { useArrival } from './composables/useArrival.js'

// One header, two heights: it opens tall with the page's claim and snaps to a
// single row as soon as the visitor scrolls into the work, and scrolling back to
// the top gives the claim back. Scroll position is the only input — the agent's
// phase never restyles the band, so navigation and the CTA never move.
const { phase, hasResult, restart, currentCta } = useCompose()
const { arrived } = useArrival()
const menuOpen = ref(false)
const atTop = ref(true)
const currentPage = ref('home')

function trackTop() {
  // Growing the band lengthens the document, so it may only happen where
  // nothing is scrolled off: a wider threshold shoved the page down mid-scroll
  // and read as resistance against the direction of travel.
  const next = window.scrollY < 2
  if (next !== atTop.value) atTop.value = next
}

function onKeydown(event) {
  if (event.key === 'Escape') menuOpen.value = false
}

// The toggle flips itself; only a click clear of the band closes the menu.
function onDocumentClick(event) {
  if (!menuOpen.value) return
  if (event.target instanceof Element && event.target.closest('.chrome')) return
  menuOpen.value = false
}

onMounted(() => {
  window.addEventListener('scroll', trackTop, { passive: true })
  window.addEventListener('keydown', onKeydown)
  document.addEventListener('click', onDocumentClick)
  trackTop()
})
onUnmounted(() => {
  window.removeEventListener('scroll', trackTop)
  window.removeEventListener('keydown', onKeydown)
  document.removeEventListener('click', onDocumentClick)
})

const NAV = [
  { label: 'Ask ATHA \u2014 Your Composer', page: 'home' },
  { label: 'The ATHA concept', page: 'about' }
]

function switchPage(page) {
  currentPage.value = page
  menuOpen.value = false
  window.scrollTo({ top: 0, behavior: 'auto' })
}
</script>

<template>
  <div class="app" :class="[phase, currentPage, { 'is-open': atTop }]">
    <ArrivalOverlay v-if="!arrived" />
    <header class="chrome" :class="{ 'is-open': atTop }">
      <span class="chrome-field" aria-hidden="true"><DotField :opacity="0.34" /></span>

      <div class="chrome-inner">
        <div class="brand">
          <button
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
        <div class="chrome-actions">
          <ModeToggle />
          <a class="mini-apply" :href="currentCta.href">{{ currentCta.label }}</a>
        </div>
      </div>

      <div v-if="currentPage === 'home'" class="chrome-open">
        <Hero />
      </div>

      <nav v-if="menuOpen" class="menu">
        <button v-for="n in NAV" :key="n.page" type="button" class="menu-link" @click="switchPage(n.page)">
          {{ n.label }}
        </button>
        <span class="rule"></span>
        <button type="button" class="menu-link reset" @click="menuOpen = false; restart()">
          New conversation
        </button>
      </nav>
    </header>

    <main class="wrap">
      <div v-if="currentPage === 'home'" class="fold">
        <section class="stage" :class="phase">
          <ChatPanel />
          <ResultPane v-if="hasResult" />
        </section>
      </div>
      <div v-if="currentPage === 'about'" class="about-page">
        <BrandSections />
        <EditionOverview />
        <ClosingBand />
      </div>
    </main>
  </div>
</template>

<style scoped>
/* The band is the page's one dark surface at the top: deep ground, paper type,
   the dot field as texture. Its slim height is fixed (--bar-h); the open state
   only adds the claim below the row. */
.chrome {
  position: sticky;
  top: 0;
  z-index: 30;
  background: var(--deep);
  color: var(--on-deep);
}
/* paper outlines for keyboard focus: the global ring is navy, which on navy is
   no ring at all */
.chrome :focus-visible { outline-color: var(--on-deep); }

/* One field, one scale, in both states. The wrapper is the band and crops; the
   SVG keeps the field's own 1000:300 proportion (width-driven, so a narrow
   screen shows fewer dots rather than bigger ones) and sits with its middle on
   the band's centre line. Collapsing the header therefore uncovers rows instead
   of sliding the seam away — nothing has to be aligned between two states. */
.chrome-field {
  position: absolute;
  inset: 0;
  overflow: hidden;
}
.chrome-field :deep(.dot-field) {
  position: absolute;
  left: 0;
  top: 50%;
  width: 100%;
  height: auto;
  aspect-ratio: 1000 / 300;
  transform: translateY(-50%);
}

.chrome-inner {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  height: var(--bar-h);
  padding-inline: var(--bar-gutter);
}
.brand { display: flex; align-items: center; gap: 14px; }
.wordmark {
  font-family: var(--f-display);
  font-variation-settings: "opsz" 144;
  font-weight: 400;
  font-size: 20px;
  letter-spacing: 0.06em;
}
.menu-toggle {
  display: flex;
  flex-direction: column;
  gap: 4px;
  width: 22px;
  padding: 5px 0;
}
.menu-toggle .bar { display: block; height: 1px; background: var(--on-deep); opacity: 0.75; }
.chrome-actions { display: flex; align-items: baseline; gap: 18px; }
.mini-apply {
  font-family: var(--f-mono);
  text-transform: uppercase;
  letter-spacing: 0.13em;
  font-size: 10.5px;
  color: var(--on-deep);
  opacity: 0.62;
  text-decoration: none;
  /* currentColor, not a gray token: the hairline is the foreground faded, so it
     stays in the navy world instead of importing the paper palette's rule */
  border-bottom: 1px solid currentColor;
  padding-bottom: 3px;
  transition: opacity 240ms var(--ease);
}
.mini-apply:hover { opacity: 1; }

/* The claim folds away by animating its own row, not a guessed max-height. */
.chrome-open {
  position: relative;
  display: grid;
  grid-template-rows: 0fr;
  transition: grid-template-rows 240ms var(--ease);
}
.chrome.is-open .chrome-open { grid-template-rows: 1fr; }
.chrome-open > * { overflow: hidden; min-height: 0; }

.menu {
  position: absolute;
  top: var(--bar-h);
  left: 0;
  right: 0;
  /* above the hairline, which otherwise crosses the open paper */
  z-index: 3;
  background: var(--ground);
  border-bottom: 1px solid var(--ink);
  padding: 8px var(--bar-gutter) 22px;
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
.menu-link.reset { font-family: var(--f-body); font-size: 14px; letter-spacing: 0; opacity: 0.7; }

.wrap { display: flex; flex-direction: column; }
.fold { display: flex; flex-direction: column; }
/* First screen = the band and the agent, nothing else. The fold fills what the
   bar leaves, and gives the claim's height back while the band is open — so
   both states end at exactly one viewport, the composer never moves and
   collapsing the band never lengthens the document. */
.app.landing .fold {
  min-height: calc(100vh - var(--bar-h));
  min-height: calc(100svh - var(--bar-h));
  transition: min-height 240ms var(--ease);
}
.app.landing.is-open .fold {
  min-height: calc(100vh - var(--bar-h) - var(--claim-h));
  min-height: calc(100svh - var(--bar-h) - var(--claim-h));
}
.stage { padding: clamp(34px, 6vh, 64px) var(--bar-gutter) 0; }
.stage.landing {
  flex: 1;
  display: flex;
  padding-top: clamp(24px, 3.6vh, 40px);
  padding-bottom: clamp(16px, 2.6vh, 26px);
}
.stage.reading {
  display: grid;
  grid-template-columns: 430px minmax(0, 1fr);
  gap: clamp(40px, 6vw, 96px);
  align-items: start;
  padding-bottom: clamp(40px, 7vh, 80px);
}
.stage.reading :deep(.chat.reading) {
  position: sticky;
  top: calc(var(--bar-h) + 15px);
  max-height: calc(100vh - var(--bar-h) - 35px);
  max-height: calc(100svh - var(--bar-h) - 35px);
}
/* About page: single-column, pure content. No chat, no split — just the
   brand sections and closing band with comfortable vertical rhythm. */
.about-page {
  padding: clamp(48px, 9vh, 104px) var(--bar-gutter) clamp(40px, 7vh, 80px);
}
.about-page :deep(.closing) { margin-top: clamp(48px, 9vh, 104px); }

@media (max-width: 980px) {
  .stage.reading { grid-template-columns: 1fr; }
  .stage.reading :deep(.chat.reading) { position: static; max-height: none; }
}
</style>
