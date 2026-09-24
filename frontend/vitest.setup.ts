import '@testing-library/jest-dom'
import { cleanup } from '@testing-library/react'
import { afterEach } from 'vitest'

function releaseClipboardStub() {
  const descriptor = Object.getOwnPropertyDescriptor(navigator, 'clipboard')
  if (!descriptor || descriptor.writable || descriptor.set) return
  Object.defineProperty(navigator, 'clipboard', {
    configurable: true,
    writable: true,
    value: {
      writeText: () => Promise.resolve(),
      readText: () => Promise.resolve(''),
    },
  })
}

// Register on the Vitest hook that stays active for every file in a shared
// worker. RTL's auto-cleanup only binds afterEach the first time its module
// loads, so later files in singleThread mode otherwise keep previous renders.
// user-event also installs a getter-only navigator.clipboard on that same
// window, which makes later Object.assign(navigator, { clipboard }) throw.
afterEach(() => {
  cleanup()
  releaseClipboardStub()
})
