"""Generate docs/parameters.md from params.py.

ADR-0007 calls the markdown and the Python a matched pair. Hand-maintaining both
means they drift - and they did, by an hour and a dozen values. This makes the
markdown a build artifact so they cannot.

Run: .venv/bin/python cad/gen_params_doc.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import params as p

OUT = Path(__file__).parent.parent / "docs" / "parameters.md"

# (attribute, status, note).  Status: M measured, S spec, D decided in an ADR,
# C calculated, A assumed and unverified.
SECTIONS = [
    ("Keyboard — Jomaa KEYBOARD098RU", [
        ("kbd_span_x", "M", ""),
        ("kbd_depth_y", "M", ""),
        ("kbd_h_rear", "M", "thickest, rear of the wedge"),
        ("kbd_h_front", "M", "thinnest, front"),
        ("kbd_keycap_rear", "M", ""),
        ("kbd_keycap_front", "M", "owner: same as rear"),
        ("kbd_mass", "M", ""),
        ("kbd_rim_width", "M", "perimeter rim on the underside"),
        ("kbd_wedge_angle", "C", "atan((h_rear - h_front) / depth)"),
    ]),
    ("Keyboard USB-C — on the RIGHT SIDE face, not the rear edge", [
        ("kbd_usbc_rear_inset", "M", "rear edge to the near end of the connector"),
        ("kbd_usbc_z_bottom", "M", "opening's lower edge above the rest plane"),
        ("kbd_usbc_z_top_inset", "M", "opening's upper edge below the top of that face"),
        ("kbd_usbc_face_h", "C", "the side face is a wedge"),
        ("kbd_usbc_h", "C", "derived opening height"),
        ("kbd_usbc_w_ASSUMED", "A", "task 0.1 — the last measurement outstanding"),
        ("usbc_centre_y", "C", "in device coordinates"),
        ("usbc_centre_z", "C", ""),
        ("usbc_cut_w", "D", "opening in the base's right wall, along Y"),
        ("usbc_cut_h", "D", "along Z"),
    ]),
    ("Phone — Pixel 3a XL", [
        ("phone_x", "S", "long axis, horizontal in the lid"),
        ("phone_y", "S", ""),
        ("phone_z", "S", "body, excluding the camera bump"),
        ("phone_mass", "S", ""),
        ("phone_corner_r_front", "M", "plan view, button edge; from Mk2's pocket sketch"),
        ("phone_corner_r_rear", "M", "plan view, hinge edge"),
        ("phone_front_wall", "D", "biased forward so the buttons are reachable"),
        ("tape_t", "D", "double-sided tape, on the pocket's FLOOR"),
        ("pocket_z", "C", "phone_z + tape_t"),
        ("button_win_x0", "M", "button window, from Mk2's STL"),
        ("button_win_x1", "M", ""),
        ("cam_x0", "M", "camera cutout, from Mk2's STL"),
        ("cam_x1", "M", ""),
        ("cam_from_edge0", "C", "referenced to the phone's own button-side edge"),
        ("cam_from_edge1", "C", ""),
        ("phone_usbc_cut_w", "D", "phone's own port, lid's right wall"),
        ("phone_usbc_cut_h", "D", ""),
    ]),
    ("Materials and clearances", [
        ("mat_density", "S", "g/mm3, PETG, SOLID — see the note in params.py"),
        ("wall_t", "A", ""),
        ("clr_kbd", "A", "per side, depth"),
        ("clr_kbd_x", "M", "per side, span: absorbs measured print shrinkage"),
        ("clr_phone", "A", "per side"),
        ("keycap_gap", "D", "held open by the base's rim, not by a liner"),
        ("corner_r", "D", "outer vertical corners"),
    ]),
    ("Base", [
        ("base_floor_t", "D", "ADR-0008"),
        ("base_x", "C", "kbd_span_x + 2*(wall_t + clr_kbd_x)"),
        ("base_depth_to_axis", "C", ""),
        ("hinge_setback", "D", "ADR-0003"),
        ("base_y", "C", "base_depth_to_axis + hinge_setback"),
        ("foot_dia", "D", "locating recesses for bumpons"),
        ("foot_recess", "D", ""),
        ("foot_y_rear", "C", "sets the tipping contact line — see ADR-0003"),
        ("foot_y_front", "D", ""),
        ("foot_inset_x", "D", ""),
    ]),
    ("Lid", [
        ("lid_rear_wall", "D", "ADR-0004, closed pocket"),
        ("lid_x", "C", "matches base_x"),
        ("lid_y", "C", "ends at the hinge axis"),
        ("lid_t", "C", "lid_rear_wall + pocket_z"),
        ("lid_rear_radius", "C", "half the lid thickness"),
    ]),
    ("Logo — the Mitya Computer dog, inlaid in the lid's outer face", [
        ("logo_height", "D", "ear tip to paws"),
        ("logo_depth", "D", "half the rear wall; three 0.2 layers"),
        ("logo_centre_y", "C", "centred over the phone"),
        ("logo_reads_open", "D", "upright to someone facing the open lid"),
    ]),
    ("Derived stack", [
        ("parting_rear", "C", "top of the keycaps"),
        ("parting_front", "C", ""),
        ("rim_rear", "C", "where the lid lands"),
        ("rim_front", "C", ""),
        ("closed_h_rear", "C", "**the N1 number**"),
        ("closed_h_front", "C", ""),
        ("close_tilt", "C", "the lid shuts nose-down onto the wedge"),
    ]),
    ("Hinge", [
        ("hinge_axis_y", "C", ""),
        ("hinge_axis_z", "C", "lid mid-thickness, NOT the parting plane"),
        ("hinge_torque_req", "C", "N*m at 90 deg"),
        ("knuckle_od", "D", "capped by the lid's thickness at the axis"),
        ("knuckle_id", "D", "M3 clearance"),
        ("knuckle_clr", "D", "per face"),
        ("station_outer_w", "D", "each base knuckle"),
        ("station_inner_w", "D", "the lid knuckle"),
        ("station_w", "C", ""),
        ("station_relief_r", "C", "lid_rear_radius + 1.0, so a post can exist"),
        ("post_half_y", "D", ""),
        ("nut_af", "D", "M3 nut across flats"),
        ("nut_depth", "D", ""),
        ("head_dia", "D", ""),
        ("head_depth", "D", "head plus a wave washer"),
    ]),
    ("Masses and balance — estimates, risk R3", [
        ("infill_chunky", "A", "chunky blocks take infill; thin walls print solid"),
        ("r_lid", "A", "superseded in build.py by a value derived from the geometry"),
        ("d_base", "A", "keyboard mass is rear-biased"),
    ]),
]

HEAD = """# Parameters

**Generated from `cad/params.py` — do not edit by hand.**
Regenerate with `.venv/bin/python cad/gen_params_doc.py`.

The Python is the source of truth; this file exists so the numbers are readable
and reviewable in a diff, as [ADR-0007](adr/0007-cad-toolchain.md) requires.

All lengths mm, masses g, angles deg.

Status: `M` measured · `S` from spec · `D` decided in an ADR · `C` calculated
from others here · `A` assumed, not yet verified

---
"""


def fmt(v):
    if isinstance(v, float):
        return f"{v:.5g}"
    if isinstance(v, tuple):
        return ", ".join(fmt(x) for x in v)
    return str(v)


def main():
    out = [HEAD]
    for title, rows in SECTIONS:
        out.append(f"\n## {title}\n")
        out.append("| Name | Value | St | Note |")
        out.append("|---|---|---|---|")
        for name, st, note in rows:
            if not hasattr(p, name):
                out.append(f"| `{name}` | **MISSING** | ! | not in params.py |")
                continue
            out.append(f"| `{name}` | {fmt(getattr(p, name))} | {st} | {note} |")
        out.append("")

    out.append("\n## Hinge stations\n")
    out.append(f"At X = {fmt(p.station_x)}, span "
               f"{p.station_x[-1] - p.station_x[0]:.1f} mm between the outermost.")

    out.append("\n## Still blocked\n")
    if p.BLOCKED:
        out.append("| Parameter | Waiting on |")
        out.append("|---|---|")
        for k, v in p.BLOCKED.items():
            out.append(f"| `{k}` | {v} |")
    else:
        out.append("Nothing.")
    out.append("")

    OUT.write_text("\n".join(out))
    print(f"wrote {OUT.relative_to(Path.cwd())}  ({len(out)} lines)")


if __name__ == "__main__":
    main()
