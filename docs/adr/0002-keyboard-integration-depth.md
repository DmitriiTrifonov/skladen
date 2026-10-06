# ADR-0002: How deeply to integrate the keyboard

> **Skladen 2:** written for Mk3 and the Pixel 3a XL. Its numbers are inherited, not re-derived; what the Pocophone F1 changes is in [ADR-0011](0011-phone-swap-pocophone-f1.md).

- **Status:** Accepted
- **Date:** 2026-09-20
- **Decides:** N1 (closed thickness). This is the highest-leverage decision in
  the project and every other ADR depends on its outcome.

## Context

Per the [thickness budget](../analysis/thickness-budget.md), the keyboard shell
is 9.52 mm of a 20-22 mm closed stack, and the phone is another 8.2 mm, fixed by
N5. Between them that is roughly 90% of the budget. Walls, clearances and keycaps
together are under 5 mm, so the keyboard shell is the only term large enough to
change the outcome by itself.

There is **one** keyboard. Its folio case is already destroyed, so a failed
teardown means buying another unit and losing the measurements this project is
built on.

Unknown, and decisive: the thickness of the keyboard's own bottom shell, of the
flat plate/PCB/scissor stack, and where the battery sits. The 2.64 deg wedge may
be pure shell geometry (in which case removing the shell removes 4 mm at the
rear) or it may follow a rear-mounted battery (in which case it removes almost
nothing).

## Options

### Option A — keyboard stays a sealed module

The keyboard drops into a pocket in the base as bought, retained by its own
perimeter rim and a printed lip. Nothing is opened.

| Pros | Cons |
|---|---|
| Zero risk to the only keyboard | Closed height floors out at 19.84 mm, and only if both skins are deleted too — 21.04 as actually built |
| Keyboard remains a replaceable part | The 2.64 deg wedge forces a wedge-shaped closed device |
| Its I/O keeps working exactly as designed | Rear I/O stays on the hinge edge (see ADR-0006) |
| Fastest path to a working Mk3 | Carries the shell's dead air and wedge into the stack |

### Option B — remove the bottom shell only

Split the keyboard's clamshell, discard its bottom half, and let the printed base
floor serve as the keyboard's bottom. The plate, PCB, battery and top shell (the
part that holds the key field) stay together.

| Pros | Cons |
|---|---|
| Saves the bottom shell thickness, est. 1.2-1.5 mm | Requires the printed floor to be stiff enough for typing, so it grows to 2.0-2.5 mm and gives ~1 mm back |
| Reversible-ish: the keyboard still works standalone if remounted | Net saving may be near zero |
| Low risk compared to C | Exposes the PCB to the base cavity; needs an insulating layer |

### Option C — strip to the plate and rebuild the wedge as a fold-out foot

Discard both shells. Mount the plate/PCB/battery directly into the printed base.
The typing angle no longer comes from the keyboard's wedge but from a fold-out or
removable rear foot, which sits *outside* the closed stack.

| Pros | Cons |
|---|---|
| The only path to <= 20 mm; est. 16.5-18.5 mm | Irreversible, and there is no second keyboard |
| Removes the wedge from the closed stack entirely | Saving is unverified — collapses if the battery is rear-mounted and thick |
| Frees the rear edge, dissolving the ADR-0006 conflict | The base must now provide scissor-plate rigidity, key retention and switch/LED/port mounting |
| Closed device becomes a flat slab rather than a wedge | Much more CAD and several more test prints |
| | Fold-out foot is another mechanism to design and another failure point |

### Option D — stage it: build A first, then C

Build and ship a working Mk3-A with the keyboard intact. Only then, with a proven
lid, hinge and balance, open the keyboard and produce an Mk3-C base that drops
into the same lid.

| Pros | Cons |
|---|---|
| Never blocks on the irreversible step | Two base designs to model and print |
| The teardown happens with a known-good reference device in hand | Target thickness is not met on the first build |
| If C fails, A still exists and is already assembled | Lid/hinge must be designed to accept both bases from the start |

## Decision

**Option A — the keyboard stays a sealed module.** Option C is deferred to Mk4.

The reasoning: a closed height around 20 mm is acceptable for Mk3, and scenario
B+ in the [thickness budget](../analysis/thickness-budget.md) reaches 19.84 with
the keyboard untouched by deleting the base floor instead. That makes the
remaining 2-3 mm that Option C would buy an expensive marginal gain — paid for
with the only keyboard in existence, on an estimate that is still a guess.

The right time to spend that risk is when there is a working Mk3 to fall back on
and the internal stack has been measured on a unit that is no longer critical.
That is Mk4.

This is Option D from the list above, with the second stage renamed to a separate
project rather than a later phase of this one.

## Consequences

- The rear edge keeps the keyboard's switch, LEDs and USB-C, so
  [ADR-0006](0006-rear-edge-io-vs-hinge.md) stays a live problem and must be
  solved rather than designed around.
- The 9.52 mm shell and the 2.64 deg wedge are fixed inputs. The closed device
  will be a wedge, ~17.1 at the front and ~21.0 at the rear.
- With the keyboard fixed, the only thickness levers left are the two 1.2 mm
  skins. [ADR-0008](0008-base-floor.md) kept the base floor, so the lid's back
  skin in [ADR-0004](0004-phone-retention.md) is the last one.
- Closed height lands at 21.04, over the N1 target of 20.0 and inside the 22.5
  hard limit.
- The keyboard must not be opened during Mk3. Any task that requires knowing its
  internal stack is out of scope, including relocating its I/O by wiring
  (ADR-0006 Option D is therefore unavailable).
- Mk4 inherits this repo's measurements and analyses. The teardown data it needs
  is listed under "Not yet known" in [measurements.md](../measurements.md).
