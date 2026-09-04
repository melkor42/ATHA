import Statement from './atoms/Statement.vue'
import FactList from './atoms/FactList.vue'
import StageFlow from './atoms/StageFlow.vue'
import PartnerLayers from './atoms/PartnerLayers.vue'
import TextBlock from './TextBlock.vue'

// Component Registry — the allowlist of renderable components (CONTEXT.md).
// The four atoms carry the structured payloads the server hydrates from the
// knowledge graph; TextBlock is the silent fallback for anything unknown, so
// the renderer never crashes on schema drift.
export const registry = {
  Statement,
  FactList,
  StageFlow,
  PartnerLayers,
  TextBlock
}
