import { useState, type FormEvent } from 'react'
import { useAuthStore } from '../../store/authStore'
import './MoodSignIn.css'

export function MoodSignIn({ onSignOut }: { onSignOut: () => void }) {
  const sessionEmail = useAuthStore((state) => state.email)
  const signingIn = useAuthStore((state) => state.signingIn)
  const error = useAuthStore((state) => state.error)
  const signIn = useAuthStore((state) => state.signIn)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')

  const submit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const credential = password
    setPassword('')
    void signIn(email.trim(), credential)
  }

  if (sessionEmail) {
    return <div className="mood-board-auth" role="group" aria-label="Mood account">
      <p>Signed in as {sessionEmail}</p>
      <button type="button" onClick={onSignOut}>Sign out</button>
    </div>
  }

  return <form className="mood-board-auth" onSubmit={submit} aria-label="Sign in for Mood">
    <p>Sign in to generate mood boards with your existing account.</p>
    <label htmlFor="mood-sign-in-email">Email</label>
    <input id="mood-sign-in-email" type="email" autoComplete="username" required
      value={email} onChange={(event) => setEmail(event.target.value)} disabled={signingIn} />
    <label htmlFor="mood-sign-in-password">Password</label>
    <input id="mood-sign-in-password" type="password" autoComplete="current-password" required
      value={password} onChange={(event) => setPassword(event.target.value)} disabled={signingIn} />
    {error && <p role="alert">{error}</p>}
    <button type="submit" disabled={signingIn}>{signingIn ? 'Signing in…' : 'Sign in'}</button>
    <p>Signing in does not start generation. Choose Generate when you are ready.</p>
  </form>
}
