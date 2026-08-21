# SIGNAL — Context Brief

Single-context file for any agent working on the SIGNAL frontend. Read this before touching UI.
Last refreshed: 20 Aug 2026.

Context layers — read only this file unless you hit a wall:
1. **This brief** — everything needed to build without inventing.
2. `docs/signal_master_hub.html` (canon hub v0.3) — provenance and status: team roster, four-week journey, status dashboard, open blockers, change log.
3. `.scratch/extracted-domain.txt` (git-ignored research extraction) — raw depth: named partners, alumni contacts, skill codes, judging logic, scenario tiers.
Live reference: `signal.onemundi.one` (public pitch surface).

## What SIGNAL is

SIGNAL 001 is a **48-hour AI-native viability event** (Q4 2026), Warwick Business School × OneMundi.
Public name: **The AI-Native Viability Sprint**. Teams do NOT prototype — they assess real enterprise AI challenges and deliver a **board-ready verdict, not a demo**.

Thesis lines (approved copy, reuse verbatim):
- "The new edge isn't AI — it's the depth that makes it viable."
- "Depth in, depth out" — the depth AI returns mirrors the depth you bring.
- "Everyone else resets. We compound."
- "Not a hackathon · Not a conference · Something new."

## The five-lens instrument (core taxonomy)

01 Desirability — "Does anyone actually want this?"
02 Feasibility — "Can it realistically be built now?"
03 Viability — "Does it make business sense?"
04 Scalability — "Can it grow beyond one use case?"
05 Responsibility — "Is it safe and fair to deploy?"

Team roles A–E map 1:1 to the lenses; judging mirrors them. Treat lens/role/rubric definitions as **versioned config** — source docs disagree on rubric variants (5 vs 7 vs 8 criteria). Never hard-code one variant.

## The four perspectives (public structure)

The live site frames four interactive perspectives, each with three deliverables:
1. **Enterprise** — bring a real AI workflow; get an evidence-grade verdict + modelled unit economics + first-look talent access.
2. **Talent** — bring depth, judgment, context; get proof of how you operate with AI + visibility to enterprises + a place in a compounding ecosystem.
3. **Infrastructure** — frontier AI substrate under real operating conditions; partner deliberately unnamed publicly ("frontier AI substrate").
4. **Education · WBS** — top-1% school, #3 online MBA worldwide (FT 2024), triple accredited; longitudinal dataset only WBS owns.

Public flow: Challenge → Cohort → 48 Hours → **Experience** → Signal.
"Wellbeing is infrastructure" — experience is built around the state of the person, supported not depleted.

## Adaptive entrance (the layer this product must deliver)

Inherited from the Hadora experience system; SIGNAL-specific values:
- **Visitor states:** discovering for the first time / deciding whether to attend / preparing to come / already experienced.
- **Exploration modes:** understand what SIGNAL is / essential details / into the atmosphere / explore my own way.
- **Session values:** `signalVisitorState`, `signalExplorationMode`, `signalEntryRoute`, `hasSeenSignalEntrance`.
- **Lifecycle phases:** Before / During / After Signal — states, content, CTAs change by phase without rebuild.
- **Essential-information rule:** personalization may reorder emphasis but must NEVER hide dates, location, registration, accessibility.

## Hard content rules

- Use only approved SIGNAL copy/assets. **Never invent** program details, people, dates, location, tickets, or promises.
- Facts that are not confirmed must carry a status: Assumption · Proposed · Recommended · Decided · Confirmed · Approved · Open (legend defined in the hub).
- Current open facts: exact dates (Q4 2026 only), headcount (30 proposed, contested vs 95/150/245), scenario tier (Standard recommended), challenges (none confirmed), infrastructure partner (unnamed).
- Entry points: hello@onemundi.one — subjects "SIGNAL 001 — Enterprise Challenge" / "SIGNAL 001 — Talent Application".

## Design language (from hub v0.3)

- Palette: ink `#0E1417`, panels `#152026`/`#1a272d`, bone text `#EDE7DA`, dim `#A6AFAC`, signal gold `#E6B84C`, sage `#83AC97`.
- Type: Fraunces (display, weights 340/460), Instrument Sans (body), IBM Plex Mono (labels, uppercase, letter-spacing .12–.3em).
- Motion: scroll-reveal (opacity+translate, ~.7s), lens bars animate on intersection; honor `prefers-reduced-motion`.
- Max content width 1080px; mono eyebrows for section numbers ("II.6 — …" pattern).

## Graph shape coming next (do not build data yet)

Planned nodes: Talent, Enterprise, Challenge, Contact, Institution, Event (edition/phase/checkpoint), Lens.
Edges carry the meaning: `tie` (typed person↔institution relation — encodes the network-first rule "why can this person say yes"), `route` (priority tier + contact status), `provides`, `works_on`, `scores`, `recruits_for`.
UI should stay node/edge-agnostic: render from graph payloads, not from hard-coded fixtures.
