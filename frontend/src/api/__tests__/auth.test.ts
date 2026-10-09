import { afterEach, describe, expect, it, vi } from 'vitest'
import { signIn } from '../auth'

afterEach(() => vi.unstubAllGlobals())

describe('hosted sign-in', () => {
  it('posts form credentials then verifies the access token with /me', async () => {
    const fetchMock = vi.fn()
      .mockResolvedValueOnce({ ok: true, json: async () => ({ access_token: 'session-token', refresh_token: 'discard' }) })
      .mockResolvedValueOnce({ ok: true, json: async () => ({ email: 'person@example.com', is_active: true }) })
    vi.stubGlobal('fetch', fetchMock)

    expect(await signIn('person@example.com', 'password')).toEqual({ accessToken: 'session-token', email: 'person@example.com' })
    expect(fetchMock.mock.calls[0][1].body.get('username')).toBe('person@example.com')
    expect(fetchMock.mock.calls[1][1].headers.Authorization).toBe('Bearer session-token')
    expect(fetchMock).toHaveBeenCalledTimes(2)
  })

  it('does not retain a token when credentials are rejected', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: false, status: 401 }))
    await expect(signIn('person@example.com', 'wrong')).rejects.toThrow('Invalid email or password')
  })
})
