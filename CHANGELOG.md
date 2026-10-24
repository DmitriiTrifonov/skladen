# Changelog

Versions follow [semantic versioning](https://semver.org/) applied to hardware:
**major** when parts no longer interchange (another phone, keyboard or hinge),
**minor** for a compatible addition or option, **patch** for fixes to dimensions,
tolerances or documentation. Tags mark the commit a version was printed from;
design reasons are in [docs/adr/](docs/adr/README.md).

## [Unreleased]

## [2.1.1] — 2026-10-24, phone fit: crush ribs and button tongues (printed)

The whole lid is printed (teal PETG lid, clear base; photo in the README). The renders and
the configurator's model view use the same colours.

### Added
- **Crush ribs on the bezel lid's pocket walls** ([ADR-0015](docs/adr/0015-phone-crush-ribs.md)),
  which stop the phone floating; the first coupon at 0.40 left it loose, so 0.50 / 0.60 / 0.70
  were tried. **0.60 confirmed on a coupon** and now the default (`phone_rib_h`).
- **Button tongues** in the bezel lid's front wall in place of the open window
  ([ADR-0016](docs/adr/0016-button-tabs.md)), with a frame closed over them
  (`export/bezel/skladen2-bezel-closed*`). The volume tongues touch through nubs (2.5 wide, at the outer ends) after the
  first coupons pressed both keys, and stand 1.75 mm further toward the phone's bottom than
  first modelled (`button_key_shift`). **Confirmed on a coupon** with tongue 1.0; a whole lid
  is not printed yet.
- The web configurator's parts are rebuilt with all of the above.
- Whole-lid variants and phone-fit coupons for those parameters, a README in every `export/`
  folder, ten named plates in `skladen2-2.1-plates.3mf`; where this stopped is in
  [docs/status.md](docs/status.md).

### Changed
- The USB-C extender seat is parked ([ADR-0013](docs/adr/0013-usbc-extender.md)): its build step
  is off, its files are unchanged.
- **Hinge head pocket has a hard stop.** On the first print the 3 x 1 O-ring under the bolt
  head was flattened or torn when the bolts were turned out, because nothing limited how hard
  the head could squeeze it. The ring now sits in a 0.8 mm deep groove in the pocket floor,
  standing 0.2 mm proud, and a flat DIN 433 washer (3.2 x 6 x 0.5) goes between head and
  ring: the head squeezes the ring 20 % and the washer lands on the floor beside the groove.
  Pocket 5.8 -> 6.5 mm, head access through the lid 6.4 -> 6.8 mm. Not yet printed.
  DIN 137B wave washers were looked at and rejected: the M3 size is 8 mm across.

## [2.1.0] — 2026-10-20, front bezel (printed)

Printed and assembled (photo in the README). Revisions after the first print — the eject
holes, the speaker and microphone openings, the notch cover, the extra clips, the switch-window
base and its plugs — are modelled and checked, not yet confirmed on a print.

### Added
- **Clip-on front bezel** and a lid for it as a separate export, `export/bezel/`: a
  0.8 mm frame covering the whole front, fifteen snap clips and no screws, a window over
  the screen and one over the phone's buttons, a nick for prying it off. The phone
  sits 1.0 mm behind the face instead of on tape, so the closed height stays 24.29 mm
  ([ADR-0012](docs/adr/0012-removable-front-bezel.md)).
- Lid ends hollowed from the screen side to save mass; tipping checked with the
  slicer's printed masses (1.154 at 150 deg, 1.000 at 180 deg).
- Two-colour logo lid for the bezel: a Bambu Studio project refilled from
  `cad/templates/` by `cad/bambu_project.py`, with the inlay placed exactly.
- [ADR-0013](docs/adr/0013-usbc-extender.md): what size of USB-C extender to buy.
- [docs/sourcing.md](docs/sourcing.md): where the Jomaa keyboard and its look-alikes
  (Doohoeek, CACOE) are sold.

- [ADR-0014](docs/adr/0014-switch-by-hand.md): a base with a window in the rear face
  and a plug, instead of the switch shuttle (`export/switch-window/`; three plug fits).
- `export/skladen2-2.1-plates.3mf`: one Bambu Studio project with every plate the 2.1
  parts need: the logo lid in two colours, the frame, the switch-window base with
  its three plugs.

### Changed
- Bezel lid: six 1.4 mm holes either side of the USB-C slot for the phone's speaker and
  microphone; the frame has an earpiece slit (grilles measured: 13.5 to 25.5 mm from the USB-C's centreline; the earpiece slit is 6 x 1.6, 4.5 mm from the top edge, also measured). End clips moved from y 70 to 74 to clear the rear grille.
- Bezel lid: a 1.6 mm eject hole from the back to every clip slot, to push out an arm
  that broke off; barb 0.4 mm with a gentler catch, so the frame lets go more easily.
- Bezel clips: 15 now (front 5, rear 5, left end 3, right end 2), nearer the corners
  and two standing 1.35 mm from the button window's edges. The left end has a third
  clip mid-way (the right end has the USB-C channel there).
- Bezel plate: legs down both sides of the button cut-out locate it in the lid's window
  (0.05 clear per side), so the edge cannot lift or drift.
- Bezel window follows the picture: 9.5 mm of plate over the notch end (8.84 mm to the
  picture, measured, plus 1 mm over the notch's dip), 8.5 mm over the USB-C
  end; both corners round, r 7. The panel is 68 x 141 mm active (mainline driver).
- `export/skladen2-2.1-plates.3mf`: every object centred on its plate; the three
  plugs in a row at the back of plate 3, 15 mm apart.
- Lid mass in the tipping check from the owner's slice of the logo lid: 57.47 g.
- The phone's USB-C slot in the lid is 9.0 mm tall (was 7.0): the plug was too tight.
- The bezel lid's end clips sit in solid blocks inside the hollow ends: on the first
  print they held nothing, standing free behind a 1.6 mm wall.
- The bezel lid's hinge end has a ramp under the cylinder's lowest arc, so the lid
  prints on its back without supports there (PETG welded to them).

### Deferred
- A steel strip under the base and further lid lightening, to lift the 180 deg
  margin above 1.0 ([plan.md](docs/plan.md)).

## [2.0.0] — 2026-10-06, Pocophone F1 (printed, in use)

Skladen 2: Mk3 re-parametrised for a Xiaomi Pocophone F1 (155.5 x 75.3 x 9.25 mm,
182 g). Keyboard, base, hinge and power-switch shuttle unchanged from 1.0.0.
Phone held by 1.0 mm double-sided tape.

### Added
- Lid pocket for the Pocophone F1, button window and camera cutout read from
  `refs/fun.fbx`; a slot in the lid's left end for the 3.5 mm headphone jack
  ([ADR-0011](docs/adr/0011-phone-swap-pocophone-f1.md)).
- A phone-fit coupon: the lid's left end.

### Changed
- Closed height 24.29 mm at the rear (1.0.0: 23.24); N1's hard limit raised to 25.0 mm,
  mass budget N4 to 420 g.
- Pocket thickness from the caliper, 9.25 mm.
- Hinge holding torque recomputed for the heavier lid.

## [1.0.0] — 2026-10-02, Skladen 1 / Mk3 (Pixel 3a XL)

The first printed design: a clamshell around a Pixel 3a XL and a Jomaa KEYBOARD098RU
salvaged from its folio case. Kept at tag `v1.0.0` and on branch `v1`.

- Parametric build123d model with checks, ADRs 0001-0010, hinge coupons and the
  power-switch shuttle, the Mitya Computer logo lid, licence CERN-OHL-S-2.0.
