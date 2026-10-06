<p align="center">
  <img src="docs/img/mitya-computer.svg" width="520"
       alt="Mitya Computer logo: a seated shiba in green, its head apart from the body, with a hex nut cut out of it, beside the words Mitya Computer">
</p>

<p align="center"><b>English</b> · <a href="README.ru.md">Русский</a></p>

# Mitya Computer Skladen 2

A clamshell that turns a Xiaomi Pocophone F1 into a pocketable laptop-shaped
terminal. The name is *skladen* (складень), a hinged Russian travel icon: two
panels that fold shut over what they carry.

Skladen 2 is the Mk3 design (Pixel 3a XL, Jomaa KEYBOARD098RU salvaged from its
folio case) re-parametrised for a new phone. **The keyboard, base, hinge and
power-switch shuttle are unchanged.** What differs is the lid:

- the pocket, corner radii, button window and camera cutout follow the Pocophone F1,
  read from `refs/fun.fbx`;
- **new: a slot in the lid's left end for the phone's 3.5 mm headphone jack**;
- the phone is 0.6 mm thicker and 15 g heavier, so the closed device is thicker and
  the mass budget moves — see [ADR-0011](docs/adr/0011-phone-swap-pocophone-f1.md).

<p align="center">
  <img src="docs/img/skladen2-open.png" width="760"
       alt="Skladen 2 rendered open at 112 degrees: the phone in the lid showing a terminal, the keyboard in the base">
  <br>
  <img src="docs/img/skladen2-closed.png" width="760"
       alt="Skladen 2 rendered closed, seen from the front right">
  <br>
  <sub>Shut: 24.29 mm at the hinge, 20.31 at the front. Both renders come straight from the
  model via <code>cad/render.py</code>; the phone and keyboard are stand-ins built from
  their measured envelopes.</sub>
</p>

## Status

**Modelled and self-checked; not printed yet.** `cad/build.py` builds both shells and
passes every check: one solid per part, no interference closed or through 0-180 deg,
the hinge bolts reachable, the power-switch shuttle clear, and a plug's path out of
the phone's USB-C and headphone jack unobstructed. What it cannot check is the
phone itself. The pocket thickness, 9.25 mm, is the owner's caliper reading;
the spec says 8.8 and the FBX 7.9. Closed height is now 0.71 mm under the
25.0 limit (raised from Mk3's 24.5 by the owner), and the tipping margin is 1.00.

The mass budget N4 is raised from 400 to 420 g (estimate ~403 g; owner-approved,
[ADR-0011](docs/adr/0011-phone-swap-pocophone-f1.md)).

Mk3's printed results (the hinge coupons and their two defects, the first full
print) are inherited lessons, not results for this build.

| | Mk3 | Skladen 2 |
|---|---|---|
| Phone | Pixel 3a XL, 160.1 x 76.1 x 8.2, 167 g | Pocophone F1, 155.5 x 75.3 x 9.25, 182 g |
| Closed, rear / front | 23.24 / 19.26 mm | **24.29 / 20.31 mm** |
| Margin to the hard limit | 1.26 (of 24.5) | **0.71** (of 25.0) |
| Printed mass (est.) | ~380 g | ~403 g |
| Tipping margin at 180 deg (est.) | 1.08 | 1.00 (holds on paper, no headroom) |
| Jack | no cutout | slot, 9 x 8 |

| Doc | What it is |
|---|---|
| [requirements.md](docs/requirements.md) | Goals, constraints, acceptance criteria |
| [measurements.md](docs/measurements.md) | Every number, with a confidence tag; the phone section is Skladen 2's |
| [adr/0011](docs/adr/0011-phone-swap-pocophone-f1.md) | What changed against Mk3, and why |
| [parameters.md](docs/parameters.md) | Every driving dimension, generated from `cad/params.py` |
| [analysis/](docs/analysis/) | Thickness, balance and clamshell geometry — **Mk3's**, kept as written |
| [plan.md](docs/plan.md) | Phases and risks — Mk3's |
| [adr/](docs/adr/README.md) | Eleven design decisions; 0001-0010 are Mk3's |

## Findings inherited from Mk3

**Neither component gets thinner, so the skins had to go.** The keyboard shell is
9.52 mm and the phone 9.25; together they are most of the budget and neither is
negotiable. The base's floor and the lid's back are the only skins, both kept for
enclosure ([ADR-0008](docs/adr/0008-base-floor.md),
[ADR-0004](docs/adr/0004-phone-retention.md)).

**The hinge is printed, not bought:** printed knuckles on two M3 bolted stations,
where the bolt sets deflection and a compliant washer sets force
([ADR-0005](docs/adr/0005-hinge-mechanism.md),
[ADR-0010](docs/adr/0010-hinge-station-count.md)).

**Tipping is fixed by geometry, not ballast:** a 15 mm rear setback, the same 15 mm
the hinge stations stand on ([ADR-0003](docs/adr/0003-lid-balance-strategy.md)).
With the heavier phone this margin is now thin; see ADR-0011.

## Layout

```
refs/          the phone model the numbers were read from (fun.fbx)
docs/          requirements, measurements, analyses, ADRs
docs/img/      renders from cad/render.py
cad/           build123d model: params.py drives it, build.py checks and exports
cad/logo/      the logo artwork the lid inlays are cut from
export/device/    STL and STEP for the device: lid + base (DIN 985 nylon nut)
export/plainnut/  base for a plain DIN 934 nut + threadlocker; lid from device/
export/coupon21/  hinge-station coupons; the base's also carries the switch slot
export/switch/    shuttle that works the keyboard's power switch from the rear face,
                  three finger lengths by five stem lengths: print the set, keep what works
export/logo/      Mitya Computer logo: lid-logo (recessed) + the green inlay
                  that fills it, for a two-filament print
```

Rebuild with `python3.12 -m venv .venv && .venv/bin/pip install build123d==0.12.0`,
then `.venv/bin/python cad/build.py`, and `cad/render.py` for the images.

## Licence

Copyright Dmitrii Trifonov 2026.

The design — the model in `cad/`, the files it exports, and the documentation — is
released under the [CERN Open Hardware Licence Version 2 – Strongly Reciprocal](LICENSE)
(CERN-OHL-S-2.0). Under this licence the Python model is the design's source: if
you adapt it, to a different phone or keyboard say, and distribute the result or
anything built from it, you share your modified source under the same terms.

**Except the Mitya Computer name and logo.** The artwork in `cad/logo/` and
`docs/img/mitya-computer.svg`, and the logo it puts into `export/logo/`, are not
released under that licence: all rights reserved. They are in the repository so the lid can be built with them, not for
reuse. A device you make and distribute from this design should use the plain lid
in `export/device/`, which carries no logo, or one of your own.

Source location: <https://github.com/DmitriiTrifonov/skladen>
