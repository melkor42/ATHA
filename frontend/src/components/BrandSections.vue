<script setup>
const ARCHITECTURES = [
  {
    name: 'Intelligence',
    text: 'Not just analytical — contextual. AI fed with what it cannot see on its own, the decision owned by a person who was in the room.'
  },
  {
    name: 'Organisation',
    text: 'Shared intelligence, redesigned. Roles, decision rights and knowledge flow rebuilt around it, not AI bolted onto the org chart.'
  },
  {
    name: 'Human',
    text: 'Healthier higher performance. The capacity AI frees goes into judgement, attention and relationships — not more output.'
  }
]

const LENSES = [
  { name: 'Desirability', text: 'Do people want it, and what changes for them?' },
  { name: 'Feasibility', text: 'Can it be built with the technology available?' },
  { name: 'Viability', text: 'Does the business case hold?' },
  { name: 'Scalability', text: 'Does it survive contact with the whole organisation?' },
  { name: 'Responsibility', text: 'Who owns the decision, and what could it harm?' }
]
</script>

<template>
  <div class="bands">
    <section id="programme" class="band">
      <span class="rule"></span>
      <h2>Real companies bring real decisions.</h2>
      <p class="lede">
        Executive MBA participants, specialists, mentors and researchers work a live
        company question for three days. Every recommendation is defended in front of
        the company in Discern, and one owned decision leaves the room. A well-supported
        no counts as a result.
      </p>
      <p class="label sub">ATHA rebuilds three architectures at once</p>
      <div class="cols">
        <div v-for="a in ARCHITECTURES" :key="a.name" class="col">
          <h3>{{ a.name }}</h3>
          <p>{{ a.text }}</p>
        </div>
      </div>
    </section>

    <section id="lenses" class="band">
      <span class="rule"></span>
      <h2>Every solution is judged on all five lenses. Most stop at two.</h2>
      <ol class="lenses">
        <li v-for="(l, i) in LENSES" :key="l.name">
          <span class="num">{{ String(i + 1).padStart(2, '0') }}</span>
          <h3>{{ l.name }}</h3>
          <p>{{ l.text }}</p>
        </li>
      </ol>
    </section>

    <section id="who" class="band">
      <span class="rule"></span>
      <h2>Run by OneMundi with Warwick Business School.</h2>
      <p class="lede">
        ATHA is a living laboratory for AI-native management education. WBS brings the
        Executive MBA cohort, the faculty and the research agenda; OneMundi brings the
        method, the partner companies and the architecture of the room. The school is
        known for producing unusually capable people. ATHA takes that to the frontier of
        AI-native management education.
      </p>
      <p class="label sub">WBS × OneMundi</p>
    </section>
  </div>
</template>

<style scoped>
.bands { display: flex; flex-direction: column; gap: 96px; }
.band { display: flex; flex-direction: column; gap: 18px; }
.band h2 { font-size: clamp(28px, 4.2vw, 46px); }
.band h3 { font-size: 22px; font-weight: 400; }
.lede { font-size: 17px; line-height: 1.5; opacity: 0.8; max-width: 68ch; }
.sub { margin-top: 18px; }
.cols {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 34px;
}
.cols .col { display: flex; flex-direction: column; gap: 8px; }
.cols p { font-size: 15px; line-height: 1.46; opacity: 0.75; }
.lenses {
  margin: 0;
  padding: 0;
  list-style: none;
  display: flex;
  flex-direction: column;
}
.lenses li {
  display: grid;
  grid-template-columns: 40px 190px 1fr;
  gap: 18px;
  align-items: baseline;
  padding: 14px 0;
  border-top: 1px solid var(--rule);
}
.lenses li:last-child { border-bottom: 1px solid var(--rule); }
.lenses h3 { font-size: 19px; font-weight: 400; }
.lenses p { font-size: 15px; opacity: 0.75; }
.num {
  font-family: var(--f-mono);
  font-size: 10px;
  letter-spacing: 0.12em;
  opacity: 0.45;
}
@media (max-width: 860px) {
  .cols { grid-template-columns: 1fr; gap: 26px; }
  .lenses li { grid-template-columns: 34px 1fr; }
  .lenses p { grid-column: 2; }
}
</style>
