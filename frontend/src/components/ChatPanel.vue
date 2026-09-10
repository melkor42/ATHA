<script setup>
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import { useCompose, GREETING } from '../composables/useCompose.js'
import { useTypewriter } from '../composables/useTypewriter.js'
import { useArrival } from '../composables/useArrival.js'
import { ROLES } from '../interview.js'
import Theater from './Theater.vue'

const {
  phase, status, busy, messages, chips, roleGate, greetingLive, settleGreeting,
  contextualCta, summaryCtaVisible, currentCta, emailDraft, leadBusy,
  pick, submitTyped, submitLead, composingLine, turns
} = useCompose()

const { arrived } = useArrival()

const draft = ref('')
const log = ref(null)
const STEPS = ['Retrieving', 'Ranking', 'Composing']

// The summary CTA opens an inline email field in the footer; when the CTA
// withdraws (a send went through, or the conversation restarted) the field
// closes with it rather than lingering open.
const summaryOpen = ref(false)
watch(summaryCtaVisible, (visible) => { if (!visible) summaryOpen.value = false })

// The agent opens the conversation, and the visitor watches it do so. Only a
// fresh session types; a reload reads a conversation that was already spoken.
const { typed, done, thinking, run: typeGreeting, skip, reset } = useTypewriter()
const speaking = computed(() => greetingLive.value && !done.value)

const placeholder = computed(() => {
  if (roleGate.value) return 'The input opens once you have chosen…'
  return phase.value === 'landing' ? 'Ask about the experience…' : 'Ask a follow-up…'
})

function speakGreeting() {
  if (!arrived.value || !greetingLive.value) return
  reset()
  typeGreeting(GREETING, { speed: 18, pause: 700 })
  if (done.value) settleGreeting() // reduced motion: nothing was typed
}

onMounted(() => { if (arrived.value) speakGreeting() })
watch(greetingLive, speakGreeting)
watch(arrived, (isArrived) => { if (isArrived) speakGreeting() })
watch(done, (finished) => { if (finished) settleGreeting() })

function letTheVisitorThrough() {
  if (!speaking.value) return
  skip(GREETING)
  settleGreeting()
}

watch(
  () => [messages.value.length, status.value],
  async () => {
    await nextTick()
    const el = log.value
    if (el) el.scrollTop = el.scrollHeight
  }
)

async function submit() {
  const text = draft.value.trim()
  if (!text || busy.value || roleGate.value) return
  draft.value = ''
  await submitTyped(text)
}
</script>

<template>
  <aside
    class="chat"
    :class="phase"
    @click="letTheVisitorThrough"
    @focusin="letTheVisitorThrough"
  >
    <p v-if="turns" class="label chat-head">
      <span>Atha agent</span>
      <span class="turns">{{ turns }} {{ turns === 1 ? 'answer' : 'answers' }}</span>
    </p>

    <div ref="log" class="log" :class="{ 'u-fade': arrived }" style="--d: 0ms" aria-live="polite">
      <article v-for="(m, i) in messages" :key="i" class="msg" :class="[m.from, { error: m.error }]">
        <p v-if="m.from === 'you'" class="you-line">{{ m.text }}</p>
        <template v-else>
          <h4 v-if="m.title" class="answer-title">{{ m.title }}</h4>
          <p v-if="i === 0 && greetingLive && thinking" class="typing-label" aria-hidden="true">
            <span class="typing-label-text">Atha is typing</span><span class="caret"></span>
          </p>
          <p v-else-if="i === 0 && greetingLive" class="answer-text typing" aria-hidden="true">
            <span class="typing-text">{{ typed }}</span><span v-if="!done" class="caret"></span>
          </p>
          <div v-else-if="m.kind === 'role-ask' && roleGate" class="role-card u-fade">
            <p class="role-card__q">{{ m.text }}</p>
            <p class="role-card__why">{{ m.why }}</p>
            <div class="role-card__options">
              <button
                v-for="r in ROLES"
                :key="r.role"
                type="button"
                class="role-option"
                @click="pick(r)"
              >
                <span class="role-option__title">{{ r.title }}</span>
                <span class="role-option__text">{{ r.text }}</span>
              </button>
            </div>
          </div>
          <p v-else class="answer-text u-fade">{{ m.text }}</p>
        </template>
      </article>

      <div v-if="busy" class="composing">
        <Theater :steps="STEPS" :cadence="420" :active="true" />
        <p class="composing-line">{{ composingLine }}</p>
      </div>
    </div>

    <form class="composer" :class="{ 'u-fade': arrived }" style="--d: 220ms" @submit.prevent="submit">
      <div class="composer__shell" :class="{ muted: roleGate }">
        <input
          v-model="draft"
          type="text"
          :placeholder="placeholder"
          aria-label="Ask the ATHA agent"
          :disabled="busy || roleGate"
          autocomplete="off"
        />
        <div class="composer__bar">
          <span class="label composer__status">Atha agent</span>
          <button type="submit" :disabled="busy || roleGate || !draft.trim()" aria-label="Ask">↑</button>
        </div>
      </div>
    </form>

    <div v-if="chips.length && !busy && !speaking" class="chips" :class="{ 'u-fade': arrived }" style="--d: 440ms">
      <button
        v-for="(c, i) in chips"
        :key="i"
        type="button"
        class="chip"
        @click="pick(c)"
      >{{ c.label }}</button>
    </div>

    <footer class="cta" :class="{ 'u-fade': arrived }" style="--d: 660ms">
      <a class="apply" :href="currentCta.href">{{ currentCta.label }}</a>

      <button
        v-if="summaryCtaVisible && !summaryOpen"
        type="button"
        class="summary-cta"
        @click="summaryOpen = true"
      >Summary per email</button>

      <form
        v-if="summaryCtaVisible && summaryOpen"
        class="lead-form"
        @submit.prevent="submitLead(emailDraft)"
      >
        <input
          v-model="emailDraft"
          type="email"
          required
          placeholder="you@example.com"
          aria-label="Email address"
          autocomplete="email"
          :disabled="leadBusy"
        />
        <button type="submit" :disabled="leadBusy || !emailDraft.trim()">Send me the summary</button>
      </form>

      <a
        v-if="contextualCta"
        class="contextual"
        :href="contextualCta.href"
        :target="contextualCta.external ? '_blank' : null"
        :rel="contextualCta.external ? 'noopener' : null"
      >{{ contextualCta.label }}<span v-if="contextualCta.external" class="external-mark">↗</span></a>
    </footer>
  </aside>
</template>

<style scoped>
/* One frame in both phases: none. The conversation sits directly on the page,
   so nothing has to disappear when the first answer arrives — the morph is
   purely where the column lives, not what it is wrapped in. */
.chat {
  display: flex;
  flex-direction: column;
  gap: 22px;
  min-height: 0;
}
.chat-head {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 12px;
}
.log {
  display: flex;
  flex-direction: column;
  gap: 18px;
  overflow-y: auto;
  min-height: 0;
  scrollbar-width: thin;
  scrollbar-color: var(--rule) transparent;
}
.msg { display: flex; flex-direction: column; gap: 6px; }
.you-line {
  font-size: 16px;
  opacity: 0.7;
  padding-left: 14px;
  border-left: 1px solid var(--rule);
}
.answer-title {
  margin: 0;
  font-family: var(--f-display);
  font-variation-settings: "opsz" 144;
  font-weight: 400;
  font-size: clamp(22px, 2.4vw, 26px);
  letter-spacing: -0.022em;
  line-height: 1.18;
}
.answer-text { font-size: 17px; line-height: 1.5; opacity: 0.8; }
/* ferrous means "alive" — the caret and the focused frame, never two at once.
   A failure line speaks in slate: the copy carries the meaning, not a colour. */
.msg.error .answer-text { color: var(--slate); opacity: 1; }

/* The one loud object in the conversation: while the seat is unnamed nothing
   else on the page is live, so the card carries the whole ask. */
.role-card {
  display: flex;
  flex-direction: column;
  gap: 14px;
  padding: 20px;
  border: 1px solid var(--rule);
  border-radius: var(--r-shell);
  background: var(--surface);
  box-shadow: 0 24px 60px -34px color-mix(in srgb, var(--signal) 50%, transparent);
}
.role-card__q {
  font-family: var(--f-display);
  font-variation-settings: "opsz" 72;
  font-weight: 300;
  font-size: clamp(19px, 2vw, 23px);
  line-height: 1.24;
  letter-spacing: -0.016em;
  text-wrap: pretty;
}
.role-card__why {
  max-width: 54ch;
  font-size: 14.5px;
  line-height: 1.45;
  opacity: 0.72;
}
/* Three seats side by side: stacked, the card alone outgrows the fold and pushes
   the composer off the first screen. */
.role-card__options {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 8px;
}
@media (max-width: 700px) {
  .role-card__options { grid-template-columns: minmax(0, 1fr); }
}
.role-option {
  display: flex;
  flex-direction: column;
  gap: 3px;
  text-align: left;
  padding: 12px 16px;
  border: 1px solid var(--rule);
  border-radius: var(--r-field);
  background: var(--ground);
  transition: border-color 240ms var(--ease), transform 240ms var(--ease);
}
.role-option:hover { border-color: var(--ink); transform: translateY(-1px); }
.role-option__title { font-size: 15.5px; font-weight: 600; }
.role-option__text { font-size: 13.5px; line-height: 1.4; opacity: 0.7; }

.typing-label {
  margin: 0;
  display: flex;
  align-items: center;
  gap: 7px;
}
.typing-label-text {
  font-family: var(--f-mono);
  text-transform: uppercase;
  letter-spacing: 0.13em;
  font-size: 11px;
  color: var(--ink);
  opacity: 0.7;
}
/* the paragraph itself stays opaque — only the words recede, never the caret */
.typing { opacity: 1; }
.typing-text { opacity: 0.8; }
.caret {
  flex: none;
  display: inline-block;
  width: 1px;
  height: 1.05em;
  background: var(--ferrous);
  animation: caret-blink 1s steps(1, end) infinite;
}
@keyframes caret-blink { 50% { opacity: 0 } }

.composing { display: flex; flex-direction: column; gap: 10px; }
.composing-line {
  font-family: var(--f-mono);
  text-transform: uppercase;
  letter-spacing: 0.13em;
  font-size: 10px;
  color: var(--ink);
  opacity: 0.7;
}

.composer__shell {
  display: flex;
  flex-direction: column;
  gap: 6px;
  border-radius: var(--r-shell);
  background: var(--surface);
  border: 1px solid var(--rule);
  padding: 12px 12px 10px 18px;
  box-shadow: 0 24px 60px -28px color-mix(in srgb, var(--signal) 55%, transparent);
  transition: box-shadow 240ms var(--ease), border-color 240ms var(--ease), opacity 240ms var(--ease);
}
/* the ferrous frame and the ferrous caret never share the surface */
.composer__shell:focus-within {
  box-shadow:
    0 24px 60px -28px color-mix(in srgb, var(--signal) 55%, transparent),
    0 0 0 1px var(--signal);
}
/* before a seat is named the composer waits: it stays on the page so the shape
   of the conversation is visible, but it does not glow and does not listen. The
   hint keeps its own opacity — it is the only line saying what to do first. */
.composer__shell.muted { opacity: 0.55; box-shadow: none; }
.composer__shell.muted input:disabled { opacity: 0.85; }
.composer__shell input {
  width: 100%;
  min-width: 0;
  border: none;
  background: none;
  padding: 6px 2px;
  font-size: 17.5px;
  color: var(--ink);
  caret-color: var(--ferrous);
}
.composer__shell input::placeholder { color: var(--ink); opacity: 0.62; }
.composer__shell input:disabled { opacity: 0.45; }
.composer__bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}
.composer__status { color: var(--ink); opacity: 0.62; }
.composer__bar button {
  flex: none;
  width: 38px;
  height: 38px;
  border-radius: 50%;
  background: var(--navy);
  color: var(--ground);
  font-size: 17px;
  line-height: 1;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  transition: background 240ms var(--ease), opacity 240ms var(--ease);
}
.composer__bar button:hover:not(:disabled) {
  background: color-mix(in srgb, var(--navy) 82%, var(--ground));
}
.composer__bar button:disabled { opacity: 0.32; cursor: default; }

.lead-form {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
  margin-top: 8px;
}
.lead-form input {
  flex: 1 1 180px;
  min-width: 0;
  border: 1px solid var(--rule);
  border-radius: var(--r-field);
  background: var(--surface);
  padding: 10px 14px;
  font-size: 14.5px;
  caret-color: var(--ferrous);
}
.lead-form input::placeholder { color: var(--ink); opacity: 0.62; }
.lead-form button {
  font-size: 13.5px;
  font-weight: 600;
  padding: 10px 18px;
  border-radius: var(--r-pill);
  background: var(--navy);
  color: var(--ground);
  transition: background 240ms var(--ease), opacity 240ms var(--ease);
}
.lead-form button:hover:not(:disabled) {
  background: color-mix(in srgb, var(--navy) 82%, var(--ground));
}
.lead-form button:disabled { opacity: 0.45; cursor: default; }

.chips { display: flex; flex-wrap: wrap; align-items: flex-start; gap: 8px; }
.chip {
  font-size: 13.5px;
  line-height: 1.3;
  text-align: left;
  padding: 7px 15px;
  border: 1px solid var(--rule);
  border-radius: var(--r-pill);
  background: var(--ground);
  color: var(--ink);
  opacity: 0.78;
  transition: border-color 240ms var(--ease), opacity 240ms var(--ease), transform 240ms var(--ease);
}
.chip:hover { opacity: 1; border-color: var(--ink); }

.cta { display: flex; flex-direction: column; gap: 12px; padding-top: 4px; }
.apply {
  display: block;
  text-align: center;
  background: none;
  border: 1px solid var(--ink);
  border-radius: var(--r-pill);
  color: var(--ink);
  text-decoration: none;
  font-size: 14px;
  font-weight: 600;
  letter-spacing: 0.01em;
  padding: 13px 18px;
  transition: background 240ms var(--ease), color 240ms var(--ease);
}
.apply:hover { background: var(--ink); color: var(--ground); }
/* the summary is a personal extra, not the primary ask: it sits below Apply as
   a quiet centred line and opens the address field in place, rather than
   stepping into the conversation as a spoken offer. */
.summary-cta {
  align-self: center;
  background: none;
  border: none;
  border-bottom: 1px solid var(--rule);
  color: var(--ink);
  opacity: 0.72;
  font-size: 14px;
  line-height: 1.3;
  padding: 2px 0;
  cursor: pointer;
  transition: opacity 240ms var(--ease), border-color 240ms var(--ease);
}
.summary-cta:hover { opacity: 1; border-color: var(--ink); }
.contextual {
  display: inline-flex;
  gap: 7px;
  align-items: baseline;
  font-size: 14px;
  color: var(--ink);
  opacity: 0.72;
  text-decoration: none;
  border-bottom: 1px solid var(--rule);
  align-self: flex-start;
  padding-bottom: 2px;
  transition: opacity 240ms var(--ease), border-color 240ms var(--ease);
}
.contextual:hover { opacity: 1; border-color: var(--ink); }
.external-mark { font-size: 11px; opacity: 0.6; }

/* landing: the centrepiece, unwrapped. The column fills the rest of the fold
   and packs toward the composer, so the slack falls between the band and the
   conversation — where a reader expects it — not inside it. */
.chat.landing {
  flex: 1 1 auto;
  width: 100%;
  max-width: 760px;
  margin: 0 auto;
  justify-content: flex-end;
}
/* the transcript holds about the greeting's own two lines while it types, so the
   composer neither creeps nor floats above an empty field */
.chat.landing .log {
  min-height: clamp(52px, 6.5vh, 80px);
  justify-content: flex-end;
}

@media (prefers-reduced-motion: reduce) {
  .caret { animation: none; }
}
</style>
