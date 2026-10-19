# Changelog

Versions follow [semantic versioning](https://semver.org/) applied to hardware:
**major** when parts no longer interchange (another phone, keyboard or hinge),
**minor** for a compatible addition or option, **patch** for fixes to dimensions,
tolerances or documentation. Tags mark the commit a version was printed from;
design reasons are in [docs/adr/](docs/adr/README.md).

## [Unreleased] — 2.1.0, front bezel (modelled, not printed)

Planned tag `v2.1.0-rc1` once the bezel is printed; `v2.1.0` when it fits.

### Added
- **Clip-on front bezel** and a lid for it as a separate export, `export/bezel/`: a
  0.8 mm frame covering the whole front, ten snap clips and no screws, a window over
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
