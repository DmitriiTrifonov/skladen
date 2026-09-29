# Requirements

## Context

Mitya Computer Skladen Mk3 is the third iteration of a clamshell that turns a
Pixel 3a XL into a pocketable laptop-shaped terminal. Mk1 (`../pixel_palmtop`,
Blender) and Mk2 (`../palmtop_mk2`, FreeCAD) both worked, but Mk2 is bulky: a
170 x 91.4 footprint with a base part 23.35 tall and a lid part 18.21 tall.

Mk3 keeps the same phone and swaps in a much slimmer keyboard (Jomaa
KEYBOARD098RU, salvaged from its folio case).

## Primary goal

**Minimise closed thickness.** Every other property is negotiable against it,
within the constraints below.

## Functional requirements

| # | Requirement |
|---|---|
| F1 | Holds a Pixel 3a XL in landscape orientation in the lid, screen facing the keyboard when closed |
| F2 | Holds the Jomaa keyboard in the base |
| F3 | Opens and stays open, hands-free, at any angle within the supported range |
| F4 | Does not tip over backwards at any supported opening angle, on a desk |
| F5 | Keyboard USB-C reachable without disassembly. The power switch stays permanently ON and needs no access in normal use; the status LEDs are not required to be visible |
| F6 | Phone USB-C reachable for charging while the device is open and in use |
| F7 | **Relaxed.** The phone is taped into the lid, as Mk2's was, so it comes out with a pry and some patience rather than in 30 seconds. An accepted trade, not a requirement met — see [ADR-0004](adr/0004-phone-retention.md) |
| F8 | Stays shut when closed, including inverted in a bag — see [ADR-0009](adr/0009-closure-retention.md) |

## Non-functional requirements

| # | Requirement |
|---|---|
| N1 | Closed thickness at the thickest point: target <= 20.0, hard limit <= 24.5. Design point is **23.24** — the target is missed by 3.24 through deliberate trades, [ADR-0008](adr/0008-base-floor.md) and [ADR-0004](adr/0004-phone-retention.md) (the lid's rear skin, and 1.0 of tape behind the phone). Limit restated by the owner, see below |
| N2 | Footprint: base ~197 x 105 including the 15 mm rear setback; lid ~197 x 90, ending at the hinge axis, leaving the tail exposed when closed (see [clamshell geometry](analysis/clamshell-geometry.md)) |
| N3 | Printable on a 256 x 256 bed without the base being split into multiple parts |
| N4 | Total mass <= 400. Currently ~374 as printed (~432 if it were solid) — measure against the slicer's figure, not `volume x density` |
| N5 | No custom electronics — keyboard and phone stay stock |
| N6 | Parametric CAD: all key dimensions driven from one table, so a different phone or keyboard is a re-parametrisation, not a redraw. Satisfied by [ADR-0007](adr/0007-cad-toolchain.md) — `docs/parameters.md` paired with `cad/params.py` |

## Explicit non-goals

- Modifying the phone or flashing anything on it
- Adding a trackpad, extra battery or any powered component
- Water or drop resistance beyond "survives being carried in a bag"

## Acceptance criteria

The build is done when all of the following hold on the physical device:

1. Closed thickness measured at the thickest point is within N1.
2. The open device does not tip backwards when the lid is at the maximum
   supported angle and the screen is tapped firmly at its top edge.
3. The lid holds position at 100, 120 and the maximum supported angle after
   50 open/close cycles.
4. Keyboard can be charged and power-cycled with the device fully assembled.
5. Phone can be charged with the device open and in use.
6. Phone can be removed and reinserted without damaging either the phone or the
   lid. Not quickly — F7 was relaxed when the phone went onto tape.

## N1 needs restating

The hard limit of 22.5 was written before any construction was chosen, as a round
number just above an early estimate of what is now the selected scenario. The
device has landed at 22.24, so the limit constrained with 0.26 mm of margin — and
it is constraining against a number derived from itself.

This matters because the contingency is real: if coupon 2.4 shows the base flexes
under typing, the floor goes from 1.2 to 2.0-2.5 and the device becomes 23.0-23.5.
There is no headroom to absorb that.

Two responses, not exclusive:

1. Pursue [ADR-0008](adr/0008-base-floor.md) Option E — a 0.8 floor ribbed into
   the keyboard's rim recess, which is *stiffer* than the flat 1.2 it replaces
   and gives back 0.4. This is the project's only remaining reduction.
2. Replace 22.5 with a limit that means something — a pocket, a bag sleeve, a
   number the owner actually cares about — rather than one back-derived from a
   spreadsheet.

**Answered 2026-09-29:** the owner accepts "a couple of millimetres" over the
old figure, so the hard limit is now **24.5**. The first 1.0 of that went
straight to tape behind the phone ([ADR-0004](adr/0004-phone-retention.md)),
leaving 1.26 — enough to absorb the thicker-floor contingency above at 2.0,
not at 2.5.

## Scope boundary with Mk4

[ADR-0002](adr/0002-keyboard-integration-depth.md) keeps the keyboard sealed for
Mk3. Stripping it to its bare plate — worth an estimated 16.5-18.5 mm closed, but
irreversible on the only unit in hand — is deferred to Mk4, to be attempted once
a working Mk3 exists as a fallback. Mk3 must therefore leave the keyboard
removable without cutting anything.

## Open decisions

See [the ADR index](adr/README.md). ADR-0002 is settled; the remaining structural
decisions are not. The analyses in `docs/analysis/` exist to inform them.
