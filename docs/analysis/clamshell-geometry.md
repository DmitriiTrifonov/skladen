# Clamshell geometry — why the lid is shallower than the base

> **Skladen 2:** written for Mk3 and the Pixel 3a XL. Its numbers are inherited, not re-derived; what the Pocophone F1 changes is in [ADR-0011](../adr/0011-phone-swap-pocophone-f1.md).

[ADR-0005](../adr/0005-hinge-mechanism.md) notes in passing that an inboard hinge
axis "costs opening angle". This document works that out, because the answer
changes what the closed device looks like and it is not recorded anywhere else.

## The parting plane

At the rear edge, the base stacks:

```
  base floor      1.20
  keyboard shell  9.52
  keycaps         1.82
  ----------------------
  parting plane  12.54 mm above the desk
```

The lid occupies 12.54 to 22.24. The hinge axis sits on or near that plane, and
per [ADR-0003](../adr/0003-lid-balance-strategy.md) it is **15 mm forward of the
base's rear edge** — the tail behind it being the setback that eliminates
backward tipping and, per
[ADR-0006](../adr/0006-rear-edge-io-vs-hinge.md), carries the keyboard's I/O.

## The problem

If the lid has the same footprint as the base, then **15 mm of lid hangs behind
the hinge axis**. Opening the lid swings that overhang downward and rearward,
into the space the tail occupies.

The interference is not marginal. With the axis exactly on the parting plane, the
lid's rear-bottom corner starts at the parting plane, 15 mm behind the axis —
that is, resting on the top of the tail. Any rotation at all drives it into the
tail. **A flush lid does not open.**

Raising the axis does not help: the corner then starts below the axis and still
sweeps downward from there.

## Options

### A — lid shallower than the base, tail exposed (chosen)

```
  lid    197 x 90     ends at the hinge axis
  base   197 x 105    including the 15 mm tail
```

The tail is uncovered even when the device is shut, exactly as the hinge region
of a laptop is.

At 180 deg the lid folds flat onto the tail, because the tail's top surface *is*
the axis height. So the full opening range that
[balance.md](balance.md) analyses is geometrically available.

| Pros | Cons |
|---|---|
| Nothing to design; the constraint simply sets the lid's depth | The closed device is not a clean rectangle — there is a 15 mm step at the rear |
| Full 0-180 deg range available | The tail's top surface is visible and must be finished, not treated as an internal face |
| Tail stays accessible for I/O at every angle, which ADR-0006 wants anyway | Debris can settle on the exposed tail |

### B — flush lid, tail top scalloped for clearance

Carve a cylindrical relief into the top of the tail, centred on the axis, so the
lid's overhang has somewhere to sweep.

**Not viable here.** The relief radius would have to be ~15 mm, and the tail is
15 mm deep by 12.54 mm tall — the scallop would consume the entire tail
cross-section and more, destroying the I/O shelf that the tail exists to provide.

### C — outboard axis, barrel outside the body

Mk2's approach: the barrel wraps around the outside of the parting line, so
nothing of the lid sits behind the axis.

| Pros | Cons |
|---|---|
| Flush lid, clean rectangle when closed | The barrel adds directly to the closed height at the thickest edge — this is the one case where the old claim in ADR-0005 was true |
| Simple to reason about | It is why Mk2 looks the way it does |

## Decision

Option A, by elimination rather than preference. B is geometrically impossible
with a 15 mm tail, and C spends closed height, which is the project's primary
constraint.

## The lid closes at a tilt, not flat

A second consequence of the inboard axis, checked late and fortunately
self-consistent.

The axis is at the rear, 12.54 mm up. The top of the base's front wall is at

```
  base floor      1.20
  keyboard shell  5.54   (front of the wedge)
  keycaps         1.82
  ----------------------
                  8.56 mm
```

A rigid flat lid pivoting about the rear axis therefore drops until its front
edge reaches 8.56, which over the 90.05 mm from axis to front face is a tilt of

```
  atan(3.98 / 90.05) = 2.53 deg
```

— near enough the keyboard's own 2.64 deg wedge. **The lid closes 2.53 deg
nose-down relative to the base floor**, and the closed device is a wedge rather
than a rectangle.

Verified in `cad/massing.py`, which builds both halves from these numbers and
asserts the closed bounding box against the derived stack.

This validates three things the [thickness budget](thickness-budget.md) had been
assuming rather than deriving:

- Rear 22.24 and front 18.26 are the real closed heights, not an idealisation.
- The gap over the keycaps is near-uniform: the lid's inner face and the keycap
  plane differ by 0.11 deg, which is 0.17 mm across 86 mm. A single clearance
  figure in the budget is legitimate.
- The felt liner sees roughly even compression everywhere rather than pinching at
  one end.

And it adds one constraint that was not recorded anywhere:

- **The base's side walls must follow the wedge.** The base's top rim is a sloped
  line from 8.56 at the front to 12.54 at the rear on both sides, not a flat
  edge. It prints without support in the flat orientation, but it has to be drawn
  that way deliberately.
- The hinge's closed stop sits 2.53 deg *past* the plane through the axis.

## The axis cannot sit on the parting plane either

Everything above assumed the hinge axis lies on the parting plane at 12.54. When
the geometry was actually built and swept through its opening range, that turned
out to be wrong twice over. Both failures were found by `cad/build.py`'s opening
sweep, which rotates the lid through 0-180 deg and measures the interference
volume against the base. Neither was visible from the closed position.

### First failure — the lid's rear-top corner

With the axis on the parting plane, the lid's rear face runs from 12.84 up to
22.24, so its **top** corner is 9.7 mm from the axis. Rotating open, that corner
sweeps down and back into the tail. The sweep showed 380 mm3 of interference at
90 deg growing to 15,000 mm3 at 180 deg.

The fix is the one every laptop uses: **put the axis at the lid's mid-thickness**
and round the lid's rear edge to that radius. The furthest corner is then only
half the lid's thickness away.

```
  axis z            = (12.84 + 22.24) / 2 = 17.54
  lid rear radius   = (22.24 - 12.84) / 2 =  4.70
  swept cylinder    = 12.84 .. 22.24
  tail top          = 12.54          -> clears by 0.30
```

The lid's rear edge is therefore a half-cylinder of radius 4.70 centred on the
axis, not a flat face.

### Second failure — nothing may stand behind the axis

A subtler constraint, and the one that actually shaped the hinge.

At 180 deg the lid lies flat behind the device, and its underside behind the axis
sits at `axis - lid_rear_radius` = **12.84**. So **no base material may rise
above 12.84 anywhere behind the axis** — which is exactly where the knuckle posts
have to be, since the knuckles are centred at 17.54 and the tail top is 12.54.

The only exception is inside the lid's relief at each station, where the lid has
no material at any angle. So the posts must reach the knuckles from **directly
underneath the axis**, through that relief — and the relief has to be larger than
the lid's own rear radius for the connection to have any thickness:

```
  station relief radius  5.70   (vs the lid's own rear radius 4.70)
  relief's lowest point  17.54 - 5.70 = 11.84
  tail top               12.54          -> 0.70 of overlap to build a post in
```

With the relief at 4.90 the overlap was 0.10 mm, which is not a connection. At
5.70 the post is a real one. The price is that the lid is cut through locally at
each station, leaving its own knuckle joined to the lid body across the station's
centre 5.8 mm only — which is simply how an interleaved hinge works.

### Verified, not asserted

```
opening    0   30   60   90  120  150  180 deg
clash      0    0    0    0    0    0    0  mm3
```

## The lid lands on the rim, not on the keys

Caught late, while working out how the keyboard is retained.

The budget puts a 0.30 gap between the keycap tops and the lid, originally as a
felt liner. But if the base's walls stop at the keycap plane, the lid's underside
rests on *the keycaps* — through the felt, which compresses. Pressing a closed
lid then presses keys. A key needs about 50 g; a hand on a closed lid is much
more than that.

Every laptop solves this the same way and so does Mk3: **the base's walls stand
`keycap_gap` proud of the keycap plane**, so the lid lands on the rim and the
keys hang clear underneath. Load on a closed lid goes into the walls.

```
  keycap plane (rear)   12.54
  rim, where the lid lands   12.84      <- walls raised by keycap_gap
  tail top                   12.54      <- NOT raised, see below
```

**The tail does not rise with the walls.** Its 0.30 of clearance under the lid's
swept cylinder at 180 deg is exactly the same 0.30; raising it would close that
gap and the lid would hit it. So the base's top edge steps down by 0.30 at the
hinge line — walls at 12.84 forward of it, tail at 12.54 behind.

Closed height is unchanged: the lid's underside was already at 12.84. Only what
it rests on changed.

## Consequences

- **Lid footprint is 197 x 90; base footprint is 197 x 105.** Neither number was
  written down before.
- The closed device has a 15 mm step at the rear. This is a visual consequence
  worth deciding deliberately rather than discovering in the first print — the
  tail can be chamfered, radiused or styled as a deliberate feature.
- The tail's top face is an exterior surface. Print orientation and finish matter
  there.
- [balance.md](balance.md) already assumed a 90-deep lid when it set
  `r_lid` = 45 mm ("phone centred in a 90-deep lid"). That assumption is now
  justified rather than incidental. No numbers change.
- **The axis is at 17.54, the lid's mid-thickness, not on the parting plane.**
  See above; this was forced by the opening sweep.
- The phone is 76.1 deep in a 90-deep lid, leaving ~7 mm of bezel front and rear.
  Retention lip depth has to come out of that — see task 0.8.
