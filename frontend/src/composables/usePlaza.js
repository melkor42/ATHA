import { ref, computed } from 'vue'

// Plus-shaped world: a 3x3 grid of viewport tiles, five of them inhabited.
// center = anchor, north = AI Corner, south = Story+Gate, west = Essentials,
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
const note = ref(null) // transient CAM line any module can raise via say()
const reduced = ref(
  typeof matchMedia !== 'undefined' &&
    matchMedia('(prefers-reduced-motion: reduce)').matches
)

const TRAVEL_MS = 1250

// singleton spatial state — the plaza is one place, one camera
export function usePlaza() {
  const travelMs = computed(() => (reduced.value ? 220 : TRAVEL_MS))

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

  return { current, traveling, pulse, slowVeins, reduced, travelMs, goTo, setPulse, toggleReduced, note, say }
}
