import TextBlock from './TextBlock.vue'
import SignalCard from './SignalCard.vue'
import StudentProfile from './StudentProfile.vue'
import EnterpriseCard from './EnterpriseCard.vue'
import EventBanner from './EventBanner.vue'

// Component Registry — the allowlist of renderable components (CONTEXT.md).
// Unknown component types render nothing; the renderer never crashes.
export const registry = {
  TextBlock,
  SignalCard,
  StudentProfile,
  EnterpriseCard,
  EventBanner
}
