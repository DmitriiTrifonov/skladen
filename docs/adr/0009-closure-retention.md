# ADR-0009: Keeping the device shut when closed

> **Skladen 2:** written for Mk3 and the Pixel 3a XL. Its numbers are inherited, not re-derived; what the Pocophone F1 changes is in [ADR-0011](0011-phone-swap-pocophone-f1.md).

- **Status:** Proposed
- **Date:** 2026-09-20
- **Decides:** F8

## Context

F8 requires the device to stay shut when closed. It has been referenced in
[ADR-0005](0005-hinge-mechanism.md) as "a separate small decision" since the
project started and has never had an owner.

The load case is not the closed device sitting on a desk — there gravity holds
the lid down. It is the device **inverted or on edge in a bag**, where the lid's
weight tries to swing it open.

That load turns out to be a number already computed. From
[balance.md](../analysis/balance.md), the torque needed to hold the lid at
90 deg is

```
M_lid * g * r_lid  =  0.207 * 9.81 * 0.045  =  0.091 N*m
```

Inverted and closed, the lid is again horizontal with its centre of mass 45 mm
from the axis, so the moment trying to open it is **the same 0.091 N*m**. The
two requirements — hold at 90 deg, and hold shut upside down — are numerically
identical, because the moment arm is the same in both cases.

[ADR-0005](0005-hinge-mechanism.md) targets 1.5-3x that figure. So the hinge, as
already specified, holds the device shut with margin, for free.

What the hinge does *not* cover is shock — a dropped bag, or a bag that squeezes
the device and levers it open.

## Options

### A — hinge friction alone

| Pros | Cons |
|---|---|
| Free; the torque is already required by F3 and already specified with margin | Static only — a shock load exceeds it |
| No parts, no geometry, nothing to fail | Torque fades with wear, and F8 fades with it |
| Nothing to align | No tactile "shut" feedback |

### B — magnets

Neodymium discs in the lid's front lip and the base's front wall.

| Pros | Cons |
|---|---|
| Positive closure with a satisfying snap | **The phone sits in the lid.** A magnetometer is used for the compass and by some apps; magnets near it need checking |
| Handles shock loads | Adds mass to the lid, which is the worst place for it (ADR-0003) |
| Tunable by magnet count and spacing | Pockets and glue, and a magnet that comes loose inside the case is a problem |
| Wears indefinitely | Attracts anything ferrous in a bag |

### C — printed snap lip or detent

An interference feature on the lid's front lip engaging the base's front wall.

| Pros | Cons |
|---|---|
| No parts, no mass | PETG creeps; the snap softens over time, same failure as a printed friction fit |
| Tactile feedback | Needs enough lip to work with — the front of the wedge is only 18.26 mm tall |
| Free once the cross-section exists | Hard to tune after printing |

### D — elastic band or strap

| Pros | Cons |
|---|---|
| Trivially strong, trivially cheap | An extra loose object; the thing people lose |
| Also secures the device against a bag squeezing it | Ugly unless designed in |
| Zero design risk | Manual step every time |

## Decision

Not yet made. **Option A is the recommendation as the baseline**, with B as
insurance if coupon 2.2 shows the hinge torque is marginal or fades badly.

The reasoning: the requirement is already satisfied by a mechanism the design
needs anyway, and the arithmetic showing that is exact rather than approximate.
Adding magnets before knowing whether they are needed would put mass in the lid,
which [ADR-0003](0003-lid-balance-strategy.md) spends real effort keeping out.

Option C is rejected on the same ground as printed friction in ADR-0005: PETG
creeps, and a feature that softens over time is a poor answer to a requirement
about carrying the thing around.

### What closes this ADR

Coupon 2.2 measures hinge torque before and after 100 cycles. If the post-cycle
figure is still above 0.091 N*m with margin, Option A stands and F8 needs no
hardware. If it is marginal, add magnets.

Additionally: a bag test. Carry the assembled device for a week and see whether
it has opened. That is Phase 4, and it is the only test that covers the squeeze
case.

## Consequences

- F8 is coupled to hinge wear. If the hinge loosens over the device's life, the
  device stops staying shut before it stops holding angles — the failure shows up
  in a bag, not on a desk. Worth noting in the Phase 4 checks.
- If magnets are added later, the pockets should be designed in from the start
  even if left empty, because retrofitting them into a finished lid is not
  possible. Same pattern as the ballast pocket in
  [ADR-0003](0003-lid-balance-strategy.md).
- **Check the magnetometer before committing to Option B.** The phone is 8.2 mm
  from where the magnets would sit. Test with a compass app and a loose magnet
  before any geometry is cut.
- Nothing here protects against a bag squeezing the device open. If that turns
  out to matter, Option D is the only reliable answer and can be added at any
  time, since it needs no geometry.
