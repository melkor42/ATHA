# Frontend: Rendering, Themes, Theater

<cite>
**Referenced Files**
- [frontend/src/App.vue](file://frontend/src/App.vue)
- [frontend/src/components/UiRenderer.vue](file://frontend/src/components/UiRenderer.vue)
- [frontend/src/components/registry.js](file://frontend/src/components/registry.js)
- [frontend/src/components/Theater.vue](file://frontend/src/components/Theater.vue)
- [frontend/src/assets/style.css](file://frontend/src/assets/style.css)
- [prototypes/brand-theater.html](file://prototypes/brand-theater.html)
</cite>

## App phases

`App.vue` moves through onboarding → composing → ready (or error). Onboarding is a single free-text input. During composing, the Theater plays the four pipeline steps and the waiting animation; sections reveal sequentially (~380ms stagger) once the response arrives and the theater has finished. A waiting hint covers slow backends; there is deliberately no client timeout. Error paths (backend down, 4xx, unknown fixture) land in a graceful error card with retry.

## Renderer and registry

`UiRenderer.vue` is recursive: it resolves `node.component` through `registry.js` onto the five shipped components (TextBlock, SignalCard, StudentProfile, EnterpriseCard, EventBanner) and recurses into `children`. Unknown component types render nothing and never crash. There is no `v-html` anywhere; all text passes through Vue template escaping. Card data comes from the response's server-hydrated entities map via `entity_ids`.

## Themes

The schema's `theme` enum selects a frontend-owned CSS variable set: boardroom (dense grid, ~10px radius, gold, numbers-forward), festival (single column, ~24px radius, mauve-tinted surface), garden (spacious single column, green wash, softest radius, quiet borders), ledger (strict grid, ~6px radius, hairline borders, blue mono numerals). The persona's accent ColorToken maps to the brand support palette (primary #5E92C4, accent #BD8794, success #8FA96E, warning #D8A24C). Base brand tokens — warm charcoal #0B0A09, cream #F1EDE6, Inter, pill CTAs, the gold→rust→violet→blue gradient headline — come from the prototype that locked the look.

## The waiting theater

`Theater.vue` renders, only while composing, a canvas animation: on the left a network graph whose light pulse travels node to node (visited nodes stay lit), on the right a neural strip firing layer to layer. It collapses to the static step checklist once the page is ready.

## Mock mode and dev

`npm run dev` serves on port 5173 (strictPort). `?fixture=miriam|jonas|david|tobias` renders hand-written schemas from `frontend/src/fixtures/` without the backend, for design work offline. Vite config, package.json, and component sources live under `frontend/`.
