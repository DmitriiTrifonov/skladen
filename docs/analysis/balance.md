# Balance analysis — will the lid tip the device over backwards?

> **Skladen 2:** written for Mk3 and the Pixel 3a XL. Its numbers are inherited, not re-derived; what the Pocophone F1 changes is in [ADR-0011](../adr/0011-phone-swap-pocophone-f1.md).

The concern: the phone (167 g) is heavier than the keyboard (95 g), so the mass
is in the lid, and a clamshell with a heavy lid falls over backwards when opened.

Short answer: **bare, it tips past 127 deg of opening. A 15 mm rear setback makes
tipping impossible across the whole plausible mass bracket, at any angle.**

Both accepted construction decisions moved this number, in opposite directions.
[ADR-0008](../adr/0008-base-floor.md) kept the base floor, adding 26 g to the
base and helping. [ADR-0004](../adr/0004-phone-retention.md) kept the lid's rear
wall, adding 25 g to the lid and hurting slightly more. The net is close to where
it started, and the fix is still free.

## Model

Tipping is a moment balance about the rear ground contact line.

| Symbol | Meaning |
|---|---|
| `M_lid` | mass of lid assembly (phone + lid shell) |
| `M_base` | mass of base assembly (keyboard + base shell) |
| `r_lid` | distance from hinge axis to lid centre of mass, along the lid |
| `d_base` | distance from hinge axis forward to base centre of mass |
| `s` | rear setback: how far the base footprint extends *behind* the hinge axis |
| `theta` | lid lean measured **from vertical**; opening angle = 90 + theta |

Stable while:

```
M_base * (d_base + s)  >=  M_lid * (r_lid * sin(theta) - s)
```

which rearranges to:

```
M_base * d_base  +  s * (M_base + M_lid)  >=  M_lid * r_lid * sin(theta)
```

## Inputs

Footprint assumed 197 (X) x 90 (Y), hinge on the rear edge. Shell masses are
estimated from PETG at 1.27 g/cm3 over the modelled wall thicknesses — these are
the weakest numbers here and must be replaced by weighing the first prints.

| Quantity | Value | Conf |
|---|---|---|
| Phone | 167 g | S |
| Keyboard | 95 g | M |
| Lid shell, closed back | 40 - 83 g | E | see below |
| Base shell, with floor | 42 - 72 g | E | see below |
| `r_lid` | 45 mm (phone centred in a 90-deep lid) | E |
| `d_base` | 41 mm (keyboard mass is rear-biased by battery + wedge) | E |

Three cases, matching the thickness scenarios:

| Case | Construction | `M_lid` | `M_base` |
|---|---|---|---|
| **A** | **floored base, closed-back lid (selected)** | **207 g** | **137 g** |
| B | floored base, frame lid (rejected) | 182 g | 137 g |
| B+ | frame base, frame lid (rejected) | 182 g | 111 g |

## Two corrections to the shell masses

### First: they were estimated far too low



The first run of the parametric model measured the modelled solids and produced
shell masses roughly **twice** the hand estimates this analysis was built on.

The error was in the lid. It was estimated as a thin frame, but the lid is
196.8 wide and the phone only 160.1, so **18 mm of solid material runs down each
side, 8.2 mm thick** — a substantial ring of plastic that the frame model simply
did not count. Same again, smaller, front and rear.

That gives a bracket rather than a guess:

| | Lower bound | Upper bound |
|---|---|---|
| | original hand estimate | massing model, fully solid |
| Lid shell | 40 g | 83 g |
| Base shell | 42 g | 72 g |

The real part sits between, depending on how much of that dead side material gets
hollowed out. Working values of 60 g and 55 g are used below.

**What matters is the ratio, not the absolute masses.** Both halves growing
together barely moves the result; the lid growing while the base does not is what
breaks it.

### Second: those measured masses assume 100% infill

`volume * density` is the solid upper bound, not what comes off a printer. Thin
walls (1.2-1.6 mm) do print essentially solid, but the chunky parts — the lid's
18 mm side spacers, the 15 mm tail — take infill and land near 40%.

Treating solid mass as printed mass had two consequences, both now corrected:

- It produced a spurious **"over the mass budget"** finding. The assembly is
  ~432 g solid but ~374 g as printed, against N4's 400 g. **No lightening work is
  needed**, and a proposal to hollow the lid has been withdrawn.
- It made the tipping margins look better than they are, since the phone and
  keyboard are fixed while only the shells shrink. `cad/build.py` now reports
  both and fails if either tips.

```
                     solid    printed(est)
  lid shell           82.7        52.1 g
  base shell          87.0        60.0 g
  assembly           431.7       374.1 g     N4 budget 400

  margin @150 deg     1.351       1.322
  margin @180 deg     1.170       1.145
```

The printed figures are an estimate. The authoritative number is whatever the
slicer reports, and after that, a scale.

## Sensitivity sweep

Margin is restoring moment over overturning moment; `>= 1.0` means it cannot tip
at that angle. Reproduce with `.venv/bin/python cad/params.py`.

At the decided `s` = 15 mm:

```
  lid  base   @180   @150  s_req   case
   40    42  1.157   1.34   10.8   both light
   83    72  1.165   1.34   10.6   both solid
   60    55  1.156   1.33   10.8   working values
   83    42  1.015   1.17   14.6   heavy lid, light base  <-- worst
   40    72  1.337   1.54    6.6   light lid, heavy base
```

The same sweep at 11 mm put the worst case at 0.878 — tipping at 160 deg — which
is what moved the decision.

Three readings:

1. **At 150 deg — a realistic maximum — every case is comfortable**, by 33% in
   the expected case and 17% in the worst.
2. **At 180 deg every case still clears**, the worst by 1.5%. At 11 mm the worst
   case failed outright, which is the whole reason for the extra 4 mm.
3. **The worst case needs 14.6 mm of setback**, not 11. This is what drove
   ADR-0003 to 15 mm; the sweep below is at the decided value.

There is also a design rule in here, and it runs against the instinct to treat
the two halves alike: **hollow the lid, leave the base solid.** Dead material in
the lid is the single worst place for mass in this device; the same material in
the base is free ballast.

## Result 1 — do nothing (hinge on the rear edge, `s = 0`)

```
sin(theta_tip) = M_base * d_base / (M_lid * r_lid)
```

| Case | `sin(theta)` | `theta_tip` | Tips at opening angle |
|---|---|---|---|
| **A** | 5617 / 9315 = 0.603 | 37.1 deg | **127 deg** |
| B | 5617 / 8190 = 0.686 | 43.3 deg | 133 deg |
| B+ | 4551 / 8190 = 0.556 | 33.8 deg | 124 deg |

The selected construction is already usable past normal laptop angles
(100-120 deg) with no mitigation at all. What it lacks is margin — this is the
*static* threshold, with nothing allowed for tapping the screen, knocking the
desk, or lap use.

## Result 2 — rear setback

Design target: stable to 150 deg opening (`theta = 60`, `sin = 0.866`).

```
s >= (M_lid * r_lid * sin(theta) - M_base * d_base) / (M_base + M_lid)
```

| Case | `s` for 150 deg | `s` for 135 deg | `s` to never tip |
|---|---|---|---|
| **A** | **7.1 mm** | **2.8 mm** | **10.8 mm** |
| B | 4.6 mm | 0.9 mm | 8.1 mm |
| B+ | 8.7 mm | 4.2 mm | 12.6 mm |

The last column solves for the restoring moment exceeding the largest overturning
moment the lid can produce at any angle (`theta = 90 deg`, lid flat back at
180 deg):

```
s_never = (M_lid * r_lid - M_base * d_base) / (M_base + M_lid)
        = (9315 - 5617) / 344  =  10.75 mm
```

[ADR-0006](../adr/0006-rear-edge-io-vs-hinge.md) independently wants **10 mm** of
setback as a shelf for the keyboard's rear-edge I/O, which is very nearly there.
At `s = 10` exactly:

```
restoring  = 5617 + 10 * 344 = 9057
max overturning = 207 * 45   = 9315
sin(theta_tip)  = 9057 / 9315 = 0.9723  ->  76.5 deg  ->  tips at 166.5 deg
```

So 10 mm gives stability to 166 deg, which is past any plausible use, and
**15 mm** eliminates tipping across the entire mass bracket, which is what
[ADR-0003](../adr/0003-lid-balance-strategy.md) decided. The extra millimetres
are free in mass and thickness and cost only footprint depth.

Treat "cannot tip" as a margin statement, not a guarantee: it holds only to the
extent the estimated masses and CoM positions hold, and it says nothing about
being knocked sideways or used on a lap.

## Result 3 — counterweight

Ballast in the front lip of the base, arm ~82 mm forward of the hinge:

```
m = (M_lid * r_lid * sin(theta) - M_base * d_base) / arm
```

| Case | Mass for 150 deg | for 135 deg | to never tip, at `s = 10` |
|---|---|---|---|
| **A** | **30 g** | **12 g** | **3.1 g** |
| B | 18 g | 4 g | 0 g |
| B+ | 31 g | 15 g | 21 g |

If the setback stays at 10 rather than going to 11, about **3 g** in the ballast
pocket closes the same gap — a steel strip of roughly 190 x 3 x 1.5 mm, or
frankly a couple of coins.

Either way the pocket is retained, empty, as insurance: every mass in the tables
above is an `E` estimate, and the pocket is the only lever that still works after
the geometry is cut. It sits in the front of the wedge, where the closed stack is
18.3 against the governing 22.2, so it costs no closed height. Brass (8.5) or
tungsten (19.3) shrink any given mass further.

## Result 4 — limit the opening angle

A hard stop at 120 deg makes the problem vanish at zero cost, at the price of
never reclining the screen. The honest answer if the 10 mm of footprint turns out
to matter.

## Recommendation

**15 mm rear setback**, decided in
[ADR-0003](../adr/0003-lid-balance-strategy.md). At 15 every case in the bracket
clears 1.0 even at 180 deg, the worst at 1.015 and the expected at 1.156; at a
realistic 150 deg the worst is 1.17.

The ballast pocket stays, empty. No case in the bracket needs it, which is
exactly why it is worth having — the bracket is itself an estimate.

## Reproducing these numbers

```
theta_tip = asin( (M_base*d_base + s*(M_base+M_lid)) / (M_lid*r_lid) )
opening   = 90 + theta_tip
```

Measure `r_lid` and `d_base` by balancing each assembly on a knife edge rather
than trusting a CAD centroid — the keyboard's internal mass distribution is not
modelled, and it is 69% of the base mass.

## Second-order effects not modelled

- **Hinge torque.** Holding the closed-back lid at 90 deg needs
  `0.207 kg * 9.81 * 0.045 m` = **0.091 N*m**, about 0.93 kgf*cm. This is below
  the bottom of the commercial torque-hinge range — Reell's scaled-down RT-50
  series for consumer electronics *starts* at 0.11 N*m — which is why
  [ADR-0005](../adr/0005-hinge-mechanism.md) recommends printed knuckles on
  bolted stations rather than a purchased hinge.
- **Forward tipping while typing.** Key force is downward and the base CoM is
  well inside the footprint. Not a risk.
- **Lap use.** No flat contact line; none of the above applies. If lap use
  matters, the opening-angle limit is the only reliable answer.
