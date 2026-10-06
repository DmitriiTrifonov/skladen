# Thickness budget

> **Skladen 2:** written for Mk3 and the Pixel 3a XL. Its numbers are inherited, not re-derived; what the Pocophone F1 changes is in [ADR-0011](../adr/0011-phone-swap-pocophone-f1.md).

Goal: understand what actually sets the closed height, so the design effort goes
where the millimetres are.

All numbers in mm. Inputs and their confidence are in
[measurements.md](../measurements.md).

## Where the height goes

The closed stack is measured at the **rear edge**, which is the thickest line of
the device, because the keyboard is a wedge that rises front-to-rear (5.54 at the
front, 9.52 at the rear, 2.64 deg).

Stack, bottom to top:

```
  lid outer skin        <- 1.20, kept by ADR-0004
  phone                 <- 8.20, fixed
  screen clearance      <- 0.3 .. 0.5, depending on ADR-0004
  keycap over shell     <- 1.82 measured at the rear
  keyboard shell rear   <- 9.52, attackable only by stripping it (deferred to Mk4)
  base floor            <- 1.20, kept by ADR-0008
```

**The keyboard shell is 9.52 of a ~21 stack and is off the table for Mk3** — see
[ADR-0002](../adr/0002-keyboard-integration-depth.md). The phone is the next
largest and is untouchable. So Mk3's entire thickness question reduced to the two
skins: does the lid have a back, and does the base have a floor. Each is worth
1.2.

[ADR-0008](../adr/0008-base-floor.md) kept the floor, for enclosure and
stiffness. [ADR-0004](../adr/0004-phone-retention.md) kept the lid's back, for
rear protection — the fingerprint reader it covers will not be used. **Both
levers are spent.** What is left is a 0.4 mm refinement to the floor itself.

## Scenarios

### A — pocket base with a floor, closed-back lid (selected)

Both components fully enclosed: the keyboard sits on a printed floor, the phone
in a printed pocket with a camera cutout.

| Layer | mm |
|---|---|
| Base floor | 1.20 |
| Keyboard shell, rear | 9.52 |
| Keycap protrusion | 1.82 |
| Keycap-to-lid gap | 0.30 |
| Phone | 8.20 |
| Lid rear wall | 1.20 |
| **Closed height, rear** | **22.24** |
| **Closed height, front** | **18.26** |

This is the design point. The closed device is a wedge, 18.3 at the front rising
to 22.2 at the rear, following the keyboard's own 2.64 deg.

Earlier drafts put this scenario at 22.44 because they carried a 0.50 air gap
between keycaps and screen.

That 0.30 is now an **air gap held open by the base's own walls**, which stand
proud of the keycap plane so the lid lands on the rim rather than on the keys —
see [clamshell-geometry.md](clamshell-geometry.md). A felt or PORON liner on the
lid's inner face is still worth having as screen protection, but it is no longer
load-bearing and no longer sets the gap.

### A-thin — as A, with a 0.8 ribbed floor (open refinement)

A 0.8 floor with 0.6-tall ribs on its upper face, sitting inside the keyboard's
sub-1 mm bottom recess. Effective structural depth 1.4 for 0.8 of height —
stiffer than a flat 1.2 floor, and 0.4 thinner.

| Layer | mm |
|---|---|
| Base floor | 0.80 |
| Keyboard shell, rear | 9.52 |
| Keycap protrusion | 1.82 |
| Keycap-to-lid gap | 0.30 |
| Phone | 8.20 |
| Lid rear wall | 1.20 |
| **Closed height, rear** | **21.84** |

Kept open as [ADR-0008](../adr/0008-base-floor.md) Option E, pending task 0.4.
With both skins now spent this is the only reduction left, and the margin problem
below makes it worth pursuing rather than optional.

### B — pocket base with a floor, open frame lid (rejected)

The lid becomes a bezel frame gripping the phone by its edges; the phone's own
back is the outer surface. A felt or PORON liner replaces the air gap and
protects the screen from the keycaps.

| Layer | mm |
|---|---|
| Base floor | 1.20 |
| Keyboard shell, rear | 9.52 |
| Keycap protrusion | 1.82 |
| Keycap-to-lid gap | 0.30 |
| Phone | 8.20 |
| Lid rear wall | 0.00 |
| **Closed height, rear** | **21.04** |
| **Closed height, front** | **17.06** |

**Rejected** by [ADR-0004](../adr/0004-phone-retention.md): the 1.2 mm is not
worth leaving the phone's back exposed. B-thin, the same construction with a 0.8
ribbed floor, would have been 20.64.

### B+ — open frame both halves (rejected)

The base drops its floor too. The keyboard's own bottom shell — which is flat and
already has a stiff 1.68-wide perimeter rim — becomes the bottom of the device.
Both halves are perimeter frames; the two outer faces of the closed device are
the phone's back and the keyboard's back.

| Layer | mm | |
|---|---|---|
| Base floor | 0.00 | keyboard's own shell serves |
| Keyboard shell, rear | 9.52 | |
| Keycap protrusion | 1.82 | |
| Keycap-to-lid gap | 0.30 | |
| Phone | 8.20 | |
| Lid rear wall | 0.00 | phone's own back serves |
| **Closed height, rear** | **19.84** | |
| **Closed height, front** | **15.86** | 5.54 shell + 1.82 + 0.30 + 8.20 |

Meets the N1 target of <= 20 with the keyboard intact, and is the thinnest
construction available without opening the keyboard.

**Rejected** by [ADR-0008](../adr/0008-base-floor.md): the exposed keyboard
underside, the retention mechanism it would need, and the 26 g of base mass it
gives up were judged not worth 1.2 mm. Recorded here because it is the fallback
if the floor turns out to be a problem, and because Mk4 will want the number.

### C — strip the keyboard to its plate

Deferred to **Mk4**. Estimated 16.5-18.5, gated on an unknown internal stack and
irreversible on the only keyboard in hand. Recorded in
[ADR-0002](../adr/0002-keyboard-integration-depth.md) so the option is not lost.

## Summary

| Scenario | Rear | Front | vs Mk2 (~32, to verify) | Meets N1 (20) | |
|---|---|---|---|---|---|
| **A** | **22.24** | **18.26** | **-30%** | **no, by 2.24** | **selected** |
| A-thin | 21.84 | 17.86 | -32% | no, by 1.84 | open refinement |
| B | 21.04 | 17.06 | -34% | no, by 1.04 | rejected by ADR-0004 |
| B-thin | 20.64 | 16.66 | -35% | no, by 0.64 | — |
| B+ | 19.84 | 15.86 | -38% | yes | rejected by ADR-0008 |
| C | 16.5 .. 18.5 | — | -42% .. -48% | yes | deferred to Mk4 |

The N1 target of 20.0 is missed by 2.24 mm. Both misses were deliberate trades
rather than failures to hit it: [ADR-0008](../adr/0008-base-floor.md) bought an
enclosed base with 1.2, [ADR-0004](../adr/0004-phone-retention.md) bought a
protected phone back with another 1.2. The project chose a 30% reduction over
Mk2 with both components enclosed, rather than a 38% reduction with both exposed.

**N1's hard limit of 22.5 is now the binding constraint, with 0.26 mm of
margin** — see Sensitivity below.

## The rim recess

The keyboard's bottom face is *recessed* inside its 1.68-wide perimeter rim by a
little under 1 mm. That recess is free volume: anything inside the rim footprint
and thinner than the recess adds **zero** to the closed height.

With the floor kept, this is what makes scenario A-thin possible — the ribs live
in that volume. It also means the floor's upper face can carry keyboard-locating
features at no height cost.

## Levers considered and rejected

| Lever | Why not |
|---|---|
| Recess the keycaps into a pocket in the lid | The phone occupies 160 x 76 of the lid's 197 x 90 and sits directly over the key field. No room. |
| Tilt the phone to match the 2.64 deg wedge | The maximum section is still at the rear; it only changes where the wasted air sits. |
| Nest the lid inside the base walls | The lid still has to clear the keycaps. Saves only wall thickness. |
| Deleting the base floor | Worth 1.2, rejected by [ADR-0008](../adr/0008-base-floor.md) on enclosure and stiffness grounds. |
| Thinner phone | Out of scope, N5 keeps the Pixel 3a XL. |

## Sensitivity

- **Front keycap protrusion is unmeasured** (task 0.3). 1.82 is the rear figure.
  If the key plane is parallel to the shell top it is constant and the front
  number above holds; if not, the front figure moves.
- The felt liner at 0.30 is a compressed thickness. Uncompressed stock is
  typically 0.5-1.0 — specify by compressed thickness when buying.
- **There is no headroom left.** At 22.24 against a 22.5 hard limit, any growth
  anywhere breaks the limit. Specifically: if coupon 2.4 shows the base flexes
  under typing and the floor has to go to 2.0-2.5, the device becomes 23.0-23.5.
  Two responses are available and they are not exclusive — take scenario A-thin's
  ribbed 0.8 floor, which is *stiffer* than a flat 1.2 and buys 0.4 back; and
  restate N1's hard limit, which was derived from an early estimate of scenario A
  and is currently self-referential.
- A-thin's 0.4 depends on the rim recess being uniform (task 0.4) and on a 0.8
  floor printing soundly (coupon 2.4). Both are cheap to check and should now be
  done early rather than treated as optional.
- An uncompressed felt liner would also eat the margin. Specify stock by
  *compressed* thickness when buying.
