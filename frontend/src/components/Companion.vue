<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { usePlaza } from '../composables/usePlaza.js'

// Companion — the plaza's walking companion (spec §4): a small layered
// bear (Warwick's mascot), eyes track the cursor continuously. The
// component is generic; the display name is a prop (default: Boris).
const props = defineProps({
  line: { type: String, default: '' },
  zone: { type: String, default: 'center' },
  prominent: { type: Boolean, default: false },
  locked: { type: Boolean, default: false },
  rolling: { type: Boolean, default: false },
  // while the companion asks a gate question, the bubble grows answer options
  options: { type: Array, default: () => [] },
  // display name — the companion is a role, the bear currently is Boris
  name: { type: String, default: 'Boris' }
})

const emit = defineEmits(['answer', 'said'])

const { reduced } = usePlaza()

// pupils follow the cursor (window listener, cheap math, cleaned up on
// unmount — same contract as the old lens tracking, minus the rAF lerp)
const root = ref(null)
let pupils = []

function trackPupils(e) {
  if (reduced.value || !root.value) return
  const r = root.value.getBoundingClientRect()
  const cx = r.left + r.width / 2
  const cy = r.top + r.height / 2
  const a = Math.atan2(e.clientY - cy, e.clientX - cx)
  const d = Math.min(3.2, Math.hypot(e.clientX - cx, e.clientY - cy) / 60)
  const x = (Math.cos(a) * d).toFixed(2)
  const y = (Math.sin(a) * d).toFixed(2)
  pupils.forEach((p) => (p.style.transform = `translate(${x}px, ${y}px)`))
}

function centerPupils() {
  pupils.forEach((p) => (p.style.transform = 'translate(0px, 0px)'))
}

onMounted(() => {
  pupils = [...root.value.querySelectorAll('.pupil')]
  window.addEventListener('mousemove', trackPupils)
})
onBeforeUnmount(() => {
  window.removeEventListener('mousemove', trackPupils)
})
// if reduced motion turns on while mounted, pupils return to center
watch(reduced, (v) => {
  if (v) centerPupils()
})

// poke curiosity: clicking the companion cycles a few atmospheric lines per
// zone (no program facts — the companion stays a companion, not a brochure)
const EXTRA = {
  center: [
    'Four paths, one plaza. Where shall we drift?',
    'I blink, therefore I am.',
    'The veins remember every visitor.'
  ],
  north: [
    'The AI Corner composes; I just watch.',
    'Panels breathe while you wait — no spinners here.'
  ],
  south: ['Stories grow slower than pages.', 'Take the long way down sometime.'],
  west: ['Facts are the quietest light.', 'Clarity before atmosphere — always.'],
  east: ['Two doors, both warm.', 'Challenges and talent: same light, different angle.']
}
const poke = ref(null)
const pokeIdx = ref(-1)
const happy = ref(false)
let happyTimer = 0

function onPoke() {
  if (props.locked) return
  const pool = EXTRA[props.zone] ?? []
  if (!pool.length) return
  pokeIdx.value = (pokeIdx.value + 1) % pool.length
  poke.value = pool[pokeIdx.value]
  happy.value = true
  clearTimeout(happyTimer)
  happyTimer = setTimeout(() => (happy.value = false), 700)
}
watch([() => props.line, () => props.zone], () => {
  poke.value = null
  pokeIdx.value = -1
})

const activeLine = computed(() => poke.value ?? props.line)

// answer options only appear once the companion has finished speaking the question
const said = ref(false)
const optionsAreActive = computed(() => props.options.length > 0 && said.value)
// chip options collapse into one wrapped multi-select group (chunking),
// regular and action options stay as stacked rows; the input marker renders
// its own text field instead of a button
const chipOptions = computed(() => props.options.filter((o) => o.chip && !o.action))
const rowOptions = computed(() => props.options.filter((o) => !o.input && (!o.chip || o.action)))
const inputOption = computed(() => props.options.find((o) => o.input))

// free-text answer: the visitor types their own question and submits it
const inputText = ref('')
function submitInput() {
  const t = inputText.value.trim()
  if (!t) return
  emit('answer', t)
  inputText.value = ''
}
watch(() => props.options, () => {
  inputText.value = ''
})

// typewriter voice: the companion writes his lines, antenna pulses while talking
const shown = ref('')
const talking = ref(false)
let typeTimer = 0

// finish the current line instantly — used when typing completes and when
// the visitor clicks the bubble to skip the per-character animation
function finishLine() {
  clearInterval(typeTimer)
  shown.value = activeLine.value
  talking.value = false // the bubble's pulse stops the moment the line is said
  if (!said.value) {
    said.value = true
    emit('said')
  }
}
function onBubbleClick() {
  if (talking.value) finishLine()
  else onPoke()
}
watch(
  activeLine,
  (v) => {
    clearInterval(typeTimer)
    said.value = false
    if (!v) {
      shown.value = ''
      talking.value = false
      return
    }
    talking.value = true
    if (reduced.value) {
      finishLine()
      return
    }
    shown.value = ''
    let i = 0
    typeTimer = setInterval(() => {
      i += 1
      shown.value = v.slice(0, i)
      if (i >= v.length) {
        clearInterval(typeTimer)
        talking.value = false
        said.value = true
        emit('said')
      }
    }, 18)
  },
  { immediate: true }
)
onBeforeUnmount(() => {
  clearInterval(typeTimer)
  clearTimeout(happyTimer)
})

// small pop whenever a new line starts
const popKey = ref(0)
watch(activeLine, (v) => {
  if (v) popKey.value++
})
</script>

<template>
  <div
    ref="root"
    class="companion"
    :class="{ prominent, rolling, talking, still: reduced }"
    @click="onPoke"
    :title="`poke ${name}`"
  >
    <div
      v-if="shown"
      class="companion-bubble"
      :class="{ talking, question: optionsAreActive }"
      :title="talking ? 'click to reveal the full line' : undefined"
      @click.stop="onBubbleClick"
    >
      {{ shown }}<span v-if="talking && !reduced" class="caret"></span>
      <div v-if="optionsAreActive" class="companion-options">
        <div v-if="chipOptions.length" class="companion-chips" role="group">
          <button
            v-for="o in chipOptions"
            :key="o.id"
            type="button"
            class="companion-option chip"
            :class="{ selected: o.selected }"
            :aria-pressed="o.selected || undefined"
            @click.stop="emit('answer', o.id)"
          >
            {{ o.label }}
          </button>
        </div>
        <button
          v-for="o in rowOptions"
          :key="o.id"
          type="button"
          class="companion-option"
          :class="[o.theme ? 'theme-' + o.theme : '', { selected: o.selected, action: o.action }]"
          :aria-pressed="o.selected || undefined"
          @click.stop="emit('answer', o.id)"
        >
          {{ o.label }}
        </button>
        <div v-if="inputOption" class="companion-inputrow">
          <input
            v-model="inputText"
            class="companion-input"
            type="text"
            placeholder="Type your own question…"
            aria-label="Your own question"
            @click.stop
            @keyup.enter.stop="submitInput"
          />
          <button
            type="button"
            class="companion-option ask"
            :disabled="!inputText.trim()"
            @click.stop="submitInput"
          >
            Ask
          </button>
        </div>
      </div>
    </div>
    <div class="companion-pop" :key="popKey" :class="{ happy }">
      <div class="bear">
        <svg viewBox="0 0 200 200" :aria-label="`${name}, your plaza companion`">
          <defs>
            <radialGradient id="companion-bodyG" cx="35%" cy="28%" r="85%">
              <stop offset="0%" stop-color="#ffffff" />
              <stop offset="62%" stop-color="#f6efe1" />
              <stop offset="100%" stop-color="#e3d6bd" />
            </radialGradient>
            <radialGradient id="companion-earG" cx="38%" cy="32%" r="80%">
              <stop offset="0%" stop-color="#8ff0fa" />
              <stop offset="100%" stop-color="#22aec6" />
            </radialGradient>
            <radialGradient id="companion-lensG" cx="38%" cy="32%" r="85%">
              <stop offset="0%" stop-color="#2c4763" />
              <stop offset="55%" stop-color="#16293c" />
              <stop offset="100%" stop-color="#0a1826" />
            </radialGradient>
            <radialGradient id="companion-irisG" cx="38%" cy="32%" r="85%">
              <stop offset="0%" stop-color="#9ff6ff" />
              <stop offset="100%" stop-color="#128ba6" />
            </radialGradient>
            <filter id="companion-blurS"><feGaussianBlur stdDeviation="2.2" /></filter>
          </defs>
          <ellipse cx="100" cy="188" rx="42" ry="6.5" fill="#203040" opacity=".16" filter="url(#companion-blurS)" />
          <line x1="100" y1="48" x2="100" y2="27" stroke="var(--outline)" stroke-width="3" stroke-linecap="round" />
          <circle class="halo" cx="100" cy="24" r="7" fill="var(--amber)" opacity="0" />
          <circle class="tip" cx="100" cy="24" r="4" fill="var(--amber)" />
          <g stroke="var(--outline)" stroke-width="4" fill="url(#companion-bodyG)">
            <circle cx="63" cy="63" r="17" /><circle cx="137" cy="63" r="17" />
          </g>
          <circle cx="63" cy="63" r="8" fill="url(#companion-earG)" />
          <circle cx="137" cy="63" r="8" fill="url(#companion-earG)" />
          <ellipse cx="64" cy="147" rx="9" ry="13" transform="rotate(18 64 147)" fill="url(#companion-bodyG)" stroke="var(--outline)" stroke-width="3.5" />
          <ellipse cx="136" cy="147" rx="9" ry="13" transform="rotate(-18 136 147)" fill="url(#companion-bodyG)" stroke="var(--outline)" stroke-width="3.5" />
          <g fill="url(#companion-bodyG)" stroke="var(--outline)" stroke-width="3.5">
            <rect x="80" y="168" width="14" height="15" rx="7" />
            <rect x="106" y="168" width="14" height="15" rx="7" />
          </g>
          <line x1="83" y1="178" x2="91" y2="178" stroke="var(--cyan)" stroke-width="2" />
          <line x1="109" y1="178" x2="117" y2="178" stroke="var(--cyan)" stroke-width="2" />
          <circle cx="100" cy="146" r="31" fill="url(#companion-bodyG)" stroke="var(--outline)" stroke-width="4" />
          <path d="M85 143 Q100 154 115 143" fill="none" stroke="var(--cyan)" stroke-width="2.5" stroke-linecap="round" />
          <circle cx="100" cy="150" r="3" fill="none" stroke="var(--cyan)" stroke-width="2.5" />
          <circle cx="100" cy="93" r="44" fill="url(#companion-bodyG)" stroke="var(--outline)" stroke-width="4" />
          <ellipse cx="83" cy="74" rx="15" ry="9" fill="#ffffff" opacity=".55" />
          <g class="lids">
            <g transform="translate(81 88)">
              <circle r="14.5" fill="#fff" stroke="var(--outline)" stroke-width="3" />
              <circle class="ring" r="10.5" fill="none" stroke="var(--cyan)" stroke-width="2" stroke-dasharray="16 6 4 6" />
              <circle r="8" fill="url(#companion-irisG)" />
              <g class="pupil"><circle r="4.5" fill="#0d2133" /><circle cx="-1.5" cy="-1.5" r="1.6" fill="#fff" /></g>
              <path d="M-6 -9 A11 11 0 0 1 6 -9" fill="none" stroke="#fff" stroke-width="1.6" opacity=".7" />
            </g>
            <g transform="translate(119 88)">
              <circle r="14.5" fill="#fff" stroke="var(--outline)" stroke-width="3" />
              <circle class="ring rev" r="10.5" fill="none" stroke="var(--cyan)" stroke-width="2" stroke-dasharray="16 6 4 6" />
              <circle r="8" fill="url(#companion-irisG)" />
              <g class="pupil"><circle r="4.5" fill="#0d2133" /><circle cx="-1.5" cy="-1.5" r="1.6" fill="#fff" /></g>
              <path d="M-6 -9 A11 11 0 0 1 6 -9" fill="none" stroke="#fff" stroke-width="1.6" opacity=".7" />
            </g>
          </g>
          <ellipse cx="100" cy="102" rx="3" ry="2.4" fill="var(--outline)" />
          <path d="M95 107 Q100 111 105 107" fill="none" stroke="var(--outline)" stroke-width="2.2" stroke-linecap="round" />
        </svg>
      </div>
    </div>
  </div>
</template>

<style scoped>
.companion {
  --outline: #1c2a3a;
  --cyan: #2fbcd3;
  --amber: #f2a44a;
  position: fixed;
  right: 24px;
  bottom: 20px;
  width: clamp(96px, 12vw, 148px);
  z-index: 45;
  transition: transform 0.9s cubic-bezier(0.22, 1, 0.36, 1);
  transform-origin: bottom right;
  cursor: pointer;
}
.companion.prominent { transform: scale(1.32) translate(-10px, -10px); }
/* arrival state: the bear waddles in from off-screen (was cam-roll) */
.companion.rolling { animation: companion-roll 1.6s cubic-bezier(0.22, 1, 0.36, 1) both; }
@keyframes companion-roll {
  from { transform: translateX(45vw); }
  to { transform: translateX(0); }
}

.companion-bubble {
  position: absolute;
  bottom: calc(100% + 10px);
  right: 8px;
  width: 230px;
  padding: 12px 16px;
  /* bubble translucency is tunable: --boris-alpha is bound on the plaza
     root (owner ?tune slider), the fallback keeps 27% transparency */
  background: rgba(248, 244, 236, var(--boris-alpha, 0.73));
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 251, 240, 0.7);
  border-radius: 26px 22px 6px 24px;
  color: #2b2622;
  font-size: 13.5px;
  line-height: 1.45;
  box-shadow: 0 10px 30px rgba(20, 30, 35, 0.2);
  animation: bubble-in 0.5s cubic-bezier(0.22, 1, 0.36, 1);
}
.companion-bubble.talking { animation: bubble-in 0.5s cubic-bezier(0.22, 1, 0.36, 1), bubble-talk 1.1s ease-in-out infinite; cursor: pointer; }
@keyframes bubble-in {
  from { opacity: 0; transform: translateY(8px) scale(0.92); }
}
@keyframes bubble-talk {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.015); }
}
.caret {
  display: inline-block;
  width: 2px;
  height: 0.9em;
  margin-left: 2px;
  vertical-align: text-bottom;
  background: #2b8fa3;
  animation: caret-blink 0.8s steps(1) infinite;
}
@keyframes caret-blink {
  50% { opacity: 0; }
}

/* big speaking bubble: the companion asks the gate questions with live answers */
.companion-bubble.question {
  width: min(320px, 78vw);
  padding: 16px 18px;
  font-size: 14.5px;
}
.companion-options {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: 12px;
}
/* a framed multi-select group: chips wrap in one cluster instead of
   stacking as competing full-width rows; the single action stays a row */
.companion-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.companion-option.chip {
  flex: 0 0 auto;
  padding: 6px 12px;
  font-size: 12.5px;
  border-radius: 999px;
  text-align: center;
}
.companion-option {
  text-align: left;
  border: 1px solid rgba(120, 105, 85, 0.28);
  background: rgba(255, 252, 246, 0.95);
  border-radius: 16px 18px 17px 14px;
  padding: 9px 12px;
  font: inherit;
  font-size: 13px;
  line-height: 1.35;
  color: #2b2622;
  cursor: pointer;
  animation: option-in 0.4s cubic-bezier(0.22, 1, 0.36, 1) both;
  transition: background 0.3s, transform 0.3s, box-shadow 0.3s;
}
/* self-preview: each style option previews its own world's material —
   identities mirror the .mode-* worlds in style.css. Bg/color/font/border
   only, so the hover/selected/action states below keep winning. */
.companion-option.theme-organic {
  font-family: 'Cormorant Garamond', Georgia, serif;
  font-size: 14px;
  background: rgba(244, 236, 214, 0.95);
  color: #3d4a2f;
  border-color: rgba(107, 128, 76, 0.5);
}
.companion-option.theme-minimal {
  font-family: 'Inter', sans-serif;
  background: rgba(255, 255, 255, var(--boris-alpha, 0.73));
  color: #2b2926;
  border-color: rgba(150, 146, 140, 0.4);
}
.companion-option.theme-retro {
  font-family: 'VT323', ui-monospace, monospace;
  font-size: 15px;
  background: rgba(12, 15, 10, var(--boris-alpha, 0.73));
  color: #7dff9e;
  border-color: rgba(64, 255, 200, 0.5);
}
.companion-option.theme-earth {
  background: rgba(201, 154, 91, var(--boris-alpha, 0.73));
  color: #332414;
  border: 2px solid #57493a;
}
.companion-option.theme-steampunk {
  font-family: 'Oswald', 'Arial Narrow', sans-serif;
  background: linear-gradient(180deg, rgba(217, 169, 95, var(--boris-alpha, 0.73)), rgba(192, 138, 62, var(--boris-alpha, 0.73)));
  color: #16110a;
  border-color: #5a4020;
}
.companion-option.theme-surprise {
  border-style: dashed;
}
/* retro keeps a dark ground on hover — the generic hover wash would
   bleach the phosphor text unreadable */
.companion-option.theme-retro:hover {
  background: rgba(22, 34, 26, var(--boris-alpha, 0.73));
  color: #a8ffc4;
}
/* compact + centered: six moods fit the bubble without towering over it */
.companion-option.theme-organic,
.companion-option.theme-minimal,
.companion-option.theme-retro,
.companion-option.theme-earth,
.companion-option.theme-steampunk,
.companion-option.theme-surprise {
  text-align: center;
  padding: 8px 12px;
}
.companion-option:nth-child(2) { animation-delay: 0.08s; }
.companion-option:nth-child(3) { animation-delay: 0.16s; }
.companion-option:nth-child(4) { animation-delay: 0.24s; }
@keyframes option-in {
  from { opacity: 0; transform: translateY(6px); }
}
.companion-option:hover {
  background: rgba(127, 227, 240, 0.26);
  transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(47, 143, 163, 0.18);
}
/* multi-select support: options may carry `selected` — accent outline,
   staying visible so the parent controls when the list closes */
.companion-option.selected {
  border-color: var(--cyan);
  background: rgba(127, 227, 240, 0.22);
  box-shadow: inset 0 0 0 1px rgba(47, 188, 211, 0.45), 0 4px 12px rgba(47, 143, 163, 0.14);
}
.companion-option.selected:hover {
  background: rgba(127, 227, 240, 0.32);
}
/* the action option (e.g. 'continue →'): the plaza's amber action material,
   mirroring .plaza-btn.solid — solid, dark text, hover lift; it is never
   'selected', so the cyan multi-select state cannot collide with it.
   Shrink-wraps to its text and centers instead of stretching full-width
   like the regular answer rows (which carry no .action class). */
.companion-option.action {
  flex: 0 0 auto;
  align-self: center;
  text-align: center;
  background: linear-gradient(135deg, rgba(242, 179, 97, var(--boris-alpha, 0.73)), rgba(226, 120, 78, var(--boris-alpha, 0.73)));
  border-color: transparent;
  color: #241f1b;
  font-weight: 600;
  box-shadow: 0 8px 22px rgba(226, 120, 78, 0.35);
}
.companion-option.action:hover {
  background: linear-gradient(135deg, rgba(242, 179, 97, var(--boris-alpha, 0.73)), rgba(226, 120, 78, var(--boris-alpha, 0.73)));
  transform: translateY(-2px);
  box-shadow: 0 12px 28px rgba(226, 120, 78, 0.45);
}

/* free-text answer row: a dark field + Ask button, in the bubble's material */
.companion-inputrow {
  display: flex;
  gap: 8px;
  align-items: stretch;
  width: 100%;
}
.companion-input {
  flex: 1 1 auto;
  min-width: 0;
  background: rgba(14, 26, 30, 0.55);
  border: 1px solid rgba(241, 237, 230, 0.18);
  border-radius: 7px;
  padding: 8px 12px;
  color: #f1ede6;
  font: inherit;
  font-size: 13.5px;
  letter-spacing: 0.02em;
  outline: none;
  transition: border-color 0.3s var(--ease), background 0.3s var(--ease);
}
.companion-input::placeholder { color: rgba(241, 237, 230, 0.4); }
.companion-input:focus {
  border-color: rgba(127, 227, 240, 0.6);
  background: rgba(18, 32, 38, 0.6);
}
.companion-option.ask {
  flex: 0 0 auto;
  margin: 0;
  width: auto;
}
.companion-option.ask:disabled {
  opacity: 0.4;
  cursor: default;
  transform: none;
}

.companion-pop { transform-origin: bottom right; }
.companion-pop.happy { animation: companion-happy 0.65s cubic-bezier(0.3, 0.8, 0.4, 1); }
@keyframes companion-happy {
  0% { transform: scale(1); }
  30% { transform: scale(1.06, 0.94) translateY(2px); }
  60% { transform: scale(0.97, 1.05) translateY(-5px); }
  100% { transform: scale(1); }
}

/* idle breathing: gentle bob; quicker waddle while talking or rolling in */
.bear { animation: bob 5s ease-in-out infinite; }
.companion.talking .bear { animation-duration: 2.4s; }
.companion.rolling .bear { animation-duration: 1.1s; }
@keyframes bob {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-3px); }
}
.bear svg { width: 100%; display: block; overflow: visible; }

.lids { transform-box: fill-box; transform-origin: center; animation: blink 4.8s infinite; }
@keyframes blink {
  0%, 94%, 100% { transform: scaleY(1); }
  96% { transform: scaleY(0.08); }
}
.ring { transform-box: fill-box; transform-origin: center; animation: spin 9s linear infinite; }
.ring.rev { animation-direction: reverse; animation-duration: 7s; }
@keyframes spin { to { transform: rotate(360deg); } }
/* antenna: always a soft pulse; talking = attention cue, faster + halo blooms */
.tip { transform-box: fill-box; transform-origin: center; animation: pulse 2.2s ease-in-out infinite; }
.companion.talking .tip { animation-duration: 0.7s; filter: drop-shadow(0 0 6px var(--amber)); }
@keyframes pulse {
  0%, 100% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.3); opacity: 0.8; }
}
.halo { transform-box: fill-box; transform-origin: center; animation: halo 2.2s ease-in-out infinite; }
.companion.talking .halo { animation-duration: 0.9s; }
@keyframes halo {
  0%, 100% { transform: scale(0.8); opacity: 0; }
  50% { transform: scale(1.7); opacity: 0.35; }
}
.pupil { transition: transform 0.09s ease-out; }

/* narrow viewports: the bubble must never leave the viewport — anchor it
   right beside Boris, compact typography, long labels wrap. The desktop
   prominent scale-up would push a 320px bubble past the left edge, so it
   yields here; the bubble stays in the right half, clear of the compass
   (its bottom edge still sits above the bear's full height). */
@media (max-width: 640px) {
  .companion { right: 10px; }
  .companion.prominent { transform: none; }
  .companion-bubble {
    right: 10px;
    left: auto;
    width: min(320px, calc(100vw - 20px));
    max-width: calc(100vw - 20px);
    padding: 9px 12px;
    font-size: 14px;
    border-radius: 18px 16px 6px 15px;
  }
  .companion-bubble.question {
    width: min(320px, calc(100vw - 20px));
    padding: 9px 12px;
    font-size: 14px;
  }
  .companion-options { gap: 6px; margin-top: 9px; }
  .companion-option {
    padding: 8px 12px;
    font-size: 13px;
    white-space: normal;
    overflow-wrap: anywhere;
  }
  .companion-option.chip { padding: 6px 10px; font-size: 12px; }
}

/* reduced motion: no bob/blink/spin/pulse/halo, pupils stay centered
   (tracking is skipped in JS), content stays fully visible */
.companion.still .bear,
.companion.still .lids,
.companion.still .ring,
.companion.still .tip,
.companion.still .halo,
.companion.still.rolling { animation: none; }
@media (prefers-reduced-motion: reduce) {
  .bear, .lids, .ring, .tip, .halo, .companion.rolling { animation: none; }
}
</style>
