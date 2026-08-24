import { ref, computed } from 'vue'

// Plus-shaped world: a 3x3 grid of viewport tiles, five of them inhabited.
// center = anchor, north = AI Corner, south = Story+Gate, west = the quiet wing,
// east = Anmeldung (spec §2).
export const ZONE_POS = {
  center: { x: 1, y: 1 },
  north: { x: 1, y: 0 },
  south: { x: 1, y: 2 },
  west: { x: 0, y: 1 },
  east: { x: 2, y: 1 }
}

export const OPPOSITE = { north: 'south', south: 'north', west: 'east', east: 'west' }

const current = ref('center')
const traveling = ref(false)
const pulse = ref(null) // zone whose light vein is invited/pulsing
const slowVeins = ref(false) // AI Corner loading: veins breathe slower
const note = ref(null) // transient companion line any module can raise via say()
const reduced = ref(
  typeof matchMedia !== 'undefined' &&
    matchMedia('(prefers-reduced-motion: reduce)').matches
)

const TRAVEL_MIN = 100
const TRAVEL_MAX = 1300
const clampTravel = (ms) => Math.min(TRAVEL_MAX, Math.max(TRAVEL_MIN, Number(ms) || 600))

// owner-dialed travel duration, persisted; the slider IS the choice
const userTravelMs = ref((() => {
  if (typeof localStorage !== 'undefined') {
    const stored = localStorage.getItem('atha.travelMs')
    if (stored !== null && !Number.isNaN(Number(stored))) return clampTravel(stored)
  }
  return 600
})())

function setTravelMs(ms) {
  userTravelMs.value = clampTravel(ms)
  if (typeof localStorage !== 'undefined') {
    try {
      localStorage.setItem('atha.travelMs', String(userTravelMs.value))
    } catch {
      /* storage unavailable — keep the in-memory value */
    }
  }
}

// veil: the flat viewport scrim that softens zone photography, uniform
// across all tiles; strength is a percentage (0 = clear, 100 = full wash)
const VEIL_MIN = 0
const VEIL_MAX = 100
const VEIL_DEFAULT = 45
const clampVeil = (v) => Math.min(VEIL_MAX, Math.max(VEIL_MIN, Number(v) || 0))

// owner-dialed veil strength, persisted; the slider IS the choice
const userVeil = ref((() => {
  if (typeof localStorage !== 'undefined') {
    const stored = localStorage.getItem('atha.veil')
    if (stored !== null && !Number.isNaN(Number(stored))) return clampVeil(stored)
  }
  return VEIL_DEFAULT
})())

function setVeil(v) {
  userVeil.value = clampVeil(v)
  if (typeof localStorage !== 'undefined') {
    try {
      localStorage.setItem('atha.veil', String(userVeil.value))
    } catch {
      /* storage unavailable — keep the in-memory value */
    }
  }
}

// boris bubble translucency: percentage of surface opacity (0 = ghost,
// 100 = fully opaque); consumed by Companion via the --boris-alpha var
const BORIS_MIN = 0
const BORIS_MAX = 100
const BORIS_DEFAULT = 80
const clampBoris = (v) => Math.min(BORIS_MAX, Math.max(BORIS_MIN, Number(v) || 0))

// owner-dialed bubble opacity, persisted; the slider IS the choice
const userBorisOpacity = ref((() => {
  if (typeof localStorage !== 'undefined') {
    const stored = localStorage.getItem('atha.borisOpacity')
    if (stored !== null && !Number.isNaN(Number(stored))) return clampBoris(stored)
  }
  return BORIS_DEFAULT
})())

function setBorisOpacity(v) {
  userBorisOpacity.value = clampBoris(v)
  if (typeof localStorage !== 'undefined') {
    try {
      localStorage.setItem('atha.borisOpacity', String(userBorisOpacity.value))
    } catch {
      /* storage unavailable — keep the in-memory value */
    }
  }
}

// singleton spatial state — the plaza is one place, one camera
export function usePlaza() {
  const travelMs = computed(() => userTravelMs.value)
  const veil = computed(() => userVeil.value)
  const borisOpacity = computed(() => userBorisOpacity.value)

  function goTo(zone, opts = {}) {
    if (!ZONE_POS[zone] || zone === current.value || traveling.value) return
    traveling.value = true
    pulse.value = zone
    current.value = zone
    window.setTimeout(() => {
      traveling.value = false
      if (pulse.value === zone && !opts.holdPulse) pulse.value = null
    }, travelMs.value + 150)
  }

  function setPulse(zone) {
    pulse.value = zone
  }

  let noteTimer = 0
  function say(text, ms = 4600) {
    note.value = text
    clearTimeout(noteTimer)
    noteTimer = setTimeout(() => (note.value = null), ms)
  }

  function toggleReduced() {
    reduced.value = !reduced.value
  }

  return { current, traveling, pulse, slowVeins, reduced, travelMs, userTravelMs, setTravelMs, veil, setVeil, borisOpacity, userBorisOpacity, setBorisOpacity, goTo, setPulse, toggleReduced, note, say }
}
