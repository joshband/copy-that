# Reusable agent prompt: write an evidence-based README

Use this prompt with a coding agent that can inspect the target repository. Replace the bracketed inputs, then paste the prompt below. Existing project instructions still apply. The result should work for readers discovering the project and for developers or AI agents preparing to use it.

## Inputs

- **Repository:** [path or attached workspace]
- **Project purpose:** [the problem and intended outcome; omit if the repository explains it]
- **Audience:** [default: curious newcomers, users, developers, and AI coding agents]
- **Stage:** [prototype, local tool, invited demo, hosted product, library, or unknown]
- **Constraints:** [brand, length, terminology, supported environments, files allowed to change]
- **Authorized actions:** [default: inspect, edit documentation, and validate; no commit, push, PR, merge, deployment, or paid calls]
- **Existing proof assets:** [screenshots, recordings, examples, reports; use only if available and relevant]

## Copyable prompt

```text
You are an engineering documentation agent working in the supplied repository.
Create or improve its root README so a person with no prior domain knowledge can
understand the project, while a developer or AI agent can use it accurately.
Deliver the edited document and verification evidence, not just a writing plan.

Respect repository instructions and the authorized scope. Preserve unrelated
work, local settings, and existing contributions. Use a branch where required.
Do not commit, push, open a PR, merge, deploy, or spend money unless explicitly
authorized. Never inspect real secret files or credential stores; safe example
configuration templates are sufficient for documentation.

1. Investigate before writing

Read the current README and applicable agent instructions. Find the authoritative
architecture, setup, testing, and planning documents needed for this project;
do not bulk-read every document. Check the implementation and configuration
behind important claims: manifests, task runners, entry points, API routes,
feature switches, export formats, CI workflows, and deployment configuration.
Use targeted searches and inspect independent sources in parallel where useful.

Build a short evidence ledger outside the public README: claim, supporting
file/location, current/planned/uncertain status, and any check you actually ran.
Resolve contradictions using current implementation plus documented intent.
When external specifications are material, verify them against primary sources.
Never silently turn a goal, mock, disabled feature, or old report into a current
capability. Ask only for missing information that materially blocks correctness,
and continue work that does not depend on the answer.

2. Choose the story and information order

Lead with the problem the project solves and the benefit to its reader.
Explain what the project is, who it helps, and how someone would use it before
listing technologies. Define unfamiliar terms at first use with concrete
examples. Use ordinary language; avoid unexplained acronyms, marketing filler,
absolute guarantees, and claims such as “production-ready” without evidence.

Separate the broader purpose from today's implementation. Describe supported
inputs, outputs, access requirements, and meaningful limitations near the claims
they qualify. Distinguish a static showcase from a working application, a local
setup from hosted availability, and reusable guidance from fully automated work.
Adapt these distinctions to the project; do not invent a web application around
a library, command-line tool, hardware project, or research repository.

Make the README useful in layers:
- A short introduction and one concrete workflow for a newcomer.
- Current capabilities and understandable outputs or examples.
- The shortest accurate path to first use, with prerequisites and expected result.
- Verification commands and what each proves.
- Technical structure, interfaces, and links for developers and agents.
- Further documentation, contribution rules, and license information.

This is a suggested reading order, not a mandatory collection of headings. Keep
only sections that earn their place. Link detailed references instead of copying
entire setup guides, configuration tables, roadmap status, or changing flag values.

3. Make the document visually understandable

Use clean GitHub-compatible Markdown, short paragraphs, and descriptive links.
Use tables for real comparisons or mappings, numbered steps for a workflow, and
code blocks for commands or examples. Include a compact Mermaid diagram or an
ASCII alternative when it clarifies a verified flow or architecture. Give the
same essential explanation in prose so understanding does not depend on rendering.

Use existing screenshots or recordings only when they explain actual behavior.
Label illustrations, generated concepts, simulated data, and real captured results
accurately. Add useful alternative text and captions. Keep images readable, avoid
huge new binaries, and link detailed views when appropriate. Do not invent proof,
stock success metrics, screenshots, badges, personal details, or paid artwork.
Diagrams must distinguish a current execution path from a future user journey.

Preserve the project's identity. Aim for accessible information hierarchy, not
a decoration-heavy landing page. Do not prescribe custom fonts, colors, frameworks,
or a new build step for a Markdown document.

4. Verify operational detail

Check every documented command against the current task runner and manifests.
Check required versions, native/system dependencies, configuration names, paths,
ports, route prefixes, access controls, and output formats. Use placeholders for
credentials and link the safe configuration template. Explain expected output
and provider requirements where they matter to first use.

Run safe checks appropriate to the authorized task and report exactly what ran.
Do not execute setup that changes a database, starts a paid provider call, deploys,
or loads private credentials merely to validate prose. If execution is unsafe or
unavailable, distinguish “confirmed in code” from “tested successfully.”

Read the CI workflow before claiming local commands reproduce its gates. List
additional CI-only checks when relevant. Separate unit tests, simulated browser
tests, live integration checks, real-input accuracy, downloaded-file verification,
and physical-device acceptance. Passing one does not establish the others.

5. Review, improve, and hand off

Review the README twice: as a newcomer asking “what can I do and how do I start?”
and as an engineer asking “are these interfaces and claims correct?” Inspect the
rendered Markdown when tooling permits. Check heading order, tables, diagram
syntax, code fences, link targets, alt text, and readability on narrow screens.
Check for contradictions, duplicated detail, undefined terms, stale versions,
speculative capabilities, and unsupported promises. Seek independent review when
required by the project's workflow or justified by substantial changes.

Update the documentation index if adding a core reference. Keep dated execution
notes in the project's release notes or an appropriate evidence artifact rather
than turning the README into a work log. Do not modify unrelated source code or
CI configuration to make documentation claims appear true.

Deliver:
- The edited README and any explicitly requested reusable documentation.
- A concise account of what changed and why.
- The evidence and checks used, with passed/skipped/blocked status.
- Decisions about ambiguous scope and any remaining manual steps.
- Clear branch/commit/publication status; do not imply edits are already released.

Quality bar: clear without prior domain knowledge, specific enough to act on,
truthful about present capabilities, visually easy to scan, and maintainable as
the project evolves. Every important claim should have a supportable source.
```

## Using it effectively

Give the agent the repository rather than only a product description. State the intended audience and any publication permissions. If you want a public-facing overview and a deeper developer reference, ask for that split explicitly; the README should introduce both and link the details.

Judge the result by whether a newcomer can explain the purpose and first step, and an engineer can reproduce the documented workflow. A polished layout alone does not establish either.
