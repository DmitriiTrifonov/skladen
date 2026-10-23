# ADR-0015: Crush ribs on the pocket walls to stop the phone rattling

- **Status:** Proposed — modelled, not printed
- **Date:** 2026-10-23
- **Decides:** how the phone is held in the bezel lid's pocket ([ADR-0012](0012-removable-front-bezel.md) removed the tape)

## Context

With the tape gone the phone floats: 0.3 per side in the pocket (`clr_phone`) and 0.2
under the plate (`bezel_play`). There is no room in Z for foam (the 0.2 is all there is),
so the side play is the one to take up.

## Decision

Thin ribs on the pocket walls, the same idea as the adapter seat's (`adapter_rib`) but
lighter: `phone_rib_h` 0.40 high, 0.8 wide, from the rear skin up to the glass with a
45 deg lead-in. Two on each long wall, two on each end, placed clear of the clip slots,
the button window, the USB-C slot, the audio holes and the jack slot. With the phone
centred the squeeze is 2 x 0.40 - 0.6 = 0.2 in total. Nothing changes in height or
(measurably) mass; the plate is untouched, so the phone still lifts out once it is off.

## Consequences

- **Unprinted.** The base pocket printed 0.6 narrower than modelled over 194 mm; the lid's
  156 mm pocket may shrink too. If the phone will not go in, lower `phone_rib_h`; if it
  still moves, raise it. Try it on the phone coupon before the whole lid.
- The 0.2 of play over the glass is not touched; a 0.4-0.5 mm foam strip under the plate's
  overlap would take it up, if it still clicks in Z.
- The USB-C extender ([ADR-0013](0013-usbc-extender.md)) is parked meanwhile: its build
  step is off, nothing else depends on it.
