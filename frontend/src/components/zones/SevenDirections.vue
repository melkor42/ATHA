<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { usePlaza } from '../../composables/usePlaza.js'

// The quiet wing's knowledge content — the ATHA decision-quality copy,
// lifted 1:1 from the former south-east Wisdom Corner into a two-layer
// card system: seven tablet cards (layer 1), an in-tile overlay panel
// (layer 2). All copy is verbatim from the approved prototype — nothing
// invented, unconfirmed items keep their status labels.
const { current, goTo, reduced } = usePlaza()

const DIRS = [
  { id: 'c1', n: '01', name: 'The Question', h: 64, d: 'Why this exists. Not what can be built, but what should be.' },
  { id: 'c2', n: '02', name: 'The Method', h: 104, d: 'Three independent teams, five lenses, one question.' },
  { id: 'c3', n: '03', name: 'The Finding', h: 104, d: 'What a challenge partner receives, and why it holds up.' },
  { id: 'c4', n: '04', name: 'The Conditions', h: 88, d: 'The environment the work is done in, and why it is part of the work.' },
  { id: 'c5', n: '05', name: 'The Rhythm', h: 80, d: 'Seven stages, and the deliberate space between them.' },
  { id: 'c6', n: '06', name: 'Edition 001', h: 64, d: 'Forming. Nothing confirmed, set out as it stands.' },
  { id: 'c7', n: '07', name: 'The Layers', h: 56, d: 'OneMundi, Warwick Business School, and the experience design.' }
]

const VERDICTS = [
  { label: 'Proceed', cap: 'Struck at proceed · conditions for success and an implementation pathway follow' },
  { label: 'Redirect', cap: 'Struck at redirect · the opportunity is real, the framing was wrong' },
  { label: 'Pause', cap: 'Struck at pause · the organisation is not yet able to answer this well' },
  { label: 'Reject', cap: 'Struck at reject · a well-supported decision not to build is a legitimate result' }
]

// [label, duration units (× 11px), gap tick shown above this stage]
const STAGES = [
  { label: 'Arrive & settle', units: 3, gap: '' },
  { label: 'Open & sense', units: 2, gap: 'rest 90′' },
  { label: 'Connect', units: 3, gap: 'meal 75′' },
  { label: 'Create', units: 9, gap: 'rest 8h' },
  { label: 'Discern', units: 7, gap: 'rest 90′' },
  { label: 'Celebrate', units: 3, gap: 'meal 120′' },
  { label: 'Integrate & return', units: 2, gap: 'rest 60′' }
]

const PARAMS = [
  { what: 'Around 45 selected participants, Warwick-centred', status: 'Proposed' },
  { what: 'Nine multidisciplinary teams of five', status: 'Proposed' },
  { what: 'Three real enterprise AI challenges', status: 'Proposed' },
  { what: 'Three independent teams per challenge', status: 'Proposed' },
  { what: 'A multi-day working experience at Warwick Business School, Coventry', status: 'Proposed' },
  { what: 'Possible later enterprise showcase at WBS The Shard, London', status: 'Under review' },
  { what: 'Dates', status: 'Not fixed' },
  { what: 'Challenge partners', status: 'Being selected' }
]

const LAYERS = [
  { who: 'OneMundi', what: 'Initiator and owner. Enterprise transformation, the AI-native methodology, the commercial model, the independence of the verdict, and the ecosystem that continues between editions.' },
  { who: 'Warwick Business School', what: 'Partner and co-host. Academic environment, knowledge, participants, research, network and institutional standards.' },
  { who: 'The experience design', what: 'Rhythm, stewardship, nourishment, psychological safety and integration — the human operating system beneath the work. Shaped as a HADORA experience.' }
]

const expanded = ref(null) // null = overview, else 'c1'..'c7'
const pressed = ref(3) // verdict line: Reject is struck by default
const scroller = ref(null) // panel scroller, focused on open

const activeIndex = computed(() => DIRS.findIndex((d) => d.id === expanded.value))
const activeDir = computed(() => (activeIndex.value >= 0 ? DIRS[activeIndex.value] : null))
const prevDir = computed(() => (activeIndex.value > 0 ? DIRS[activeIndex.value - 1] : null))
const nextDir = computed(() => (activeIndex.value >= 0 && activeIndex.value < DIRS.length - 1 ? DIRS[activeIndex.value + 1] : null))

function open(id) {
  expanded.value = id
}
function collapse() {
  expanded.value = null
}
// prev/next + in-article cross-links switch direction without returning
// to the overview
function navigate(id) {
  if (expanded.value !== id) expanded.value = id
}

function onKey(e) {
  // only collapse from Escape while the camera is actually on this zone
  if (e.key === 'Escape' && expanded.value && current.value === 'west') collapse()
}
onMounted(() => window.addEventListener('keydown', onKey))
onBeforeUnmount(() => window.removeEventListener('keydown', onKey))

// every open starts at the top of the article, focus on the panel scroller
watch(expanded, (v) => {
  if (!v) return
  nextTick(() => {
    scroller.value?.scrollTo({ top: 0 })
    scroller.value?.focus({ preventScroll: true })
  })
})
</script>

<template>
  <div class="seven" :class="{ reduced }">
    <!-- ============ LAYER 1 — seven tablet cards ============ -->
    <p class="say">The quality of a decision depends on the conditions in which it was made.</p>
    <div class="dirs">
      <button
        v-for="d in DIRS"
        :key="d.id"
        type="button"
        class="dir"
        :aria-label="`${d.n} ${d.name} — ${d.d}`"
        @click="open(d.id)"
      >
        <span class="dir-no">{{ d.n }}</span>
        <span class="dir-name">{{ d.name }}</span>
        <span class="dir-teaser">{{ d.d }}</span>
      </button>
    </div>

    <!-- ============ LAYER 2 — expanded direction overlay ============
         the scrim resolves `position: absolute; inset: 0` against the
         zone's tile: `position: fixed` would resolve against the
         transformed .plaza-world (300vw×300vh) and land off-screen. -->
    <div
      class="overlay"
      :class="{ open: !!expanded }"
      :aria-hidden="expanded ? 'false' : 'true'"
      @click.self="collapse"
    >
      <div class="panel">
        <button type="button" class="close" aria-label="Close direction" @click="collapse">
          Close ✕
        </button>
        <div
          ref="scroller"
          class="panel-scroll scrollable"
          tabindex="-1"
          role="dialog"
          aria-modal="true"
          :aria-label="activeDir ? `${activeDir.n} ${activeDir.name}` : 'Direction'"
        >
          <!-- ================= 01 THE QUESTION ================= -->
          <article v-if="expanded === 'c1'" class="comp">
            <div class="wrap comp-in">
              <div class="eyebrow">01 · The Question</div>
              <h2 class="dsp">Not what can be built. What should be.</h2>
              <p class="lede">Most organisations can tell an AI opportunity from an AI expense only after they have spent the money.</p>
            </div>

            <div class="band band--slip">
              <div class="wrap">
                <div class="blocks blocks--2">
                  <div>
                    <h3 class="blk-h">The inversion</h3>
                    <p class="blk-p">Teams do not ask whether something can be built. Almost everything can. They determine whether it should be pursued, under what conditions, and with what consequences — for the business, for the people in it, and for everyone downstream of the decision.</p>
                  </div>
                  <div>
                    <h3 class="blk-h">A reject is a result</h3>
                    <p class="blk-p">A well-supported decision not to build can be worth more than an impressive prototype. It is the outcome no consultancy is paid to reach and no hackathon is structured to produce.</p>
                  </div>
                </div>
              </div>
            </div>

            <div class="wrap pad-top-lg">
              <div class="blocks">
                <div>
                  <h3 class="blk-h">What an organisation actually needs to know</h3>
                  <p class="blk-p">Which AI opportunities are genuinely valuable. Which ideas should not be implemented at all. How the work changes people, culture and leadership. Whether it is commercially and operationally viable. What ethical, social and environmental consequences follow. And how humans and AI can work together without anyone quietly losing responsibility for the outcome.</p>
                </div>
                <div>
                  <h3 class="blk-h">Why it needs conditions</h3>
                  <p class="blk-p">Discernment is not a faster kind of thinking. It needs enough time, enough disagreement, enough evidence and enough rest to be worth trusting. Those are conditions, and conditions can be designed.</p>
                </div>
              </div>
            </div>
          </article>

          <!-- ================= 02 THE METHOD ================= -->
          <article v-if="expanded === 'c2'" class="comp">
            <div class="wrap comp-in">
              <div class="eyebrow">02 · The Method</div>
              <h2 class="dsp">Three teams. One question. No shared reasoning.</h2>
              <p class="lede">Three independent multidisciplinary teams investigate the same challenge separately, without knowledge of one another's work — then converge in a facilitated process.</p>
            </div>

            <div class="wrap pad-top-md">
              <div class="teams">
                <div class="team"><div class="k">Team 01</div><p>Investigates independently. Its own evidence, its own assumptions, its own verdict.</p></div>
                <div class="team"><div class="k">Team 02</div><p>Same question. No contact. Arrives somewhere the first team did not.</p></div>
                <div class="team"><div class="k">Team 03</div><p>Same again. Three findings, and the disagreements between them preserved rather than reconciled.</p></div>
              </div>
              <p class="lede lede-mid">Where the three disagree is often the most useful part of what a partner receives.</p>
            </div>

            <div class="band">
              <div class="wrap">
                <div>
                  <h3 class="blk-h">Five lenses</h3>
                  <p class="blk-p">An AI opportunity is an organisational and human system, not a technical product. Each team examines the same five dimensions, and a weakness in any one of them is a finding in itself.</p>
                </div>
                <div class="lenses">
                  <div class="lens"><div class="k">01</div><div class="v">Desirability</div></div>
                  <div class="lens"><div class="k">02</div><div class="v">Feasibility</div></div>
                  <div class="lens"><div class="k">03</div><div class="v">Viability</div></div>
                  <div class="lens"><div class="k">04</div><div class="v">Scalability</div></div>
                  <div class="lens"><div class="k">05</div><div class="v">Responsibility</div></div>
                </div>
              </div>
            </div>

            <div class="wrap pad-top-lg">
              <div class="blocks blocks--2">
                <div>
                  <h3 class="blk-h">AI-native means process redesign</h3>
                  <p class="blk-p">Not tool use. AI organises context, tests assumptions, surfaces blind spots and preserves reasoning so that nothing is lost between the room and the board. Every finding carries a transparent record of how AI contributed to it.</p>
                </div>
                <div>
                  <h3 class="blk-h">Humans keep the decision</h3>
                  <p class="blk-p">Context, meaning, ethics, verification and the final judgement stay with people. The record exists so that a board can see exactly where the machine helped and exactly where a person decided.</p>
                </div>
              </div>
              <hr />
              <div>
                <h3 class="blk-h">No overall winner</h3>
                <p class="blk-p">There is no ranking and no prize for first place. Recognition celebrates different forms of excellence, which is a structural decision rather than a courtesy — a single winner would reintroduce the competition the format exists to remove.</p>
              </div>
            </div>
          </article>

          <!-- ================= 03 THE FINDING ================= -->
          <article v-if="expanded === 'c3'" class="comp">
            <div class="wrap comp-in">
              <div class="eyebrow">03 · The Finding</div>
              <h2 class="dsp">Proceed. Redirect. Pause. Reject.</h2>
              <p class="lede">What a challenge partner receives is not a prototype and not a pitch. It is a defensible, board-ready implementation verdict — three of them, and the reasoning behind each.</p>
            </div>

            <div class="band">
              <div class="wrap">
                <div class="vline" role="group" aria-label="Verdict states">
                  <button
                    v-for="(v, i) in VERDICTS"
                    :key="v.label"
                    type="button"
                    class="vst"
                    :aria-pressed="pressed === i ? 'true' : 'false'"
                    @click="pressed = i"
                  >
                    <span class="t">{{ v.label }}</span><span class="d"></span>
                  </button>
                </div>
                <div class="vrule"></div>
                <div class="vcap">{{ VERDICTS[pressed].cap }}</div>
              </div>
            </div>

            <div class="wrap pad-top-lg">
              <div class="blocks blocks--2">
                <div>
                  <h3 class="blk-h">What is in it</h3>
                  <p class="blk-p">The proposed opportunity. Supporting evidence. The assumptions that were challenged, and what happened to them. Organisational and commercial implications. Human, ethical and environmental consequences. Risks and the conditions under which the thing would actually succeed. An implementation pathway, recommended next actions, and the record of how AI contributed.</p>
                </div>
                <div>
                  <h3 class="blk-h">Prototypes are evidence</h3>
                  <p class="blk-p">Something may get built during the work. If it does, it exists to test an assumption — never as the point, and never as the deliverable.</p>
                </div>
                <div>
                  <h3 class="blk-h">We are not paid to recommend action</h3>
                  <p class="blk-p">A vendor has an interest in the answer. A consultancy is usually engaged on the assumption that something will proceed. Here the verdict can be no, and the commercial model does not punish that.</p>
                </div>
                <div>
                  <h3 class="blk-h">Bring a challenge</h3>
                  <p class="blk-p">One real, unresolved AI question your organisation has not been able to settle internally. Challenge partners for Edition 001 are being selected now; nothing is confirmed and the process is open.</p>
                  <div class="paths paths-blk">
                    <button type="button" class="btn" @click="navigate('c6')">See Edition 001</button>
                  </div>
                </div>
              </div>
            </div>
          </article>

          <!-- ================= 04 THE CONDITIONS ================= -->
          <article v-if="expanded === 'c4'" class="comp">
            <div class="wrap comp-in">
              <div class="eyebrow">04 · The Conditions</div>
              <h2 class="dsp">Human energy is an input into the quality of the work.</h2>
              <p class="lede">Not a benefit placed around the work. An input to it — and therefore designed with the same seriousness as the analysis.</p>
            </div>

            <div class="wrap pad-top-md2">
              <div class="blocks blocks--2">
                <div>
                  <h3 class="blk-h">Rest is scheduled as work is scheduled</h3>
                  <p class="blk-p">Sleep, meals, movement, time outside and reflection sit on the same measure as the working blocks, at the same scale, with the same status. That single scheduling decision states the whole position, and it is the reason nobody has to be told about it.</p>
                </div>
                <div>
                  <h3 class="blk-h">The room is made, not booked</h3>
                  <p class="blk-p">Warm layered light rather than overhead fluorescent. Real plates. Paper, wood, wool and ceramic. No banners, no branded gilets, nothing that would be thrown away on the Monday. If it cannot be kept, it is not produced.</p>
                </div>
                <div>
                  <h3 class="blk-h">Ambition without exhaustion</h3>
                  <p class="blk-p">Rigour, commercial consequence and genuine ambition do not require depletion, fragmentation or unhealthy competition. That claim is the thing being tested here, alongside the enterprise questions.</p>
                </div>
                <div>
                  <h3 class="blk-h">You should leave more capable</h3>
                  <p class="blk-p">Not needing to recover. Participants should end more energised, more connected and better at the work than when they arrived, and if that is not what happens, the format is wrong.</p>
                </div>
              </div>
            </div>

            <div class="band band--deep">
              <div class="wrap">
                <p class="pull">Design the conditions, not the person.</p>
              </div>
            </div>
          </article>

          <!-- ================= 05 THE RHYTHM ================= -->
          <article v-if="expanded === 'c5'" class="comp">
            <div class="wrap comp-in">
              <div class="eyebrow">05 · The Rhythm</div>
              <h2 class="dsp">Seven stages. The gaps are designed too.</h2>
              <p class="lede">ATHA is not an agenda. It follows a human and intellectual arc, and the length of each stage is a decision rather than a leftover.</p>
              <div class="rail">
                <template v-for="(s, i) in STAGES" :key="s.label">
                  <div v-if="i > 0" class="rg" :style="{ height: (i === 3 ? 26 : 12) + 'px' }" aria-hidden="true">
                    <span class="sp"></span><span class="tk">{{ s.gap }}</span>
                  </div>
                  <div class="rs" :class="{ hi: i === 4 }">
                    <span class="bar" :style="{ height: s.units * 11 + 'px' }"></span>
                    <span class="lb">{{ s.label }}</span>
                  </div>
                </template>
              </div>
              <p class="lede lede-rail">DISCERN is given more room than any stage except the work itself. A conventional programme of the same length would be a single unbroken block.</p>
            </div>

            <div class="band band--slip">
              <div class="wrap">
                <div class="blocks blocks--2">
                  <div>
                    <h3 class="blk-h">Arrive, open, connect</h3>
                    <p class="blk-p">People are met rather than processed. The question is opened before it is attacked — partners present the problem as it actually sits with them, including what they have already tried and what they are afraid the answer might be. Teams then form across disciplines.</p>
                  </div>
                  <div>
                    <h3 class="blk-h">Create, discern, celebrate, return</h3>
                    <p class="blk-p">The longest stage is the investigation, and the second longest is deciding what it means. Recognition is shared rather than ranked. People leave with something integrated, and the relationships carry into the next edition.</p>
                  </div>
                </div>
              </div>
            </div>
          </article>

          <!-- ================= 06 EDITION 001 ================= -->
          <article v-if="expanded === 'c6'" class="comp">
            <div class="wrap comp-in">
              <div class="eyebrow">06 · Edition 001</div>
              <h2 class="dsp">Forming.</h2>
              <p class="lede">Nothing below is confirmed. No challenge partner, sponsor or funding is agreed, and the dates are not fixed. It is set out here as it actually stands, because the alternative is to imply otherwise.</p>
            </div>

            <div class="wrap pad-top-sm">
              <div class="params">
                <div v-for="p in PARAMS" :key="p.what" class="prow">
                  <span>{{ p.what }}</span><span class="s">{{ p.status }}</span>
                </div>
              </div>
            </div>

            <div class="band">
              <div class="wrap">
                <div class="blocks blocks--2">
                  <div>
                    <h3 class="blk-h">Who takes part</h3>
                    <p class="blk-p">Students and emerging leaders, founders, researchers, creatives, and other carefully selected contributors from the Warwick ecosystem and partner networks. Places are limited and selected. Executives and investors take part as challenge partners, mentors and expert contributors rather than as participants.</p>
                  </div>
                  <div>
                    <h3 class="blk-h">Take part</h3>
                    <p class="blk-p">You would spend several days on a question a real organisation has not been able to answer — with access to the people who have to make the decision, alongside people from disciplines other than your own, and with the time and conditions to think properly.</p>
                    <div class="paths paths-blk">
                      <button type="button" class="btn btn--inv" @click="navigate('c4')">See the conditions</button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </article>

          <!-- ================= 07 THE LAYERS ================= -->
          <article v-if="expanded === 'c7'" class="comp">
            <div class="wrap comp-in">
              <div class="eyebrow">07 · The Layers</div>
              <h2 class="dsp">ATHA exists only where three systems meet.</h2>
              <p class="lede">None of the three is an addition to the others. Remove any one and what remains is something ATHA is specifically not.</p>
            </div>

            <div class="wrap pad-top-sm">
              <div v-for="l in LAYERS" :key="l.who" class="layer">
                <div class="who">{{ l.who }}</div>
                <div class="what">{{ l.what }}</div>
              </div>
            </div>

            <div class="wrap pad-top-xl">
              <div>
                <h3 class="blk-h">A series, not an event</h3>
                <p class="blk-p">ATHA is built to recur. Every relationship formed in an edition is intended to persist into the next one, and the archive of findings compounds rather than resets. Edition 001 is the first, not the whole thing.</p>
              </div>
            </div>
          </article>

          <!-- ============ PANEL FOOTER: prev/next + east-gate CTAs ============ -->
          <footer class="cfoot">
            <div class="wrap">
              <div class="cnav">
                <button v-if="prevDir" type="button" @click="navigate(prevDir.id)">← {{ prevDir.name }}</button>
                <span v-else class="mid"></span>
                <button type="button" @click="collapse">All directions</button>
                <button v-if="nextDir" type="button" @click="navigate(nextDir.id)">{{ nextDir.name }} →</button>
                <span v-else class="mid"></span>
              </div>
              <div class="paths cpaths">
                <button type="button" class="btn" @click="goTo('east')">Bring a challenge</button>
                <button type="button" class="btn btn--g" @click="goTo('east')">Take part</button>
              </div>
              <div class="meta cfoot-meta">Edition 001 · Forming · Nothing confirmed</div>
            </div>
          </footer>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.seven {
  --gut: clamp(20px, 5.5vw, 72px);
  --max: 1180px;
  /* tone derivatives the prototype kept as literal rgba */
  --muted: rgba(42, 38, 34, 0.56);
  --muted-l: rgba(242, 237, 228, 0.62);
  --hair-l: rgba(242, 237, 228, 0.22);
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: clamp(14px, 2.4vh, 22px);
  color: var(--atha-clay);
  font-family: var(--atha-font-body);
  line-height: 1.62;
  -webkit-font-smoothing: antialiased;
}
.seven ::selection { background: var(--atha-rind); color: var(--atha-clay); }
.seven button { font: inherit; color: inherit; background: none; border: 0; padding: 0; cursor: pointer; }
.seven :focus-visible { outline: 2px solid var(--atha-ferrous); outline-offset: 3px; }

/* ============ LAYER 1 — tablet cards (InfosZone tablet optics) ============ */
/* the wing's thesis line — verbatim from the old hub head, kept quiet */
.say {
  margin: 0;
  max-width: 34ch;
  text-align: center;
  font-family: var(--atha-font-display);
  font-weight: 300;
  font-variation-settings: "opsz" 60;
  font-size: clamp(15px, 1.7vw, 19px);
  line-height: 1.4;
  letter-spacing: -0.005em;
  color: rgba(43, 38, 34, 0.6);
}
.dirs {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 14px;
  width: min(920px, 94%);
}
.dir {
  background: rgba(250, 247, 240, 0.93);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 251, 240, 0.9);
  border-radius: 22px 26px 24px 20px;
  padding: 18px 20px;
  box-shadow: 0 10px 30px rgba(30, 40, 45, 0.14);
  display: flex;
  flex-direction: column;
  gap: 8px;
  text-align: left;
  color: #241f1b;
  transition: transform 0.35s var(--atha-ease), box-shadow 0.35s var(--atha-ease), background 0.35s ease;
}
.dir:hover {
  transform: translateY(-4px);
  background: rgba(252, 250, 244, 0.97);
  box-shadow: 0 16px 38px rgba(30, 40, 45, 0.2);
}
.dir-no {
  font-family: var(--atha-font-mono);
  font-size: 11.5px;
  letter-spacing: 0.22em;
  color: rgba(43, 38, 34, 0.55);
}
.dir-name {
  font-family: var(--atha-font-display);
  font-weight: 400;
  font-variation-settings: "opsz" 40;
  font-size: 19px;
  line-height: 1.2;
}
.dir-teaser {
  font-size: 13.5px;
  line-height: 1.5;
  color: var(--muted);
}

/* ============ LAYER 2 — overlay + panel ============ */
.overlay {
  position: absolute;
  inset: 0;
  z-index: 30;
  background: rgba(30, 36, 25, 0.32);
  opacity: 0;
  visibility: hidden;
  transition: opacity 0.4s var(--atha-ease), visibility 0s linear 0.4s;
}
.overlay.open {
  opacity: 1;
  visibility: visible;
  transition: opacity 0.4s var(--atha-ease);
}
.panel {
  position: absolute;
  inset: 5%;
  background: rgba(250, 247, 240, 0.93);
  border: 1px solid rgba(255, 251, 240, 0.9);
  border-radius: 22px 26px 24px 20px;
  box-shadow: 0 24px 64px rgba(20, 30, 35, 0.28);
  transform: translateY(16px) scale(0.985);
  transition: transform 0.4s var(--atha-ease);
}
.overlay.open .panel { transform: none; }
.close {
  position: absolute;
  top: 14px;
  right: 18px;
  z-index: 4;
  font-family: var(--atha-font-mono);
  font-size: 0.6875rem;
  letter-spacing: 0.11em;
  text-transform: uppercase;
  color: var(--muted);
  transition: color 0.2s ease;
}
.close:hover { color: var(--atha-ferrous); }
.panel-scroll {
  position: absolute;
  inset: 0;
  overflow-y: auto;
  scrollbar-width: thin;
  scrollbar-color: rgba(42, 38, 34, 0.35) transparent;
  border-radius: inherit;
  font-size: 1rem;
}
.panel-scroll:focus { outline: none; }

/* ============ shared article grammar (ported from the old zone) ============ */
.wrap { max-width: var(--max); margin: 0 auto; padding: 0 var(--gut); }
.meta {
  font-family: var(--atha-font-mono); font-size: var(--atha-s0); letter-spacing: 0.1em;
  text-transform: uppercase; color: var(--muted); line-height: 1.7;
}
.dsp {
  font-family: var(--atha-font-display); font-weight: 300;
  font-variation-settings: "opsz" 144; letter-spacing: -0.018em; line-height: 1.1; margin: 0;
}
.panel-scroll p { margin: 0 0 1.05em; max-width: 60ch; }
.panel-scroll p:last-child { margin-bottom: 0; }
.panel-scroll hr { border: 0; border-top: 1px solid var(--atha-hair); margin: clamp(30px, 4.5vw, 54px) 0; }

/* pad helpers replacing prototype inline styles */
.pad-top-sm { padding-top: clamp(36px, 5vw, 58px); }
.pad-top-md { padding-top: clamp(40px, 5vw, 64px); }
.pad-top-md2 { padding-top: clamp(40px, 5.5vw, 72px); }
.pad-top-lg { padding-top: clamp(48px, 7vw, 92px); }
.pad-top-xl { padding-top: clamp(44px, 6vw, 76px); }

/* pathways */
.paths {
  display: flex; flex-wrap: wrap; gap: clamp(14px, 2.4vw, 26px); align-items: center;
  margin-top: clamp(36px, 5vw, 60px);
}
.paths-blk { margin-top: 22px; }
.btn {
  display: inline-block; background: var(--atha-clay); color: var(--atha-chalk);
  padding: 14px 26px; font-family: var(--atha-font-mono); font-size: 0.6875rem;
  letter-spacing: 0.12em; text-transform: uppercase; transition: background 0.25s ease;
}
.btn:hover { background: var(--atha-ferrous); }
.btn--g { background: none; color: var(--atha-clay); padding: 14px 0; border-bottom: 1px solid var(--atha-clay); }
.btn--g:hover { background: none; color: var(--atha-ferrous); border-color: var(--atha-ferrous); }
.btn--inv { background: var(--atha-chalk); color: var(--atha-clay); }
.btn--inv:hover { background: var(--atha-rind); }

/* ============ DIRECTION ARTICLES ============ */
.comp { padding-bottom: 0; }
.comp-in { padding-top: clamp(48px, 6vw, 80px); }
.eyebrow {
  font-family: var(--atha-font-mono); font-size: 0.6875rem; letter-spacing: 0.14em;
  text-transform: uppercase; color: var(--atha-ferrous); margin-bottom: clamp(20px, 3vw, 30px);
}
.comp h2 { font-size: clamp(1.75rem, 4.4vw, 3.2rem); max-width: 17ch; font-weight: 300; }
.lede {
  font-size: clamp(1.02rem, 1.5vw, 1.2rem); line-height: 1.55; max-width: 52ch;
  margin-top: clamp(26px, 3.6vw, 40px);
}
.lede-mid { margin-top: clamp(28px, 4vw, 42px); }
.lede-rail { margin-top: clamp(32px, 4vw, 48px); }
.blocks { margin-top: clamp(40px, 6vw, 76px); display: grid; gap: clamp(30px, 4vw, 52px); }
@media (min-width: 800px) { .blocks--2 { grid-template-columns: 1fr 1fr; } }
.blk-h {
  font-family: var(--atha-font-display); font-weight: 400; font-variation-settings: "opsz" 40;
  font-size: 1.15rem; line-height: 1.3; margin: 0 0 12px; letter-spacing: -0.004em;
}
.blk-p { font-size: 0.9375rem; color: var(--muted); max-width: 48ch; }
.band {
  background: var(--atha-field); color: var(--atha-chalk);
  padding: clamp(48px, 7vw, 92px) 0; margin-top: clamp(48px, 7vw, 92px);
}
.band .blk-p, .band .lede { color: var(--muted-l); }
.band .blk-h { color: var(--atha-chalk); }
.band--slip { background: var(--atha-slip); color: var(--atha-clay); }
.band--slip .blk-p { color: var(--muted); }
.band--deep { background: var(--atha-deep); color: var(--atha-chalk); }
.band--deep .blk-p { color: var(--muted-l); }

/* conditions pull line */
.pull {
  margin: 0; font-family: var(--atha-font-display); font-weight: 300; font-style: italic;
  font-variation-settings: "opsz" 60; font-size: clamp(1.3rem, 2.8vw, 2rem);
  line-height: 1.35; max-width: 26ch; color: var(--atha-chalk);
}

/* lenses */
.lenses {
  display: grid; gap: 1px; background: var(--hair-l); border: 1px solid var(--hair-l);
  margin-top: clamp(28px, 4vw, 42px);
}
@media (min-width: 700px) { .lenses { grid-template-columns: repeat(5, 1fr); } }
.lens { background: var(--atha-field); padding: 22px 18px; }
.lens .k { font-family: var(--atha-font-mono); font-size: 0.625rem; letter-spacing: 0.12em; color: var(--atha-rind); }
.lens .v {
  font-family: var(--atha-font-display); font-weight: 300; font-variation-settings: "opsz" 40;
  font-size: 1.05rem; margin-top: 10px; line-height: 1.2;
}

/* three teams */
.teams {
  display: grid; gap: 1px; background: var(--atha-hair); border: 1px solid var(--atha-hair);
  margin-top: clamp(28px, 4vw, 42px);
}
@media (min-width: 700px) { .teams { grid-template-columns: repeat(3, 1fr); } }
.team { background: var(--atha-chalk); padding: 26px 22px; }
.team .k { font-family: var(--atha-font-mono); font-size: 0.625rem; letter-spacing: 0.12em; color: var(--atha-rule); }
.team p { font-size: 0.875rem; color: var(--muted); margin-top: 12px; max-width: none; }

/* verdict line */
.vline { display: flex; margin-top: clamp(30px, 4vw, 46px); }
.vst { flex: 1; text-align: center; }
.vst .t {
  font-family: var(--atha-font-mono); font-size: 0.6875rem; letter-spacing: 0.14em;
  text-transform: uppercase; color: var(--muted-l); display: block; padding-bottom: 15px;
  transition: color 0.25s ease;
}
.vst .d {
  width: 8px; height: 8px; background: var(--atha-chalk); opacity: 0.32; margin: 0 auto;
  transition: all 0.3s var(--atha-ease);
}
.vst[aria-pressed="true"] .t { color: var(--atha-chalk); }
.vst[aria-pressed="true"] .d { background: var(--atha-rind); opacity: 1; transform: scale(1.9); }
.vrule { height: 1px; background: var(--hair-l); margin-top: -4px; }
.vcap {
  font-family: var(--atha-font-mono); font-size: 0.6875rem; letter-spacing: 0.1em;
  text-transform: uppercase; color: var(--muted-l); margin-top: 26px; min-height: 1.4em;
}

/* rhythm rail — content is fully visible on expand, bars stand at full height */
.rail { display: flex; flex-direction: column; margin-top: clamp(28px, 4vw, 44px); max-width: 520px; }
.rs { display: flex; align-items: center; gap: 16px; }
.rs .bar { width: 46px; flex: none; background: var(--atha-field); }
.rs.hi .bar { background: var(--atha-ferrous); }
.rs .lb {
  font-family: var(--atha-font-mono); font-size: 0.6875rem; letter-spacing: 0.09em;
  text-transform: uppercase; color: var(--muted);
}
.rs.hi .lb { color: var(--atha-clay); }
.rg { display: flex; align-items: center; gap: 16px; }
.rg .sp { width: 46px; flex: none; }
.rg .tk {
  font-family: var(--atha-font-mono); font-size: 0.5625rem; letter-spacing: 0.11em;
  text-transform: uppercase; color: var(--atha-rule);
}

/* parameters */
.params { border-top: 1px solid var(--atha-hair); margin-top: clamp(28px, 4vw, 42px); }
.prow {
  display: flex; gap: 16px; justify-content: space-between; align-items: baseline;
  padding: 14px 0; border-bottom: 1px solid var(--atha-hair); font-size: 0.9375rem;
}
.prow .s {
  font-family: var(--atha-font-mono); font-size: 0.625rem; letter-spacing: 0.12em;
  text-transform: uppercase; color: var(--atha-ferrous); flex: none;
}

/* layers */
.layer {
  display: grid; gap: 8px clamp(20px, 4vw, 44px); padding: clamp(22px, 3vw, 30px) 0;
  border-bottom: 1px solid var(--atha-hair);
}
@media (min-width: 760px) { .layer { grid-template-columns: 190px minmax(0, 1fr); } }
.layer:first-of-type { border-top: 1px solid var(--atha-hair); }
.layer .who {
  font-family: var(--atha-font-display); font-weight: 400; font-variation-settings: "opsz" 40;
  font-size: 1.1rem;
}
.layer .what { font-size: 0.9375rem; color: var(--muted); max-width: 50ch; }

/* panel footer nav */
.cfoot {
  border-top: 1px solid var(--atha-hair); margin-top: clamp(56px, 8vw, 104px);
  padding: clamp(32px, 4.5vw, 54px) 0 clamp(48px, 7vw, 84px);
}
.cnav {
  display: flex; justify-content: space-between; gap: 18px; flex-wrap: wrap;
  font-family: var(--atha-font-mono); font-size: 0.6875rem; letter-spacing: 0.11em;
  text-transform: uppercase;
}
.cnav button { color: var(--muted); transition: color 0.2s ease; }
.cnav button:hover { color: var(--atha-ferrous); }
.cnav .mid { color: var(--muted); }
.cpaths { margin-top: clamp(34px, 4.5vw, 52px); }
.cfoot-meta { margin-top: clamp(28px, 3.6vw, 42px); }

/* narrow viewports: bottom safe area below the fixed compass widget,
   which otherwise overlaps the card grid and the panel's lower edge */
@media (max-width: 900px) {
  .dirs { padding-bottom: 104px; }
  .panel { inset: 3% 3% 104px; }
}

/* reduced motion: the plaza's toggle and the OS preference both flatten
   the overlay's opacity/transform transitions */
.seven.reduced .overlay,
.seven.reduced .panel,
.seven.reduced .dir { transition: none; }
@media (prefers-reduced-motion: reduce) {
  .overlay, .panel, .dir { transition: none; }
}
</style>
