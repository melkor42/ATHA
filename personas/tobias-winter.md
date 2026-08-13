# Persona — Dr. Tobias Winter (ISTJ, Capricorn Sun)
> Test fixture for Agent 1 (Persona Modeler / Human Eval)

## Core Data
- Gender: male
- Born: January 10, 1990, 23:10, Munich, Germany
- Role in the network: Head of Data & Research at an enterprise partner; evaluates the signal network's data quality
- DISG tag: G/C (Conscientiousness) — secondary label only, low weight by design decision

## 16 Personalities (primary system)
- Type: ISTJ-A ("Logistician")
- Cognitive stack: Si (dominant) → Te → Fi (tertiary) → Ne (inferior)
- Behavioral reading: Dominant Si holds the reference standard; Te enforces it efficiently. He distrusts adjectives without definitions and promises without evidence. Inferior Ne makes unstructured brainstorming his personal hell.

## Zodiac (primary system)
- Sun in Capricorn: thoroughness as ambition; builds for the long term.
- Ascendant Virgo: the walking proofreader; notices the error in the footnote.
- Moon in Aquarius: cool, systemic distance; loves patterns, not feelings.
- Mercury in Capricorn: economical, precise communication; says less than he knows.
- Horoscope synthesis: The Capricorn Sun builds, the Virgo rising audits, the Aquarius Moon abstracts. A chart like an audit protocol — and he would accept that metaphor only if the term "audit protocol" were methodologically defined.

## Why the systems interlock
Si's reference-keeping is the Virgo rising as cognition; Te is the Capricorn Sun's results-through-rigor; the Aquarius Moon shifts the focus from single cases to systems, which is exactly what separates him from Miriam: both are results-oriented, but she wants the result *now*, he wants it *correct*. The generated pages must show that contrast (ranking vs. methodology).

## CV
- 2009–2012 B.Sc. Statistics, LMU Munich
- 2012–2014 M.Sc. Data Science, LMU Munich
- 2014–2018 PhD (Statistics), University of Warwick
- 2018–2021 Senior Data Scientist, insurance industry
- 2021–present Head of Data & Research, enterprise partner of the signal network

## Self-description (one sentence)
"Trust is sympathetic — but a robust data basis is better."

## Example prompt calling the Signal agent
"Signal, build me a page that makes the network's data structure transparent: active connections per sector, the methodology behind the match score, and a filterable list of enterprises with complete metadata. No adjectives — numbers and sources."

## Expected output of Agent 1 (PersonaModel)
```json
{
  "interests": ["data quality", "methodology", "network analysis"],
  "tone": "analytical",
  "accent_color": "primary",
  "expertise_level": "expert"
}
```