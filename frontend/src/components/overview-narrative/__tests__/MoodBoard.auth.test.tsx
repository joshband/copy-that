import { beforeEach, afterEach, describe, expect, it, vi } from 'vitest'
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { MoodBoard } from '../MoodBoard'
import { useAuthStore } from '../../../store/authStore'
import type { ColorToken } from '../../../types'

const colors: ColorToken[] = [{ hex: '#336699', rgb: 'rgb(51,102,153)', name: 'Blue', confidence: 0.9 }]

beforeEach(() => {
  useAuthStore.getState().signOut()
  localStorage.clear()
})
afterEach(() => {
  cleanup()
  vi.unstubAllGlobals()
  useAuthStore.getState().signOut()
})

function mockHostedFlow() {
  const fetchMock = vi.fn().mockImplementation(async (url: RequestInfo | URL) => {
    if (String(url).endsWith('/health')) return { ok: true, json: async () => ({ auth_required: true }) }
    if (String(url).endsWith('/token')) return { ok: true, json: async () => ({ access_token: 'access-only', refresh_token: 'not-retained' }) }
    if (String(url).endsWith('/me')) return { ok: true, json: async () => ({ email: 'person@example.com', is_active: true }) }
    if (String(url).endsWith('/generate')) return { ok: false, status: 401 }
    throw new Error(`Unexpected fetch: ${String(url)}`)
  })
  vi.stubGlobal('fetch', fetchMock)
  return fetchMock
}

async function login() {
  fireEvent.change(screen.getByLabelText('Email'), { target: { value: 'person@example.com' } })
  fireEvent.change(screen.getByLabelText('Password'), { target: { value: 'secret-password' } })
  fireEvent.click(screen.getByRole('button', { name: 'Sign in' }))
  await screen.findByText('Signed in as person@example.com')
}

describe('Mood hosted authentication', () => {
  it('requires sign-in, never generates on login, attaches bearer, and allows explicit retry after expiry', async () => {
    const fetchMock = mockHostedFlow()
    render(<MoodBoard colors={colors} />)
    await screen.findByRole('form', { name: 'Sign in for Mood' })
    expect(screen.getByRole('button', { name: 'Generate themes' })).toBeDisabled()
    await login()
    expect(fetchMock.mock.calls.some(([url]) => String(url).endsWith('/generate'))).toBe(false)
    expect(localStorage.length).toBe(0)
    expect(sessionStorage.length).toBe(0)

    fireEvent.click(screen.getByRole('button', { name: 'Generate themes' }))
    await screen.findByText(/Your session expired or sign-in is required/)
    expect(useAuthStore.getState().accessToken).toBeNull()
    const calls = fetchMock.mock.calls.filter(([url]) => String(url).endsWith('/generate'))
    expect(calls).toHaveLength(1)
    expect(calls[0][1].headers.Authorization).toBe('Bearer access-only')
    await login()
    expect(fetchMock.mock.calls.filter(([url]) => String(url).endsWith('/generate'))).toHaveLength(1)
    expect(screen.getByRole('button', { name: 'Generate themes' })).toBeEnabled()
    fireEvent.click(screen.getByRole('button', { name: 'Generate themes' }))
    await waitFor(() => expect(fetchMock.mock.calls.filter(([url]) => String(url).endsWith('/generate'))).toHaveLength(2))
    await screen.findByRole('form', { name: 'Sign in for Mood' })
    await login()
    fireEvent.click(screen.getByRole('button', { name: 'Sign out' }))
    await screen.findByRole('form', { name: 'Sign in for Mood' })
    expect(useAuthStore.getState().accessToken).toBeNull()
  })

  it('shows rejected credentials and permits another sign-in attempt', async () => {
    const fetchMock = mockHostedFlow()
    render(<MoodBoard colors={colors} />)
    await screen.findByRole('form', { name: 'Sign in for Mood' })
    fetchMock.mockImplementationOnce(async () => ({ ok: false, status: 401 }))
    fireEvent.change(screen.getByLabelText('Email'), { target: { value: 'person@example.com' } })
    fireEvent.change(screen.getByLabelText('Password'), { target: { value: 'wrong' } })
    fireEvent.click(screen.getByRole('button', { name: 'Sign in' }))
    await screen.findByRole('alert')
    expect(screen.getByRole('alert')).toHaveTextContent('Invalid email or password')
    expect(screen.getByLabelText('Password')).toHaveValue('')
    expect(useAuthStore.getState().accessToken).toBeNull()
    await login()
    await waitFor(() => expect(screen.getByRole('button', { name: 'Generate themes' })).toBeEnabled())
  })
})
