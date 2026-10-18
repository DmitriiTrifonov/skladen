# ADR-0003: How to keep the device from tipping over backwards

> **Skladen 2:** written for Mk3 and the Pixel 3a XL. Its numbers are inherited, not re-derived; what the Pocophone F1 changes is in [ADR-0011](0011-phone-swap-pocophone-f1.md).

- **Status:** Accepted
- **Date:** 2026-09-20
- **Decides:** F4

## Context

The phone weighs 167 g and the keyboard 95 g, so the mass is in the lid. Mk2
addressed this with ballast — the file is literally named
`palmtop_weighted_mk2` — and Mk3's keyboard is lighter still.

The full derivation is in [balance.md](../analysis/balance.md). The load-bearing
results, with the hinge on the rear edge and no mitigation at all:

| Construction | Tips at |
|---|---|
| **Floored base + closed-back lid (137 / 207 g) — selected** | **127 deg opening** |
| Floored base + frame lid (137 / 182 g) — rejected | 133 deg opening |
| Frame base + frame lid (111 / 182 g) — rejected | 124 deg opening |

Both construction decisions moved this, in opposite directions.
[ADR-0008](0008-base-floor.md) kept the base floor, adding 26 g low down.
[ADR-0004](0004-phone-retention.md) kept the lid's rear wall, adding 25 g high
up. The second slightly outweighs the first, and the design lands where it
started.

So the problem is real but much smaller than it feels. Normal laptop use is
100-120 deg, which the bare design already survives; what it lacks is margin for
tapping the screen, bumping the desk, and reclining for reading.

Design target for this ADR: **stable to 150 deg opening**, i.e. `theta = 60 deg`
from vertical.

## Options

### Option A — rear setback

Move the hinge axis forward of the base's rear edge so the base extends behind
it as a tail, moving the tipping fulcrum backwards. This is what laptops do.

Required setback for 150 deg: **7.1 mm** on the working mass estimates, and
**10.8 mm** to make tipping impossible at any angle.

Those figures moved once `cad/massing.py` measured the real shells. The hand
estimates this analysis started from were about half of reality — the lid's
18 mm-wide solid side rings were never counted — so the masses are now a
*bracket*, 40-83 g for the lid and 42-72 g for the base, and the required setback
is a range rather than a number:

| Mass case | `s` to never tip |
|---|---|
| both light | 10.8 mm |
| both solid | 10.6 mm |
| working values | 10.8 mm |
| **heavy lid, light base** | **14.6 mm** |
| light lid, heavy base | 6.6 mm |

11 mm covers the expected cases and fails the worst one. **15 mm covers the whole
bracket.**

| Pros | Cons |
|---|---|
| Zero mass, zero thickness, zero parts | Adds 15 mm of footprint depth (90 -> 105) |
| At 15 mm it is elimination across the entire mass bracket, not just the expected case | Only ~7 mm is earned by the expected case; the rest buys insurance against R3 |
| Works identically at every opening angle | The tail is an overhang that must still print well |
| Also gives the rear I/O somewhere to breathe (ADR-0006) | Interacts with the hinge geometry; cannot be bolted on later |

### Option B — dense ballast at the front lip

A steel strip in the front wall of the base, ~82 mm forward of the hinge.

Required mass for 150 deg: **30 g** on the working estimates. With 15 mm of
setback in, no ballast is needed in any case in the bracket — which is precisely
why the pocket should still exist, empty, since the bracket itself is the thing
that might be wrong.

| Pros | Cons |
|---|---|
| Tunable after the fact, without changing geometry | Adds 30 g to a 400 g budget (N4) |
| Sits in the front of the wedge, where the closed stack is 15.9 against the governing 19.8 — so it costs no closed height | Needs a sourced strip cut to size, or a pocket for coins/bolts |
| Makes the device feel solid rather than hollow | Ballast is dead weight in a project whose goal is minimalism |
| Removable for tuning during bring-up | If glued in, a later rebalance means destroying the base |

### Option C — hard stop at ~120 deg

A mechanical stop in the hinge that never lets the lid reach an unstable angle.

| Pros | Cons |
|---|---|
| Free, and cannot be got wrong | Cannot recline the screen for reading or for a low viewing position |
| Removes the failure mode entirely rather than managing it | Does nothing for lap use, where there is no flat contact line anyway |
| | Feels like a limitation rather than a design |

### Option D — lid tail resting on the desk

Extend the lid below the hinge axis so that past ~110 deg its lower edge touches
the desk behind the device, converting the lid from a cantilever into a strut.

| Pros | Cons |
|---|---|
| Zero mass; stability improves as the lid reclines further, the opposite of the usual behaviour | The tail is visible and adds to the closed footprint or the closed thickness |
| Fully supports very reclined angles | Only engages past a certain angle, so it does not help the 100-130 deg band |
| | Scratches the desk unless padded |

### Option E — A + B: setback as structure, ballast pocket as trim

Design in the setback, and add an empty ballast pocket in the front of the base
that can be loaded during bring-up if the real masses differ from the estimates.

| Pros | Cons |
|---|---|
| The structural answer costs nothing; the ballast is only spent if needed | Slightly more CAD |
| Absorbs the fact that every shell mass in the analysis is an estimate | Pocket is wasted volume if never used |

## Decision

**Option E: a 15 mm rear setback, plus an empty ballast pocket in the front of
the base.**

15 rather than the 11 an earlier draft proposed. The reason is the mass bracket
above: 11 mm is derived from the *expected* masses, and those masses turned out
to be the weakest numbers in the project — the first parametric model showed the
hand estimates were roughly half of reality. 15 mm is the figure that holds
across the whole plausible bracket, including the case where the lid ends up
heavy and the base light.

The extra 4 mm is 4 mm of footprint depth and nothing else: no mass, no
thickness, no parts. Against that, the alternative is discovering after assembly
that the device tips and having no lever left but ballast, which adds mass in a
device whose whole point is being small.

The ballast pocket stays even though no case in the bracket now needs it. The
bracket is itself an estimate, and the pocket is the only correction that still
works after the geometry is cut.

## Consequences

- Base footprint becomes **196.8 x 105.05**; the lid stays 196.8 x 90.05 and ends
  at the axis, per [clamshell-geometry.md](../analysis/clamshell-geometry.md).
- The hinge axis is no longer on the rear edge of the base, which changes the
  hinge mounting geometry — [ADR-0005](0005-hinge-mechanism.md) must assume this.
- **The 15 mm is earned entirely here.** An earlier draft had
  [ADR-0006](0006-rear-edge-io-vs-hinge.md) sharing the cost as an I/O shelf;
  that ADR has since been rejected, its premise having been a misread photograph.
  The worst mass case needs 14.6 mm on balance grounds alone, so nothing changes.
- There is now a design rule worth following through detail design:
  **hollow the lid, leave the base solid.** Dead material in the lid is the worst
  place for mass in this device; the same material in the base is free ballast.
- The 15 mm tail sits directly behind the keyboard's rear I/O edge, which is
  useful for [ADR-0006](0006-rear-edge-io-vs-hinge.md): it is somewhere to route
  a port or place a switch paddle.
- **The ballast pocket was dropped when the geometry was built.** It was carried
  as insurance against a mass *bracket*; that bracket has since been replaced by
  masses measured off the model, and the margins pass on the pessimistic printed
  estimate. Hosting a pocket would mean thickening the base's front wall by about
  6 mm, because the keyboard fills the base almost edge to edge and there is no
  free volume. If the built device ever needs ballast, a steel strip tapes to the
  **underside of the base at the front, between the feet** — free in closed
  height, since the front is the thin end of the wedge.
- **The rear feet, not the tail's rear edge, set the tipping contact line.** This
  is easy to lose: the whole analysis measures the setback from where the device
  touches the desk. A 10 mm foot pad placed 1 mm in from the tail edge gives an
  effective setback of 14.0 rather than 15.0 — margin 1.113 instead of 1.149.
  Moving the feet just 5 mm further inboard gives 9.0 and **the device tips**
  (margin 0.934). `cad/build.py` now computes the margin from the actual foot
  position.
- Before the ballast pocket is sized, the first printed lid and base must be
  weighed and their balance points found on a knife edge. Until then, the pocket
  is drawn at the maximum plausible size (30 g of steel) and can only shrink.
- Lap use is out of scope for this ADR; nothing here helps it.
