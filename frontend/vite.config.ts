import type { UserConfig } from 'vite'
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'

const createConfig = (): UserConfig => {
  const devPort = Number(process.env.VITE_PORT ?? 5173)

  return {
    plugins: [react()],
    server: {
      host: '127.0.0.1',
      port: devPort,
      strictPort: true,
      proxy: {
        '/api': {
          // Prefer IPv4 loopback: uvicorn often binds 127.0.0.1 only, while
          // `localhost` may resolve to ::1 and break create-project via proxy.
          target: 'http://127.0.0.1:8000',
          changeOrigin: true,
          timeout: 120000,
        },
      },
    },
    build: {
      cssCodeSplit: true,
      rolldownOptions: {
        output: {
          codeSplitting: {
            groups: [
              {
                debugName: 'app-chunks',
                name(id: string) {
                  if (id.includes('node_modules/react')) return 'react-vendor'
                  if (id.includes('node_modules')) return 'vendor'
                  if (id.includes('features/upload')) return 'upload'
                  if (id.includes('features/explorer')) return 'explorer'
                  return undefined
                },
              },
            ],
          },
        },
      },
      chunkSizeWarningLimit: 800,
    },
    test: {
      globals: true,
      environment: 'jsdom',
      setupFiles: './vitest.setup.ts',
      include: ['src/**/*.{test,spec}.{ts,tsx}', 'tests/**/*.{test,spec}.{ts,tsx}'],
      // Forks recycle per file group. A single thread kept every isolated
      // jsdom context and aborted the suite on the heap limit.
      pool: 'forks',
      maxWorkers: 4,
      testTimeout: 30000,
      hookTimeout: 30000,
      isolate: true,
      exclude: ['tests/playwright/**', 'node_modules/**'],
    },
  }
}

export default defineConfig(createConfig)
