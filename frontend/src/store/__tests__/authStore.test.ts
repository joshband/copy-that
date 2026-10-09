import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { useAuthStore } from '../authStore'

beforeEach(() => useAuthStore.getState().signOut())
afterEach(() => {
  useAuthStore.getState().signOut()
  vi.unstubAllGlobals()
})

describe('memory-only auth session', () => {
  it('keeps the session empty when /me rejects the issued token', async () => {
    vi.stubGlobal('fetch', vi.fn()
      .mockResolvedValueOnce({ ok: true, json: async () => ({ access_token: 'unverified' }) })
      .mockResolvedValueOnce({ ok: false, status: 401 }))
    await useAuthStore.getState().signIn('person@example.com', 'password')
    expect(useAuthStore.getState().accessToken).toBeNull()
    expect(useAuthStore.getState().signingIn).toBe(false)
    expect(useAuthStore.getState().error).toContain('Could not verify your session')
  })

  it('does not restore a session when an in-flight login completes after sign-out', async () => {
    let finishLogin!: (response: Response) => void
    const pending = new Promise<Response>((resolve) => { finishLogin = resolve })
    vi.stubGlobal('fetch', vi.fn()
      .mockReturnValueOnce(pending)
      .mockResolvedValueOnce({ ok: true, json: async () => ({ email: 'person@example.com', is_active: true }) }))
    const signIn = useAuthStore.getState().signIn('person@example.com', 'password')
    useAuthStore.getState().signOut()
    finishLogin(new Response(JSON.stringify({ access_token: 'late-token' }), { status: 200 }))
    await signIn
    expect(useAuthStore.getState().accessToken).toBeNull()
    expect(useAuthStore.getState().email).toBeNull()
  })
})
