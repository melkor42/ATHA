# Prototype brand shell and step theater

Type: prototype
Status: resolved
Blocked by: —

## Question

Extract the visual identity (colors, type, tone) from signal.onemundi.one and build a rough Vue shell that performs the client-side staged-reveal theater over a static, hand-written ExperienceSchema (the real pipeline steps as animated stages, then sections revealing in sequence). The user reacts to the prototype; the reaction decides the theater's pacing and the brand-token set the frontend build inherits.

## Answer

User reaction 2026-08-12: approved — "exactly what I was looking for". Brand tokens (warm charcoal, cream Inter, pill CTAs, gold→rust→violet→blue gradient) and the staged-reveal theater are the frontend's reference; `prototypes/brand-theater.html` stays in the repo as the brand artifact. New requirement from the reaction: the final build must differentiate **design** per persona, not only content — color, card layout, background. Captured as a Theme enum in [Define the composition grammar](07-composition-grammar.md) and folded into tickets 10/11.
