# ADR-0012: A removable front bezel in place of tape

- **Status:** Proposed — modelled as a separate export (`export/bezel/`), not printed
- **Date:** 2026-10-17
- **Decides:** would restore F7 (relaxed in [ADR-0004](0004-phone-retention.md)); touches N1 and the tipping margin

## Context

The idea comes from a Reddit build of a Boox Palma in a printed clamshell: the lid is
a tray, the phone drops into it, and a separate thin frame snaps over the phone's
front face. Photographed assembled, and again with the frame lifted off beside the
tray.

Skladen 2 holds the phone with 1.0 mm of double-sided tape on the pocket floor
([ADR-0004](0004-phone-retention.md)). That was inherited from Mk2 and accepted as a
trade: the phone comes out by prying, and F7 was relaxed rather than met. The tape
also costs 1.0 of closed height, which is why the phone stands flush with the lid's
face. The pocket is a plain recess with nothing over the screen, so task 0.8 (front
bezel width) was superseded.

Numbers that matter here:

| | |
|---|---|
| Margin to N1's hard limit (25.0) | 0.71 mm |
| Tipping margin at 180 deg, printed estimate | 1.002, no headroom |
| Phone screen side bezels (portrait), from the spec sheet | ~3.6 mm each, **estimate** |
| Keycap gap under the lid | 0.30 |

## Options

### Option A — tape only (current)

| Pros | Cons |
|---|---|
| Zero parts, nothing over the screen | The phone is pried out; the tape is single-use |
| Already modelled | 1.0 mm of closed height spent on tape |

### Option B — full front frame, snapped on (the Reddit design)

A frame with a window over the screen, retained by snap tabs on the lid's walls.

| Pros | Cons |
|---|---|
| The phone is removable, so F7 is met again | A second part, with snap tabs that must survive repeated use in PETG |
| The lip replaces the tape's 1.0 mm, so closed height can stay put | A full 197 x 90 frame is ~7-9 g up high in the lid, where the tipping margin has nothing to give |
| Frame can carry the logo and the button window | Lip must clear the keycaps by 0.30 and not cover the touch edge |

### Option C — small retaining frame, phone ring only

Same idea, but only the ring around the phone pocket (about 165 x 84 outside), not the whole lid face.

| Pros | Cons |
|---|---|
| About half the mass of B, ~3-4 g (estimate) | Still adds mass high in the lid |
| Same removability and same thickness trade | The lid's own face stays bare plastic around it |

### Option D — corner clips instead of a frame

Four small tabs at the pocket corners, screwed or snapped.

| Pros | Cons |
|---|---|
| Lightest, <1 g | Holds the phone at points only; a 182 g phone will rattle without a foam pad |

## Decision

**Not decided.** Leaning to **Option C**, with the lip thickness taken from the tape's
1.0 mm rather than added to the stack. The pocket goes from
`phone_z + tape_t` to `phone_z + lip_t`, and a 0.5 foam pad behind the phone, if one
is wanted, takes the rest. Closed height would then stay at 24.29. Option B is
rejected on mass alone until the model says otherwise.

## As modelled (2026-10-17)

`cad/build.py` builds the frame and a lid for it as a separate export in
`export/bezel/`; `export/device/` is untouched. The frame covers the **whole front**
of the lid, as in the Reddit build, and holds on snap clips with no screws.

| | |
|---|---|
| Frame | 0.8 plate, flush with the lid's face, 198 x 84, window over the screen; 7.0 g |
| Phone | on the rear wall, glass 1.0 behind the face; 0.2 of play to the frame |
| Overlap | 2.0 over the long edges, 3.0 over the ends — **guesses**, task 0.13 |
| Clips | 15 in all (since 2026-10-19): 5 in the front wall, 5 in the rear, 3 at the left end, 2 at the right; arm 1.0 x 10, barb 0.5 into a recess in the wall |
| Prying | a nick under the front edge, X 30-42, for a fingernail |
| Closed height | 24.29, unchanged: the lid's own face layer is gone under the plate |
| Pocket in X | 156.1, not 158.1: with no tape the ends need no room |
| Lid | ends hollowed from the screen side; the plate roofs them and the USB-C / jack slots |

Checked in `build.py`: one solid each, no interference with lid, base or phone, the
frame covers the glass, 1.32 of rear skin left under the USB-C slot.

**Lightening.** The Reddit lid is a thin-walled tray, so the 21 mm end blocks are hollow
here: outer wall 1.6 (on the base's own wall), one rib across each end, walls beside the
USB-C and jack channels. Solid plastic 105.7 g -> 76.6 g, frame 7.0 g on top.

**It does not pass the tipping check on paper.** For 180 deg to hold, lid shell + frame
must print at **67.4 g or less** (150 deg: 125 g). Solid they are 83.6 g together; walls
print nearly solid, so the real figure sits above 67 and only the slicer says where.
`build.py`'s 0.85 factor for this lid gives 0.987 at 180 deg and 1.140 at 150 deg; it is a
guess, not a result. The levers are in ADR-0003: a steel strip under the front of the base,
or more lightening.

**Slicer masses, 2026-10-17** (Bambu A1, 0.2 layers, 20% infill, 4 walls, brim and supports
taken off): lid 56.02 g, frame 6.35 g, base 56.46 g. With those, the tipping margin is
**1.154 at 150 deg** (the design target, ADR-0003) and **1.000 at 180 deg**. `build.py` now
enforces 150 deg and only reports 180. A steel strip under the front of the base would
add margin at 180 deg (~7.5 g for ~1.06); **deferred by the owner**, noted in
[plan.md](../plan.md).

**After the first print (2026-10-19).** The clips moved toward the corners: front
x -70 / 16 / 70, rear -72 / -36 / 0 / 36 / 72 (the front row keeps clear of the button
window, X -52.5 to -7.5). The left end got a third clip at y 42, mid-way; the right end
cannot, the USB-C channel is there. The plate also covers the notch end of the phone down to the
picture: the owner measured 8.84 mm from the top edge to where the picture starts, so the
window now begins 8.5 mm in at the -X end (3.0 stays at the USB-C end, where the picture
starts ~5.7 in: 155.5 - 141 - 8.84; the panel is 68 x 141 mm active, from the
mainline driver `panel-ebbg-ft8719.c`). The window is 144.0 long, offset 2.75 toward +X.
The owner asked for the plastic across the whole notch side, so the window started 5 mm
later there (moved 4 mm back toward the end on 2026-10-20: now 1 mm) (`bezel_notch_d_ASSUMED`), with the same corner radius as at the other end,
hiding the status bar beside the notch as well; both tab sizes are **assumed** (`bezel_notch_*_ASSUMED`), measure them.

**Button window edges.** The plate's cut-out over the buttons left its edges free to lift,
and the front clips were far from it. Two front clips now stand at x -59 and -1, 1.35 mm
clear of the window's walls (front row -72 / -59 / -1 / 35 / 70). Each side of the cut-out
also keeps a 1.2 mm strip of plate with a 3.0 mm leg hanging into the lid's window, 0.05
from its wall, so the plate sits square and cannot drift sideways or lift there. The
cut-out is 2.4 mm narrower for it. Not yet printed; if the legs bind, raise
`bezel_leg_clr`.

**First removal (2026-10-20).** Pulling the frame off broke it, and the arms stayed in
their slots, so both parts were lost. The arms stand upright, their layers across the
bend, and one pry notch loads all fifteen at once. Changes: a 1.6 mm hole from the
lid's back to the top of each slot (`clip_eject_d`), so a pin pushes a broken arm out;
barb 0.4 instead of 0.5, with a gentler catch (0.4 over 1.0 instead of 0.5 over 0.6) so
it lets go sooner. Not yet printed.

**Audio openings (2026-10-20).** The F1's bottom edge has a six-hole
grille either side of the USB-C, one for the speaker and one for the microphone
(reviews do not say which side). The USB-C end wall of the bezel lid has a row of six
1.4 mm holes either side of the slot, the grilles' edges 13.5 and 25.5 mm from the
USB-C's centreline (owner, measured, the same both sides), level with the phone's
mid-thickness (`audio_*`). The end clips moved from y 70 to 74 to clear the rear grille.
The frame has a 12 x 1.6 slit for the earpiece 3.5 mm from the phone's top edge, a
guess: set `earpiece_*_ASSUMED` once measured. A second
microphone in the top edge, if the phone has one, is not opened.

**Risks, not yet seen on a print:**
- Clip arms print standing up, so they bend across the layers: the likeliest thing to
  break first. A fallback is a thicker arm or a metal-free alternative such as a sliding
  tab; both are CAD changes.
- The front clips leave 1.1 mm of outer wall and about 1.0 beside the pocket; the front
  wall is only 4.0 thick.
- A 0.8 plate over a 198 x 84 area is a flexible sheet; it is held at fifteen points.

**Printing the logo lid in two colours.** The lid with the logo recess and the
inlay are printed as one multi-part object, one filament each (on the owner's A1 with
an AMS: lid 3, inlay 4, both PETG). `cad/templates/bezel-lid-logo.3mf` is a project
saved from Bambu Studio with the lid already lying on its back (rear wall on the
bed, the 0.6 mm inlay as the first layers), filaments assigned and process settings
as the owner likes them. `cad/bambu_project.py` refills it with the current meshes on
every `build.py` run and writes `export/bezel/skladen2-lid-bezel-logo-petg.3mf`,
leaving settings alone. It also places the inlay exactly: the slicer's *Assemble* had
left it 0.21 mm off in X and 0.11 in Y, which is a hairline gap beside the recess.
To change settings, re-save the template from the slicer, not the exported file.
**Supports under the hinge end.** The slicer lays the lid on its back, which puts the
rear cylinder's first 45 deg of arc in the air; in PETG those supports weld to the lid
and have to be cut off. The bezel lid (not the printed `device/` lid) now fills that
corner with a flat ramp, about 36 deg from horizontal, which Bambu's default 30 deg
threshold leaves unsupported. The ramp's foot is `lid_ramp_out` = 0.25 mm outside
the cylinder; the opening sweep of this lid against the base is 0.000 mm3 from 0 to 180
deg (it first collided at 150 deg with a 45 deg ramp, 0.47 mm out). Overhang area
shallower than 30 deg fell from ~1 500 mm2 to ~110 mm2 of short ceilings inside. Also
useful with PETG: top Z distance 0.25-0.3, interface layers 2.

**First print: the end clips held nothing** (owner, 2026-10-19); the front and rear
clips, which stand in the 4.0 front wall and rear wall, held well. The end clips stood
in the hollow end with only the 1.6 outer wall behind the barb, which simply flexed.
Each end clip now has a solid block round its slot (`clip_pad` = 1.2 mm each side of
the slot), like the long-side ones; +0.7 cm3 in all, about 0.9 g solid. Only the lid
changes; the frame's arms are the same. Not yet printed.

Things that went wrong on the way, so they are not repeated:

- Two separate objects (lid and inlay) overlap and the slicer reports conflicting
  G-code paths: *Assemble* them into one object first.
- The plain lid (`skladen2-lid-bezel.stl`) has no recess, so the inlay is swallowed.
- A prime tower near the plate edge gives "G-code path goes beyond plate
  boundaries"; move it inward.
- PLA with PETG in one print warns and bonds weakly; use both as PETG.
- `export/bezel/skladen2-lid-bezel-logo-2color.3mf` is a plain (non-Bambu) two-part
  file, kept for other slicers.

## Consequences

- **Thickness is a wash only if the lip is about 1.0.** A thinner lip (0.6-0.8) is a
  few layers and fragile; a thicker one spends margin the project does not have.
- **Mass is the real cost.** Run the bezel through `cad/params.py` before choosing.
  At 1.002 on paper, 3-4 g at `r_lid` ~47 mm may flip the 180 deg case. The levers
  already recorded apply: lighten the lid's 20 mm solid end blocks, or tape a steel
  strip under the front of the base ([ADR-0003](0003-lid-balance-strategy.md)).
- **The plate and the lip must stay off the screen's active area and the keycaps.** Phone ends sit
  over keys, so the lip is inside the 0.30 keycap gap's concern as well as the
  thickness one.
- **Task 0.8 comes back:** measure the real lip overlap the Pocophone's glass allows.
- **The phone's USB-C and the jack slots stay open on the screen side**
  ([ADR-0011](0011-phone-swap-pocophone-f1.md)), so the phone lifts out vertically
  once the frame is off. [ADR-0013](0013-usbc-extender.md) interacts.
- The hinge stations' reliefs and the button window are unaffected; the frame has to
  carry the window's edge if it covers it.
