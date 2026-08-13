# Build the Vue frontend

Type: task
Status: resolved
Blocked by: 04, 06, 07

## Question

Build the Vue + Vite app: onboarding page with the single free-text input; Component Registry with the five shipped components; recursive UiRenderer (no `v-html`); client-side staged-reveal theater per the prototype from [Prototype brand shell and step theater](06-brand-shell-theater.md); brand tokens; accent color applied from the persona; plus the four theme CSS variable sets (background tint, card radius, spacing, border style, type emphasis) driven by the schema's theme field, per [Define the composition grammar](07-composition-grammar.md). Resolved when a hand-fed ExperienceSchema renders correctly for all five component types.

## Answer

2026-08-13 — built and verified.

**Scaffold method**: manual Vue 3 + Vite scaffold in `frontend/` (no create-vue): hand-written `package.json` (vue ^3.5, vite ^6, @vitejs/plugin-vue ^5), `vite.config.js` (port 5173, strictPort), `index.html` (Inter + JetBrains Mono with system fallbacks), `src/` with `App.vue`, `assets/style.css` (prototype brand tokens + four theme variable sets), `components/` (`Theater`, `WowPage`, `UiRenderer`, `registry.js`, five leaf components), `fixtures/` (four hand-written schemas). `npm install` + `npm run dev` on Node 26 / npm 11.

**Mock mode**: `npm run dev`, then `http://localhost:5173/?fixture=miriam|jonas|david|tobias` — one fixture per theme; fixtures follow the exact backend contract (`{persona, experience}` envelope, `entity_ids` lists, EntityPayload fields). Type anything and submit; a 1.6s delay keeps the theater visible. Without the query param the app POSTs `{text}` to `http://localhost:8000/api/experience` with no client timeout.

**Verified in the browser**:
- All four themes visibly differ (boardroom: gold #D8A24C, 10px radius, dense grid, mono numerals; festival: mauve #BD8794, 24px radius, mauve-tinted surface, single column; garden: green #8FA96E, 26px radius, quiet 5% borders, green wash; ledger: blue #5E92C4, 6px radius, hairline borders, mono blue numerals). Layout grid vs single_column and persona accent from `persona.accent_color` confirmed.
- All five component types render (SignalCard score bar + Contact pill, StudentProfile role + story, EnterpriseCard sector/size/hq/metadata/seeks rows, EventBanner accent left border with date·location, TextBlock), nested children recurse through UiRenderer; unknown component type renders nothing without crashing.
- No `v-html` / `innerHTML` anywhere (grep-clean); all text goes through Vue template escaping.
- Theater plays persona → traversal → compose → grounding at 350ms cadence with checkmarks; sections reveal at ~380ms stagger after the JSON arrives; a waiting hint shows if the backend is still composing.
- Live end-to-end: with ticket 10's backend running, a real POST composed a boardroom page from real graph entities (SignalCards, StudentProfiles, EnterpriseCard) — frontend renders the actual pipeline output unmodified.
- Error paths: backend down/4xx and unknown fixture both land in a graceful error card with retry.

2026-08-13 addition (user request): waiting-period animation in Theater.vue — canvas with a signal pulse traveling node-to-node through a network graph (left) and a neural strip firing layer-to-layer (right), brand palette, runs only while composing, collapses to the static checklist on ready.
