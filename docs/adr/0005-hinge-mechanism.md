# ADR-0005: Hinge mechanism

> **Skladen 2:** written for Mk3 and the Pixel 3a XL. Its numbers are inherited, not re-derived; what the Pocophone F1 changes is in [ADR-0011](0011-phone-swap-pocophone-f1.md).

- **Status:** Proposed
- **Date:** 2026-09-20
- **Decides:** F3, F8; sets the rear-edge geometry that ADR-0003 and ADR-0006
  both depend on

## Context

The hinge must hold the lid at any angle hands-free (F3). From
[balance.md](../analysis/balance.md), the torque needed at 90 deg is

```
M_lid * g * r_lid  =  0.207 kg * 9.81 * 0.045 m  =  0.091 N*m  =  0.93 kgf*cm
```

**That is a very small number, and it is the single most important fact in this
ADR.** For calibration: Reell's RT-50 is a deliberately scaled-down 5 mm series
marketed for consumer electronics and mobile devices, and its range *starts* at
0.11 N*m — the smallest industrial hinge built for this class of application
already exceeds what this entire device needs. Mk3 sits below the bottom of the
commercial range.

The hinge sits on the rear edge, which per
[ADR-0006](0006-rear-edge-io-vs-hinge.md) also carries the keyboard's switch,
LEDs and USB-C, and per [ADR-0003](0003-lid-balance-strategy.md) its axis is
~15 mm forward of the base's rear edge rather than at the corner.

Mk2 used a printed barrel with a rod. On the side photo that barrel protrudes
beyond the body outline.

### Where the axis sits

Not on the parting plane, as earlier drafts assumed, but at the **lid's
mid-thickness, z = 17.54**. Two independent collisions forced this, both found by
building the geometry and sweeping it through its opening range rather than by
reasoning about the closed position. They are worked out in
[clamshell-geometry.md](../analysis/clamshell-geometry.md); the consequences for
this ADR are:

- Knuckle OD is capped by the lid's thickness at the axis, not by load. **9.0 mm**
  fits inside 12.84-22.24 with margin.
- The base's knuckles are **posts rising out of the tail**, not bosses on the
  parting plane, and they must approach the axis from directly underneath.
  Nothing may stand behind the axis above 12.84, or the lid hits it at 180 deg.
- Each station needs a **relief in the lid of radius 5.70** — larger than the
  lid's own rear radius of 4.70 — or the post has no cross-section to exist in.

### A correction to an earlier claim

Earlier drafts of this ADR asserted that a printed barrel's diameter "adds
directly to the closed height at the thickest edge". That is true only of an
**outboard** barrel wrapped around the outside of the parting line — which is how
Mk2 did it, and why it looks the way it does.

An **inboard** axis sitting on the parting plane costs nothing. The parting plane
here is at floor 1.2 + keyboard 9.52 + keycaps 1.82 = **12.54 mm**, inside a
22.24 mm envelope, so even a 10 mm barrel centred there fits with room above and
below. What an inboard axis costs instead is opening angle — the two bodies
collide sooner — which is a geometry problem, not a thickness penalty. It is
worked out in [clamshell-geometry.md](../analysis/clamshell-geometry.md), and the
answer is that the lid ends at the axis rather than overhanging it. The rest of
this ADR assumes the corrected version.

## Options

### Option A — printed knuckles, bolted stations, elastomer sets the force (recommended)

Three or four discrete hinge stations spread across the 193 mm rear edge.
Interleaved knuckles printed into both halves, each station closed by an M3 bolt
and nut. Friction is **axial**: the bolt squeezes the knuckle end faces together.
A compliant element in each stack — an O-ring, a TPU washer or a wave washer —
carries the clamp load.

#### The governing principle

**The bolt sets deflection; the elastomer sets force.**

A bolt clamping rigid PETG against rigid PETG sets force by tightening torque,
which cannot be judged by feel at this scale and which the plastic then sheds by
creeping. A bolt compressing an elastomer sets force by *how far it is
compressed*, which is repeatable ("half a turn"), tunable after assembly, and
survives creep — the plastic's relaxation consumes a small fraction of the
elastomer's travel instead of all of the clamp load.

This is why the reference designs carry a soft core rather than relying on the
fit itself.

#### The torque is not close to being a constraint

Friction on an annular knuckle face of Ø14 outer / Ø3.5 inner has an effective
radius

```
r_eff = (2/3) * (r_o^3 - r_i^3) / (r_o^2 - r_i^2) = 4.9 mm
```

With PETG on PETG (`mu` ~ 0.35), three stations contributing two sliding
interfaces each:

```
N = 0.091 / (6 * 0.35 * 0.0049) = 8.8 N of axial force per station
```

(That `r_eff` was computed for a 14 mm knuckle. At the 9.0 mm the packaging
actually allows, `r_eff` is 2.7 and the clamp becomes 16 N per station — still
barely finger-tight, and still far below what the elastomer can deliver.)

**8.8 N on an M3 bolt is barely finger-tight.** As with every other load in this
project, the requirement sits far below what the mechanism can deliver. The
design problem is making the friction *low and repeatable*, not high — which is
exactly what the compliant element is for.

The radial alternative — O-rings gripping a full-width rod — was evaluated and
reaches the same conclusion by a different route: at a Ø8 rod and 80 mm of total
sleeve length the contact pressure works out to 0.019 MPa, roughly 2% of an
O-ring's ordinary sealing duty, or about 26x headroom. Either mechanism works.
The bolted version is preferred for the reasons below.

| Pros | Cons |
|---|---|
| Torque requirement met with enormous margin by either mechanism | Actual torque unknown until a coupon is printed and measured |
| **Adjustable with a screwdriver after assembly** — the single best property here, and one no purchased hinge has | Adds bolts, nuts and compliant washers to the BOM |
| Compliant element makes the setting survive PETG creep | The wear mode is real, just slow; patent literature calls out the lack of wear compensation as the classic weakness |
| Friction elements are consumables: a worn washer costs pennies | Several stations must be co-linear, though far less precisely than a rod demands |
| **Zero lead time** — unblocks the rear-edge cross-section immediately | |
| Discrete stations leave gaps between them for ADR-0006's port tunnels | |
| Tolerant of print warp — see below | |

#### Why stations rather than one full-width rod

An earlier draft of this ADR specified a single steel rod through a continuous
full-width barrel, on the argument that continuity resists racking on a 197 mm
lid. Two things were wrong with it.

**Racking resistance comes from the span between the outermost engagement points,
not from continuity.** Three or four stations spread across 193 mm resist racking
nearly as well as a continuous barrel, and far better than two purchased pods
clustered at the ends.

**A 193 mm continuous knuckle array is a manufacturing problem.** It requires
both printed parts to be straight and co-axial to a fraction of a millimetre over
193 mm. A PETG part that size will bow — 0.3-0.5 mm is realistic — leaving a
choice between a rod that binds and clearance that is slop. Discrete stations
self-align individually and are indifferent to bow between them.

A full-width rod remains the fallback if coupon 2.2 shows unacceptable racking.

### Option B — purchased mini torque hinges (upgrade path)

Two small friction hinges pocketed into base and lid, fixed with screws into
heat-set inserts.

| Pros | Cons |
|---|---|
| Known, specified torque and cycle life | **Longest lead time on the critical path**; blocks the cross-section until in hand |
| Thin leaves, typically 1-2 mm | Pods only — much weaker against racking on a 197 mm lid |
| Torque does not fade the way an interference fit does | Pocket geometry is dictated by whatever part actually arrives |
| No consumables | Metal in thin printed walls concentrates stress at pocket corners |
| | Two pockets must align precisely or the lid racks |

Sourcing spec, if this route is taken:

| Filter | Value |
|---|---|
| Torque, **total across all hinges** | 1-2 kgf*cm (0.10-0.20 N*m) |
| Count | 2, for anti-racking rather than for torque |
| Leaf thickness | <= 1.5 mm |
| Barrel diameter | <= 6 mm |
| Range | 0-180 deg |

Search terms: *torque hinge*, *friction hinge*, *position control hinge*. In
Russian, *петля с трением* / *фрикционная петля*.

Avoid: "soft close" and "damping" hinges (one-way dampers, they do not hold
position), spring-loaded or self-closing types, furniture hinges, and any listing
that does not state a torque figure. **Do not over-specify** — the common
"2 pcs, 3 kgf*cm" listing is six times the requirement; it will be stiff to open
and the moment will pull heat-set inserts out of PETG.

Salvaging hinges from a dead laptop screen is the same part for free, at the cost
of a chassis-specific leaf shape.

### Option C — printed barrel with an interference fit only (Mk2's approach)

| Pros | Cons |
|---|---|
| No purchased parts beyond the rod; proven to work on Mk2 | Friction comes from PETG pressed against PETG, which creeps under sustained load and goes loose |
| Full-width barrel is very stiff | No way to re-tension without reprinting |
| | This is the failure mode Option A exists to avoid |

### Option D — printed pods at the ends

Option A or C, but as two short barrels, leaving the middle of the rear edge
clear.

| Pros | Cons |
|---|---|
| Frees the rear centre, if ADR-0006 needs it | Short barrels are much weaker against racking |
| | Option A's full-width barrel solves ADR-0006 a better way — see below |

### Option G — Option A, but with the knuckles as separate bolted parts

The knuckle blocks are printed as their own small parts and bolted to the base
and lid, rather than being printed integral with them.

This exists because of a conflict inside Option A that has no solution while the
knuckles are integral. The base is 197 x 105 and realistically prints floor-down;
any other orientation puts overhangs everywhere. But printed floor-down, the
knuckles rise from the rear rim with their bores horizontal, which means **the
layer lines run across the bending load the knuckles carry.** That is the weak
direction, and it is the one direction the lid's whole weight acts in.

| Pros | Cons |
|---|---|
| Each knuckle block prints in its own optimal orientation, with layers along the load rather than across it | More parts, more fasteners, more assembly |
| The hinge becomes replaceable and re-positionable without reprinting a 197 mm part | Two bolted interfaces per station instead of one — more places for play to accumulate |
| Bores print vertically, so no teardrop compensation and no support | Blocks must locate precisely against each other or the lid racks; needs dowels or a keyed seat |
| Lets the knuckle be a denser, more solid part than a shell wall can be | Adds height at the interface unless the blocks seat into pockets |
| A damaged knuckle is a small reprint, not a scrapped base | |

### Option E — flexure / living hinge

| Pros | Cons |
|---|---|
| Thinnest possible | No position holding at all; fails F3 outright |
| No moving parts | Poor fatigue life in PETG |

### Option F — magnetic mount with discrete angle slots

| Pros | Cons |
|---|---|
| Thin, simple, no friction to wear | Not a clamshell; the lid becomes a losable separate object |
| The slot sets the angle, which helps ADR-0003 | Discrete angles only |

## Decision

Not yet made. **Option A is the recommendation**, with Option B as a defined
upgrade path rather than a fallback.

Three reasons, in ascending order of weight:

1. **The torque requirement is trivially met.** 26x headroom on a first-pass
   calculation is not a close call, and the low working stress puts the elastomer
   in the regime where it degrades slowest.
2. **It can be spread across the full width.** A 197 mm lid on two small pods
   clustered at the ends will rack. Three or four stations spanning 193 mm will
   not — and unlike a continuous barrel, they tolerate the bow a PETG part that
   size will have.
3. **It has no lead time.** Hinge sourcing is currently the longest item on the
   critical path and it blocks the rear-edge cross-section, which is where three
   open ADRs converge. Option A unblocks all of it today.

Whether the knuckles are integral or separate bolted blocks (Option G) is a
sub-decision inside this one, and it turns on print orientation rather than on
mechanics. Coupon 2.2 should print the knuckle section both ways and load it to
failure; the answer is whichever survives.

This reverses an earlier recommendation in favour of purchased hinges. That
recommendation rested on "printed friction degrades", which is a fair objection
to Option C and not to Option A — the mechanism is different, and the numbers
were never checked.

### What closes this ADR

Coupon 2.2: a printed two-station knuckle section with bolts and compliant
washers, torque measured with a spring scale at a known radius, then 100
open/close cycles and measured again. Print the knuckles both integral and as
separate blocks (Option G) and load both to failure, since the choice between
them is a print-orientation question that no amount of reasoning settles.
Accept Option A if the torque lands between 1x and 3x of 0.091 N*m and loses less
than 30% over the cycles. Otherwise fall back to Option B.

## Consequences

- **Hinge sourcing comes off the critical path.** M3 bolts, nuts, O-rings and
  wave washers are stock items. [plan.md](../plan.md) is updated accordingly.
- **Station placement is free.** [ADR-0006](0006-rear-edge-io-vs-hinge.md) has
  been rejected — the USB-C is on the keyboard's side face, not the rear edge —
  so nothing competes for that edge. Stations sit at **-88, 0, +88**, chosen
  purely for anti-racking span: 176.0 mm against a 178.6 mm ideal.
- Discrete stations were originally chosen partly to leave gaps for port tunnels.
  That reason evaporated; the print-orientation and warp reasons did not, and
  they are sufficient on their own.
- Station count and spacing are a racking question, not a torque one: place the
  outermost stations as far apart as the rear edge allows, and add a middle one
  for knuckle support rather than for friction.
- **Knuckle print orientation conflicts with printing the base as one part.**
  Floor-down is the only sane orientation for a 197 x 105 base, and it puts the
  knuckle layers across the load. Option G above is the way out; if the knuckles
  stay integral, they need to be thickened to compensate for working across
  layers, and that thickening has to fit inside the 15 mm section.
- **The base's rear pocket wall takes the hinge's point loads.** It is 12.54 mm
  tall at ~1.6 mm thick. The tail braces it from behind, so it is a channel
  rather than a free-standing wall, but local gussets under each station are
  likely needed and should be in the coupon.
- Nuts want capture pockets, not free nuts — a hex pocket in the knuckle, or
  heat-set inserts if the geometry allows. A nut that spins is a hinge that
  cannot be adjusted.
- F8 (stays shut) turns out to be solved by this ADR after all, and is written up
  as [ADR-0009](0009-closure-retention.md): holding the lid shut while inverted
  needs the same 0.091 N*m as holding it at 90 deg, so the torque specified here
  covers it. Coupon 2.2's post-cycle figure therefore decides F8 as well as F3.
- A hard stop for the maximum opening angle is easier as printed geometry in the
  knuckles than as a purchased hinge's own stop. Relevant if
  [ADR-0003](0003-lid-balance-strategy.md) Option C is ever revisited.
- Buy a range of compliant elements at once — O-rings in several cross-sections,
  TPU washers, M3 wave washers — so coupon 2.2 tunes by swapping rather than
  reordering. They are pennies.
- Adjustability is the property to protect through detail design. If the bolt
  heads end up buried where a screwdriver cannot reach once assembled, the main
  advantage of this option is lost.

## Update 2026-10-22: waiting for a print

On the first print the O-ring under the bolt head was crushed or torn: nothing limited how hard the head squeezed it, and a wave washer does not fit (an M3 DIN 137B is 8 mm across). The head pocket now has a groove for the ring and a flat DIN 433 washer that lands on the pocket floor and stops the squeeze at 20 %. It is modelled and checked, **not printed**; this section changes once it has been. See plan item 2.2b and the changelog.
