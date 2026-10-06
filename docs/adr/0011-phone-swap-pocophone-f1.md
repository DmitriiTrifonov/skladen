# ADR-0011: Pocophone F1 in place of the Pixel 3a XL, and a headphone-jack slot

- **Status:** Accepted, including the mass budget (N4 420 g, confirmed by the owner
  2026-10-06)
- **Date:** 2026-10-06
- **Decides:** what Skladen 2 changes against Mk3, and what it inherits

## Context

Skladen 2 holds a Xiaomi Pocophone F1 instead of a Pixel 3a XL. The keyboard, the
base, the hinge and the power-switch shuttle are untouched. The only dimensional
source for the new phone is `refs/fun.fbx` (a hobbyist model, binary FBX 7.x),
read directly: its mesh, the world transform of every part, and the geometry of the
buttons and the camera plateau. `cad/` does not depend on the file; the numbers
below were copied out of it into `params.py`.

| | Pixel 3a XL | Pocophone F1 | Source |
|---|---|---|---|
| Body, plan | 160.1 x 76.1 | **155.5 x 75.3** | FBX; matches the spec sheet to 0.1 |
| Thickness | 8.2 | **8.8** | spec — see the first decision |
| Mass | 167 g | **182 g** | spec |
| Plan corner radius | 8.9 front, 10.4 rear | **9.5, all four** | fitted to the FBX outline |
| Buttons | right long side | right long side, three, 0.5 proud | FBX |
| USB-C | bottom, assumed centred | bottom, **centred (X -4 to +4)** | FBX |
| 3.5 mm jack | top, unused | top, 21.8 toward the button side | FBX |
| Camera | upper third, offset | **one tall plateau**, 11.9 x 31.6, centred across | FBX |

Orientation is unchanged ([ADR-0004](0004-phone-retention.md)): the phone's bottom
edge is the lid's right end, so the buttons face the front and **the jack faces
the lid's left end**, where the Pixel's was unused.

## Decisions

**1. The pocket takes the spec thickness, 8.8, not the FBX's 7.9.** The file
squashes Z by 0.856 and reads 6.8 mm of body plus a 1.0 plateau; its plan size
is right and its thickness is not. A pocket too thin for the real phone fails the
fit; one too thick costs 0.6 against the Pixel's 8.2. The closed height is
**23.84 rear / 19.86 front**, 0.66 under the 24.5 limit. This is the first thing
to settle with a caliper (`BLOCKED` in `params.py`); if the phone is thinner,
`phone_z` is the only number that moves.

**2. Camera cutout from the FBX plateau.** X -64.2 to -30.6, and 30.7 to 44.7 from
the phone's button-side edge, 1.0 clear all round. It sits well clear of the logo
(X +-16.7).

**3. A slot for the headphone jack, in the lid's left end.** Open on the screen
side like the USB-C slot of [ADR-0004](0004-phone-retention.md), for the same
reason: closed, its roof would be a thin bridge that sags into the opening
when printed. 9.0 wide, 8.0 high, centred on the phone's mid-plane. The wall it
cuts through is 20 mm, so the plug lies in the slot for most of its length; a
right-angle plug is the better choice. `build.py` checks that a 3.5 mm rod runs
from the phone's jack out of the lid without touching either shell, and the same
for the USB-C.

*The jack's height is assumed.* The FBX gives the jack's position along the edge
but no usable opening, so Z is taken as mid-thickness, which the 8.0 slot covers
with 2 mm either side.

**4. Mass budget: N4 raised to 420 g, from 400 (owner-approved).** The phone is 15 g heavier and
the estimate lands at **401** printed. The build was failing against 400 by a gram
the estimate cannot resolve (it multiplies solid mass by two guessed infill
factors). 420 keeps the check meaningful; the real number comes from the slicer.
The alternative, lightening the lid (its end walls are now 20 mm of solid
plastic each), was not taken.

## Consequences

- **Tipping margin got thinner.** Printed estimate: 1.165 at 150 deg (Mk3: 1.25), **1.009** at
  180 deg (Mk3: 1.08). The heavier phone is most of the change. It still holds at
  every angle, but 0.9% at the theoretical worst case is not headroom; a steel
  strip taped under the front of the base is the remedy noted in `params.py`.
- **The thickness contingency no longer fits.** Margin to 24.5 is 0.66; ADR-0008's
  fallback of a 2.0 mm floor (+0.8) would break the limit.
- **The fingerprint reader is under the lid's rear wall,** as the Pixel's was.
  The Pocophone's is on the back as well. The owner does not need it, so no
  window is cut.
- **Everything measured on Mk3 still holds:** the keyboard, the hinge torque, the
  stations, the switch shuttle. But **Skladen 2 has not been printed.** The first
  article and the coupons in `export/coupon21/` are the next steps; the Mk3 print
  results in ADR-0010 are inherited lessons, not results for this build.
