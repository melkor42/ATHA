<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { usePlaza } from '../../composables/usePlaza.js'

// S? Wisdom Corner — the ATHA decision-quality microsite, lifted 1:1 from
// .scratch/atha-wisdom-corner.html into a plaza zone. Hash routing is replaced
// by local `view` state (the plaza owns the URL/camera); all copy is verbatim
// from the approved prototype — nothing invented, unconfirmed items keep
// their status labels.
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

const scroller = ref(null)
const view = ref(null) // null = hub, else 'c1'..'c7'
const pressed = ref(3) // verdict line: Reject is struck by default
const revealed = ref(new Set())

const activeIndex = computed(() => DIRS.findIndex((d) => d.id === view.value))
const prevDir = computed(() => (activeIndex.value > 0 ? DIRS[activeIndex.value - 1] : null))
const nextDir = computed(() => (activeIndex.value >= 0 && activeIndex.value < DIRS.length - 1 ? DIRS[activeIndex.value + 1] : null))
const hasIO = typeof IntersectionObserver !== 'undefined'
const instant = computed(() => reduced.value || !hasIO)

let obs = null
onMounted(() => {
  // reveal observer, StoryGateZone pattern: rooted at the zone scroller,
  // one-shot unobserve, disconnect on unmount. Created unconditionally so a
  // later motion toggle (reduced → full) can start using it; its USE is
  // gated on `instant` when arming targets.
  if (hasIO) {
    obs = new IntersectionObserver(
      (entries) => {
        for (const en of entries) {
          if (!en.isIntersecting) continue
          const i = Number(en.target.dataset.i)
          if (!revealed.value.has(i)) {
            revealed.value.add(i)
            revealed.value = new Set(revealed.value) // retrigger reactivity
          }
          obs.unobserve(en.target)
        }
      },
      { root: scroller.value, rootMargin: '0px 0px -10% 0px', threshold: 0.05 }
    )
  }
  window.addEventListener('keydown', onKey)
})
onBeforeUnmount(() => {
  window.removeEventListener('keydown', onKey)
  obs?.disconnect()
})

function navigate(id) {
  if (view.value !== id) view.value = id
}
function goHome() {
  view.value = null
}
function onKey(e) {
  // only reset from Escape while the camera is actually on this zone
  if (e.key === 'Escape' && view.value && current.value === 'wisdom') goHome()
}

// route() equivalent: on view change scroll the zone scroller to top,
// focus the article, re-arm the reveals for the fresh DOM
watch(view, () => {
  revealed.value = new Set()
  obs?.disconnect() // drop the old view's targets before re-arming
  nextTick(() => {
    scroller.value?.scrollTo({ top: 0 })
    if (view.value) {
      scroller.value.querySelector('article.comp')?.focus({ preventScroll: true })
      if (!instant.value && obs) scroller.value.querySelectorAll('.rv').forEach((el) => obs.observe(el))
    }
  })
})

// motion toggle while a view is open: instant reveals via the `.instant`
// class (CSS), full motion needs the targets (re-)armed
watch(instant, (v) => {
  obs?.disconnect()
  if (v || !view.value || !obs) return
  nextTick(() => {
    scroller.value?.querySelectorAll('.rv').forEach((el) => obs.observe(el))
  })
})
</script>

<template>
  <section ref="scroller" class="zone zone-wisdom scrollable" :class="{ instant }">
    <!-- ============ MASTHEAD (sticky in-zone) ============ -->
    <header class="mast">
      <div class="wrap mast-in">
        <button type="button" class="home" aria-label="Atha — back to all directions" @click="goHome">
          <span class="glyph" aria-hidden="true">
            <i
              v-for="(d, i) in DIRS"
              :key="d.id"
              :class="{ on: i === activeIndex }"
              :style="{ height: Math.max(2, Math.round(d.h / 16)) + 'px' }"
            ></i>
          </span>
          <span>
            <span class="wm">Atha</span>
            <span class="sub">Initiated by OneMundi</span>
          </span>
        </button>
        <button v-if="view" type="button" class="back" @click="goHome">All directions ↖</button>
      </div>
    </header>

    <!-- ============ SIDE INDEX (desktop only) ============ -->
    <nav class="side" :class="{ show: !!view }" aria-label="Directions">
      <button
        v-for="(d, i) in DIRS"
        :key="d.id"
        type="button"
        :class="{ on: i === activeIndex }"
        :aria-label="`${d.n} ${d.name}`"
        @click="navigate(d.id)"
      >
        <i :style="{ height: Math.max(3, Math.round(d.h / 11)) + 'px' }"></i>
        <span>{{ d.name }}</span>
      </button>
    </nav>

    <main>
      <!-- ================= HUB ================= -->
      <section v-if="!view" class="hub wrap">
        <div class="hub-head">
          <h1 class="dsp">The quality of a decision depends on the conditions in which it was made.</h1>
          <div class="say">Seven directions · choose one</div>
        </div>

        <div class="strata">
          <button
            v-for="d in DIRS"
            :key="d.id"
            type="button"
            class="stratum"
            @click="navigate(d.id)"
          >
            <span class="row" :style="{ height: d.h + 'px' }">
              <span class="no">{{ d.n }}</span>
              <span class="nm">{{ d.name }}</span>
              <span class="ds">{{ d.d }}</span>
              <span class="ar">→</span>
            </span>
          </button>
        </div>

        <div class="hub-foot">
          <div class="paths paths--quiet">
            <button type="button" class="btn btn--q" @click="goTo('east')">Bring a challenge</button>
            <button type="button" class="btn btn--q" @click="goTo('east')">Take part</button>
          </div>
          <div class="meta hub-meta">
            Edition 001 · Forming · No partners, dates or funding confirmed<br />
            Co-hosted with Warwick Business School
          </div>
        </div>
      </section>

      <!-- ================= 01 THE QUESTION ================= -->
      <article v-if="view === 'c1'" class="comp" tabindex="-1">
        <div class="wrap comp-in">
          <div class="eyebrow">01 · The Question</div>
          <h2 class="dsp">Not what can be built. What should be.</h2>
          <p class="lede">Most organisations can tell an AI opportunity from an AI expense only after they have spent the money.</p>
        </div>

        <div class="band band--slip">
          <div class="wrap">
            <div class="blocks blocks--2">
              <div class="rv" :class="{ in: revealed.has(0) }" data-i="0">
                <h3 class="blk-h">The inversion</h3>
                <p class="blk-p">Teams do not ask whether something can be built. Almost everything can. They determine whether it should be pursued, under what conditions, and with what consequences — for the business, for the people in it, and for everyone downstream of the decision.</p>
              </div>
              <div class="rv" :class="{ in: revealed.has(1) }" data-i="1">
                <h3 class="blk-h">A reject is a result</h3>
                <p class="blk-p">A well-supported decision not to build can be worth more than an impressive prototype. It is the outcome no consultancy is paid to reach and no hackathon is structured to produce.</p>
              </div>
            </div>
          </div>
        </div>

        <div class="wrap pad-top-lg">
          <div class="blocks">
            <div class="rv" :class="{ in: revealed.has(2) }" data-i="2">
              <h3 class="blk-h">What an organisation actually needs to know</h3>
              <p class="blk-p">Which AI opportunities are genuinely valuable. Which ideas should not be implemented at all. How the work changes people, culture and leadership. Whether it is commercially and operationally viable. What ethical, social and environmental consequences follow. And how humans and AI can work together without anyone quietly losing responsibility for the outcome.</p>
            </div>
            <div class="rv" :class="{ in: revealed.has(3) }" data-i="3">
              <h3 class="blk-h">Why it needs conditions</h3>
              <p class="blk-p">Discernment is not a faster kind of thinking. It needs enough time, enough disagreement, enough evidence and enough rest to be worth trusting. Those are conditions, and conditions can be designed.</p>
            </div>
          </div>
        </div>
      </article>

      <!-- ================= 02 THE METHOD ================= -->
      <article v-if="view === 'c2'" class="comp" tabindex="-1">
        <div class="wrap comp-in">
          <div class="eyebrow">02 · The Method</div>
          <h2 class="dsp">Three teams. One question. No shared reasoning.</h2>
          <p class="lede">Three independent multidisciplinary teams investigate the same challenge separately, without knowledge of one another's work — then converge in a facilitated process.</p>
        </div>

        <div class="wrap pad-top-md">
          <div class="teams rv" :class="{ in: revealed.has(0) }" data-i="0">
            <div class="team"><div class="k">Team 01</div><p>Investigates independently. Its own evidence, its own assumptions, its own verdict.</p></div>
            <div class="team"><div class="k">Team 02</div><p>Same question. No contact. Arrives somewhere the first team did not.</p></div>
            <div class="team"><div class="k">Team 03</div><p>Same again. Three findings, and the disagreements between them preserved rather than reconciled.</p></div>
          </div>
          <p class="lede lede-mid">Where the three disagree is often the most useful part of what a partner receives.</p>
        </div>

        <div class="band">
          <div class="wrap">
            <div class="rv" :class="{ in: revealed.has(1) }" data-i="1">
              <h3 class="blk-h">Five lenses</h3>
              <p class="blk-p">An AI opportunity is an organisational and human system, not a technical product. Each team examines the same five dimensions, and a weakness in any one of them is a finding in itself.</p>
            </div>
            <div class="lenses rv" :class="{ in: revealed.has(2) }" data-i="2">
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
            <div class="rv" :class="{ in: revealed.has(3) }" data-i="3">
              <h3 class="blk-h">AI-native means process redesign</h3>
              <p class="blk-p">Not tool use. AI organises context, tests assumptions, surfaces blind spots and preserves reasoning so that nothing is lost between the room and the board. Every finding carries a transparent record of how AI contributed to it.</p>
            </div>
            <div class="rv" :class="{ in: revealed.has(4) }" data-i="4">
              <h3 class="blk-h">Humans keep the decision</h3>
              <p class="blk-p">Context, meaning, ethics, verification and the final judgement stay with people. The record exists so that a board can see exactly where the machine helped and exactly where a person decided.</p>
            </div>
          </div>
          <hr />
          <div class="rv" :class="{ in: revealed.has(5) }" data-i="5">
            <h3 class="blk-h">No overall winner</h3>
            <p class="blk-p">There is no ranking and no prize for first place. Recognition celebrates different forms of excellence, which is a structural decision rather than a courtesy — a single winner would reintroduce the competition the format exists to remove.</p>
          </div>
        </div>
      </article>

      <!-- ================= 03 THE FINDING ================= -->
      <article v-if="view === 'c3'" class="comp" tabindex="-1">
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
            <div class="rv" :class="{ in: revealed.has(0) }" data-i="0">
              <h3 class="blk-h">What is in it</h3>
              <p class="blk-p">The proposed opportunity. Supporting evidence. The assumptions that were challenged, and what happened to them. Organisational and commercial implications. Human, ethical and environmental consequences. Risks and the conditions under which the thing would actually succeed. An implementation pathway, recommended next actions, and the record of how AI contributed.</p>
            </div>
            <div class="rv" :class="{ in: revealed.has(1) }" data-i="1">
              <h3 class="blk-h">Prototypes are evidence</h3>
              <p class="blk-p">Something may get built during the work. If it does, it exists to test an assumption — never as the point, and never as the deliverable.</p>
            </div>
            <div class="rv" :class="{ in: revealed.has(2) }" data-i="2">
              <h3 class="blk-h">We are not paid to recommend action</h3>
              <p class="blk-p">A vendor has an interest in the answer. A consultancy is usually engaged on the assumption that something will proceed. Here the verdict can be no, and the commercial model does not punish that.</p>
            </div>
            <div class="rv" :class="{ in: revealed.has(3) }" data-i="3">
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
      <article v-if="view === 'c4'" class="comp" tabindex="-1">
        <div class="wrap comp-in">
          <div class="eyebrow">04 · The Conditions</div>
          <h2 class="dsp">Human energy is an input into the quality of the work.</h2>
          <p class="lede">Not a benefit placed around the work. An input to it — and therefore designed with the same seriousness as the analysis.</p>
        </div>

        <div class="wrap pad-top-md2">
          <div class="blocks blocks--2">
            <div class="rv" :class="{ in: revealed.has(0) }" data-i="0">
              <h3 class="blk-h">Rest is scheduled as work is scheduled</h3>
              <p class="blk-p">Sleep, meals, movement, time outside and reflection sit on the same measure as the working blocks, at the same scale, with the same status. That single scheduling decision states the whole position, and it is the reason nobody has to be told about it.</p>
            </div>
            <div class="rv" :class="{ in: revealed.has(1) }" data-i="1">
              <h3 class="blk-h">The room is made, not booked</h3>
              <p class="blk-p">Warm layered light rather than overhead fluorescent. Real plates. Paper, wood, wool and ceramic. No banners, no branded gilets, nothing that would be thrown away on the Monday. If it cannot be kept, it is not produced.</p>
            </div>
            <div class="rv" :class="{ in: revealed.has(2) }" data-i="2">
              <h3 class="blk-h">Ambition without exhaustion</h3>
              <p class="blk-p">Rigour, commercial consequence and genuine ambition do not require depletion, fragmentation or unhealthy competition. That claim is the thing being tested here, alongside the enterprise questions.</p>
            </div>
            <div class="rv" :class="{ in: revealed.has(3) }" data-i="3">
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
      <article v-if="view === 'c5'" class="comp" tabindex="-1">
        <div class="wrap comp-in">
          <div class="eyebrow">05 · The Rhythm</div>
          <h2 class="dsp">Seven stages. The gaps are designed too.</h2>
          <p class="lede">ATHA is not an agenda. It follows a human and intellectual arc, and the length of each stage is a decision rather than a leftover.</p>
          <div class="rail rv" :class="{ in: revealed.has(0) }" data-i="0">
            <template v-for="(s, i) in STAGES" :key="s.label">
              <div v-if="i > 0" class="rg" :style="{ height: (i === 3 ? 26 : 12) + 'px' }" aria-hidden="true">
                <span class="sp"></span><span class="tk">{{ s.gap }}</span>
              </div>
              <div class="rs" :class="{ hi: i === 4 }">
                <span class="bar" :style="{ height: s.units * 11 + 'px', animationDelay: i * 90 + 'ms' }"></span>
                <span class="lb">{{ s.label }}</span>
              </div>
            </template>
          </div>
          <p class="lede lede-rail">DISCERN is given more room than any stage except the work itself. A conventional programme of the same length would be a single unbroken block.</p>
        </div>

        <div class="band band--slip">
          <div class="wrap">
            <div class="blocks blocks--2">
              <div class="rv" :class="{ in: revealed.has(1) }" data-i="1">
                <h3 class="blk-h">Arrive, open, connect</h3>
                <p class="blk-p">People are met rather than processed. The question is opened before it is attacked — partners present the problem as it actually sits with them, including what they have already tried and what they are afraid the answer might be. Teams then form across disciplines.</p>
              </div>
              <div class="rv" :class="{ in: revealed.has(2) }" data-i="2">
                <h3 class="blk-h">Create, discern, celebrate, return</h3>
                <p class="blk-p">The longest stage is the investigation, and the second longest is deciding what it means. Recognition is shared rather than ranked. People leave with something integrated, and the relationships carry into the next edition.</p>
              </div>
            </div>
          </div>
        </div>
      </article>

      <!-- ================= 06 EDITION 001 ================= -->
      <article v-if="view === 'c6'" class="comp" tabindex="-1">
        <div class="wrap comp-in">
          <div class="eyebrow">06 · Edition 001</div>
          <h2 class="dsp">Forming.</h2>
          <p class="lede">Nothing below is confirmed. No challenge partner, sponsor or funding is agreed, and the dates are not fixed. It is set out here as it actually stands, because the alternative is to imply otherwise.</p>
        </div>

        <div class="wrap pad-top-sm">
          <div class="params rv" :class="{ in: revealed.has(0) }" data-i="0">
            <div v-for="p in PARAMS" :key="p.what" class="prow">
              <span>{{ p.what }}</span><span class="s">{{ p.status }}</span>
            </div>
          </div>
        </div>

        <div class="band">
          <div class="wrap">
            <div class="blocks blocks--2">
              <div class="rv" :class="{ in: revealed.has(1) }" data-i="1">
                <h3 class="blk-h">Who takes part</h3>
                <p class="blk-p">Students and emerging leaders, founders, researchers, creatives, and other carefully selected contributors from the Warwick ecosystem and partner networks. Places are limited and selected. Executives and investors take part as challenge partners, mentors and expert contributors rather than as participants.</p>
              </div>
              <div class="rv" :class="{ in: revealed.has(2) }" data-i="2">
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
      <article v-if="view === 'c7'" class="comp" tabindex="-1">
        <div class="wrap comp-in">
          <div class="eyebrow">07 · The Layers</div>
          <h2 class="dsp">ATHA exists only where three systems meet.</h2>
          <p class="lede">None of the three is an addition to the others. Remove any one and what remains is something ATHA is specifically not.</p>
        </div>

        <div class="wrap pad-top-sm">
          <div
            v-for="(l, i) in LAYERS"
            :key="l.who"
            class="layer rv"
            :class="{ in: revealed.has(i) }"
            :data-i="i"
          >
            <div class="who">{{ l.who }}</div>
            <div class="what">{{ l.what }}</div>
          </div>
        </div>

        <div class="wrap pad-top-xl">
          <div class="rv" :class="{ in: revealed.has(3) }" data-i="3">
            <h3 class="blk-h">A series, not an event</h3>
            <p class="blk-p">ATHA is built to recur. Every relationship formed in an edition is intended to persist into the next one, and the archive of findings compounds rather than resets. Edition 001 is the first, not the whole thing.</p>
          </div>
        </div>
      </article>

      <!-- ============ PER-VIEW FOOTER NAV (injected by prototype JS) ============ -->
      <footer v-if="view" class="cfoot">
        <div class="wrap">
          <div class="cnav">
            <button v-if="prevDir" type="button" @click="navigate(prevDir.id)">← {{ prevDir.name }}</button>
            <span v-else class="mid"></span>
            <button type="button" @click="goHome">All directions</button>
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
    </main>
  </section>
</template>

<style scoped>
/* zone shell — flat chalk, no plaza background image */
.zone-wisdom {
  --gut: clamp(20px, 5.5vw, 72px);
  --max: 1180px;
  /* tone derivatives the prototype kept as literal rgba */
  --muted: rgba(42, 38, 34, 0.56);
  --muted-l: rgba(242, 237, 228, 0.62);
  --hair-l: rgba(242, 237, 228, 0.22);
  overflow-y: auto;
  scrollbar-width: thin;
  scrollbar-color: rgba(42, 38, 34, 0.35) transparent;
  background: var(--atha-chalk);
  color: var(--atha-clay);
  font-family: var(--atha-font-body);
  font-size: 1rem;
  line-height: 1.62;
  -webkit-font-smoothing: antialiased;
}
.zone-wisdom ::selection { background: var(--atha-rind); color: var(--atha-clay); }
.zone-wisdom button { font: inherit; color: inherit; background: none; border: 0; padding: 0; cursor: pointer; }
.zone-wisdom :focus-visible { outline: 2px solid var(--atha-ferrous); outline-offset: 4px; }

.wrap { max-width: var(--max); margin: 0 auto; padding: 0 var(--gut); }
.meta {
  font-family: var(--atha-font-mono); font-size: var(--atha-s0); letter-spacing: 0.1em;
  text-transform: uppercase; color: var(--muted); line-height: 1.7;
}
.dsp {
  font-family: var(--atha-font-display); font-weight: 300;
  font-variation-settings: "opsz" 144; letter-spacing: -0.018em; line-height: 1.1; margin: 0;
}
.zone-wisdom p { margin: 0 0 1.05em; max-width: 60ch; }
.zone-wisdom p:last-child { margin-bottom: 0; }
.zone-wisdom hr { border: 0; border-top: 1px solid var(--atha-hair); margin: clamp(30px, 4.5vw, 54px) 0; }

/* pad helpers replacing prototype inline styles */
.pad-top-sm { padding-top: clamp(36px, 5vw, 58px); }
.pad-top-md { padding-top: clamp(40px, 5vw, 64px); }
.pad-top-md2 { padding-top: clamp(40px, 5.5vw, 72px); }
.pad-top-lg { padding-top: clamp(48px, 7vw, 92px); }
.pad-top-xl { padding-top: clamp(44px, 6vw, 76px); }

/* ============ MASTHEAD ============ */
.mast {
  position: sticky; top: 0; z-index: 80; background: var(--atha-chalk);
  border-bottom: 1px solid var(--atha-hair);
}
.mast-in { display: flex; align-items: center; justify-content: space-between; gap: 18px; height: 62px; }
.home { display: flex; align-items: center; gap: 14px; text-align: left; }
.home .wm {
  font-family: var(--atha-font-display); font-variation-settings: "opsz" 90; font-weight: 300;
  font-size: 0.95rem; letter-spacing: 0.32em; text-indent: 0.32em; text-transform: uppercase;
  display: block;
}
.home .sub {
  font-family: var(--atha-font-mono); font-size: 0.625rem; letter-spacing: 0.12em;
  text-transform: uppercase; color: var(--muted); display: none;
}
@media (min-width: 640px) { .home .sub { display: block; } }
.mast .back {
  font-family: var(--atha-font-mono); font-size: 0.6875rem; letter-spacing: 0.11em;
  text-transform: uppercase; color: var(--muted); transition: color 0.2s ease;
}
.mast .back:hover { color: var(--atha-ferrous); }

/* index glyph in masthead */
.glyph { display: flex; flex-direction: column; gap: 2px; width: 15px; flex: none; }
.glyph i {
  display: block; background: var(--atha-clay); opacity: 0.3;
  transition: opacity 0.3s var(--atha-ease), background 0.3s var(--atha-ease);
}
.glyph i.on { opacity: 1; background: var(--atha-ferrous); }

/* ============ HUB ============ */
.hub {
  min-height: calc(100% - 62px); display: flex; flex-direction: column;
  padding-top: clamp(48px, 9vw, 104px); padding-bottom: clamp(28px, 4vw, 44px);
}
.hub-head { margin-bottom: clamp(40px, 6vw, 72px); }
.hub-head h1 { font-size: clamp(1.6rem, 3.6vw, 2.9rem); max-width: 20ch; font-weight: 300; }
.hub-head .say {
  font-family: var(--atha-font-mono); font-size: 0.6875rem; letter-spacing: 0.14em;
  text-transform: uppercase; color: var(--muted); margin-top: clamp(24px, 3.4vw, 38px);
}

/* strata navigation — hover shift via transform, never padding (no layout thrash) */
.strata { border-top: 1px solid var(--atha-hair); }
.stratum {
  display: block; width: 100%; text-align: left; position: relative;
  border-bottom: 1px solid var(--atha-hair);
  transition: background 0.34s var(--atha-ease), color 0.34s var(--atha-ease);
}
.stratum .row {
  display: flex; align-items: center; gap: clamp(14px, 3vw, 34px);
  padding: 0 clamp(12px, 2vw, 20px);
  transition: transform 0.34s var(--atha-ease);
}
.stratum .no {
  font-family: var(--atha-font-mono); font-size: 0.6875rem; letter-spacing: 0.12em;
  color: var(--atha-rule); flex: none; width: 22px; transition: color 0.34s var(--atha-ease);
}
.stratum .nm {
  font-family: var(--atha-font-display); font-weight: 300; font-variation-settings: "opsz" 90;
  font-size: clamp(1.15rem, 2.5vw, 1.7rem); letter-spacing: -0.008em; flex: none;
}
.stratum .ds {
  font-size: 0.8125rem; color: var(--muted); margin-left: auto; text-align: right;
  max-width: 34ch; line-height: 1.4; transition: color 0.34s var(--atha-ease); display: none;
}
@media (min-width: 820px) { .stratum .ds { display: block; } }
.stratum .ar {
  font-family: var(--atha-font-mono); font-size: 0.8125rem; opacity: 0; flex: none;
  transition: opacity 0.34s var(--atha-ease); margin-left: auto;
}
@media (min-width: 820px) { .stratum .ar { margin-left: 22px; } }
.stratum:hover, .stratum:focus-visible { background: var(--atha-field); color: var(--atha-chalk); }
.stratum:hover .row, .stratum:focus-visible .row { transform: translateX(clamp(6px, 1.4vw, 16px)); }
.stratum:hover .no, .stratum:focus-visible .no { color: var(--atha-rind); }
.stratum:hover .ds, .stratum:focus-visible .ds { color: var(--muted-l); }
.stratum:hover .ar, .stratum:focus-visible .ar { opacity: 1; }
.stratum:focus-visible { outline-offset: -3px; outline-color: var(--atha-rind); }

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
/* the hub's own job is the seven directions; the east-gate CTAs sit below
   as quiet mono links rather than competing solid buttons */
.paths--quiet { gap: clamp(18px, 3vw, 30px); margin-top: clamp(28px, 4vw, 44px); }
.btn--q {
  background: none; color: var(--muted); padding: 2px 0;
  border-bottom: 1px solid transparent;
}
.btn--q:hover { background: none; color: var(--atha-ferrous); border-color: var(--atha-ferrous); }
.btn--inv { background: var(--atha-chalk); color: var(--atha-clay); }
.btn--inv:hover { background: var(--atha-rind); }
.hub-foot { margin-top: auto; padding-top: clamp(36px, 5vw, 56px); }
.hub-meta { margin-top: clamp(30px, 4vw, 46px); }

/* ============ DIRECTION VIEWS ============ */
.comp { padding-bottom: 0; }
.comp:focus { outline: none; }
.comp-in { padding-top: clamp(48px, 8vw, 96px); }
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

/* rhythm rail */
.rail { display: flex; flex-direction: column; margin-top: clamp(28px, 4vw, 44px); max-width: 520px; }
.rs { display: flex; align-items: center; gap: 16px; }
.rs .bar {
  width: 46px; flex: none; background: var(--atha-field);
  transform: scaleY(0); transform-origin: top;
}
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
/* bars grow once their reveal lands (opacity/transform only) */
.rv.in .rs .bar { animation: rail-grow 0.76s var(--atha-ease) forwards; }
@keyframes rail-grow { to { transform: scaleY(1); } }

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

/* footer nav */
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

/* side index (desktop) — sticky inside the zone scroller: `position: fixed`
   would resolve against the transformed .plaza-world (300vw×300vh) and land
   off-screen. height:0 keeps it out of flow; top:50% pins it mid-viewport. */
.side {
  position: sticky; top: 50%; height: 0; overflow: visible; width: max-content;
  margin-left: auto; margin-right: clamp(14px, 2.2vw, 30px);
  z-index: 70; display: none; flex-direction: column; gap: 5px;
}
@media (min-width: 1100px) { .side.show { display: flex; } }
.side button { position: relative; display: block; width: 16px; padding: 2px 0; }
.side button i {
  display: block; background: var(--atha-clay); opacity: 0.26; width: 16px;
  /* grow via transform, not width — same visual result, compositor-friendly.
     Origin left center mirrors the old width animation: the bar grows
     rightward from its left-anchored edge. */
  transform: scaleX(1); transform-origin: left center;
  transition: opacity 0.3s var(--atha-ease), background 0.3s var(--atha-ease), transform 0.3s var(--atha-ease);
}
.side button:hover i { opacity: 0.7; }
.side button.on i { opacity: 1; background: var(--atha-ferrous); transform: scaleX(1.375); }
.side button span {
  position: absolute; right: 28px; top: 50%; transform: translateY(-50%);
  white-space: nowrap; font-family: var(--atha-font-mono); font-size: 0.625rem;
  letter-spacing: 0.1em; text-transform: uppercase; color: var(--muted);
  opacity: 0; pointer-events: none; transition: opacity 0.25s ease;
}
.side button:hover span, .side button:focus-visible span { opacity: 1; }

/* narrow viewports: bottom safe area below the fixed compass widget,
   which otherwise overlaps the last rows of hub and direction views */
@media (max-width: 900px) {
  .hub { padding-bottom: 104px; }
  .cfoot { padding-bottom: 104px; }
}

/* reveal (opacity/transform only) */
.rv {
  opacity: 0; transform: translateY(12px);
  transition: opacity 0.7s var(--atha-ease), transform 0.7s var(--atha-ease);
}
.rv.in { opacity: 1; transform: none; }
.zone-wisdom.instant .rv { opacity: 1; transform: none; }
.zone-wisdom.instant .rs .bar { transform: scaleY(1); }

@media (prefers-reduced-motion: reduce) {
  .zone-wisdom *, .zone-wisdom *::before, .zone-wisdom *::after {
    animation-duration: 0.001ms !important; transition-duration: 0.001ms !important;
  }
  .rv { opacity: 1; transform: none; }
  .rs .bar { transform: scaleY(1); }
}
</style>
