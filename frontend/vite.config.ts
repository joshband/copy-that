import path from 'path'
import type { UserConfigExport } from 'vite'
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

const createConfig = ({ command }: { command: 'serve' | 'build' | 'test' }): UserConfigExport => {
  const isTest = command === 'test'
  const devPort = Number(process.env.VITE_PORT ?? 5173)

  const cssStub = {
    find: /\.css$/,
    replacement: path.resolve(__dirname, 'src/test/__mocks__/styleMock.ts'),
  }

  const stubCssPlugin = () => ({
    name: 'stub-css',
    enforce: 'pre' as const,
    resolveId(id: string) {
      if (isTest && /\.css$/.test(id)) {
        return `stub:${id}`
      }
    },
    load(id: string) {
      if (isTest && id.startsWith('stub:')) {
        return 'export default {}'
      }
    },
  })

  return {
    plugins: [react(), ...(isTest ? [stubCssPlugin()] : [])],
    server: {
      host: '127.0.0.1',
      port: devPort,
      strictPort: true,
      proxy: {
        '/api': {
          target: 'http://localhost:8000',
          changeOrigin: true,
          timeout: 120000,
        },
      },
    },
    resolve: {
      alias: isTest ? [cssStub] : [],
    },
    build: {
      cssCodeSplit: true,
      rollupOptions: {
        output: {
          manualChunks(id: string) {
            if (id.includes('node_modules/react')) return 'react-vendor'
            if (id.includes('node_modules')) return 'vendor'
            if (id.includes('features/upload')) return 'upload'
            if (id.includes('features/explorer')) return 'explorer'
            return undefined
          },
        },
      },
      chunkSizeWarningLimit: 800,
    },
    test: {
      globals: true,
      environment: 'jsdom',
      setupFiles: './vitest.setup.ts',
      alias: {
        '\\.css$': cssStub.replacement,
      },
      include: ['src/**/*.{test,spec}.{ts,tsx}', 'tests/**/*.{test,spec}.{ts,tsx}'],
      pool: 'threads',
      poolOptions: {
        threads: {
          singleThread: true,
          maxThreads: 1,
          minThreads: 1,
        },
      },
      // Memory management
      testTimeout: 30000,
      hookTimeout: 30000,
      isolate: true,
      // Disable source maps to save memory
      sourcemap: false,
      exclude: ['tests/playwright/**', 'node_modules/**'],
    },
  }
}

export default defineConfig(createConfig)
