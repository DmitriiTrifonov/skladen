# bezel/

ADR-0012: the lid with no tape, and the frame (a thin plate with a screen window) that
snaps over the phone. The lid files here now also carry the crush ribs on the pocket
walls (ADR-0015) and the three button tongues in place of the open window (ADR-0016);
both are modelled and checked, not printed. The first print (2026-10-19) was before them.

## The frame

| File | What it is |
|---|---|
| `skladen2-bezel.stl`, `.step` | The frame, in place |
| `skladen2-bezel-flat.stl` | The frame laid flat for printing |
| `skladen2-bezel-closed.stl`, `.step` | The frame closed over the buttons: no cut-out, no legs there (ADR-0016) |
| `skladen2-bezel-closed-flat.stl` | The closed frame laid flat for printing |

Use the closed frame with the button tongues in the lid. The tongues are pressed from the
lid's front edge, under the plate; the plate roofs them. The first frame, with the
cut-out, is for the lid without tongues (`button_tabs = False`) and for the one printed on
2026-10-19.

## The lid

| File | What it is |
|---|---|
| `skladen2-lid-bezel.stl`, `.step` | Plain lid, no logo |
| `skladen2-lid-bezel-logo.stl`, `.step` | Lid with the logo recess (the inlay is in [`../logo/`](../logo/)) |
| `skladen2-lid-bezel-logo-through.stl`, `.step` | Logo cut through the whole rear wall, for a different look |
| `skladen2-lid-bezel-logo-2color.3mf`, `.step` | Lid and inlay as a plain two-part 3MF, for other slicers |
| `skladen2-lid-bezel-logo-petg.3mf` | Bambu Studio project, lid and inlay in PETG on the A1/AMS |

The Bambu project is refilled from `cad/templates/bezel-lid-logo.3mf` on every build and
only the meshes change, not the slicer settings. Every 2.1 plate is also in one project,
`../skladen2-2.1-plates.3mf` (the closed frame is plate 5).

Phone-fit coupons of this lid are in [`../coupon-phone/`](../coupon-phone/).
