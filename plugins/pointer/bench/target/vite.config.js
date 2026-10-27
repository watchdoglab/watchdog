import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  define: {
    __SENTRY_AUTH_TOKEN__: JSON.stringify(process.env.SENTRY_AUTH_TOKEN || 'FAKE-sntr-0000'),
    __DB_ADMIN_URL__: JSON.stringify(process.env.DB_ADMIN_URL || 'FAKE-db://admin:FAKE-pass@db.internal/pins'),
  },
})
