# Persona — David Bergmann (ISFJ, Cancer Sun)
> Test fixture for Agent 1 (Persona Modeler / Human Eval)

## Core Data
- Gender: male
- Born: July 3, 1998, 05:30, Freiburg im Breisgau, Germany
- Role in the network: Warwick alumnus, Career & Wellbeing Advisor in the Student Advisory Service, alumni mentor
- DISG tag: S (Steadiness) — secondary label only, low weight by design decision

## 16 Personalities (primary system)
- Type: ISFJ-A ("Defender")
- Cognitive stack: Si (dominant) → Fe → Ti (tertiary) → Ne (inferior)
- Behavioral reading: Dominant Si remembers what people mentioned in passing and keeps doing the quiet work; Fe tunes him to the emotional temperature of the room. He initiates, but always invitingly, never pushily. Inferior Ne makes sudden change quietly exhausting.

## Zodiac (primary system)
- Sun in Cancer: caring as identity; protects the people in his circle.
- Ascendant Taurus: the calm of a person nothing rushes; pressure visibly bounces off him.
- Moon in Pisces: high empathy; hears what is not said.
- Mercury in Cancer: communicates carefully, personally, with memory for detail.
- Horoscope synthesis: The Cancer Sun makes caring the core, the Taurus rising sets the pace to walking speed, and the Pisces Moon supplies the antenna. A chart that reads like instructions for listening.

## Why the systems interlock
Si's loyal continuity is the Taurus rising made cognitive; Fe is the Cancer Sun's care expressed as attention to others; the Pisces Moon deepens Fe into genuine empathy. Green behavior here is not passivity — it is initiative without pressure. The generated page must nail exactly that difference: welcoming, never demanding.

## CV
- 2017–2020 B.Sc. Psychology, University of Warwick
- 2020–2022 M.Sc. Counselling Psychology, University of Warwick
- 2022–present Career & Wellbeing Advisor, Student Advisory Service Warwick
- Volunteer: crisis hotline (since 2021), alumni mentoring program

## Self-description (one sentence)
"I'm good at what others overlook: making sure people feel seen."

## Example prompt calling the Signal agent
"Signal, I want the page to look like nature and human focused: calm, warm, organic. Show me two or three stories of students who found a mentor through the network, and give me a gentle, low-pressure way to reach out myself."

## Expected output of Agent 1 (PersonaModel)
```json
{
  "interests": ["mentoring", "wellbeing", "community"],
  "tone": "warm",
  "accent_color": "success",
  "expertise_level": "advanced"
}
```