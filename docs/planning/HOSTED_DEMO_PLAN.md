# Hosted application demo plan

**Status:** Plan only · **Updated:** 2026-10-09

The hiring site under [site/](../../site/) is the existing static showcase. This plan
covers a separate application demo; it does not authorize provisioning or publishing.

## First release: bounded access

Use an invited staging audience before exposing an interactive app publicly. Host
FastAPI and a built frontend with HTTPS, a managed database, explicit CORS origins,
and server-side secrets. Start from [deployment options](../setup/deployment_options.md);
select providers and verify their actual pricing when deployment is requested.
Do not promise a free tier or deploy the local development stack unchanged.

Local Mood remains anonymous. Hosted Mood uses the existing backend account/token
endpoints and an authenticated UI. Sign-in must not start generation; the user must
click Generate after signing in. Keep access tokens in memory, clear credentials
when the request finishes, and support expired-token recovery and sign-out.
Accounts can be provisioned through existing auth endpoints; there is no new hosted
account administration or password recovery flow in this maintenance scope.

## Before hosted use

- Run Alembic, configure a strong signing secret, and set the environment explicitly
  to staging/production. Check which optional dependency extras the chosen host needs.
- Verify unauthenticated/expired/refresh-token rejection and an authenticated enqueue
  against the actual deployment. Use a stub provider first; paid generation requires
  an explicit action and a bounded budget.
- Keep parked routers disabled unless the demo needs them. Review every exposed paid
  extraction/generation route and place the demo behind an access boundary: Mood's
  token check does not protect the whole API.
- Choose worker/broker configuration and confirm polling reaches persisted jobs.
  Jobs currently has no per-user ownership enforcement; keep the audience restricted
  until job-result isolation is designed and verified.
- The Mood limiter is process-local. Before multiple replicas or public access,
  provide a shared limiter and enforce deployment-level/provider spend controls.
- Confirm upload-size limits, error reporting, logs without credentials, CORS,
  database backups, and a rollback path. Do not reuse deleted Redis credentials.

## Acceptance and evidence

Run `make verify`, the mocked MVP browser pack, and a production frontend build.
Capture a fresh deployed browser session showing upload, truthful token provenance,
exported-file contents, Mood sign-in, and an explicit generation action. Label mocked,
fixture, local-live, and deployed evidence separately. A green build or screenshot
alone does not prove provider behavior or downloaded-file correctness.

A read-only, clearly labelled fixture showcase is a lower-cost alternative if invited
live use is unnecessary. It would need its own implementation; the current hiring
site does not become an interactive extraction demo by changing a deployment setting.

## Deployment boundary

No Cloud Run resources, billing changes, public endpoint, or frontend hosting are
created by this plan. Select the audience, infrastructure, and budget before an
explicit deployment request; update the plan with verified choices at that point.
