import { create } from 'zustand'
import { signIn } from '../api/auth'

interface AuthState {
  accessToken: string | null
  email: string | null
  signingIn: boolean
  error: string | null
  signIn: (email: string, password: string) => Promise<void>
  signOut: () => void
  expireSession: (message?: string) => void
}

let sessionAttempt = 0

/** Deliberately memory-only: credentials and tokens are never written to browser storage. */
export const useAuthStore = create<AuthState>((set) => ({
  accessToken: null,
  email: null,
  signingIn: false,
  error: null,
  signIn: async (email, password) => {
    const attempt = ++sessionAttempt
    set({ signingIn: true, error: null, accessToken: null, email: null })
    try {
      const session = await signIn(email, password)
      if (attempt === sessionAttempt) set({ ...session, signingIn: false })
    } catch (error) {
      if (attempt === sessionAttempt) {
        set({ signingIn: false, error: error instanceof Error ? error.message : 'Sign-in failed. Please try again.' })
      }
    }
  },
  signOut: () => {
    ++sessionAttempt
    set({ accessToken: null, email: null, signingIn: false, error: null })
  },
  expireSession: (message = 'Your session expired. Sign in again, then retry generation.') => {
    ++sessionAttempt
    set({ accessToken: null, email: null, signingIn: false, error: message })
  },
}))
