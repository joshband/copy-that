import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { downloadTextFile } from '../download'

describe('downloadTextFile', () => {
  const originalCreateObjectURL = URL.createObjectURL
  const originalRevokeObjectURL = URL.revokeObjectURL

  beforeEach(() => {
    URL.createObjectURL = vi.fn(() => 'blob:mock')
    URL.revokeObjectURL = vi.fn()
  })

  afterEach(() => {
    URL.createObjectURL = originalCreateObjectURL
    URL.revokeObjectURL = originalRevokeObjectURL
    vi.restoreAllMocks()
  })

  it('creates an anchor click download and revokes the object URL', () => {
    const click = vi.fn()
    const append = vi.spyOn(document.body, 'appendChild').mockImplementation((node) => node)
    const remove = vi.spyOn(document.body, 'removeChild').mockImplementation((node) => node)
    vi.spyOn(document, 'createElement').mockImplementation(() => {
      return {
        click,
        set href(_v: string) {},
        get href() {
          return 'blob:mock'
        },
        set download(_v: string) {},
        get download() {
          return 'tokens.json'
        },
      } as unknown as HTMLAnchorElement
    })

    downloadTextFile('tokens.json', '{"a":1}', 'application/json')

    expect(URL.createObjectURL).toHaveBeenCalled()
    expect(click).toHaveBeenCalled()
    expect(append).toHaveBeenCalled()
    expect(remove).toHaveBeenCalled()
    expect(URL.revokeObjectURL).toHaveBeenCalledWith('blob:mock')
  })
})
