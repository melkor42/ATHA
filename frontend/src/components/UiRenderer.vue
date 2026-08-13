<script>
import { h } from 'vue'
import { registry } from './registry.js'

// Recursive UI renderer: maps node.component through the Component Registry.
// No v-html anywhere — all text flows through Vue templates/escaping.
// Unknown component type or malformed node → renders nothing (never crashes).
export default {
  name: 'UiRenderer',
  props: {
    node: { type: Object, default: null }
  },
  render() {
    const node = this.node
    if (!node || typeof node !== 'object') return null
    const comp = registry[node.component]
    if (!comp) return null
    return h(comp, { node })
  }
}
</script>
