import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import react from '@vitejs/plugin-react'
import { defineConfig, type Plugin } from 'vite'

// The process overview lives in docs/ as a standalone page; the site serves the same file at /guide.html.
const GUIDE = fileURLToPath(new URL('../docs/流程说明.html', import.meta.url))

function guidePage(): Plugin {
  return {
    name: 'guide-page',
    configureServer(server) {
      server.middlewares.use('/guide.html', (_req, res) => {
        res.setHeader('Content-Type', 'text/html; charset=utf-8')
        res.end(readFileSync(GUIDE))
      })
    },
    generateBundle() {
      this.emitFile({ type: 'asset', fileName: 'guide.html', source: readFileSync(GUIDE) })
    },
  }
}

export default defineConfig({
  plugins: [react(), guidePage()],
  server: {
    proxy: { '/api': 'http://127.0.0.1:8000' },
  },
})
