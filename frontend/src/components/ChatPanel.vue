<script setup>
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import { useCompose, GREETING, APPLY_HREF, APPLY_LABEL } from '../composables/useCompose.js'
import { useTypewriter } from '../composables/useTypewriter.js'
import Theater from './Theater.vue'

const {
  phase, status, busy, messages, chips, greetingLive, settleGreeting,
  contextualCta, asking, composingLine, turns
} = useCompose()

const draft = ref('')
const log = ref(null)
const STEPS = ['Retrieving', 'Ranking', 'Composing']

// The agent opens the conversation, and the visitor watches it do so. Only a
// fresh session types; a reload reads a conversation that was already spoken.
const { typed, done, thinking, run: typeGreeting, skip, reset } = useTypewriter()
const speaking = computed(() => greetingLive.value && !done.value)

function speakGreeting() {
  if (!greetingLive.value) return
  reset()
  typeGreeting(GREETING)
  if (done.value) settleGreeting() // reduced motion: nothing was typed
}

onMounted(speakGreeting)
watch(greetingLive, speakGreeting)
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
  if (!text || busy.value) return
  draft.value = ''
  await asking({ label: text })
}

function pick(chip) {
  if (busy.value) return
  asking({ label: chip.label, intent: chip.intent })
}
</script>

<template>
  <aside
    class="chat"
    :class="phase"
    @click="letTheVisitorThrough"
    @focusin="letTheVisitorThrough"
  >
    <p class="label chat-head">
      <span>Atha agent</span>
      <span v-if="turns" class="turns">{{ turns }} {{ turns === 1 ? 'answer' : 'answers' }}</span>
    </p>

    <div ref="log" class="log" aria-live="polite">
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
          <p v-else class="answer-text">{{ m.text }}</p>
        </template>
      </article>

      <div v-if="busy" class="composing">
        <Theater :steps="STEPS" :cadence="420" :active="true" />
        <p class="composing-line">{{ composingLine }}</p>
      </div>
    </div>

    <form class="ask" @submit.prevent="submit">
      <input
        v-model="draft"
        type="text"
        :placeholder="phase === 'landing' ? 'Ask about the three days…' : 'Ask a follow-up…'"
        :aria-label="'Ask the ATHA agent'"
        :disabled="busy"
        autocomplete="off"
      />
      <button type="submit" :disabled="busy || !draft.trim()">Ask</button>
    </form>

    <div v-if="chips.length && !busy && !speaking" class="chips">
      <button
        v-for="(c, i) in chips"
        :key="i"
        type="button"
        class="chip"
        @click="pick(c)"
      >{{ c.label }}</button>
    </div>

    <footer class="cta">
      <a class="apply" :href="APPLY_HREF">{{ APPLY_LABEL }}</a>
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
}
.msg { display: flex; flex-direction: column; gap: 6px; }
.you-line {
  font-size: 16px;
  opacity: 0.55;
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
  opacity: 0.5;
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
  opacity: 0.45;
}

.ask {
  display: flex;
  align-items: stretch;
  border: 1px solid var(--ink);
  background: var(--paper);
  transition: border-color 240ms var(--ease);
}
/* the ferrous frame and the ferrous caret never share the surface */
.ask:focus-within { border-color: var(--ferrous); }
.ask input {
  flex: 1;
  min-width: 0;
  padding: 18px 16px;
  font-size: 18px;
  background: none;
}
.ask input::placeholder { color: var(--ink); opacity: 0.38; }
.ask input:disabled { opacity: 0.45; }
.ask button {
  padding: 0 22px;
  align-self: stretch;
  font-family: var(--f-mono);
  text-transform: uppercase;
  letter-spacing: 0.13em;
  font-size: 11px;
  background: var(--navy);
  color: var(--paper);
  transition: background 240ms var(--ease), opacity 240ms var(--ease);
}
.ask button:hover:not(:disabled) { background: var(--deep); }
.ask button:disabled { opacity: 0.32; cursor: default; }
.ask button:focus-visible { outline: 2px solid var(--paper); outline-offset: -4px; }

.chips { display: flex; flex-wrap: wrap; align-items: flex-start; gap: 8px; }
.chip {
  font-size: 13.5px;
  line-height: 1.3;
  text-align: left;
  padding: 5px 11px;
  border: 1px solid var(--rule);
  background: var(--paper);
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
  color: var(--ink);
  text-decoration: none;
  font-size: 14px;
  font-weight: 600;
  letter-spacing: 0.01em;
  padding: 13px 18px;
  transition: background 240ms var(--ease), color 240ms var(--ease);
}
.apply:hover { background: var(--ink); color: var(--paper); }
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

/* landing: the conversation is the centrepiece — a field of its own, on the
   unused --surface step, filling exactly the rest of the fold */
.chat.landing {
  flex: 1 1 auto;
  width: 100%;
  max-width: 920px;
  margin: 0 auto;
  background: var(--surface);
  border: 1px solid var(--rule);
  padding: clamp(16px, 2.2vh, 24px) clamp(16px, 2.4vw, 26px);
}
.chat.landing .log {
  flex: 1 1 auto;
  min-height: clamp(88px, 13vh, 180px);
  justify-content: flex-end;
}

/* reading: docked column, open on paper so the result keeps the stage */
.chat.reading .log { max-height: none; }

@media (prefers-reduced-motion: reduce) {
  .caret { animation: none; }
}
</style>
