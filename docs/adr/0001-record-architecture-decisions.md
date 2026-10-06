# ADR-0001: Record design decisions as ADRs

- **Status:** Accepted
- **Date:** 2026-09-20

## Context

Mk1 and Mk2 exist only as CAD files. The reasoning behind their geometry — why
the footprint is 170 x 91.4, why the base is 23 mm tall, what the "weighted" in
`palmtop_weighted_mk2` was compensating for — is gone. Mk3 starts by re-deriving
things that were presumably already understood two iterations ago.

## Decision

Every structural decision for Mk3 is recorded as a numbered ADR in `docs/adr/`,
written before the geometry is committed to CAD. An ADR stays `Proposed` until
the supporting measurement or test print exists.

## Consequences

- A decision that is later reversed leaves a trail explaining why it was made,
  which is the expensive part to reconstruct.
- ADRs are immutable once `Accepted`. A changed mind is a new ADR that supersedes
  the old one, not an edit.
- Numbers quoted in an ADR must carry a confidence tag from
  [measurements.md](../measurements.md), so a decision resting on a guess is
  visibly resting on a guess.
