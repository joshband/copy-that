import { API_BASE } from './client'

export interface AuthSession {
  accessToken: string
  email: string
}

export class AuthenticationError extends Error {
  constructor(message: string, readonly status: number) {
    super(message)
    this.name = 'AuthenticationError'
  }
}

/** Authenticate an existing account and verify it before retaining the access token. */
export async function signIn(email: string, password: string): Promise<AuthSession> {
  const response = await fetch(`${API_BASE}/auth/token`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({ username: email, password }),
  })
  if (!response.ok) {
    throw new AuthenticationError(
      response.status === 401 ? 'Invalid email or password.'
        : response.status === 403 ? 'This account is disabled.'
          : 'Sign-in failed. Please try again.',
      response.status
    )
  }
  const tokens: unknown = await response.json()
  if (!tokens || typeof tokens !== 'object' || !('access_token' in tokens)
    || typeof tokens.access_token !== 'string' || !tokens.access_token) {
    throw new Error('Sign-in returned an invalid session. Please try again.')
  }
  const meResponse = await fetch(`${API_BASE}/auth/me`, {
    headers: { Authorization: `Bearer ${tokens.access_token}` },
  })
  if (!meResponse.ok) {
    throw new AuthenticationError('Could not verify your session. Please sign in again.', meResponse.status)
  }
  const user: unknown = await meResponse.json()
  if (!user || typeof user !== 'object' || !('email' in user) || typeof user.email !== 'string'
    || !('is_active' in user) || user.is_active !== true) {
    throw new Error('Could not verify your account. Please sign in again.')
  }
  return { accessToken: tokens.access_token, email: user.email }
}
