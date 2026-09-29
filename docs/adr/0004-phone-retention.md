# ADR-0004: How the phone is held in the lid

- **Status:** Accepted
- **Date:** 2026-09-20
- **Decides:** F1, F6, F7; contributes 1.2-1.5 mm to N1 and ~25 g to the
  [balance problem](../analysis/balance.md)

## Context

The lid is ~197 x 90; the phone is 160.1 x 76.1 x 8.2 and sits in it in
landscape, leaving ~18 mm of margin on each side and ~7 mm front and rear.

The phone's camera bump takes the envelope to 9.4 mm over part of the rear face.
Its fingerprint reader is on the rear, upper third — reachable only if the rear
is open. Its USB-C is on a short edge, which in landscape points sideways, so
charging access (F6) is easy in every option here.

This decision is doubly weighted: the lid skin is 1.2 mm of the closed stack
*and* ~25 g of lid mass, and lid mass is the thing that tips the device over. The
lighter option is also the thinner option and the more stable one.

## Options

### Option A — closed pocket (chosen)

A tray with a full rear wall; the phone drops in and is captured by a lip on the
front face. Cutouts for the camera, fingerprint reader and USB-C.

| Pros | Cons |
|---|---|
| Phone's rear is fully protected | +1.2 mm closed height, +25 g lid mass |
| Stiffest lid for the least material, no rib scheme needed | Fingerprint reader is covered — decisive, and the reason this option was previously discounted |
| Cleanest exterior | Heat from the phone has nowhere to go |
| Simple to model and print flat | Tool-free removal needs a deliberate push-out feature |
| Camera bump passes through a cutout; the wall does not thicken | |

### Option B — open bezel frame

A perimeter frame with lips that grip the phone's front face; the phone's own
rear is the outer surface of the closed device.

| Pros | Cons |
|---|---|
| Thinnest and lightest: 0 mm of skin, ~15 g | Zero rear protection — the phone's glass back faces the world |
| Camera bump protrudes into free air, needs no pocket | Frame must grip the front bezel, which intrudes on screen edges |
| Fingerprint reader and rear fully accessible | Least stiff; a 197 x 90 open frame in PETG will flex |
| Best case in the balance analysis | Phone retention relies entirely on lip engagement and friction |
| Phone dissipates heat normally | |

### Option C — frame plus removable rear cover

Model B, and additionally a snap-on rear panel that can be fitted or left off.

| Pros | Cons |
|---|---|
| The user picks thin-and-exposed or thick-and-protected, per outing | Two parts to design, two to keep aligned, one to lose |
| The frame can be stiffened by the cover when fitted | The frame must be stiff enough to work *without* the cover anyway, so the weight saving is smaller than in B |
| Good fallback if B turns out too flexible | Most CAD work of the three |

### Option D — frame with a skeletal rear brace

A frame as in B, plus a diagonal or X-shaped rib across the rear that stiffens
the lid without closing it, routed to clear the camera bump and the fingerprint
reader.

| Pros | Cons |
|---|---|
| Recovers most of B's lost stiffness for ~5 g and 0 mm of added stack (the rib sits over the phone's rear, outside the closed stack) | Rib is the outermost surface and takes every scratch |
| Keeps the fingerprint reader usable | Looks deliberate or looks unfinished, depending on execution |
| Gives somewhere to mount the hinge leaves properly | Needs care to avoid pressing on the camera bump |

## Decision

**Option A — closed pocket with a full rear wall.**

The fingerprint reader is the main function a closed back gives up, and it will
not be used. With that objection removed, the remaining trade is 1.2 mm against
full rear protection for the phone, a stiff lid that needs no rib scheme, and a
clean exterior — and the owner's call is that the protection is worth it.

Closed height becomes **22.24 mm** at the rear, 18.26 at the front.

Note this is 0.40 better than the 22.44 quoted while this ADR was open: that
figure carried a 0.50 air gap between keycaps and screen, which was an artifact
of how the scenario was first written. A closed-back lid takes the same 0.30
felt liner as an open frame — there is no reason for the gap to differ.

## Consequences

### Thickness

- **Every thickness lever in the project is now spent.** 22.24 mm is the design
  point and there is no remaining way to reduce it without reopening
  [ADR-0002](0002-keyboard-integration-depth.md) or
  [ADR-0008](0008-base-floor.md).
- The one refinement still available is ADR-0008 Option E — a 0.8 ribbed floor
  sitting in the keyboard's rim recess — which would give **21.84 mm**. It is
  now worth pursuing rather than optional, because of the margin problem below.
- **N1's hard limit of 22.5 is now binding, with 0.26 mm of margin.** The
  sensitivity note in the [thickness budget](../analysis/thickness-budget.md)
  says that if coupon 2.4 shows the base flexes under typing, the floor goes to
  2.0-2.5 — which would put the device at 23.0-23.5 and break the limit. There
  is no headroom left to absorb that. The limit itself should be restated with a
  real rationale, since 22.5 was derived from an early estimate of this very
  scenario and is self-referential.

### Balance

- The lid gains ~25 g, so `M_lid` goes from 182 to 207 and the bare device tips
  at 127 deg rather than 133.
- That, compounded by the shell masses turning out roughly double the original
  estimates, is what drove [ADR-0003](0003-lid-balance-strategy.md) to a **15 mm**
  rear setback rather than 11. See [balance.md](../analysis/balance.md).
- A design rule follows for this part specifically: **hollow the lid wherever it
  carries no load.** The 18 mm-wide solid rings down each side are dead mass in
  the worst possible place, and removing them moves the balance directly.

### Phone orientation — determined, not chosen

Screen rotation is a software matter. The hardware constraint is that the **power
and volume buttons must end up on the top edge and stay reachable**, which fixes
the orientation rather than leaving it open.

On the Pixel 3a XL, power and volume are both on the right-hand edge in portrait.
Rotating the phone 90 deg counter-clockwise to bring that edge upward puts:

| Phone edge | Lands on | Needs |
|---|---|---|
| Right — power, volume | Lid's top long edge, away from the hinge | Cutouts or relief |
| Bottom — USB-C | Lid's **right** short edge | Cutout, required by F6 |
| Top — 3.5 mm jack | Lid's left short edge | **Nothing — no cutout.** Decided; the jack is not used |
| Left — SIM tray | Lid's bottom long edge, at the hinge | Nothing; inaccessible and unimportant |

This is the same orientation Mk2 used, which is visible in
`../palmtop_mk2/maker_world/palmtop.jpg` — the earpiece and front camera sit on
the left of the landscape screen, meaning the portrait top points left.

**Accidental button presses: not a problem in practice.** The lid's top edge is
both where the buttons are and where a hand grips to open the clamshell, which
looks like it should cause trouble. Mk2 used the same phone in the same
orientation and did not, over its whole service life. That is field evidence from
the predecessor and it outranks reasoning from the geometry.

One difference is worth a glance before assuming it transfers: Mk2's lid was an
open frame, and in `../palmtop_mk2/maker_world/full_opened.jpg` its top edge
appears to be relieved in the middle, with printed material only at the corners.
Mk3's closed pocket will have a continuous wall along that edge instead. If that
relief is *why* fingers stayed off the buttons, the change matters; if the reason
is simply that the grip naturally falls on the base, it does not. Worth thirty
seconds with the physical Mk2 rather than a guess from a photograph.

Pressing the buttons themselves is not a tipping concern: the force is directed
down the lid toward the hinge, not perpendicular to the screen. Tapping the
*screen* is the tipping case, and it is already in the acceptance criteria.

### Where the phone sits in the lid, and the button window

The phone is **biased forward**, not centred: 4.00 mm of wall on the button edge,
9.35 mm on the hinge side. Centred would put 6.68 mm in front of the buttons,
which is not an opening but a shaft — a phone case manages with about 1.5.

Mk2 solved this the same way, and its STL was measured rather than guessed:
4.70 front, 9.60 rear, with **one 54.0 x 10.0 window spanning both buttons**
instead of two holes. Mk3 uses 4.00 rather than 4.70 because Mk2's full-width
hinge barrel needed no station reliefs and Mk3's stations do — the bias buys the
material between the phone pocket and the relief, which went from 0.97 mm to
3.65 mm.

Both lids centre the same phone in X in the same orientation, so Mk2's window
span transfers directly: **X -48.6 to +5.0**. Task 0.10 is superseded.

The bias costs balance: it moves `r_lid` from 45.03 to 47.05 and the tipping
margin at 180 deg from 1.225 to about 1.17. The lightening work that N4 requires
anyway more than repays it, but the two must be done in that order.

### The phone is taped in, not gripped

Mk2 held its phone with double-sided tape and no retention lips at all, and that
carries over. The pocket is therefore a plain recess the depth of the phone, with
nothing overlapping the screen — which is what this model already had, so no
geometry changed and **task 0.8 (front bezel width) is superseded**.

**The tape goes on the pocket's floor, and the pocket is 1.0 deeper for it.**
This was first decided the other way: side walls, to keep the closed stack at
22.24 under N1's then hard limit of 22.5. On the side walls it cost only pocket
width — 160.7 to 162.7, side blocks 18.05 to 17.05 — and that widening is kept.

It did not survive assembly (2026-09-29). The first full build went together
with 1 mm tape on the floor, the phone stood 1 mm proud of the lid's face, and
with only `keycap_gap` (0.3) to the keycaps it landed on the keys. Because the
lid pivots about the hinge, the contact nearest the axis governs, and the lid
stood ~4 mm open at its front edge — roughly the whole close tilt.

The owner chose the height over the side-wall discipline: the pocket is now
`phone_z + tape_t` deep, the lid 10.40 thick, and the device closes at
**23.24**. N1's hard limit was restated to 24.5 to match
([requirements](../requirements.md)). Floor tape also means the phone seats
against a flat plane rather than being wedged between walls, which is how it
naturally went together.

Adhesion is nowhere near the constraint. Holding an inverted phone is 1.64 N
against roughly 1250 mm2 of contact on the two short ends alone, and the pocket
already captures the phone on all four sides — the tape only has to stop it
falling out.

### Detail design

- The camera cutout is a **through-hole in the rear wall**, 11.2 x 23.2, again
  taken from Mk2's STL and referenced to the phone's edges. Because it goes
  through, the bump's height never mattered and task 0.6 is superseded — a bump
  taller than the 1.2 wall simply protrudes, as it does on the naked phone.
- A USB-C cutout on the short edge is still required by F6.
- The phone's rear is fully covered, so it sheds heat only through the screen.
  The Pixel 3a XL is not a hot device, but sustained use in a sealed pocket is
  worth watching during Phase 4.
- **Unlocking is PIN or password only.** Recorded as an accepted consequence, not
  an objection — it follows directly from the reason this option was chosen.
- **F7 has been relaxed rather than met.** With the phone taped in, removal means
  prying, not a thumb push. Mk2 lived with this for its whole service life, so it
  is an accepted trade — but it is a trade, and it should not be rediscovered as
  a defect two iterations from now.
- The 53.6 mm button window gives somewhere to get a tool in when the phone does
  have to come out.
