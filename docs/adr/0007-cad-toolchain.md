# ADR-0007: CAD toolchain

> **Skladen 2:** written for Mk3 and the Pixel 3a XL. Its numbers are inherited, not re-derived; what the Pocophone F1 changes is in [ADR-0011](0011-phone-swap-pocophone-f1.md).

- **Status:** Accepted
- **Date:** 2026-09-20
- **Decides:** N6

## Context

Mk1 was modelled in Blender (`../pixel_palmtop/*.blend`), Mk2 in FreeCAD
(`../palmtop_mk2/*.FCStd`). The move to FreeCAD between iterations was already a
judgement that mesh modelling is the wrong tool for a mechanical part.

N6 requires the key dimensions to be parametric. Mk3 has an unusual number of
dimensions that are still unknown — the entire rear-edge cross-section is blocked
on ADR-0005 and ADR-0006, and the keyboard's internal stack is blocked on
ADR-0002. The design will be re-dimensioned repeatedly, and possibly split into
two base variants (ADR-0002 Option D).

There are also reusable assets: `Pixel_3A_XL_Body.stl` from Mk2 is a good
reference solid and should not be remade.

## Options

### Option A — FreeCAD with a spreadsheet-driven model

Continue with Mk2's tool. All dimensions live in a `Spreadsheet` object;
sketches reference named cells.

| Pros | Cons |
|---|---|
| Continuity: Mk2's model can be opened and cannibalised | FreeCAD's topological naming problem makes deep edit histories fragile — exactly the situation repeated re-dimensioning creates |
| Spreadsheet parametrics satisfy N6 directly | GUI-driven history is hard to diff in git |
| Imports the existing phone STL as a reference solid | |
| Native STEP export | |

### Option B — OpenSCAD / CadQuery / build123d — code-first

Model the whole device as a script with a parameters block at the top.

| Pros | Cons |
|---|---|
| Parametric by construction; N6 is free | Rewrite from scratch; nothing from Mk2 carries over |
| Diffs cleanly in git, which matters for a repo built around ADRs | Fillets and organic shapes are painful in OpenSCAD (better in CadQuery/build123d) |
| Two base variants become a boolean flag rather than two files | Harder to fit geometry against a scanned/imported reference mesh |
| Re-dimensioning after a measurement is a one-line change | Learning curve if not already fluent |

### Option C — FreeCAD for shape, a parameters file as the source of truth

Keep FreeCAD, but hold every driving dimension in a version-controlled
`docs/parameters.md` or a CSV that the spreadsheet imports, so the numbers are
reviewable in git even though the geometry is not.

| Pros | Cons |
|---|---|
| Keeps FreeCAD's ease of shaping | The geometry itself is still an opaque binary in git |
| The numbers — the part that ADRs argue about — become diffable | Requires discipline to keep the file and the model in sync |
| Low effort on top of Option A | Does not fix topological naming fragility |

## Decision

**Option B, code-first — build123d.** The model is Python; the repo is the CAD.

The decisive factor was not in the original options list: **the modelling is being
done by an agent, not by hand in a GUI.** That inverts the ergonomics argument
entirely. FreeCAD's strength is the GUI, and reaching it through a scripted or
MCP interface gives up that strength while keeping the topological naming
fragility — which bites hardest under exactly the repeated re-dimensioning this
project will do as Phase 0 measurements land.

build123d over the alternatives:

- **over FreeCAD scripted** — FreeCAD's Python API is clunky and its rebuilds are
  fragile; `freecadcmd` ships in the app bundle, so this was available and still
  rejected.
- **over CadQuery** — same OCCT kernel, more current API.
- **over OpenSCAD** — fillets and the wedge geometry are painful there, and there
  is no STEP export, only mesh.

No MCP is involved or needed.

## Environment

| | |
|---|---|
| Python | 3.12 (brew), in `.venv/`, gitignored |
| build123d | 0.12.0 |
| Kernel | OCCT via cadquery-ocp |
| Run | `.venv/bin/python cad/massing.py` |

Python 3.14 is the system default and is too new for the OCP wheels; the venv
pins 3.12 deliberately.

## Consequences

- **`docs/parameters.md` is generated from `cad/params.py`, not maintained
  beside it.** The original intent was a matched pair kept in step by hand. They
  drifted within the hour — by a dozen values — which is the predictable outcome.
  `cad/gen_params_doc.py` now emits the markdown, and `cad/build.py` runs it on
  every build, so the two cannot disagree. The Python is the source of truth; the
  markdown exists so the numbers are readable and reviewable in a diff, which is
  what N6 actually wanted. Nothing else may hard-code a dimension.
- Every model script exports both STEP and STL to `export/`, so a later
  toolchain change does not start from a mesh.
- Model scripts carry their own assertions. `cad/massing.py` checks its bounding
  boxes against the derived stack and exits non-zero on a mismatch, which makes
  the geometry self-verifying against the analyses rather than merely consistent
  with them by eye.
- **This immediately paid for itself.** The first run reproduced the derived
  closed height exactly and simultaneously showed that the shell mass estimates
  underpinning the whole balance analysis were roughly half of reality — see
  [balance.md](../analysis/balance.md). That is a class of error a GUI model
  would not have surfaced without being finished first.
- The owner cannot nudge geometry with a mouse. Changing a dimension means
  editing a constant, which is a fair trade given the agent does the modelling,
  but it is a real change in how the project is worked on.
- `.venv/` is gitignored. Reproducing the environment needs
  `python3.12 -m venv .venv && .venv/bin/pip install build123d`.
- `Pixel_3A_XL_Body.stl` from Mk2 is no longer needed as a reference solid — the
  phone is a parametric box in `params.py`. It stays in `reference/` for
  visualisation only.
