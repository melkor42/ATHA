# Persona — Miriam Stahl (ENTJ, Aries Sun)
> Test fixture for Agent 1 (Persona Modeler / Human Eval)

## Core Data
- Gender: female
- Born: March 28, 1988, 06:45, Frankfurt am Main, Germany
- Role in the network: Head of Talent Acquisition, Nordwind Technologies AG (Warwick alumna)
- DISG tag: D (Dominance) — secondary label only, low weight by design decision

## 16 Personalities (primary system)
- Type: ENTJ-A ("Commander")
- Cognitive stack: Te (dominant) → Ni → Se → Fi (inferior)
- Behavioral reading: Dominant Te organizes her world by outcomes, efficiency and accountability. Ni supplies the long-range strategy behind every quick decision. Inferior Fi means her values are private — she rarely explains herself, and recognition matters more than she would ever admit out loud.

## Zodiac (primary system)
- Sun in Aries: the impulse to be first; results over deliberation.
- Ascendant Capricorn: the impulse disciplined into posture — she never appears hectic, only unstoppable.
- Moon in Leo: needs visible achievement; she does not win quietly.
- Mercury in Aries: communication is fast, blunt, and allergic to preamble.
- Horoscope synthesis: The Aries Sun ignites, the Capricorn rising builds the ignition into a career-shaped machine, and the Leo Moon demands that the machine's output be seen. A chart of controlled forward pressure.

## Why the systems interlock
Te's outcome-obsession is the Aries Sun expressed as cognition; Capricorn rising is the Ni strategy made visible; the Leo Moon is the inferior Fi's hidden need for recognition, worn confidently on the surface. MBTI and zodiac describe the same person from two angles — the DISG "D" is merely the shadow these two systems cast.

## CV
- 2007–2010 B.Sc. Business Administration, Goethe University Frankfurt
- 2010–2012 M.Sc. Management, Warwick Business School
- 2012–2015 Strategy Consultant, Frankfurt
- 2015–2019 Head of Recruiting, mid-sized mechanical engineering company
- 2019–present Head of Talent Acquisition, Nordwind Technologies AG
- Side roles: conference speaker on recruiting, mentor in "Women in Leadership"

## Self-description (one sentence)
"I think in outcomes, not intentions — and I expect the same from a system."

## Example prompt calling the Signal agent
"Signal, build me a page that shows the top five Warwick students matching my current hiring need in cybersecurity and data science, ranked by match score, each with a one-click contact button. No stories, no decoration — data, score, contact."

## Expected output of Agent 1 (PersonaModel)
```json
{
  "interests": ["cybersecurity", "data science", "talent acquisition"],
  "tone": "direct",
  "accent_color": "warning",
  "expertise_level": "expert"
}
```