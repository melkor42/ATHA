---
name: Atha
description: The personal front door to ATHA — a page composed only for you.
colors:
  soil: "#0B0A09"
  soil-surface: "#131110"
  soil-surface2: "#1A1715"
  chalk-text: "#F1EDE6"
  stone-muted: "#9C948A"
  stone-subtle: "#6A635B"
  border-hairline: "rgba(241, 237, 230, 0.09)"
  border-mid: "rgba(241, 237, 230, 0.16)"
  rust: "#CF7053"
  violet: "#9A7FC8"
  token-primary: "#5E92C4"
  token-accent: "#BD8794"
  token-success: "#8FA96E"
  token-warning: "#D8A24C"
  spectrum-aurora-accent: "#5FD9CB"
  spectrum-aurora-accent2: "#9A7FC8"
  spectrum-mycelium-accent: "#8FA96E"
  spectrum-terra-accent: "#D8A24C"
  spectrum-neon-accent: "#6FC7F2"
  spectrum-void-accent: "#CFE0EE"
  plaza-limestone: "#e9e2d4"
  plaza-ink: "#2b2622"
  plaza-ember-a: "#f2b361"
  plaza-ember-b: "#e2784e"
  atha-clay: "#2A2622"
  atha-chalk: "#F2EDE4"
  atha-slip: "#E0D8C9"
  atha-field: "#4C5A3E"
  atha-ferrous: "#8A3B26"
  atha-rind: "#C9D34A"
  atha-rule: "#A39C90"
  atha-deep: "#1E2419"
typography:
  display:
    fontFamily: "Inter, system-ui, sans-serif"
    fontSize: "26px"
    fontWeight: 800
    lineHeight: 1.2
    letterSpacing: "-0.03em"
  title:
    fontFamily: "Inter, system-ui, sans-serif"
    fontSize: "17px"
    fontWeight: 700
    lineHeight: 1.3
    letterSpacing: "-0.02em"
  body:
    fontFamily: "Inter, system-ui, sans-serif"
    fontSize: "15px"
    fontWeight: 400
    lineHeight: 1.6
  label:
    fontFamily: "JetBrains Mono, ui-monospace, Consolas, monospace"
    fontSize: "11px"
    fontWeight: 500
    lineHeight: 1.4
    letterSpacing: "0.08em"
  atha-display:
    fontFamily: "Fraunces, serif"
    fontSize: "44px"
  atha-body:
    fontFamily: "Instrument Sans, sans-serif"
    fontSize: "14px"
  atha-mono:
    fontFamily: "IBM Plex Mono, monospace"
    fontSize: "12px"
rounded:
  card: "18px"
  page: "22px"
  pill: "100px"
  atha-flat: "0px"
  plaza-pill: "999px"
spacing:
  gap: "16px"
  pad: "22px"
  shell-pad: "32px"
components:
  pill-button:
    backgroundColor: "transparent"
    textColor: "{colors.chalk-text}"
    rounded: "{rounded.pill}"
    padding: "8px 18px"
  pill-button-solid:
    backgroundColor: "{colors.chalk-text}"
    textColor: "{colors.soil}"
    rounded: "{rounded.pill}"
    padding: "8px 18px"
  signal-cta:
    backgroundColor: "transparent"
    textColor: "var(--accent)"
    rounded: "{rounded.pill}"
    padding: "7px 16px"
  card:
    backgroundColor: "{colors.soil-surface}"
    textColor: "{colors.chalk-text}"
    rounded: "{rounded.card}"
    padding: "{spacing.pad}"
  plaza-button:
    backgroundColor: "rgba(250, 247, 240, 0.72)"
    textColor: "{colors.plaza-ink}"
    rounded: "{rounded.plaza-pill}"
    padding: "12px 22px"
  plaza-button-solid:
    backgroundColor: "linear-gradient(135deg, #f2b361, #e2784e)"
    textColor: "#241f1b"
    rounded: "{rounded.plaza-pill}"
    padding: "12px 22px"
---

# Design System: ATHA - A HADORA EXPERIENCE

## Overview

**Creative North Star: "The Clearing"**

The experience is a journey from underground to daylight. The composed page lives in the dark: near-black soil (#0B0A09) under a slow-breathing bioluminescent aura, film grain, and hairline-bordered cards that read as objects found in the dark rather than UI panels laid on top of it. Depth comes from glow and tonal layering, never from stacked shadows. The page composes itself section by section — revelation is choreography, not loading.

Above ground sits the Plaza: a bright limestone town square (#e9e2d4) with photographic tile zones softened by a flat veil wash, glassy plaza buttons, and one warm ember gradient reserved for the primary action. The two worlds share one grammar of restraint: flat washes over filter blur, compositor-friendly motion, and accent color used sparingly enough that its rarity carries meaning.

Two vocabularies coexist and must not bleed into each other: the legacy SIGNAL tokens (`--primary`, `--accent-tok`, ...) drive the composed page, while the newer ATHA Wisdom Corner tokens (`--atha-*`, Fraunces/Instrument Sans/IBM Plex Mono) follow a strict flat doctrine — no gradients, no drop shadows, no rounded containers.

**Key Characteristics:**
- Dark bioluminescent soil for the composed page; bright limestone for the Plaza.
- Spectrum (hue family) × StyleMode (materiality) axis grammar — orthogonal, persona-derived.
- Glow and tonal layering instead of stacked shadows.
- Choreographed sequential section reveals; motion character belongs to each StyleMode.
- Hairline borders (≤1px, low-alpha chalk) as the default structural device.
- Grain at 0.035 opacity as global texture; modes may push or quiet it.

## Colors

The palette is soil and glow: near-black warm neutrals holding persona-tinted spectral accents; the Plaza inverts to limestone with ember.

### Primary
- **Spectral Accent** (`--s-accent`, aurora default #5FD9CB): the persona's hue family. Score bars, CTAs, banner ribs, numerals. The Spectrum axis owns it: mycelium #8FA96E, terra #D8A24C, aurora #5FD9CB, neon #6FC7F2, void #CFE0EE.
- **Ember Gradient** (#f2b361 → #e2784e): the Plaza's single saturated gesture, used only on the solid plaza button.

### Secondary
- **Spectral Accent 2** (`--s-accent2`): the glow pair for ambient auras and dual-source gradients (aurora pairs teal with violet #9A7FC8).

### Tertiary
- **Persona ColorTokens** (`--primary` #5E92C4, `--accent-tok` #BD8794, `--success` #8FA96E, `--warning` #D8A24C): persona accent selection for the Theater network pulses; `--accent` mirrors the chosen token across the composed page.

### Neutral
- **Soil** (#0B0A09): document background of the dark world.
- **Soil Surface / Surface 2** (#131110 / #1A1715): card and inset layering; also re-set per Spectrum (`--s-surface`).
- **Chalk Text** (#F1EDE6): primary text on dark; inverted as the solid pill's background.
- **Stone Muted / Subtle** (#9C948A / #6A635B): secondary text and placeholders; spectra carry their own `--s-dimtext`.
- **Plaza Limestone** (#e9e2d4): the light world's base tile color and the veil wash.
- **Plaza Ink** (#2b2622): text on limestone surfaces.
- **ATHA ceramics** (clay #2A2622, chalk #F2EDE4, slip #E0D8C9, field #4C5A3E, ferrous #8A3B26, rind #C9D34A, rule #A39C90, deep #1E2419): the Wisdom Corner's flat ceramic palette.

### Named Rules
**The One Glow Rule.** The ambient aura is a radial gradient pair at ≤12% alpha, breathing over `--breathe-dur` (calm 26s / direct 16s / playful 9s). Glow is atmosphere, not decoration — never add a third source.
**The Ferrous Rule.** In ATHA ceramic surfaces, `--atha-ferrous` appears at most once per view; `--atha-rind` covers ≤5% of a view and never carries text.
**The Flat Chalk Rule.** The Wisdom Corner admits no gradients, no drop shadows, no rounded containers — the veil wash in the Plaza stays flat for the same reason.

## Typography

**Display Font:** Inter (with system-ui) — overridden per StyleMode: VT323 (retro), Cormorant Garamond (organic, earth), Oswald (steampunk), Fraunces (ATHA ceramic).
**Body Font:** Inter (with system-ui); Instrument Sans in ATHA ceramic surfaces.
**Label/Mono Font:** JetBrains Mono (with ui-monospace, Consolas); VT323 in retro, IBM Plex Mono in ATHA ceramic.

**Character:** A quiet sans carries the structure while each world borrows a voice — terminal phosphor, humanist serif, transit grotesque, editorial Fraunces. Type changes are materiality changes; that is the StyleMode axis doing its job.

### Hierarchy
- **Display** (800, 26px, -0.03em): shell headings, brand moments; the `.grad` spectral gradient text is reserved for the brand word.
- **Title** (700, 17px, -0.02em): card headings `.card h3`; modes re-voice it (21px light in minimal, 26px serif in organic).
- **Body** (400, 15px/1.6): default document text; card paragraphs run 14px in `--s-dimtext`.
- **Label** (500, 11px mono, 0.08em, uppercase): the `.k` eyebrow above every card section.

### Named Rules
**The Eyebrow Rule.** Every card section opens with a mono uppercase `.k` eyebrow; modes may ornament it (hedera ❧, pigment ◆, title-bar ▓░) but never delete it.

## Layout

`#app` is a centered column, max-width 1080px with 32px shell padding. The composed page (`.composed`; the composed sheet exists only inside the north wing, so its selectors in style.css are anchored as `.zone-north .composed…`) is a vertical stack with 16px gap, optionally a two-column grid (`.section.wide` spans both); below 720px it collapses to one column. Minimal mode narrows to 720px single-column. The Plaza is a full-viewport horizontal world of absolutely positioned zones panned by transform — no document scroll for travel. Spacing rhythm is mode-owned: `--gap` ranges 0px (minimal, hairline-divided) to 34px (steampunk, conduit-linked).

## Elevation & Depth

This system is glow-first and nearly shadow-free at rest. The dark world's default `--shadow` is `none`; depth comes from the breathing aura, the top-of-page radial `--bg-tint` wash, and 1-px hairline borders at 9–16% chalk alpha. Shadows appear only as mode character: retro's 4px 4px hard offset, organic's soft accent bloom, earth's pressed-fiber double shadow, steampunk's riveted-panel drop — and in `mode-none` solely as a hover response. The light world uses one soft lift on plaza-button hover (0 10px 24px rgba(30,40,45,.18)).

### Named Rules
**The Flat-By-Default Rule.** Surfaces are flat at rest. A shadow is a material statement owned by a StyleMode or a hover state — never a generic card default.

## Shapes

Two silhouettes divide the worlds. The dark world is grown: 18px card radius, 22px page radius, 100px pills — and organic mode breaks the geometry with asymmetric grown radii (26px 10px 24px 12px, alternated per section). Retro and steampunk square everything off (0–4px) as their material demands. The light world is a single shape: the 999px plaza pill over full-bleed rectangular zones. ATHA ceramic surfaces stay at 0 radius by doctrine. Borders are hairlines: 1px at 9% chalk by default; modes may thicken to 2–3px only as a material property (retro's CRT frame, earth's soil border).

## Components

### Buttons
- **Shape:** full pill (100px radius) in the dark world; 999px plaza pill in the light world; modes re-shape (0px retro, 8px earth, 5px steampunk brass).
- **Pill (ghost):** transparent, 1px border-mid, chalk text, 8px 18px; hover brightens the border to full chalk over 0.3s `cubic-bezier(0.22, 1, 0.36, 1)`.
- **Pill (solid):** chalk background on soil text — the inversion is the emphasis, no color needed.
- **Signal CTA:** accent-outlined pill (7px 16px, 600 12px); hover floods the accent and inverts text to soil.
- **Plaza button:** glassy limestone (rgba(250,247,240,.72) with blur 10px), hover lifts 2px with soft shadow; the solid variant is the only ember gradient in the product.

### Cards / Containers
- **Corner Style:** 18px radius (mode-owned; see Shapes).
- **Background:** surface #131110, per-spectrum `--s-surface`; organic/earth/steampunk layer material gradients.
- **Shadow Strategy:** flat at rest (see Elevation); mode shadows are material, hover bloom is `mode-none`'s signature.
- **Border:** `--bdw` (1px default) solid border-hairline; spectrum-tinted `--s-border`.
- **Internal Padding:** 22px `--pad`; nested `.child` cards pad at 0.7×.

### Inputs / Fields
- **Style:** onboarding textarea on surface, 1px border-mid, 18px radius, 16px 18px padding.
- **Focus:** border shifts to full chalk over 0.3s ease — no glow ring, no outline beyond the border itself.
- **Placeholder:** subtle #6A635B.

### Navigation
The Plaza is the navigation: spatial zones reached by panning a transformed world, with a Compass for orientation and a travel-speed control. Zone entry is a camera move, not a page jump.

### Signature: The Axis Grammar
Every composed page is the product of two orthogonal axes: **Spectrum** (`mycelium | terra | aurora | neon | void`) owns the hue family — surfaces, borders, glow pair, aura; **StyleMode** (`none | minimal | retro | organic | earth | steampunk`) owns materiality, typography, atmosphere, and reveal choreography. Modes may mute or push the spectral hue via `color-mix()` but must never leave the hue family. New surfaces must compose from these axes, not invent a third vocabulary.

## Do's and Don'ts

### Do:
- **Do** derive new surfaces, borders, and glows from the Spectrum's `--s-*` tokens via `color-mix()`; the spectrum owns the hue family.
- **Do** animate opacity/transform only for ambient motion; softness comes from gradient stops, never `filter: blur()` on animated layers.
- **Do** keep reveal choreography sequential (`.section.on`) and give each StyleMode its own entrance character; honor `prefers-reduced-motion`.
- **Do** keep the Wisdom Corner's flat ceramic doctrine: Fraunces/Instrument Sans/IBM Plex Mono, no gradients, no shadows, no rounding.
- **Do** persist user-tuned atmosphere (e.g. veil strength under the `atha.veil` key) rather than resetting it.

### Don't:
- **Don't** introduce stacked box-shadows as a generic depth device; depth is glow, wash, and hairline.
- **Don't** add a third aura source or exceed ~12% alpha on ambient glows.
- **Don't** let the legacy SIGNAL ColorToken palette and the `--atha-*` ceramic palette mix in one surface.
- **Don't** rename or drift domain terms (Signal, Spectrum, StyleMode, PersonaModel) — the wire contract depends on them.
- **Don't** use `v-html` to render composed content; the UiRenderer registry is the only path.
- **Don't** fabricate people, companies, or testimonials; all content beyond ATHA 001 is fictional synthetic data.
