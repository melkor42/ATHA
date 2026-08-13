# Persona — Jonas Neumann (ENFP, Sagittarius Sun)
> Test fixture for Agent 1 (Persona Modeler / Human Eval)

## Core Data
- Gender: male
- Born: December 9, 1999, 14:20, Cologne, Germany
- Role in the network: Warwick undergraduate (final year), president of the Warwick Entrepreneurship Society
- DISG tag: I (Initiative) — secondary label only, low weight by design decision

## 16 Personalities (primary system)
- Type: ENFP-T ("Campaigner")
- Cognitive stack: Ne (dominant) → Fi → Te (tertiary) → Si (inferior)
- Behavioral reading: Dominant Ne sees possibilities and people-potential everywhere; Fi makes his enthusiasm genuinely felt rather than performed. Tertiary Te lets him actually ship events when it matters; inferior Si explains why routine paperwork physically pains him.

## Zodiac (primary system)
- Sun in Sagittarius: explorer's optimism, big gestures, allergy to small talk about small things.
- Ascendant Gemini: the born conversation-starter; people experience him as a friendly rapid-fire of ideas.
- Moon in Aries: spontaneous ignition — first on stage, first to suggest the after-party.
- Mercury in Sagittarius: talks in visions and stories, occasionally at the expense of precision.
- Horoscope synthesis: A chart like a confetti cannon diagram — Sagittarius aims at meaning and adventure, Gemini rising turns it into constant connection, and the Aries Moon pulls the trigger without a countdown. Warm, not chaotic.

## Why the systems interlock
Ne's idea-firework is the Sagittarius Sun as cognition; Gemini rising is Ne made audible; the Aries Moon is the spontaneous spark that Fi then warms into genuine care for people. Note for testing: his networking is strategic (entrepreneurship society), only the *style* is playful — the generated page must capture energy without mistaking him for shallow.

## CV
- 2018 Abitur, Cologne; 2018–2019 volunteer year (FSJ) in cultural work, youth theatre
- 2019–present B.Sc. Management, University of Warwick
- 2022–present President, Warwick Entrepreneurship Society
- 2023 Internship in Community & Events, Berlin startup
- 2024–present Organizer, Warwick Hackathon Nights

## Self-description (one sentence)
"I'm the person who makes ten new friends at an event before the first talk even starts."

## Example prompt calling the Signal agent
"Signal, give me a page that feels like the aftermovie of a great night: the three best moments from the last Signal event, the people I absolutely have to meet, and the next events I can't miss. Colorful, fast, full of energy."

## Expected output of Agent 1 (PersonaModel)
```json
{
  "interests": ["networking", "entrepreneurship", "events"],
  "tone": "playful",
  "accent_color": "accent",
  "expertise_level": "advanced"
}
```