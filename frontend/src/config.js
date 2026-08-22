// Plaza lifecycle + session keys (spec §6).
// BEFORE = pre-event default. DURING / AFTER unlock gated states
// (Q1 option 4, reflection content) via this one config value — no rebuild.
export const LIFECYCLE = 'BEFORE'

export const SESSION_KEYS = {
  arrival: 'atha.arrivalPlayed',
  entrance: 'atha.hasSeenEntrance'
}
