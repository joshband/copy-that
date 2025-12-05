import path from 'path'
import type { UserConfigExport } from 'vite'
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

const createConfig = ({ command }: { command: 'serve' | 'build' | 'test' }): UserConfigExport => {
  const isTest = command === 'test'

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
      port: 5173,
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
    test: {
      globals: true,
      environment: 'jsdom',
      setupFiles: './vitest.setup.ts',
      alias: {
        '\\.css$': cssStub.replacement,
      },
      pool: 'threads',
      poolOptions: {
        threads: {
          singleThread: true,
        },
      },
    },
  }
}

export default defineConfig(createConfig)
