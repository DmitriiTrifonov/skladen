# ADR-0008: Base floor

> **Skladen 2:** written for Mk3 and the Pixel 3a XL. Its numbers are inherited, not re-derived; what the Pocophone F1 changes is in [ADR-0011](0011-phone-swap-pocophone-f1.md).

- **Status:** Accepted
- **Date:** 2026-09-20
- **Decides:** F2, and 1.2 mm of N1

## Context

[ADR-0002](0002-keyboard-integration-depth.md) fixed the keyboard as a sealed
9.52 mm block, leaving exactly two levers on closed thickness: the lid's back
skin ([ADR-0004](0004-phone-retention.md)) and the base's floor, this ADR. Each
is worth 1.2 mm.

The floor is optional in a way the lid's back is not. The keyboard's own bottom
shell is already flat, already stiffened by a 1.68-wide perimeter rim, and
already designed to be the underside of a device — it could simply *be* the
bottom of the base, the way the phone's back could be the top of the lid.

Two useful measurements from [measurements.md](../measurements.md):

- The keyboard's bottom face is **recessed inside its perimeter rim by a little
  under 1 mm**. Anything thinner than that recess, sitting within the rim
  footprint, adds zero to the closed height.
- The base is 197 x 90; an unsupported floor spans the full key field, which is
  where typing force lands.

The floor also carries ~26 g of mass at the base, which matters to
[ADR-0003](0003-lid-balance-strategy.md): removing it moves the tipping point
from 133 deg of opening to 124 deg.

## Options

### Option A — full floor, 1.2 mm (chosen)

A conventional pan. The keyboard drops in and sits on it.

| Pros | Cons |
|---|---|
| Keyboard's underside is protected and enclosed | +1.2 mm closed height: 21.04 instead of 19.84 |
| Stiff base with no additional mechanism to design | Misses the N1 target of 20.0, though inside the 22.5 hard limit |
| +26 g at the base, which improves stability directly | ~26 g against the 400 g budget (N4) |
| Feet mount on printed geometry, not on the keyboard | Encloses the keyboard's own vents, if it has any |
| Keyboard needs no retention mechanism beyond a lip or friction | |
| Dust and debris stay out of the base cavity | |
| Keyboard remains trivially removable for Mk4 | |

### Option B — no floor, retaining straps in the rim recess

Two or three straps ~0.8 thick spanning the underside within the sub-1 mm
recess, so they cost nothing in height.

| Pros | Cons |
|---|---|
| 19.84 mm, meets the N1 target | Depends on the recess being uniform; measured at one point only |
| Zero height cost for the straps themselves | Straps are unsupported spans and the likely failure point |
| | Device rests on the keyboard's own shell; feet load it directly |
| | Removes 26 g from the base, costing 9 deg of tipping margin |

### Option C — no floor, keyboard bonded to the frame

| Pros | Cons |
|---|---|
| Thinnest and simplest | Semi-permanent; contradicts ADR-0002's reason for keeping the keyboard intact |
| Stiffens the frame considerably | Adhesive creep in a warm bag |

### Option D — partial floor: solid at the front, straps at the rear

The front of the closed stack has 3.98 mm of headroom relative to the rear
(15.86 vs 19.84), so a floor under the front costs nothing at the governing
section.

| Pros | Cons |
|---|---|
| Free at the governing section | Two retention mechanisms in one part |
| Solid anchor for the ADR-0003 ballast pocket, which is at the front anyway | The rear still needs straps, so Option B's risk is not eliminated |
| 19.84 mm | Rear of the keyboard — the heavy, battery-bearing end — is the unsupported one |

### Option E — thin floor with ribs into the rim recess

A 0.8 floor with 0.6-tall ribs on its **upper** face, sitting inside the
keyboard's bottom recess. Effective structural depth 1.4 mm for 0.8 mm of height.

| Pros | Cons |
|---|---|
| 20.64 mm — recovers 0.4 of Option A's 1.2 | Same dependency on recess uniformity as Option B |
| Stiffer than a flat 1.2 floor, not weaker | A 0.8 floor feels flexible in hand before the keyboard is in |
| Keeps every benefit of a full floor: enclosure, feet, mass, removability | Ribs must clear whatever is on the keyboard's underside (labels, pads) |
| Ribs give the keyboard defined bearing points rather than a floppy plane | More print-orientation sensitivity |

## Decision

**Option A — a full 1.2 mm floor.** Closed height becomes **21.04 mm** at the
rear, 17.06 at the front.

This is the owner's call rather than a conclusion from the analysis: 21 mm is
acceptable, and an enclosed base is worth the millimetre. It is also the option
that needs no new mechanism, keeps the keyboard removable for Mk4 without
depending on an unverified recess dimension, and makes the balance problem easier
rather than harder.

**Option E stays open as a refinement**, and has since become the more important
half of this decision. It preserves every property of Option A, gives back
0.4 mm, and is *stiffer* than the flat 1.2 floor rather than weaker. With
[ADR-0004](0004-phone-retention.md) having spent the lid's skin as well, it is
the only reduction left anywhere in Mk3. Resolve it with task 0.4 and coupon 2.4,
early.

## Consequences

- Closed height is 21.04 mm, over the N1 target of 20.0 and inside the 22.5 hard
  limit. **N1's target is not met, by 1.04 mm, by choice.** Recorded rather than
  quietly redefined.
- The lid's back skin became the only remaining thickness lever.
  [ADR-0004](0004-phone-retention.md) has since spent it too, on rear protection
  for the phone, putting the device at **22.24 mm**. Option E below is now the
  only reduction left in the project, and the 0.26 mm of margin against N1's hard
  limit makes it worth pursuing rather than optional.
- Base mass returns to ~137 g, worth nine degrees of tipping margin. ADR-0004
  then added 25 g to the *lid*, which took most of that back: the device tips at
  127 deg, and the rear setback goes to 15 mm to eliminate tipping outright. See
  [balance.md](../analysis/balance.md).
- Task 0.4 (recess depth around the perimeter) was expected to drop off the
  critical path. It has not: it gates Option E, which is now the project's only
  remaining way to reduce thickness.
- **Keyboard retention turned out to need nothing at all.** The pocket captures
  the keyboard on all four sides with 0.30 of clearance, and when the device is
  shut the lid is 0.30 above the keycaps — so the keyboard cannot lift out.
  Closed and inverted, it stays; open and inverted is not a use case. The
  fallback, if it rattles, is a compliant strip in the pocket floor or tape on
  the pocket's side walls, the same trick the phone uses; tape on the floor would
  cost its own thickness in closed height and must be avoided.
