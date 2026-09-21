# Security

## Reporting a vulnerability

Please open a [GitHub security advisory](https://github.com/joshband/copy-that/security/advisories/new) (preferred) or contact the repository maintainers privately. Do not open a public issue for undisclosed vulnerabilities.

Include: impact, affected versions/commits if known, and reproduction steps. We will acknowledge and work toward a fix or mitigation.

## Credentials and history exposure

If a secret (API key, database password, token) was ever committed—even if later removed by a history rewrite—**assume it is compromised**:

1. **Rotate** the credential immediately in the provider console (do not reuse the old value).
2. Update deployed environments and local `.env` files with the new secret.
3. Treat GitHub `refs/pull/*/head` as durable: rewriting `main` does **not** remove secrets from old pull-request refs. Ask [GitHub Support](https://support.github.com/contact) to purge affected PR refs and run GC after rotation.

Never commit real connection strings, passwords, or cloud keys into docs, sessions notes, or fixtures. Use placeholders in examples (see `.env.example`).
