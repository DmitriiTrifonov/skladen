# Plan

> **Skladen 2:** written for Mk3 and the Pixel 3a XL. Its numbers are inherited, not re-derived; what the Pocophone F1 changes is in [ADR-0011](adr/0011-phone-swap-pocophone-f1.md).

## Where the project stands

Measurements for the keyboard and phone are in hand, two analyses are written,
and the first decision is made.

Five decisions are made, and the model is now code.

**[ADR-0002](adr/0002-keyboard-integration-depth.md): the keyboard stays sealed.**
Stripping it to its plate — worth an estimated 16.5-18.5 mm closed, but
irreversible on the only unit in hand — is deferred to Mk4. That fixed 9.52 mm of
the stack as untouchable and left exactly two 1.2 mm skins as thickness levers.

**[ADR-0008](adr/0008-base-floor.md): the base keeps a full floor**, for
enclosure and stiffness. **[ADR-0004](adr/0004-phone-retention.md): the lid keeps
a rear wall**, for rear protection — the fingerprint reader it covers will not be
used. Both levers spent. Design point:

```
   rear edge   23.24 mm      front edge   19.26 mm   (22.24 / 18.26 before
                                                    floor tape, ADR-0004)
   (Mk2 is roughly 32 mm, to be confirmed with calipers)
```

A 30% reduction over Mk2 with both components fully enclosed, rather than the 38%
that was available with both exposed. That left 0.26 mm against N1's original hard
limit of 22.5; the limit has since been restated to 24.5 and 1.0 of it spent on
tape behind the phone — see
[requirements.md](requirements.md#n1-needs-restating).

On balance the two decisions nearly cancelled — 26 g added low, 25 g added high —
and the device tips at 127 deg. A **15 mm** rear setback eliminates tipping at any
angle across the whole plausible mass bracket, and
[ADR-0006](adr/0006-rear-edge-io-vs-hinge.md) uses that tail as an I/O shelf. See
[balance.md](analysis/balance.md).

Five ADRs remain open. Four are blocked on measurements rather than preference.

## Phase 0 — close the blocking unknowns

Nothing in CAD should start before these exist. Each unblocks a specific ADR.

| # | Task | Unblocks |
|---|---|---|
| 0.1 | ~~USB-C position~~ done — right side face, 8 mm back from the rear edge. Still needed: the port **opening's width**, and the overmould size of the cable actually used | sizes the opening in the base's right wall |
| 0.4 | Measure the bottom-rim recess depth at 6+ points around the perimeter | ADR-0008 Option E — **the only remaining thickness reduction** |
| 0.5 | Measure the physical Mk2's closed height with calipers | benchmark for N1 |
| ~~0.6~~ | Superseded — Mk2's camera cutout measured off its STL and transferred. It is a through-hole, so the bump height never mattered | — |
| 0.7 | Buy M3 x 16 socket caps (DIN 912), M3 nylon-insert nuts (DIN 985 — the pocket is sized for their 4.00 height, and a plain nut would need a threadlocker nobody can re-apply once the lid is in) and a range of compliant elements — 3 x 1 NBR O-rings, TPU washers — so coupon 2.2 tunes torque by swapping rather than reordering. DIN 137B wave washers are 6.0 OD and do not fit the Ø5.80 head pocket | ADR-0005, ADR-0010 |
| ~~0.8~~ | Superseded — the phone is taped in, as Mk2's was, so there are no retention lips to size | — |
| 0.9 | Check the phone's magnetometer against a loose magnet at ~8 mm | ADR-0009 Option B |
| ~~0.10~~ | Superseded — Mk2's button window measured off its STL and transferred; same phone, same orientation, centred in X in both | — |
| 0.12 | Buy two short USB-C male-to-female extenders (straight and right-angle); caliper their bodies and compare charging current against the bare cable on a power meter | [ADR-0013](adr/0013-usbc-extender.md), sizes the lid's USB-C slot |
| 0.13 | Measure how much of the Pocophone's front glass a retaining lip may overlap, and its edge radius (revives the superseded 0.8) | [ADR-0012](adr/0012-removable-front-bezel.md) |
| ~~0.14~~ | Done 2026-10-17 — the ring is 1.7 g, the variant lid + ring gives 1.151 at 150 deg and **0.997 at 180 deg**; see [ADR-0012](adr/0012-removable-front-bezel.md) | — |
| 0.11 | Look at how Mk2's lid treats its top edge around the buttons — relieved, or continuous | ADR-0004; confirms Mk2's no-accidental-press evidence transfers |


Task 0.4 is back on the critical path. With both skins spent, scenario A-thin — a
0.8 floor ribbed into the keyboard's rim recess, taking 22.24 to 21.84 — is the
only reduction left in Mk3, and the 0.26 mm of margin against the hard limit
makes it worth having. It is also data Mk4 will want.

Checking whether a spare keyboard is purchasable is off the critical path, but
still worth knowing for Mk4.

**Owner decision needed, not a measurement:** what the real thickness ceiling is.
See [requirements.md](requirements.md#n1-needs-restating).

Hinge sourcing used to be the longest item here. It is gone:
[ADR-0005](adr/0005-hinge-mechanism.md) now recommends printed knuckles on
bolted stations with a compliant element setting the friction force, all of it
stock hardware. Purchased torque hinges remain
a defined upgrade path, with a sourcing spec recorded in that ADR.

## Risks

Named explicitly, because the task table above lists unknowns that are cheap to
close and says nothing about the ones that are not.

### ~~R1 — the rear edge may not have room for both the hinge and the USB-C~~

**Gone.** The USB-C is on the keyboard's right side face, not on the rear edge,
so the hinge has all 193 mm of that edge to itself. The stations are symmetric at
±88 and the span between them is 1.5% short of ideal rather than 10.8%.

The risk was real given what was believed at the time, and it was tracked and
mitigated correctly. It was also founded on a misread photograph — see
[ADR-0006](adr/0006-rear-edge-io-vs-hinge.md), which is kept as the record.

### R2 — no thickness margin at all

22.24 against a 22.5 hard limit. If coupon 2.4 shows the base flexes under
typing, the floor goes to 2.0-2.5 and the device becomes 23.0-23.5. Nothing
absorbs that.

Mitigated by [ADR-0008](adr/0008-base-floor.md) Option E (worth 0.4 and
*stiffer* than the floor it replaces) and by restating N1's ceiling — see
[requirements.md](requirements.md#n1-needs-restating).

### R3 — the balance analysis rests on estimated masses

**Partly realised already.** The first parametric model showed the hand estimates
were roughly half of reality — the lid's 18 mm-wide solid side rings had never
been counted. The masses are now a bracket (lid 40-83 g, base 42-72 g) rather
than a guess, and [ADR-0003](adr/0003-lid-balance-strategy.md) went from 11 mm of
setback to 15 to cover the whole of it.

What remains is that the bracket is itself estimated, and `r_lid` and `d_base`
still are too. The keyboard's internal mass distribution is not modelled at all,
and it is 69% of the base mass.

Mitigated by coupon 2.5 (weigh and re-run `cad/params.py`) and by carrying the
ballast pocket as a correction lever.

### R4 — the Mk2 benchmark was never measured

"Roughly 32 mm" is an estimate from a photograph. Every "-30% vs Mk2" claim in
this repo rests on it. Task 0.5 fixes it for the price of picking up calipers.

### R6 — knuckle print orientation conflicts with printing the base as one part

A 197 x 105 base realistically prints floor-down, which puts the hinge knuckles'
layer lines across the bending load they carry — the weak direction, and the only
direction the lid's weight acts in. [ADR-0005](adr/0005-hinge-mechanism.md)
Option G (separate bolted knuckle blocks) is the way out, at the cost of parts
and of play accumulating across two bolted interfaces.

Mitigated by printing the knuckle section both ways in coupon 2.2 and loading
both to failure.

### R7 — a removable bezel spends mass the balance does not have

Proposed in [ADR-0012](adr/0012-removable-front-bezel.md). Thickness can be held at
24.29 by letting the lip replace the tape's 1.0 mm, but the ring sits high in the lid
and the 180 deg margin was 1.002. Task 0.14 is done: modelled, the ring is only 1.7 g,
but with the tape gap gone the lid's ends are heavier and the margin lands at **0.997**.
The remedy is lightening the lid's end blocks or a steel strip under the base, not a
thinner lip. Open until the owner chooses.

### R5 — single-point measurements

Keycap protrusion (1.82) and the bottom-rim recess (<1 mm) were each measured at
one point and are used as if uniform. Tasks 0.3 and 0.4.

## Unassigned detail problems

Real work with no owner and no ADR. None blocks the cross-section, but all of
them have to exist before Phase 3.

| Problem | Note |
|---|---|
| Local gussets under the hinge stations | The base's rear pocket wall is 12.54 tall at 1.6 thick and takes point loads ([ADR-0005](adr/0005-hinge-mechanism.md)) |
| Where the opening grip goes | Mk2 had no accidental-press problem with the same layout, so this is a styling choice rather than a fix |
| Felt liner, now optional | No longer sets the keycap gap — the base's rim does. Worth having as screen protection |
| Steel strip under the base, **deferred** | Only buys margin at 180 deg (1.000 on slicer masses; 150 deg is 1.154). About 100 x 12 x 0.8 mm (7.5 g) taped between the front feet, as far forward as it goes, and thinner than the bumpons stand proud (their height minus the 0.4 recess). Gives ~1.06 at 180 deg. Take it up if the lid is ever used laid flat back, or if the printed lid comes out heavier than 62 g with its frame — see [ADR-0012](adr/0012-removable-front-bezel.md) |
| Lid lightening, **deferred** | The other way to buy margin at 180 deg. Lid + frame must print at 62.3 g or less; they are 62.4 g (56.02 + 6.35). Each gram off adds ~0.3% there: -3 g gives 1.009. Candidates: lower sparse infill, fewer wall loops in the hollow ends, a thinner outer wall than 1.6. Costs nothing in CAD |
| Steel in the base instead of under it, **deferred** | A 100 x 12 x 0.5-0.6 mm plate (4.7-5.7 g, ~+4% at 180 deg) between the keyboard and the floor. Free in height only two ways: in the keyboard's bottom rim recess (depth unmeasured, < 1.0, needs >= 0.7; it is also where [ADR-0008](adr/0008-base-floor.md) Option E lives, so it is one or the other), or in a 0.6 pocket in the floor's top face, flush (a CAD change to the base; leaves 0.6 of plastic under it). Raw, under the keyboard, it adds its thickness to the closed height and to the walls. Keep it clear of the keyboard's board: steel can detune the Bluetooth antenna, and where that is is not known |
| Styling of the exposed tail | [clamshell-geometry.md](analysis/clamshell-geometry.md) makes it an exterior surface; better decided than discovered |

## Phase 1 — decide

Close [ADR-0007](adr/0007-cad-toolchain.md) immediately; it depends on nothing.

Then resolve **0003, 0005 and 0006 as a single rear-edge cross-section drawing**,
not as three separate decisions. They share the same 10 mm of depth and the same
9.5 mm of height: the hinge, the setback tail and the keyboard's switch, LEDs and
USB-C all have to coexist in that section.

[ADR-0004](adr/0004-phone-retention.md) can close in parallel, after coupon 1.3.

## Phase 2 — coupons before the whole thing

Small test prints, each answering one question.

| # | Coupon | Question it answers |
|---|---|---|
| 2.1 | Rear-edge cross-section, 40 mm wide, both halves | Does hinge + setback + I/O access actually fit in the section, and does the lid open? **Do this one first** (R1) |
| 2.2 | Printed two-station knuckle section with M3 bolts and compliant washers | What torque does it actually produce, measured with a spring scale? Is it adjustable by feel? How much is lost over 100 cycles? Does it rack? |
| 2.3 | Lid pocket corner, full thickness | Does the phone seat and stay in? Does the camera cutout clear the bump? Can the phone be pushed back out? |
| 2.4 | Base pocket, full 193 x 86 footprint but short, printed at both 1.2 and 0.8+ribs | Does the keyboard seat and stay in? Does the floor flex under typing? Is the 0.8 ribbed floor sound (scenario A-thin)? |
| 2.3b | Lid right-end coupon with the retaining ring and the USB-C slot, phone and adapter in place (extends the phone-fit coupon in `export/coupon-phone/`) | Does the lip hold the phone without touching the keycaps? Do snap tabs survive 50 cycles? Does a real cable plug into the adapter with the lid shut? |
| 2.5 | Weigh 2.3 and 2.4, extrapolate to full shells | Replaces the `E`-confidence masses in the balance analysis (R3) |

Re-run the balance numbers after 2.5. If they move materially, revisit ADR-0003
before Phase 3 rather than after.

## Phase 3 — v1

Full base and lid, assembled with the real keyboard and phone. Expect this to be
wrong in at least two places; the point is to find out which two.

## Phase 4 — validate

Against the acceptance criteria in [requirements.md](requirements.md). The ones
that will actually bite:

- Closed thickness against whatever N1's restated ceiling turns out to be
- Tip test at maximum opening angle with a firm tap on the top of the screen
- 50 open/close cycles, then re-check that the lid still holds 120 deg
- Keyboard removable without cutting anything — Mk4 depends on it
- Phone temperature under sustained use, with its back fully enclosed

## Phase 5 — publish

Mk2 was published on MakerWorld (`../palmtop_mk2/maker_world/`). Same for Mk3:
STL + STEP + photos, and a link back to this repo for the reasoning.

## Critical path

```
0.1 I/O positions    --> ADR-0006 --+--> 2.1 rear cross-section --> Phase 3
                         ADR-0003 --+
                         ADR-0005 --+ (2.2 validates, does not block)
0.4 rim recess depth --> ADR-0008 opt E --> 2.4 base floor --> Phase 3
```

**Nothing on this path has a lead time any more.** Task 0.1 is now the only thing
blocking the rear-edge cross-section, and it is a caliper and ten minutes. Task
0.4 is the same, and it gates the only millimetres left in the budget. Both
should happen next.
