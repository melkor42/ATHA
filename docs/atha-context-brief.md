# ATHA — Context Brief

Single-context file for any agent working on the ATHA frontend. Read this before touching UI.
Last refreshed: 22 Aug 2026 (Signal → Atha rebrand).

Context layers — read only this file unless you hit a wall:
1. **This brief** — everything needed to build without inventing.
2. `docs/atha_master_hub.html` (canon hub v0.3) — provenance and status from the pre-rebrand phase: team roster, four-week journey, status dashboard, open blockers, change log.
3. `.scratch/Atha_Context_dump.md` + `.scratch/atha-wisdom-corner.html` — the approved ATHA canon (identity, method, rhythm, Edition 001).
4. `.scratch/ATHA_Design-Direction.html` — the visual authority for the ATHA surface.
Live reference: `signal.onemundi.one` (public pitch surface — rename pending, external task).

## What ATHA is

ATHA is a **temporary AI-native innovation culture** — an enterprise innovation experience in which multidisciplinary teams investigate real organisational AI challenges and produce holistic, evidence-based decisions. **Initiated by OneMundi, co-hosted with Warwick Business School.**

Beneath the surface, the experience design is shaped as a **HADORA experience** — rhythm, stewardship, nourishment, psychological safety and integration. HADORA is experienced through ATHA's rhythm, atmosphere, relationships, aesthetics, rest and contribution — **never prominent branding**.

What a challenge partner receives is not a prototype and not a pitch: a defensible, board-ready implementation verdict — three of them, and the reasoning behind each. A well-supported decision not to build can be worth more than an impressive prototype.

ATHA is built to recur: every relationship formed in an edition persists into the next one, and the archive of findings compounds rather than resets. Edition 001 is the first, not the whole thing.

## Naming discipline

- **Atha** = the brand (the experience itself).
- **Signal** survives as a *domain term only*: a derived Person↔Enterprise match in the composed-page graph. Never use it for the brand again. (The old wire strings `SignalCard`, `save_signal`, `SIGNAL_CARD` were removed with the 2026-09-10 agent-flow restoration.)

## Edition 001 — current working direction

Nothing below is confirmed. No challenge partner, sponsor or funding is agreed, and the dates are not fixed. It is set out here as it actually stands, because the alternative is to imply otherwise.

| Fact | Status |
|---|---|
| Around 45 selected participants, Warwick-centred | Proposed |
| Nine multidisciplinary teams of five | Proposed |
| Three real enterprise AI challenges | Proposed |
| Three independent teams per challenge | Proposed |
| Warwick/Coventry as the core working location | Proposed |
| A multi-day working experience at Warwick Business School | Proposed |
| Possible later enterprise showcase at WBS The Shard, London | Under review |
| Dates (direction: around March 2027) | Not fixed |
| Challenge partners | Being selected |

The earlier 48-hour format is no longer fixed: the duration is determined by the rhythm required for strong work, meaningful connection, adequate rest, careful discernment and integration.

## The seven-stage rhythm

ATHA is not an agenda. It follows a human and intellectual arc, and the length of each stage is a decision rather than a leftover. The gaps are designed too.

01 Arrive & Settle — people are met rather than processed; the room is made, not booked.
02 Open & Sense — the question is opened before it is attacked, presented as it actually sits.
03 Connect — teams form across disciplines, around the question.
04 Create — the longest stage: AI-native investigation, AI used fully, never accepted blindly.
05 Discern — given more room than any stage except the work itself: evidence, consequences, uncertainty, trade-offs.
06 Celebrate — recognition is shared rather than ranked; different forms of excellence, no overall winner.
07 Integrate & Return — leave with something integrated; the relationships carry into the next edition.

## The four verdict states (the finding)

Proceed · Redirect · Pause · Reject — the implementation verdict a challenge partner receives, per team. A reject is a result: the commercial model does not punish a well-supported no.

## The five-lens instrument (core taxonomy)

01 Desirability — "Does anyone actually want this?"
02 Feasibility — "Can it realistically be built now?"
03 Viability — "Does it make business sense?"
04 Scalability — "Can it grow beyond one use case?"
05 Responsibility — "Is it safe and fair to deploy?"

Each team examines the same five dimensions; a weakness in any one of them is a finding in itself. Treat lens/role/rubric definitions as **versioned config** — source docs disagree on rubric variants (5 vs 7 vs 8 criteria). Never hard-code one variant.

## Zone map (plaza)

The Town Square shell: one place, five zones, a soft camera — and Boris, the bear companion.
- **Center** — the resting point: promise, grounding, belonging, two doors into the east wing.
- **North** — the AI Corner: everything composed live, for you.
- **West** — the quiet wing: how ATHA works and what makes a decision good — the seven directions (question, method, finding, conditions, rhythm, Edition 001, layers) as tablet cards with expandable articles (ATHA design tokens).
- **East** — where you join: bring a challenge, or bring your talent.
- **South** — the story: the seven-stage rhythm, revealed on scroll; the entrance gate.

## Adaptive entrance (the layer this product must deliver)

Inherited from the Hadora experience system; ATHA-specific values:
- **Visitor states (Q1):** discovering Atha for the first time / deciding whether to attend / preparing to come / already experienced.
- **Exploration modes (Q2):** understand what Atha is / essential details / into the atmosphere / explore my own way.
- **Session values (canonical):** `athaVisitorState`, `athaExplorationMode`, `athaEntryRoute`, `atha.arrivalPlayed`, `atha.hasSeenEntrance`.
- **Travel preference:** `atha.travelMs` (localStorage) — owner-dialed zone-transfer duration in ms; a preference, not gate state.
- **Veil preference:** `atha.veil` (localStorage) — owner-dialed strength (0–100%) of the plaza's flat background-softening wash; a preference, not gate state.
- **Lifecycle phases:** Before / During / After Atha — states, content, CTAs change by phase without rebuild.
- **Essential-information rule:** personalization may reorder emphasis but must NEVER hide dates, location, registration, accessibility.

### Gate copy — EXACT, must match `frontend/src/composables/useGate.js`

Q1 — "How are you meeting ATHA today?"
- "I am discovering ATHA for the first time"
- "I am deciding whether to attend"
- "I am preparing to come"
- "I have already experienced ATHA" (after the event only)

Q2 — "What would be most helpful now?"
- "Help me understand what ATHA is"
- "Show me the essential details"
- "Guide me into the atmosphere"
- "Let me explore in my own way"

## The companion — Boris

The plaza's assistant is **Boris**, Warwick's mascot — a small layered bear with antenna and tracking eyes (`frontend/src/components/Companion.vue`, generic companion component; "Boris" is the display name, not a hard-coded identity). Behavioral rules, unchanged from the previous assistant:
- After arrival, Boris asks the gate questions Q1 then Q2, in his bubble, anywhere in the plaza.
- On the closing line he names the lit path, then walks the visitor there (Plaza waits for his `said` event before traveling).
- One context sentence per zone; poking him cycles atmospheric lines only — never program facts.
- Honors `prefers-reduced-motion`: no bob/blink/pulse, pupils centered, lines appear instantly.

## Hard content rules

- Use only approved ATHA copy/assets. **Never invent** program details, people, dates, partners, funding, tickets, or promises.
- Facts that are not confirmed must carry a status label: **Forming · Proposed · Not fixed** (plus the hub's fuller legend: Assumption · Recommended · Decided · Confirmed · Approved · Open · Under review · Being selected).
- Current open facts: exact dates (Not fixed), challenge partners (Being selected — none confirmed), sponsorship/funding (nothing confirmed), facilities and Shard availability (unconfirmed).
- Entry points: hello@onemundi.one — subjects "ATHA 001 — Enterprise Challenge" / "ATHA 001 — Talent Application".

## Design language (ATHA surface)

Authority: `.scratch/ATHA_Design-Direction.html`; tokens live in `frontend/src/assets/style.css` under the `/* ATHA tokens */` block (`--atha-*` prefix).
- Palette: clay `#2A2622`, chalk `#F2EDE4`, slip `#E0D8C9`, field `#4C5A3E`, ferrous `#8A3B26`, rind `#C9D34A`, rule `#A39C90`, deep `#1E2419`.
- Rules: no gradients, no drop shadows, no rounded containers. Ferrous appears at most once per view. Rind covers ≤5% of a view and never carries text.
- Type: Fraunces (display, 300 + italics), Instrument Sans (body 400/500), IBM Plex Mono (labels, uppercase, letter-spaced) — scale `--atha-s0`…`--atha-s7` (12/13/14/16/20/28/44/72).
- Motion: `--atha-ease: cubic-bezier(.2,.7,.25,1)`; scroll-reveal (opacity+translate); honor `prefers-reduced-motion`.
- Legacy (pre-rebrand) tokens in the same `:root` stay untouched for the existing composed-page/plaza surfaces.

## Graph shape coming next (do not build data yet)

Planned nodes: Talent, Enterprise, Challenge, Contact, Institution, Event (edition/phase/checkpoint), Lens.
Edges carry the meaning: `tie` (typed person↔institution relation — encodes the network-first rule "why can this person say yes"), `route` (priority tier + contact status), `provides`, `works_on`, `scores`, `recruits_for`.
UI should stay node/edge-agnostic: render from graph payloads, not from hard-coded fixtures.
