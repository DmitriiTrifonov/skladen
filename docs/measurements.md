# Measurements

All dimensions in mm, masses in g. Axis convention used throughout the project:

- **X** — span, left-to-right along the key rows (the long axis)
- **Y** — depth, front-to-back (user's body towards the hinge)
- **Z** — height, table to top of the closed device

Confidence tags: `M` measured with calipers, `S` from spec sheet / open sources,
`E` estimated or derived, `?` unknown, must be captured.

## Keyboard — Jomaa KEYBOARD098RU "Ardor Plum"

Bluetooth keyboard, Russian layout, salvaged from its folio case (case discarded).

| Property | Value | Conf |
|---|---|---|
| Span (X) | 194.00 (first reading 193.00; re-measured when it would not go into a printed pocket) | M |
| Depth (Y) | 86.25 | M |
| Height, shell only, rear edge (thickest) | 9.52 | M |
| Height, shell only, front edge (thinnest) | 5.54 | M |
| Height incl. keycaps, rear edge | 11.34 | M |
| Keycap protrusion above shell, rear | 1.82 (design value 2.0) | M |
| Keycap protrusion above shell, front | 1.82 | M | owner: same as rear |
| Mass | 95 | M |
| Bottom face | flat, with a perimeter rim 1.68 wide and < 1.0 tall | M |
| Top face | wedge, rises front → rear | M |
| Wedge angle (derived) | atan((9.52-5.54)/86.25) = 2.64 deg | E |

### I/O

The rear (thick) edge carries the OFF/ON slide switch and the four status LEDs —
see `reference/photos/keyboard-rear-edge-switch-leds.jpg`.

**The USB-C port is on the keyboard's RIGHT SIDE face**, not on the rear edge.
`reference/photos/keyboard-rear-edge-usb-c.jpg` shows that face, and an earlier
reading of it as the rear edge seen at an angle was wrong. That misreading
invented the hinge-versus-I/O conflict that
[ADR-0006](adr/0006-rear-edge-io-vs-hinge.md) existed to solve.

> `reference/` is gitignored — the photos and borrowed models in it are local
> only and do not travel with a clone. Every dimension they support is recorded
> in this file; the images are corroboration, not the source of record.

Datums: distance measured **back from the keyboard's rear (high) edge** along the
right side face; Z from the plane the keyboard rests on.

| Feature | Value | Conf |
|---|---|---|
| USB-C, rear edge to the near end of the connector | 8.00 | M |
| USB-C opening, lower edge above the rest plane | 3.00 | M |
| USB-C opening, upper edge below the top of that face | 2.00 | M |
| Side face height at the port (derived, the face is a wedge) | 8.94 | C |
| USB-C opening height (derived) | 3.94 | C |
| USB-C opening width, along the keyboard's depth | assumed 9.0 | ? - confirmed by fit |
| OFF/ON slide switch | rear edge, niche 12.5 from the right side face — see below | M |
| LEDs x4 | rear edge, not needed | D |

In device coordinates the opening centres on **Y 75.65, Z 6.17**, in the base's
right wall.

Two things worth a second look: the assumed 9.0 opening width, and whether the
3 and 2 were taken to the visible opening or to the connector housing.

The switch was first left permanently ON and the LEDs are not required to be visible, so
**USB-C was the only feature on this edge needing access** — see
[ADR-0006](adr/0006-rear-edge-io-vs-hinge.md) and F5.

**Height matters as much as X.** The hinge axis sits at 12.54 above the desk and
the keyboard's rear face tops out at 10.72, so a port mounted high on that face
cannot share an X position with a hinge station — see R1 in
[plan.md](plan.md). Tasks 0.1 and 0.1b.

**Task 0.1 is closed by fit, not by callipers (2026-09-22).** The first printed
coupon's window lines up with the real keyboard's port, so the assumed 9.0 never
has to become a measurement. The tolerance was worked out beforehand and is
recorded next to the parameter: the opening spans 6.0 to 19.0 back from the
keyboard's rear edge, against a measured 8.00 where the connector starts, so any
true width up to 11.0 is cleared with 2.0 to spare at the rear end. A USB-C
receptacle is 8.34.

This edge is also the natural hinge edge, which is a direct conflict — see
[ADR-0006](adr/0006-rear-edge-io-vs-hinge.md).

### Power switch (measured 2026-09-29)

A glitching keyboard wanted power-cycling, so the switch is now reached after
all — by a shuttle through the base's tail, worked from its rear face. It sits
in a niche right under the right-hand hinge station. ON is toward the
keyboard's left, OFF toward its right.

| Feature | Value | Conf |
|---|---|---|
| Niche, right side face to its near end | 12-13, taken as 12.5 | M |
| Niche, width x height | 7.45 x 4.10 | M |
| Knob, width x height | 4.24 x 3.10 | M |
| Knob to the niche's end, at either end of travel | 1.00 | M |
| Knob travel (derived) | 1.21 | C |
| Knob, proud of the rear face | 0.75, nearer 1.0 by feel | M |
| Knob centre above the rest plane | 4.25 | M |
| Niche edges, above the rest plane / below the top | 3.24 / 2.60 | M |

The two Z readings disagree by about a millimetre: the niche's edges put its
centre near 5.1, against 4.25 read at the knob. The shuttle's prongs span 2.4
to 7.0 above the rest plane, so `build.py` checks that they drive the knob at
both, and the question does not have to be settled before printing.

### Not yet known (requires teardown)

| Property | Conf |
|---|---|
| Thickness of the keyboard's own bottom shell | ? |
| Thickness of plate + PCB + scissor stack (flat portion) | ? |
| Battery size and location | ? |
| Whether the wedge is pure shell or follows internal parts | ? |

These gate [ADR-0002](adr/0002-keyboard-integration-depth.md).

## Phone — Google Pixel 3a XL

| Property | Value | Conf |
|---|---|---|
| Body | 160.1 x 76.1 x 8.2 | S |
| Envelope incl. camera bump (from Mk2 STL) | 160.1 x 77.1 x 9.4 | E |
| Mass | 167 | S |
| Screen | 6.0" 18:9, used in landscape | S |
| USB-C | bottom edge (short edge) | S |
| Fingerprint reader | rear face, upper third | S |
| Power + volume buttons | right edge in portrait; top long edge of the lid once mounted | S |
| 3.5 mm jack | top edge in portrait; left short edge of the lid — no cutout, unused | S |
| SIM tray | left edge in portrait; hinge-side edge of the lid | S |
| Button positions along the edge, and protrusion | — | ? |
| USB-C position on the short edge | assumed centred | A |
| Front bezel width | not needed | D | no retention lips; the phone is taped in |
| Camera bump height | — | ? | not needed: the cutout is a through-hole |

Orientation is fixed by the requirement that power and volume stay reachable —
see [ADR-0004](adr/0004-phone-retention.md). Edge assignments above assume it.

A reusable solid model exists: `../palmtop_mk2/Pixel_3A_XL_Body.stl`.

## Mk2 reference (the device being replaced)

| Property | Value | Conf |
|---|---|---|
| Footprint | 170.0 x 91.4 | M (from STL) |
| Lid phone pocket | Y -38.55 .. +38.55 | M (from STL) |
| Lid wall, button edge | **4.70** | M (from STL) |
| Lid wall, hinge edge | **9.60** | M (from STL) |
| Button window | **54.0 x 10.0**, at X -48.6 .. +5.0 | M (from STL) |
| Camera cutout | 11.2 x 23.2, at X -69.8 .. -58.6, Y -29.2 .. -6.0 | M (from STL) |

Both the button window and the camera cutout transfer to Mk3 by referencing them
to the **phone's own edges** rather than the lid's, since the two lids differ in
depth and in how the phone sits in them. X transfers unchanged, both lids
centring the same phone on X = 0.

**Mk2 biased the phone forward in the lid** — a thin wall where the buttons are,
a thick one on the hinge side — and cut **one window over both buttons** rather
than two holes. Mk3 does the same. Since both lids centre the same phone in X in
the same orientation, Mk2's window span transfers directly and task 0.10 stops
being a blocker.
| Base part height | 23.35 | M (from STL) |
| Lid part height | 18.21 | M (from STL) |
| Closed height, assembled | ~32 | ? |

The two printed parts interleave at the hinge, so the closed height is less than
the sum. **Action: measure the physical Mk2 with calipers** — this is the number
Mk3 is benchmarked against.

## Print material

| Property | Value | Conf |
|---|---|---|
| Material | PETG (as Mk2) | E |
| Density | 1.27 g/cm3 | S |
