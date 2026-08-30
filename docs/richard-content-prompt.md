# Content extraction prompt for Richard's AI

Handoff prompt (2026-08-29): Richard's AI holds the full ATHA context; this prompt
extracts visitor-facing answers keyed to our question catalog, in a format we can
ingest into the knowledge graph. Expected output: one JSON array (schema below the
prompt). On delivery: review against the honesty rules, then convert into passages +
ANSWERED_BY/SUPPORTS edges via a `digest_rules_cluster3.json` round.

---

You are helping us prepare high-quality, VISITOR-FACING knowledge content for the ATHA website. You have been given rich context about ATHA (OneMundi × Warwick Business School × the experience design behind it). Your job is to extract and shape that context into structured answers our website can show to visitors, keyed to the exact questions our visitors ask.

THE PRODUCT
The ATHA website composes a personal page for each visitor. The visitor arrives anonymously, picks a role, and the page answers the questions that matter most to them. We do NOT show internal strategy — we show clear, honest, visitor-facing answers. Every answer must be grounded in the context you have. Nothing may be invented.

THE THREE VISITOR ROLES (use these exact ids)
- student   — a person considering joining a team
- business  — an organisation considering bringing a challenge
- warwick   — someone approaching from the university / education / research side

THE FOUR VISITOR STATES (where the visitor is in their journey)
- discovering, deciding, preparing, experienced

STATUS VOCABULARY — CRITICAL (ATHA is in formation; honesty is a hard rule)
- confirmed — settled and publicly true
- proposed  — the current working direction, not yet confirmed
- open      — genuinely unresolved / not yet decided
Never present a proposed or open fact as confirmed. Dates, challenge partners, funding/sponsorship and facilities are NOT confirmed — label them honestly.

YOUR TASK
For each item in the CATALOG below, write a visitor-facing answer (60–180 words, English) grounded in the context you have. Return a single JSON array. You may return MULTIPLE entries for the same target when there are genuinely different facets (e.g. "day to day" has rhythm / food / space / rest) — give each a unique id.

Each entry must have:
- id:             short kebab-case slug, unique across the whole array
- target:         the catalog id you are answering (from the CATALOG)
- question:       the visitor question or facet label in plain words
- roles:          array, at least one of [student, business, warwick]
- visitor_states: array, any of [discovering, deciding, preparing, experienced]
- perspective:    one of [om, hadora, joint, operational] — use "joint" for most visitor content; use "hadora" only when the content is specifically about the experience-design philosophy
- status:         one of [confirmed, proposed, open]
- answer:         the visitor-facing answer. Warm, concrete, factual, plain sentences. No markup, no bullet dashes, no internal jargon, no sales hype. Written for someone who knows nothing about ATHA.
- grounding:      one short sentence naming what in the context supports this
- confidence:     one of [supported, partial, gap]. Use "gap" when the context genuinely has nothing for this item — then set answer to a short honest sentence like "This is not defined yet and will take shape with the first edition." Do NOT invent content to fill a gap; the gaps themselves are valuable to us.

VOICE RULES
- Never name or brand HADORA in the answer text. If the content is about that dimension, call it "the experience design behind ATHA".
- Do not over-promise. Where ATHA is honestly in formation, let that honesty show — it is a strength.
- Prefer concrete, human language over abstract strategy language.

CATALOG — QUESTIONS (target id — the visitor's question)
- q01-what-is-atha        — What is ATHA, really?
- q02-why-different       — Why does ATHA exist, and what makes it different?
- q03-role-fits-me        — Which role in a team would fit me?
- q04-teams-formed        — How are teams formed?
- q05-how-judged          — How is the teams' work judged?
- q06-day-to-day          — What does the experience feel like day to day?
- q07-takeaway            — What do I personally take away from it?
- q08-partner-receives    — What exactly do we receive as a challenge partner?
- q09-challenge-evaluated — How is our challenge evaluated?
- q10-partner-brings      — What do we need to bring as a partner?
- q11-confidentiality-ip  — How is confidentiality and IP handled?
- q12-after-experience    — What happens after the experience?
- q13-education-research  — How does ATHA serve education and research?
- q14-wbs-role            — What is Warwick Business School's role in ATHA?

CATALOG — FACETS: TEAM FUNCTIONS (what a team role actually does)
- func-domain-expert                  — Domain Expert: understanding the problem and the people it affects
- func-ai-workflow-lead               — AI Workflow Lead: the AI approach and technical feasibility
- func-responsible-ai-risk            — Responsible AI & Risk Lead: governance, risk and ethics
- func-business-viability-coordinator — Business Viability & Coordinator: the business case and coordination
- func-pitch-design-lead              — Pitch & Design Lead: communicating the decision

CATALOG — FACETS: VALUE FORMS (what a challenge partner receives)
- value-experience  — Experience: living a different way of working
- value-perspective — Perspective: seeing AI more fully
- value-decision    — Decision: a clear, defensible verdict
- value-belonging   — Belonging: joining a community
- value-continuity  — Continuity: the relationship continues after the event

CATALOG — FACETS: LENSES (how the work is judged)
- lens-desirability    — Desirability: does anyone actually want this?
- lens-feasibility     — Feasibility: can it realistically be built now?
- lens-viability       — Viability: does it make business sense?
- lens-scalability     — Scalability: can it grow beyond one use case?
- lens-responsibility  — Responsibility: is it safe and fair?

SPECIAL ATTENTION — THIN AREAS
Our "value forms" currently have almost no content. Give particular depth to value-experience, value-perspective, value-decision, value-belonging and value-continuity (what a challenge partner actually receives). Also enrich q06 (day to day) and q07 (what I take away) with concrete, human detail wherever the context supports it.

OUTPUT
Return ONLY the JSON array — no prose before or after it. Aim for full coverage of the catalog, and mark honest gaps with confidence:"gap".

EXAMPLE ENTRY
{
  "id": "value-decision-verdict",
  "target": "value-decision",
  "question": "Decision: what we receive as a challenge partner",
  "roles": ["business"],
  "visitor_states": ["deciding"],
  "perspective": "joint",
  "status": "proposed",
  "answer": "You receive a clear, defensible verdict on your challenge, not a pitch deck. A team looks at your opportunity through five lenses — desirability, feasibility, viability, scalability and responsibility — and tells you, with evidence, whether it should proceed, be redirected, wait, or stop. A well-supported 'not yet' is treated as a genuine result, because it can save you from committing to the wrong build.",
  "grounding": "The five-lens assessment framework and the proceed/redirect/pause/reject verdict states.",
  "confidence": "supported"
}
