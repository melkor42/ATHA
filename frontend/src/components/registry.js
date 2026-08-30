import TextBlock from './TextBlock.vue'

// Component Registry — the allowlist of renderable components (CONTEXT.md).
// The knowledge page is TextBlock-only (the person/enterprise/event cards
// retired with the synthetic network data). Unknown component types render
// nothing; the renderer never crashes.
export const registry = {
  TextBlock
}
