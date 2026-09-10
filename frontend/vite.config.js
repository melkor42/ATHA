import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

// The concept page renders the edition's standing context straight from the
// committed knowledge sources that also seed the graph, so the page and the
// graph cannot drift. Those JSON files live outside the Vite root (repo
// `data/knowledge`), hence the alias and the dev-server fs allow.
const knowledgeDir = fileURLToPath(new URL('../data/knowledge', import.meta.url))

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@knowledge': knowledgeDir
    }
  },
  server: {
    port: 5173,
    strictPort: true,
    fs: {
      // '..' resolves against the Vite root (frontend/), opening the repo root
      // so the @knowledge JSON can be served in dev as well as bundled.
      allow: ['..']
    }
  }
})
