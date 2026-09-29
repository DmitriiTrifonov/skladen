# Parameters

**Generated from `cad/params.py` — do not edit by hand.**
Regenerate with `.venv/bin/python cad/gen_params_doc.py`.

The Python is the source of truth; this file exists so the numbers are readable
and reviewable in a diff, as [ADR-0007](adr/0007-cad-toolchain.md) requires.

All lengths mm, masses g, angles deg.

Status: `M` measured · `S` from spec · `D` decided in an ADR · `C` calculated
from others here · `A` assumed, not yet verified

---


## Keyboard — Jomaa KEYBOARD098RU

| Name | Value | St | Note |
|---|---|---|---|
| `kbd_span_x` | 194 | M |  |
| `kbd_depth_y` | 86.25 | M |  |
| `kbd_h_rear` | 9.52 | M | thickest, rear of the wedge |
| `kbd_h_front` | 5.54 | M | thinnest, front |
| `kbd_keycap_rear` | 1.82 | M |  |
| `kbd_keycap_front` | 1.82 | M | owner: same as rear |
| `kbd_mass` | 95 | M |  |
| `kbd_rim_width` | 1.68 | M | perimeter rim on the underside |
| `kbd_wedge_angle` | 2.642 | C | atan((h_rear - h_front) / depth) |


## Keyboard USB-C — on the RIGHT SIDE face, not the rear edge

| Name | Value | St | Note |
|---|---|---|---|
| `kbd_usbc_rear_inset` | 8 | M | rear edge to the near end of the connector |
| `kbd_usbc_z_bottom` | 3 | M | opening's lower edge above the rest plane |
| `kbd_usbc_z_top_inset` | 2 | M | opening's upper edge below the top of that face |
| `kbd_usbc_face_h` | 8.9432 | C | the side face is a wedge |
| `kbd_usbc_h` | 3.9432 | C | derived opening height |
| `kbd_usbc_w_ASSUMED` | 9 | A | task 0.1 — the last measurement outstanding |
| `usbc_centre_y` | 75.65 | C | in device coordinates |
| `usbc_centre_z` | 6.1716 | C |  |
| `usbc_cut_w` | 13 | D | opening in the base's right wall, along Y |
| `usbc_cut_h` | 7.5 | D | along Z |


## Phone — Pixel 3a XL

| Name | Value | St | Note |
|---|---|---|---|
| `phone_x` | 160.1 | S | long axis, horizontal in the lid |
| `phone_y` | 76.1 | S |  |
| `phone_z` | 8.2 | S | body, excluding the camera bump |
| `phone_mass` | 167 | S |  |
| `phone_corner_r_front` | 8.86 | M | plan view, button edge; from Mk2's pocket sketch |
| `phone_corner_r_rear` | 10.4 | M | plan view, hinge edge |
| `phone_front_wall` | 4 | D | biased forward so the buttons are reachable |
| `tape_t` | 1 | D | double-sided tape, on the pocket's FLOOR |
| `pocket_z` | 9.2 | C | phone_z + tape_t |
| `button_win_x0` | -48.6 | M | button window, from Mk2's STL |
| `button_win_x1` | 5 | M |  |
| `cam_x0` | -69.8 | M | camera cutout, from Mk2's STL |
| `cam_x1` | -58.6 | M |  |
| `cam_from_edge0` | 8.85 | C | referenced to the phone's own button-side edge |
| `cam_from_edge1` | 32.05 | C |  |
| `phone_usbc_cut_w` | 12 | D | phone's own port, lid's right wall |
| `phone_usbc_cut_h` | 7 | D |  |


## Materials and clearances

| Name | Value | St | Note |
|---|---|---|---|
| `mat_density` | 0.00127 | S | g/mm3, PETG, SOLID — see the note in params.py |
| `wall_t` | 1.6 | A |  |
| `clr_kbd` | 0.3 | A | per side, depth |
| `clr_kbd_x` | 0.6 | M | per side, span: absorbs measured print shrinkage |
| `clr_phone` | 0.3 | A | per side |
| `keycap_gap` | 0.3 | D | held open by the base's rim, not by a liner |
| `corner_r` | 3 | D | outer vertical corners |


## Base

| Name | Value | St | Note |
|---|---|---|---|
| `base_floor_t` | 1.2 | D | ADR-0008 |
| `base_x` | 198.4 | C | kbd_span_x + 2*(wall_t + clr_kbd_x) |
| `base_depth_to_axis` | 90.05 | C |  |
| `hinge_setback` | 15 | D | ADR-0003 |
| `base_y` | 105.05 | C | base_depth_to_axis + hinge_setback |
| `foot_dia` | 10 | D | locating recesses for bumpons |
| `foot_recess` | 0.4 | D |  |
| `foot_y_rear` | 99.05 | C | sets the tipping contact line — see ADR-0003 |
| `foot_y_front` | 8 | D |  |
| `foot_inset_x` | 12 | D |  |


## Lid

| Name | Value | St | Note |
|---|---|---|---|
| `lid_rear_wall` | 1.2 | D | ADR-0004, closed pocket |
| `lid_x` | 198.4 | C | matches base_x |
| `lid_y` | 90.05 | C | ends at the hinge axis |
| `lid_t` | 10.4 | C | lid_rear_wall + pocket_z |
| `lid_rear_radius` | 5.2 | C | half the lid thickness |


## Logo — Mitya Computer, inlaid in the lid's outer face

| Name | Value | St | Note |
|---|---|---|---|
| `logo_width` | 80 | D | across the lockup |
| `logo_depth` | 0.6 | D | half the rear wall; three 0.2 layers |
| `logo_centre_y` | 42.35 | C | centred over the phone |
| `logo_reads_open` | True | D | upright to someone facing the open lid |


## Derived stack

| Name | Value | St | Note |
|---|---|---|---|
| `parting_rear` | 12.54 | C | top of the keycaps |
| `parting_front` | 8.56 | C |  |
| `rim_rear` | 12.84 | C | where the lid lands |
| `rim_front` | 8.86 | C |  |
| `closed_h_rear` | 23.24 | C | **the N1 number** |
| `closed_h_front` | 19.26 | C |  |
| `close_tilt` | 2.5307 | C | the lid shuts nose-down onto the wedge |


## Hinge

| Name | Value | St | Note |
|---|---|---|---|
| `hinge_axis_y` | 90.05 | C |  |
| `hinge_axis_z` | 18.04 | C | lid mid-thickness, NOT the parting plane |
| `hinge_torque_req` | 0.091 | C | N*m at 90 deg |
| `knuckle_od` | 9 | D | capped by the lid's thickness at the axis |
| `knuckle_id` | 3.5 | D | M3 clearance |
| `knuckle_clr` | 0.2 | D | per face |
| `station_outer_w` | 6 | D | each base knuckle |
| `station_inner_w` | 5.8 | D | the lid knuckle |
| `station_w` | 18.2 | C |  |
| `station_relief_r` | 6.2 | C | lid_rear_radius + 1.0, so a post can exist |
| `post_half_y` | 2.5 | D |  |
| `nut_af` | 5.7 | D | M3 nut across flats |
| `nut_depth` | 4.3 | D |  |
| `head_dia` | 5.8 | D |  |
| `head_depth` | 3.8 | D | head plus a wave washer |


## Masses and balance — estimates, risk R3

| Name | Value | St | Note |
|---|---|---|---|
| `infill_chunky` | 0.42 | A | chunky blocks take infill; thin walls print solid |
| `r_lid` | 45 | A | superseded in build.py by a value derived from the geometry |
| `d_base` | 41 | A | keyboard mass is rear-biased |


## Hinge stations

At X = -87.5, 87.5, span 175.0 mm between the outermost.

## Still blocked

| Parameter | Waiting on |
|---|---|
| `kbd_rim_recess` | task 0.4 |
| `phone_camera_bump` | task 0.6 |
