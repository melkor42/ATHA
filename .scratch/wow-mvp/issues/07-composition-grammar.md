# Define the composition grammar

Type: grilling
Status: resolved
Blocked by: 05

## Question

The mapping from persona axes (perspective, tone, expertise) to layout, section mix, and copy register across the five shipped components — the mechanics of visible difference. Deliverable: a contrast table over the four fixtures (Miriam: ranked data, direct register; Jonas: events and energy; David: stories, calm, low-pressure CTA; Tobias: methodology and metadata, no adjectives) plus the rules Agent 2's prompt encodes. Grilling with the user; his taste for how personality becomes layout is the irreducible core.

## Comments

2026-08-12 — user reaction: content axes approved; added requirement that design itself differentiates per persona (color, card layout, background). Refined grammar, pending close:

- New axis **theme** (design variant within SIGNAL identity), enum in ui_schema: `boardroom` (Miriam: dense grid, tight radius, gold, numbers-forward) · `festival` (Jonas: single column, large radius, mauve-tinted surface, energetic spacing) · `garden` (David: spacious single column, green-tinted wash, softest radius, quiet borders) · `ledger` (Tobias: strict grid, hairline borders, blue, mono numerals).
- Each theme = a CSS variable set (bg tint, surface, radius, spacing, border style, type emphasis); the LLM selects only the enum, never raw CSS — allowlist discipline preserved.
- Full row per persona: perspective→mix, tone→register, expertise→density, persona→accent, perspective→theme.

## Answer

Grammar final (user approval 2026-08-12, including the design-differentiation requirement): perspective→section mix AND theme; tone→copy register; expertise→density; persona→accent token. Themes: boardroom / festival / garden / ledger, each a frontend-owned CSS variable set; the LLM selects only the enum. Encoding lands in prompts/experience_builder.md (ticket 10) and the theme sets in the frontend (ticket 11).
