# Design Tokens Community Group Specs (Local Copies)

This folder holds local, offline references for the W3C Design Tokens CG specs.

Contents:
- `2025.10/`: static mirror of the 2025.10 spec pages (format, color, resolver).
- `community-group/`: git submodule of https://github.com/design-tokens/community-group
  for full source and history.
  - See `community-group/technical-reports/` for additional examples and reports.

Update guidance:
- Static mirror: re-run the wget mirror command used in the implementation notes.
- Submodule: `git submodule update --remote docs/standards/design_tokens_cg/community-group`.

Notes:
- Some spec URLs return 404 (non-existent pages), so they are not mirrored.
