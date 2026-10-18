# ADR-0010: Two hinge stations, not three

> **Skladen 2:** written for Mk3 and the Pixel 3a XL. Its numbers are inherited, not re-derived; what the Pocophone F1 changes is in [ADR-0011](0011-phone-swap-pocophone-f1.md).

- **Status:** Proposed — the span stiffness of two stations is what the first article decides
- **Date:** 2026-09-22
- **Decides:** how many stations the hinge has, and how a bolt head reaches its pocket

## Context

ADR-0005 put three bolted stations on the hinge line, at X = -87.5, 0 and +87.5.
The count was chosen for load sharing across a 197 mm span. Nobody checked
whether a bolt could physically get into the middle one.

It cannot. The lid's rear edge is rounded on a radius equal to its own
half-thickness, 4.70, struck about the hinge axis. That rounding is not
decoration — it is what makes the 0-180 deg sweep clean, and it was added
precisely to stop the lid's rear corner driving into the setback tail. But it
is a **solid cylinder, Ø9.40, coaxial with the hinge, running the full 196.8**.
Between stations it fills the axis completely.

Measured as the obstruction inside a Ø5.6 x 30 corridor running out from each
pocket — 0 mm³ would be clear, 739 mm³ is solid:

| Station | Head corridor | Nut corridor |
|---|---|---|
| X = -87.5 | 716.7 | 24.0 |
| X = 0.0 | 716.7 | 716.7 |
| X = +87.5 | 24.0 | 716.7 |

The 24.0 mm³ figure is the annulus of lid left around the Ø3.5 bore over the
1.6 mm of lid standing outboard of a station. A Ø5.5 head does not pass a Ø3.5
hole. The 716.7 figures are 87 mm of solid lid.

Two properties of the obstruction matter more than its size:

- **Opening the lid does not clear it.** The blockage is coaxial with the axis
  the lid rotates about, so it occupies the same corridor at every angle. The
  numbers above are identical at 0 deg and at 120 deg.
- **Nothing in the check suite could see it.** Closed interference and the
  0-180 deg sweep both ask whether two solids overlap. An unassemblable joint
  overlaps nothing — the parts simply cannot be brought together in that order.

The nut is recoverable: its pocket is a hex socket, so it can be dropped in
before the lid is nested and is captive thereafter. Only the **bolt** needs a
clear axial path from outside the device.

## Options

### Option A — two stations at the ends, heads outboard

Drop the centre station. Keep ±87.5. Orient each station's fasteners so the head
pocket faces **outboard** and the nut pocket inboard, and bore Ø6.40 through the
1.6 mm of lid standing outboard of each station so the head can pass.

| Pros | Cons |
|---|---|
| No new parts, no new fasteners, no change to how either shell prints | Two hinge points across 197 mm instead of three |
| Both corridors measure 0.0 mm³ clear, at every opening angle | Mid-span lid stiffness becomes a thing to verify rather than assume |
| The arrangement every laptop uses | |

### Option B — three stations, the centre one a separate bolted block

The centre station's knuckles become their own printed part. The M3 stack is
assembled off the device and the block is then fastened down into the tail.
This is ADR-0005's Option G, applied to one station rather than all three.

| Pros | Cons |
|---|---|
| Keeps three points of support | A new part, its own fasteners, its own seating tolerance |
| Assembly access stops being a constraint on the hinge line at all | The block's fixing has to carry hinge moment through a printed interface |
| | Solves a problem that may not exist |

### Option C — bore an access channel along the whole hinge line

Open the lid's rear cylinder to Ø6.40 for its full width so a head can travel to
any station.

| Pros | Cons |
|---|---|
| Station count stays free | A 197 mm horizontal bore, unprintable without gutting the rear |
| | Leaves ~1.5 mm of wall on the one feature that carries the whole lid |
| | Still too small for a nut across corners (6.35) |

Rejected on printability alone.

## Decision

**Option A, provisionally** — two stations, heads outboard, with the span
stiffness treated as an open question rather than a settled one.

Option B solves a problem that has not been shown to exist. The cheapest way to
find out whether it exists is to print the two-station lid, hang the phone in it
and see whether the middle sags; if it does, Option B is still there and we will
have a measurement instead of an argument.

## Consequences

The bolt head corridor is now a **check in `build.py`**, not a thing to remember.
It sits with the connectivity check added the same day, after a lid printed as
four solids because nothing asked whether a part was one solid. Both failures
share a shape: the model was geometrically correct and physically impossible, and
the suite only knew how to ask geometric questions.

`fasteners()` is no longer symmetric — it mirrors on `outboard(x0)`. A station
added at X = 0 in future will silently get an arbitrary orientation and an
obstructed corridor; the access check is what will catch it.

Masses barely move: one station less is 431.0 g solid, 373.7 g printed, against
the 400 g budget in N4. Tipping margins stay above 1 at 150 and 180 deg on both
estimates.

**Each station now carries half the hinge torque, not a third** — and the
torque itself has grown. ADR-0005 sized it at 0.091 N*m from a 207 g lid at
45 mm; the model now gives 219-250 g (printed estimate to solid, phone
included) at an arm of 47.70 mm:

```
device       0.219..0.250 kg * 9.81 * 0.0477 m  =  0.103..0.117 N*m
per station                                     =  0.051..0.058 N*m
```

The axial clamp that delivers it — PETG on PETG at mu 0.35, two sliding faces
per station, r_eff 3.33 mm for a Ø9.00 face around a Ø3.5 bore — is **22-25 N
per station**, up from ADR-0005's 8.8. Still small for an M3, but no longer an
order of magnitude below what a 3 x 1 NBR ring gives at 20 % compression, so
coupon 2.2's measurement now decides something rather than confirming it.

On the one-station coupon, lid held horizontal, that requirement is **58-66 g
hung at the lid's front edge**, 90.05 mm from the axis. ADR-0005's 1x-3x
acceptance window becomes roughly: must hold 66 g, should slip before ~175 g.
The coupon lid's own ~15 g adds about 7 g-equivalent at the edge, which the
figures ignore, so they err on the demanding side.

**To revisit if the first article sags:** Option B, for the centre station only.
The number that settles it is deflection at mid-span with the phone's 167 g in
the lid, at full opening, measured against the base's rim.

Supersedes the station count in [ADR-0005](0005-hinge-mechanism.md); the
mechanism itself — printed knuckles, bolted, elastomer setting the force — is
unchanged.
