"""Build, check and export. Run: .venv/bin/python cad/build.py"""

import struct
import sys
from math import asin, degrees, radians, sin
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import numpy as np
from build123d import Pos, export_step, export_stl

import logo
import model as m
import params as p

FAIL = []


def check(label, got, want, tol=0.01, unit="mm"):
    ok = abs(got - want) <= tol
    print(f"  {label:32s} {got:8.2f} {unit}   want {want:.2f}   {'ok' if ok else 'MISMATCH'}")
    if not ok:
        FAIL.append(label)


def open_edges(stl):
    """Mesh edges used by one triangle only: holes a slicer calls non-manifold.

    The B-rep checks above cannot see these. A face the mesher cannot
    triangulate is simply left out of the STL, and every edge around the gap
    goes open - which is how the first logo lid reached the slicer broken.
    """
    raw = stl.read_bytes()
    n = struct.unpack("<I", raw[80:84])[0]
    tri = np.frombuffer(raw[84:84 + 50 * n], dtype=np.dtype(
        [("n", "<f4", 3), ("v", "<f4", (3, 3)), ("a", "<u2")]))["v"]
    _, idx = np.unique(tri.reshape(-1, 3), axis=0, return_inverse=True)
    idx = idx.reshape(-1, 3)
    edges = np.sort(np.concatenate([idx[:, [0, 1]], idx[:, [1, 2]], idx[:, [2, 0]]]), axis=1)
    _, count = np.unique(edges, axis=0, return_counts=True)
    return int((count != 2).sum())


def save(part, sub, name, step=True):
    """STEP and STL side by side, one folder per thing you would print together."""
    d = m.OUT / sub
    d.mkdir(parents=True, exist_ok=True)
    if step:
        export_step(part, str(d / f"skladen2-{name}.step"))
    export_stl(part, str(d / f"skladen2-{name}.stl"))
    bad = open_edges(d / f"skladen2-{name}.stl")
    if bad:
        print(f"  skladen2-{name}.stl: {bad} non-manifold edges")
        FAIL.append(f"skladen2-{name}.stl mesh")


PARTS = {}   # shapes the multi-plate project is built from


def switch_window_variant():
    """ADR-0014: no shuttle; a window in the base's rear face with a plug in it, and the
    knob reached with a toothpick or tweezers. A separate export; device/ is untouched."""
    from build123d import Cylinder, Pos, Rot

    base_w, lid = m.build(switch_window=True)
    print("\nswitch window   slot %.1f wide in the wall, tunnel %.1f x %.1f through the tail"
          % (p.sw_win_w, p.sw_tun_w, p.sw_tun_h))
    n = len(base_w.solids())
    print(f"  {'base solids':32s} {n:8d}      want 1      {'ok' if n == 1 else 'DETACHED ISLAND'}")
    if n != 1:
        FAIL.append("switch-window base is not one solid")
    clash = (base_w & lid).volume
    print(f"  {'closed interference':32s} {clash:8.3f} mm3  want 0.00   "
          f"{'ok' if clash < 1.0 else 'COLLISION'}")
    if clash >= 1.0:
        FAIL.append("switch-window closed interference")

    # A toothpick (2.0 round) from outside the tail to the knob's face, at either end
    # of its travel and between: nothing of the base in the way.
    z_knob = p.base_floor_t + p.kbd_sw_knob_z
    worst = 0.0
    for x in (p.sw_knob_x_on, p.sw_win_xc, p.sw_knob_x_off):
        pick = Pos(x, (p.kbd_rear_y + 0.2 + p.base_y + 12) / 2, z_knob) * Rot(90, 0, 0) * Cylinder(
            1.0, p.base_y + 12 - p.kbd_rear_y - 0.2)
        worst = max(worst, (base_w & pick).volume)
    print(f"  {'toothpick to the knob':32s} {worst:8.3f} mm3  want 0.00   "
          f"{'ok' if worst < 0.01 else 'BLOCKED'}")
    if worst >= 0.01:
        FAIL.append("switch-window toothpick path blocked")

    save(base_w, "switch-window", "base-switchwindow")
    PARTS["base"] = base_w
    for clr in p.sw_plug_clr:
        plug = m.switch_plug(clr)
        hit = (plug & base_w).volume
        print(f"  {'plug, %.2f per side' % clr:32s} {hit:8.3f} mm3 in the base   "
              f"{'ok' if hit < 0.01 else 'INTERFERES'}")
        if hit >= 0.01:
            FAIL.append(f"switch plug {clr} interferes")
        # Nipple up, peg on the bed: the flange overhangs by about a millimetre.
        flat = Rot(X=90) * plug
        flat = Pos(0, 0, -flat.bounding_box().min.Z) * flat
        PARTS.setdefault("plugs", []).append((f"Plug {clr:.2f}", flat))
        save(flat, "switch-window", f"switch-plug-clr{clr:.2f}", step=False)
    print(f"  exported to {m.OUT / 'switch-window'}")


def bezel_variant(base):
    """ADR-0012: the lid with no tape, and the ring that holds the phone instead.

    A separate export; device/ is untouched. Same base, same hinge, same closed
    height - the ring replaces the tape's 1.0 rather than adding to the stack.
    """
    from math import atan, degrees
    from build123d import Rot

    _, lid_b = m.build(bezel=True)
    ring = m.bezel_ring()
    print(f"\nbezel variant   frame {p.bezel_t:.2f} thick, {p.bezel_overlap_side:.1f} over the"
          f" long edges, {p.bezel_overlap_top:.1f} over the notch end, {p.bezel_overlap_end:.1f} over the other")

    for name, part in (("lid", lid_b), ("ring", ring)):
        n = len(part.solids())
        print(f"  {name + ' solids':32s} {n:8d}      want 1      {'ok' if n == 1 else 'DETACHED ISLAND'}")
        if n != 1:
            FAIL.append(f"bezel {name} is {n} solids")

    closed = (base + lid_b).bounding_box().size.Z
    check("closed height", closed, p.closed_h_rear)
    clash = (base & lid_b).volume + (base & ring).volume
    print(f"  {'closed interference':32s} {clash:8.3f} mm3  want 0.00   {'ok' if clash < 1.0 else 'COLLISION'}")
    if clash >= 1.0:
        FAIL.append("bezel closed interference")

    # The lid's rear edge carries a 45 deg chamfer in this variant (no supports when
    # printed on its back), which sits a little outside the hinge cylinder: sweep it.
    from build123d import Axis
    hinge = Axis((0, p.hinge_axis_y, p.hinge_axis_z), (1, 0, 0))
    worst = max((base & lid_b.rotate(hinge, -(a + p.close_tilt))).volume
                for a in (0, 15, 30, 45, 60, 90, 120, 150, 180))
    print(f"  {'opening sweep, worst':32s} {worst:8.3f} mm3  want < 1.00   "
          f"{'ok' if worst < 1.0 else 'COLLISION'}")
    if worst >= 1.0:
        FAIL.append("bezel opening sweep")

    # The ring seats in the lid without touching it, and clears the phone's glass
    # by the play - and still covers it, which is its whole job.
    seat = (ring & lid_b).volume
    print(f"  {'ring vs lid':32s} {seat:8.3f} mm3  want 0.00   {'ok' if seat < 0.01 else 'COLLISION'}")
    if seat >= 0.01:
        FAIL.append("bezel ring collides with lid")
    ph_y0 = p.phone_front_wall + p.clr_phone
    phone = m._slab(-p.phone_x / 2, p.phone_x / 2, ph_y0, ph_y0 + p.phone_y,
                    p.bezel_phone_off, p.pocket_z) & m.rounded_outline(
        p.phone_x, p.phone_y, ph_y0, p.phone_corner_r_front, p.phone_corner_r_rear)
    hit = (ring & phone).volume
    print(f"  {'ring vs phone':32s} {hit:8.3f} mm3  want 0.00   {'ok' if hit < 0.01 else 'PRESSES'}")
    if hit >= 0.01:
        FAIL.append("bezel ring presses the phone")
    # The crush ribs (ADR-0015): the phone, centred, must meet them - and only them.
    squeeze = (phone & lid_b).volume
    print(f"  {'phone meets the crush ribs':32s} {squeeze:8.3f} mm3  want > 0     "
          f"{'ok' if squeeze > 0 else 'NO RIBS TOUCH'}")
    if squeeze <= 0:
        FAIL.append("phone ribs do not touch the phone")
    clip_cut = sum((c[1] & m.phone_ribs(p.phone_x + 2 * p.clr_phone, p.phone_front_wall,
                                        p.phone_y + 2 * p.clr_phone)).volume for c in m.clips())
    print(f"  {'clip slots cutting the ribs':32s} {clip_cut:8.3f} mm3  want 0.00   "
          f"{'ok' if clip_cut < 0.01 else 'CLIPS CUT RIBS'}")
    if clip_cut >= 0.01:
        FAIL.append("clip slots cut the phone ribs")
    # Button tabs (ADR-0016): at rest each key is free of its tongue, and pushed in by the
    # pre-travel plus a little it meets it. The keys' height is ASSUMED (3.0, centred).
    if p.button_tabs:
        kz = p.bezel_phone_off + p.phone_z / 2
        ky0 = p.phone_front_wall + p.clr_phone
        sh = p.button_key_shift
        for name, kx0, kx1 in (("volume down", -49.85 + sh, -39.15 + sh), ("volume up", -39.15 + sh, -28.45 + sh),
                               ("power", -19.85 + sh, -9.95 + sh)):
            key = m._slab(kx0, kx1, ky0 - p.button_proud, ky0, kz - 1.5, kz + 1.5)
            rest = (key & lid_b).volume
            pushed = (Pos(0, -(p.button_tab_pre + 0.05), 0) * key & lid_b).volume
            print(f"  {'key ' + name + ' at rest / pushed':32s} {rest:8.3f} / {pushed:6.2f} mm3  "
                  f"want 0 / > 0   {'ok' if rest < 0.01 and pushed > 0.1 else 'TAB MISSES'}")
            if rest >= 0.01 or pushed <= 0.1:
                FAIL.append(f"button tab {name}")
        # The volume split is not measured: keys stretched toward each other, as far as the
        # nubs' spacing allows, must still be pressed by their own tongue only.
        for name, kx0, kx1, other in (("volume down", -49.85 + sh, -31.4, "x > -31.5"),
                                      ("volume up", -44.0, -28.45 + sh, "x < -44.1")):
            key = Pos(0, -(p.button_tab_pre + 0.05), 0) * m._slab(
                kx0, kx1, ky0 - p.button_proud, ky0, kz - 1.5, kz + 1.5)
            hit = key & lid_b
            xs = [v.X for v in hit.vertices()]
            wrong = (max(xs) > -31.5) if other == "x > -31.5" else (min(xs) < -44.1)
            print(f"  {'stretched ' + name + ' hits only its own':32s} {'ok' if not wrong else 'HITS BOTH':>8s}")
            if wrong:
                FAIL.append(f"stretched {name} key reaches the other tongue")
    covered = (m._slab(-p.phone_x / 2, p.phone_x / 2, ph_y0, ph_y0 + p.phone_y, 0.0, p.bezel_t)
               & m.rounded_outline(p.phone_x, p.phone_y, ph_y0,
                                   p.phone_corner_r_front, p.phone_corner_r_rear)
               & ring).volume
    print(f"  {'ring over the phone face':32s} {covered:8.1f} mm3  want > 0   "
          f"{'ok' if covered > 1.0 else 'DOES NOT COVER'}")
    if covered <= 1.0:
        FAIL.append("bezel does not cover the phone")

    # Wall left under the slots: the phone sits 1.0 deeper, and so do they.
    skin = p.lid_t - (p.bezel_phone_off + p.phone_z / 2 + p.phone_usbc_cut_h / 2)
    print(f"  {'rear skin left under the USB-C':32s} {skin:8.2f} mm   want >= 1.20  "
          f"{'ok' if skin >= 1.2 else 'THIN'}")
    if skin < 1.2:
        FAIL.append("bezel USB-C slot too deep")

    # Real slicer masses, not factors: lid, frame and base as printed. 150 deg is the
    # design target (ADR-0003) and what has to pass; 180 deg, the lid laid flat back, is
    # the theoretical worst case and is reported, not enforced.
    lid_print = p.slice_g_lid_bezel + p.slice_g_frame
    r_lid = p.base_depth_to_axis - (p.phone_front_wall + (p.phone_y + 2 * p.clr_phone) / 2)
    s_eff = p.foot_y_rear + p.foot_dia / 2 - p.base_depth_to_axis
    L, B = lid_print + p.phone_mass, p.slice_g_base + p.kbd_mass
    restoring = B * p.d_base + s_eff * (B + L)
    m150 = restoring / (L * r_lid * sin(radians(60)))
    m180 = restoring / (L * r_lid)
    print(f"  {'frame mass (model)':32s} {ring.volume * p.mat_density:8.1f} g   slicer {p.slice_g_frame:.2f} g")
    print(f"  {'tipping, slicer masses':32s} lid + frame {lid_print:.1f} g, base {p.slice_g_base:.1f} g   "
          f"margin @150 {m150:.3f} {'ok' if m150 >= 1 else 'TIPS'}   @180 {m180:.3f} (not enforced)")
    if m150 < 1:
        FAIL.append("tipping at 150 deg (bezel)")

    save(lid_b, "bezel", "lid-bezel")

    # The same logo recess as the device lid. The rear wall it is cut into is the
    # same, so the inlays in export/logo/ fit this lid too.
    inlays = logo.inlays()
    recess = None
    for part in inlays.values():
        recess = part if recess is None else recess + part
    lid_b_logo = lid_b - recess
    n = len(lid_b_logo.solids())
    print(f"  {'logo lid solids':32s} {n:8d}      want 1      {'ok' if n == 1 else 'DETACHED ISLAND'}")
    if n != 1:
        FAIL.append("bezel logo lid is not one solid")
    check("logo recess vs inlays", (lid_b & recess).volume,
          sum(part.volume for part in inlays.values()), tol=0.05, unit="mm3")
    clash = (lid_b_logo & ring).volume
    print(f"  {'logo lid vs frame':32s} {clash:8.3f} mm3  want 0.00   {'ok' if clash < 0.01 else 'COLLISION'}")
    if clash >= 0.01:
        FAIL.append("bezel logo lid meets the frame")
    save(lid_b_logo, "bezel", "lid-bezel-logo")

    # Both bodies in one file for a two-filament print: STEP carries each as a
    # separate coloured solid, 3MF as two objects; the slicer takes them as one
    # multi-part object and the colour goes to a filament.
    from build123d import Color, Compound, Mesher
    green = None
    for part in inlays.values():
        green = part if green is None else green + part
    body = lid_b_logo.moved(Pos(0, 0, 0))
    body.color, body.label = Color(0.18, 0.34, 0.82), "lid"
    green = green.moved(Pos(0, 0, 0))
    green.color, green.label = Color(0.15, 0.70, 0.35), "logo-inlay"
    d2 = m.OUT / "bezel"
    export_step(Compound(label="skladen2-lid-bezel-logo-2color", children=[body, green]),
                str(d2 / "skladen2-lid-bezel-logo-2color.step"))
    # One assembly object of two mesh parts and a single build item: what Orca and
    # Bambu take as one multi-part object. (build123d's Mesher writes two loose items.)
    import bambu_project
    import zipfile
    f3 = d2 / "skladen2-lid-bezel-logo-2color.3mf"
    meshes = []
    for shp in (lid_b_logo, green):
        vs, ts = bambu_project.welded(shp)
        assert not bambu_project.open_edges(ts), "open edges in the 2-colour 3mf"
        meshes.append((vs.tolist(), ts))
    res = []
    for i, ((vs, ts), name) in enumerate(zip(meshes, ("lid", "logo-inlay")), 1):
        v = "".join(f'<vertex x="{x:.5f}" y="{y:.5f}" z="{z:.5f}"/>' for x, y, z in vs)
        t = "".join(f'<triangle v1="{a}" v2="{b}" v3="{c}"/>' for a, b, c in ts)
        res.append(f'<object id="{i}" name="{name}" type="model"><mesh><vertices>{v}'
                   f'</vertices><triangles>{t}</triangles></mesh></object>')
    res.append('<object id="3" name="skladen2-lid-bezel-logo" type="model"><components>'
               '<component objectid="1"/><component objectid="2"/></components></object>')
    xml = ('<?xml version="1.0" encoding="UTF-8"?><model unit="millimeter" '
           'xml:lang="en-US" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">'
           f'<resources>{"".join(res)}</resources><build><item objectid="3"/></build></model>')
    with zipfile.ZipFile(f3, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", '<?xml version="1.0" encoding="UTF-8"?><Types '
                   'xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
                   '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
                   '<Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>')
        z.writestr("_rels/.rels", '<?xml version="1.0" encoding="UTF-8"?><Relationships '
                   'xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                   '<Relationship Target="/3D/3dmodel.model" Id="rel0" '
                   'Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
        z.writestr("3D/3dmodel.model", xml)
    back = Mesher().read(str(f3))
    print(f"  {'2-colour 3mf, parts read back':32s} {len(back):8d}      want 2      "
          f"{'ok' if len(back) == 2 else 'WRONG'}")
    if len(back) != 2:
        FAIL.append("bezel 2-colour 3mf")
    off = bambu_project.write(lid_b_logo, green, d2 / "skladen2-lid-bezel-logo-petg.3mf")
    print(f"  {'slicer project, inlay moved by':32s} {off:8.3f} mm   (template had it off)")
    save(ring, "bezel", "bezel")
    # The face is tilted with the keyboard's wedge, which a printer would see as a
    # ramp under a 0.8 part. Laid flat, face down, for printing.
    tilt = degrees(atan((p.rim_rear - p.rim_front) / p.base_depth_to_axis))
    flat = Rot(X=-tilt) * ring
    flat = Pos(0, 0, -flat.bounding_box().min.Z) * flat
    check("flat frame height", flat.bounding_box().size.Z, p.clip_arm_top, tol=0.35)
    save(flat, "bezel", "bezel-flat", step=False)
    PARTS["frame"] = flat

    # The frame closed over the buttons (ADR-0016): no cut-out, no legs; the tongues are
    # pressed from the front edge, under the plate. Only meaningful with the tongues.
    if p.button_tabs:
        closed = m.bezel_frame(closed=True)
        n = len(closed.solids())
        print(f"  {'closed frame solids':32s} {n:8d}      want 1      {'ok' if n == 1 else 'DETACHED ISLAND'}")
        if n != 1:
            FAIL.append("closed frame is not one solid")
        hit = (closed & lid_b).volume
        print(f"  {'closed frame vs lid':32s} {hit:8.3f} mm3  want 0.00   {'ok' if hit < 0.01 else 'COLLISION'}")
        if hit >= 0.01:
            FAIL.append("closed frame collides with lid")
        save(closed, "bezel", "bezel-closed")
        flat_c = Rot(X=-tilt) * closed
        flat_c = Pos(0, 0, -flat_c.bounding_box().min.Z) * flat_c
        save(flat_c, "bezel", "bezel-closed-flat", step=False)
        PARTS["frame_closed"] = flat_c
    PARTS["lid"], PARTS["inlay"] = lid_b_logo, green

    # The through-logo lid: the recess and the inlay go the whole way through the 1.2 rear
    # wall instead of half of it. Same lid otherwise, so plate 4 can never drift from plate 1.
    deep = logo.inlays(p.lid_rear_wall)
    recess_t = None
    for part in deep.values():
        recess_t = part if recess_t is None else recess_t + part
    lid_through = lid_b - recess_t
    clash = (lid_through & recess_t).volume
    print(f"  {'through lid vs its inlay':32s} {clash:8.3f} mm3  want 0.00   "
          f"{'ok' if clash < 0.01 else 'COLLISION'}")
    if clash >= 0.01:
        FAIL.append("through lid meets its inlay")
    save(lid_through, "bezel", "lid-bezel-logo-through")
    PARTS["lid_through"], PARTS["inlay_through"] = lid_through, recess_t
    print(f"  exported to {m.OUT / 'bezel'}")


def adapter_variant(base):
    """ADR-0013: the bezel lid with a seat for the USB-C extender, and a coupon of the
    lid's right end to try the real adapter in before the whole lid is printed."""
    _, lid_a = m.build(bezel=True, seat=True)
    print("\nadapter seat    extender body "
          f"{p.adapter_body_w_ASSUMED} x {p.adapter_body_t_ASSUMED} x {p.adapter_body_len_ASSUMED} (ASSUMED)")
    n = len(lid_a.solids())
    print(f"  {'seat lid solids':32s} {n:8d}      want 1      {'ok' if n == 1 else 'DETACHED ISLAND'}")
    if n != 1:
        FAIL.append("adapter lid is not one solid")
    clash = (base & lid_a).volume
    print(f"  {'closed interference':32s} {clash:8.3f} mm3  want 0.00   {'ok' if clash < 1.0 else 'COLLISION'}")
    if clash >= 1.0:
        FAIL.append("adapter lid closed interference")

    # The extender's body, seated, against the seat. It squeezes the ribs and the ridge
    # by design (a press fit); anything else it touches is a mistake.
    x0, x1 = m.adapter_dims()
    uy = p.phone_front_wall + (p.phone_y + 2 * p.clr_phone) / 2
    axis = p.bezel_phone_off + p.phone_z / 2
    w, t = p.adapter_body_w_ASSUMED, p.adapter_body_t_ASSUMED

    def body(dx=0.0, dz=0.0, width=w):
        return m._slab(x0 + dx, x1 + dx, uy - width / 2, uy + width / 2,
                       axis - t / 2 + dz, axis + t / 2 + dz)

    squeeze = (body() & lid_a).volume
    print(f"  {'body squeezes ribs + ridges':32s} {squeeze:8.3f} mm3  want > 0     {'ok' if squeeze > 0 else 'LOOSE'}")
    if squeeze <= 0:
        FAIL.append("adapter seat does not grip")
    loose = (body(width=w - 2 * (p.adapter_rib_h - p.adapter_seat_clr) - 0.05) & lid_a).volume
    print(f"  {'body 0.6 narrower touches':32s} {loose:8.3f} mm3  want 0.00   {'ok' if loose < 0.01 else 'FOULED'}")
    if loose >= 0.01:
        FAIL.append("adapter seat fouls a narrow body")
    lifted = (body(dz=-0.5) & lid_a).volume
    print(f"  {'body lifted 0.5 meets ridge':32s} {lifted:8.3f} mm3  want > 0     {'ok' if lifted > 0 else 'NO DETENT'}")
    if lifted <= 0:
        FAIL.append("adapter ridge does not catch")
    # The cable's overmould, from the body's socket face to the lid's end, must be as free
    # as it was without the seat.
    cable = m._slab(x1, p.lid_x / 2, uy - p.phone_usbc_cut_w / 2, uy + p.phone_usbc_cut_w / 2,
                    axis - p.phone_usbc_cut_h / 2, axis + p.phone_usbc_cut_h / 2)
    base_lid = m.lid_shell(True, False)
    dv = (cable & lid_a).volume - (cable & base_lid).volume
    print(f"  {'seat in the cable zone':32s} {dv:8.3f} mm3  want 0.00   {'ok' if abs(dv) < 0.01 else 'BLOCKED'}")
    if abs(dv) >= 0.01:
        FAIL.append("adapter seat blocks the cable")
    save(lid_a, "adapter", "lid-bezel-adapter")
    coupon = m.usbc_coupon(lid_a)
    save(coupon, "adapter", "coupon-usbc-lid")
    # For printing: the face's wedge levelled, then the lid turned over onto its rear wall,
    # screen side up, so the seat prints without bridges.
    from math import atan, degrees
    from build123d import Rot
    import bambu_project
    tilt = degrees(atan((p.rim_rear - p.rim_front) / p.base_depth_to_axis))
    flat = Rot(Y=180) * (Rot(X=-tilt) * coupon)
    flat = Pos(0, 0, -flat.bounding_box().min.Z) * flat
    bb = flat.bounding_box()
    print(f"  {'coupon, printing pose':32s} {bb.size.X:.1f} x {bb.size.Y:.1f} x {bb.size.Z:.1f} mm")
    bambu_project.write_single(flat, m.OUT / "adapter" / "skladen2-coupon-usbc-lid.3mf", "coupon-usbc-lid")


def main():
    base, lid = m.build()

    print("parts")
    for name, part in (("base", base), ("lid", lid)):
        bb = part.bounding_box()
        print(f"  {name:6s} {bb.size.X:7.2f} x {bb.size.Y:7.2f} x {bb.size.Z:6.2f}"
              f"   {part.volume/1000:6.1f} cm3   {part.volume*p.mat_density:5.1f} g")

    # One part must be ONE solid. A floating island slices as a separate object
    # and lifts off the bed: the lid's middle knuckle did exactly that, because
    # the station relief was cut across its own band and severed it from the lid.
    print("\nconnectivity")
    for name, part in (("base", base), ("lid", lid)):
        n = len(part.solids())
        print(f"  {name + ' solids':32s} {n:8d}      want 1      "
              f"{'ok' if n == 1 else 'DETACHED ISLAND'}")
        if n != 1:
            FAIL.append(f"{name} is {n} solids")

    # A bolt head that cannot travel down the axis into its pocket is a joint
    # that cannot be assembled at all - and neither the interference check nor
    # the opening sweep notices, because the obstruction is coaxial with the
    # hinge and so moves with it. This is what killed the centre station.
    print("\nassembly access")
    half = p.station_w / 2
    for x0 in p.station_x:
        s_dir = m.outboard(x0)
        corridor = m.x_cyl(p.head_dia + 0.1, 30,
                           x0 + s_dir * (half + 15), p.hinge_axis_y, p.hinge_axis_z)
        blocked = ((base + lid) & corridor).volume
        label = f"bolt head corridor X={x0:+.1f}"
        print(f"  {label:32s} {blocked:8.1f} mm3  want 0.00   "
              f"{'ok' if blocked < 1.0 else 'OBSTRUCTED'}")
        if blocked >= 1.0:
            FAIL.append(label)

    print("\ngeometry")
    closed = (base + lid).bounding_box()
    check("closed height", closed.size.Z, p.closed_h_rear)
    check("footprint Y", closed.size.Y, p.base_y)
    check("footprint X", closed.size.X, p.base_x)

    # The lid's knuckles legitimately overhang its rear face by one radius.
    check("lid depth incl. rounded rear", lid.bounding_box().size.Y,
          p.base_depth_to_axis + p.lid_rear_radius)
    # Base knuckles rise above the parting plane but must stay inside the lid.
    check("base top (knuckles)", base.bounding_box().size.Z,
          p.hinge_axis_z + p.knuckle_od / 2)

    # The assertion that actually matters: the two halves do not occupy the same
    # space when closed. Anything but ~0 means a collision.
    clash = (base & lid).volume
    print(f"  {'closed interference':32s} {clash:8.3f} mm3  want 0.00   "
          f"{'ok' if clash < 1.0 else 'COLLISION'}")
    if clash >= 1.0:
        FAIL.append("closed interference")

    # --- phone ports -------------------------------------------------------
    # A plug's axis must run from the phone's port out through the lid's end
    # without touching the lid or the base, closed. The jack's is new here.
    print("\nphone ports   (rod from the port out through the lid's end, closed)")
    slope = (p.rim_rear - p.rim_front) / p.base_depth_to_axis
    py0 = p.phone_front_wall + p.clr_phone
    ph_end = p.phone_x / 2 + p.clr_phone + p.tape_t
    for label, sign, y, d in (
            ("headphone jack, -X", -1, py0 + p.phone_jack_from_edge, 3.5),
            ("USB-C, +X", 1, p.phone_front_wall + p.clr_phone + p.phone_y / 2, None)):
        z = p.rim_front + slope * y + p.phone_z / 2
        length, xc = p.lid_x / 2 - ph_end + 4.0, sign * (ph_end + p.lid_x / 2 + 4.0) / 2
        # The jack's tip is round; the USB-C receptacle is a 8.3 x 2.6 slot.
        rod = (m.x_cyl(d, length, xc, y, z) if d
               else m.box_between(xc - length / 2, xc + length / 2, y - 4.15, y + 4.15, z - 1.3, z + 1.3))
        hit = (rod & lid).volume + (rod & base).volume
        print(f"  {label:32s} {hit:8.3f} mm3  want 0.00   {'ok' if hit < 0.01 else 'BLOCKED'}")
        if hit >= 0.01:
            FAIL.append(f"{label} blocked")

    # --- mass and balance, from the geometry ---
    # Solid is the 100%-infill upper bound; printed is a rough lower bound at
    # typical settings. The real figure is whatever the slicer says.
    lid_solid = lid.volume * p.mat_density
    base_solid = base.volume * p.mat_density
    lid_print = lid_solid * 0.63   # this lid is ~1/3 chunky blocks
    base_print = base_solid * 0.69
    r_lid = p.base_depth_to_axis - (p.phone_front_wall + (p.phone_y + 2 * p.clr_phone) / 2)

    print(f"\nmass                       solid    printed(est)")
    print(f"  lid shell             {lid_solid:7.1f}  {lid_print:9.1f} g")
    print(f"  base shell            {base_solid:7.1f}  {base_print:9.1f} g")
    tot_s = lid_solid + base_solid + p.phone_mass + p.kbd_mass
    tot_p = lid_print + base_print + p.phone_mass + p.kbd_mass
    print(f"  assembly              {tot_s:7.1f}  {tot_p:9.1f} g    N4 budget {p.N4_BUDGET:.0f}")
    if tot_p > p.N4_BUDGET:
        print("  OVER BUDGET even at printed estimate"); FAIL.append("N4 mass")

    # The contact line is where the REAR FEET touch, not the tail's rear edge.
    s_eff = p.foot_y_rear + p.foot_dia / 2 - p.base_depth_to_axis
    print(f"\nbalance   (r_lid {r_lid:.2f} mm, effective setback {s_eff:.1f} mm"
          f" - set by the rear feet, not the tail edge)")
    for label, ls, bs in (("solid", lid_solid, base_solid),
                          ("printed est", lid_print, base_print)):
        L, B = ls + p.phone_mass, bs + p.kbd_mass
        restoring = B * p.d_base + s_eff * (B + L)
        m150 = restoring / (L * r_lid * sin(radians(60)))
        m180 = restoring / (L * r_lid)
        flag = "" if min(m150, m180) >= 1 else "   TIPS"
        print(f"  {label:12s} lid {L:5.0f} g  base {B:5.0f} g"
              f"   margin @150 {m150:5.3f}  @180 {m180:5.3f}{flag}")
        if min(m150, m180) < 1:
            FAIL.append(f"tipping ({label})")

    # --- opening sweep: the reason the lid is shallower than the base -------
    # clamshell-geometry.md argues a flush lid would not open at all. This is
    # that argument, checked rather than asserted.
    from build123d import Axis
    axis = Axis((0, p.hinge_axis_y, p.hinge_axis_z), (1, 0, 0))
    print("\nopening sweep (interference of lid against base, mm3)")
    worst = 0.0
    for opening in (0, 30, 60, 90, 120, 150, 180):
        turn = -(opening + p.close_tilt)
        clash = (base & lid.rotate(axis, turn)).volume
        worst = max(worst, clash)
        print(f"  {opening:3d} deg   {clash:9.3f}   {'ok' if clash < 1.0 else 'COLLISION'}")
    if worst >= 1.0:
        FAIL.append("opening sweep")

    # --- power-switch shuttle ---------------------------------------------
    # It has to slide the whole way without touching the base, drive the knob
    # at either reading of its height, and be unable to leave through the rear.
    print(f"\npower-switch shuttle   knob travel {p.kbd_sw_travel:.2f}, "
          f"ON at X {p.sw_knob_x_on:.2f}, OFF at {p.sw_knob_x_off:.2f}")
    lo, hi = p.sw_knob_x_on - p.sw_overtravel, p.sw_knob_x_off + p.sw_overtravel
    niche_z = (p.kbd_sw_knob_z, 3.24 + p.kbd_sw_niche_h / 2)   # direct, and from the niche
    for label, x in (("at the ON end of its slot", lo), ("ON", p.sw_knob_x_on),
                     ("OFF", p.sw_knob_x_off), ("at the OFF end of its slot", hi)):
        sh = m.switch_shuttle(x)
        clash = (base & sh).volume
        print(f"  {'vs base ' + label:32s} {clash:8.3f} mm3  want 0.00   "
              f"{'ok' if clash < 0.01 else 'BINDS'}")
        if clash >= 0.01:
            FAIL.append(f"shuttle binds {label}")
    for label, x in (("ON", p.sw_knob_x_on), ("OFF", p.sw_knob_x_off)):
        sh = m.switch_shuttle(x)
        for z in niche_z:
            knob = m.switch_knob(x, p.base_floor_t + z)
            hit = (knob & sh).volume + (knob & base).volume
            # Pushed half a clearance toward the knob, a prong must meet it.
            push = m.switch_shuttle(x + (p.sw_fork_clr + 0.05) * (1 if label == "ON" else -1))
            drives = (knob & push).volume > 0.01
            ok = hit < 0.01 and drives
            print(f"  {f'knob {label}, centre Z {z:.2f}':32s} {hit:8.3f} mm3  "
                  f"{'drives' if drives else 'MISSES'}      {'ok' if ok else 'FAIL'}")
            if not ok:
                FAIL.append(f"knob {label} at Z {z:.2f}")
    # Fingers in the niche, beside the knob, at either end of its travel and at
    # either reading of the niche's height. The keyboard around the niche is a slab
    # behind its rear face with the niche taken out.
    for z in niche_z:
        zc = p.base_floor_t + z
        for label, x in (("ON", p.sw_knob_x_on), ("OFF", p.sw_knob_x_off)):
            face = m.box_between(x - 10, x + 10, p.kbd_rear_y - 3, p.kbd_rear_y,
                                 p.base_floor_t, p.base_floor_t + p.kbd_h_rear)
            face -= m.box_between(p.sw_niche_x1 - p.kbd_sw_niche_w, p.sw_niche_x1,
                                  p.kbd_rear_y - 4, p.kbd_rear_y + 1,
                                  zc - p.kbd_sw_niche_h / 2, zc + p.kbd_sw_niche_h / 2)
            hit = (face & m.switch_shuttle(x)).volume
            print(f"  {f'fingers in niche {label}, Z {z:.2f}':32s} {hit:8.3f} mm3  want 0.00   "
                  f"{'ok' if hit < 0.01 else 'JAMS'}")
            if hit >= 0.01:
                FAIL.append(f"fingers jam niche {label} at Z {z:.2f}")
    # Pulled back to seat the keyboard: clear of it, and still free in the base.
    sh = m.switch_shuttle(back=p.sw_retract)
    reach = p.kbd_rear_y - sh.bounding_box().min.Y
    clash = (base & sh).volume
    ok = reach < 0 and clash < 0.01
    print(f"  {'pulled back, fingers out':32s} {-reach:8.2f} mm   clear of the keyboard, "
          f"{clash:.3f} mm3 vs base   {'ok' if ok else 'FAIL'}")
    if not ok:
        FAIL.append("shuttle cannot clear the keyboard")
    sh = m.switch_shuttle()
    pulled = (base & Pos(0, p.sw_retract + 1.0, 0) * sh).volume
    print(f"  {'held from leaving by the rear':32s} {pulled:8.1f} mm3  want > 0   "
          f"{'ok' if pulled > 1.0 else 'FALLS OUT'}")
    if pulled <= 1.0:
        FAIL.append("shuttle not retained")
    under = m.base_station(p.station_x[1]).bounding_box().min.Z - sh.bounding_box().max.Z
    print(f"  {'clear under the station posts':32s} {under:8.2f} mm   want > 0    "
          f"{'ok' if under > 0 else 'CLASH'}")
    if under <= 0:
        FAIL.append("shuttle meets station posts")
    n = len(base.solids())
    if n != 1:
        FAIL.append("base split by switch cut")
    # The stem stands out of the rear face, so the lid must clear it all the way open.
    for opening in (0, 30, 60, 90, 120, 150, 180):
        clash = (sh & lid.rotate(axis, -(opening + p.close_tilt))).volume
        if clash >= 0.01:
            print(f"  {f'vs lid at {opening} deg':32s} {clash:8.3f} mm3  want 0.00   COLLISION")
            FAIL.append(f"shuttle meets lid at {opening} deg")
    print(f"  {'clear of the lid, 0-180 deg':32s} {'':8s}      "
          f"{'ok' if not any('meets lid' in f for f in FAIL) else 'COLLISION'}")
    # One per stem length, to print as a set and pick from. Moved to the origin
    # by whole millimetres: an exact offset leaves vertices a rounding error
    # either side of zero, and the STL opens along them.
    for f in (m.OUT / "switch").rglob("skladen2-switch-shuttle*"):
        f.unlink()
    for d in (m.OUT / "switch").glob("finger*"):
        d.rmdir()
    for finger in p.sw_finger_len:
        for proud in p.sw_stem_proud:
            sh = m.switch_shuttle(proud=proud, finger=finger)
            sh_print = Pos(-round(p.sw_knob_x_on), -round(p.sw_head_y0), -round(p.sw_z0)) * sh
            # A folder per finger length, STL only: these are printed, never edited.
            save(sh_print, f"switch/finger{finger:.1f}",
                 f"switch-shuttle-finger{finger:.1f}-proud{proud:.1f}", step=False)
    print(f"  exported fingers {', '.join(f'{v:.1f}' for v in p.sw_finger_len)} into the niche,"
          f" each with stems proud by {', '.join(f'{v:.1f}' for v in p.sw_stem_proud)}")

    cb, cl = m.coupon(base, lid)
    print(f"\ncoupon 2.1   base {cb.volume/1000:.1f} cm3   lid {cl.volume/1000:.1f} cm3")

    # Phone-fit coupon: the lid's left end only, with everything new in Skladen 2.
    pc = m.phone_coupon(lid)
    n = len(pc.solids())
    print(f"phone coupon   lid {pc.volume/1000:.1f} cm3   {pc.volume*p.mat_density:.0f} g solid   "
          f"{'one solid' if n == 1 else f'{n} SOLIDS'}")
    if n != 1:
        FAIL.append("phone coupon is not one solid")
    save(pc, "coupon-phone", "coupon-phone-lid")

    # The same coupon from the bezel lid (ADR-0015), longer so it takes in the rib on the
    # front wall at X 17 and the one on the rear wall at 18 as well as the left end's.
    # The bezel frame itself is not in it: try the phone alone, then the frame from a
    # full print.
    from math import atan, degrees
    from build123d import Rot
    import bambu_project
    _, lid_rb = m.build(bezel=True)
    pcb = m.phone_coupon(lid_rb, x1=24.0)
    n = len(pcb.solids())
    print(f"phone coupon (bezel lid, ribs)   {pcb.volume/1000:.1f} cm3   "
          f"{'one solid' if n == 1 else f'{n} SOLIDS'}")
    if n != 1:
        FAIL.append("bezel phone coupon is not one solid")
    save(pcb, "coupon-phone", "coupon-phone-lid-ribs")
    tilt = degrees(atan((p.rim_rear - p.rim_front) / p.base_depth_to_axis))

    def laid_flat(part):
        flat = Rot(Y=180) * (Rot(X=-tilt) * part)
        return Pos(0, 0, -flat.bounding_box().min.Z) * flat

    bambu_project.write_single(laid_flat(pcb), m.OUT / "coupon-phone" / "skladen2-coupon-phone-lid-ribs.3mf",
                               "coupon-phone-lid-ribs")
    # The same coupon with taller ribs (the first one, 0.40, left the phone loose on the
    # 2026-10-23 print): 0.2 per side of squeeze at 0.50, 0.3 at 0.60, 0.4 at 0.70.
    for h in (0.50, 0.60, 0.70):
        _, lid_h = m.build(bezel=True, rib_h=h)
        part = m.phone_coupon(lid_h, x1=24.0)
        name = f"coupon-phone-lid-ribs-h{h:.2f}"
        if h != 0.60:      # 0.60 is already printed; the plates file carries the others
            PARTS.setdefault("coupons", {})[f"Ribs {h:.2f}, tab 1.0"] = laid_flat(part)
        save(part, "coupon-phone", name, step=False)
        bambu_project.write_single(laid_flat(part), m.OUT / "coupon-phone" / f"skladen2-{name}.3mf", name)
        print(f"  ribs {h:.2f}: {len(part.solids())} solid(s)")
    # The whole lid in the same five variants, for the plates: ribs 0.50 / 0.60 / 0.70 with the
    # 1.0 tongue, and 0.8 / 1.2 tongues at ribs 0.60. Plain lids, no logo.
    PARTS["variants"] = {}
    deep_inlay = None
    for part in logo.inlays(p.lid_rear_wall).values():
        deep_inlay = part if deep_inlay is None else deep_inlay + part
    for label, kw in (("Ribs 0.50, tab 1.0", dict(rib_h=0.50)), ("Ribs 0.60, tab 1.0", dict(rib_h=0.60)),
                      ("Ribs 0.70, tab 1.0", dict(rib_h=0.70)),
                      ("Ribs 0.60, tab 0.8", dict(rib_h=0.60, tab_t=0.8)),
                      ("Ribs 0.60, tab 1.2", dict(rib_h=0.60, tab_t=1.2))):
        _, lid_v = m.build(bezel=True, **kw)
        n = len(lid_v.solids())
        if n != 1:
            FAIL.append(f"lid variant {label} is {n} solids")
        # with the dog cut through the rear wall, as plate 4's lid has it
        lid_v = lid_v - deep_inlay
        file = "lid-bezel-rib{:.2f}-tab{:.1f}-through".format(kw["rib_h"], kw.get("tab_t", 1.0))
        save(lid_v, "lid-variants", file, step=False)
        PARTS["variants"][label] = lid_v
        print(f"  lid variant {label}: {n} solid(s)")
    save(deep_inlay, "lid-variants", "logo-through-inlay", step=False)
    # The same coupon with the other tongue thicknesses, to pick the push by feel.
    # (at ribs 0.60, the height to try first; the 1.0 one is `-ribs-h0.60`)
    for t in (0.8, 1.2):
        _, lid_t = m.build(bezel=True, tab_t=t, rib_h=0.60)
        part = m.phone_coupon(lid_t, x1=24.0)
        name = f"coupon-phone-lid-ribs-tab{t:.1f}"
        PARTS["coupons"][f"Ribs 0.60, tab {t:.1f}"] = laid_flat(part)
        save(part, "coupon-phone", name, step=False)
        bambu_project.write_single(laid_flat(part), m.OUT / "coupon-phone" / f"skladen2-{name}.3mf", name)
        print(f"  tongue {t:.1f}: {len(part.solids())} solid(s)")
    # The coupons not yet printed, two to a plate, in one Bambu project of their own.
    cp = PARTS["coupons"]
    order = [["Ribs 0.50, tab 1.0", "Ribs 0.70, tab 1.0"], ["Ribs 0.60, tab 0.8", "Ribs 0.60, tab 1.2"]]
    bambu_project.write_plates(
        m.OUT / "coupon-phone" / "skladen2-coupon-phone-plates.3mf", None, None,
        [[(f"Coupon {n}", cp[n], 3) for n in row] for row in order],
        plate_names=[f"{i} Coupons: " + " + ".join(n.replace("Ribs ", "ribs ").replace("tab", "tab")
                                                     for n in row) for i, row in enumerate(order, 1)])

    for sub, name, part in (("device", "base", base), ("device", "lid", lid),
                            ("coupon21", "coupon21-base", cb),
                            ("coupon21", "coupon21-lid", cl)):
        save(part, sub, name)
    print(f"exported to {m.OUT}")

    # Logo: the lid with a recess, and the inlay to fill it. The
    # device/ lid is left plain; this is a variant of it, printed instead.
    inlays = logo.inlays()
    recess = None
    for part in inlays.values():
        recess = part if recess is None else recess + part
    lid_logo = lid - recess
    print(f"\nlogo   {p.logo_height:.0f} mm tall, {p.logo_depth:.2f} deep, "
          f"{'upright when open' if p.logo_reads_open else 'upright when closed'}")
    n = len(lid_logo.solids())
    print(f"  {'lid solids':32s} {n:8d}      want 1      {'ok' if n == 1 else 'DETACHED ISLAND'}")
    if n != 1:
        FAIL.append("logo lid is not one solid")
    # The inlays must exactly fill what the recess took out. Less taken than
    # filled means an inlay pokes out of the lid - past its face, or through the
    # rear wall into the phone pocket or the camera cutout.
    filled = sum(part.volume for part in inlays.values())
    # Measured as what the lid and the recess share, not as the difference of two
    # whole-lid volumes: those carry ~0.05 mm3 of B-rep rounding on 80 cm3, which
    # sat just under the tolerance on Mk3 and just over it here.
    check("recess taken vs inlays", (lid & recess).volume, filled, tol=0.05, unit="mm3")
    names = list(inlays)
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            clash = (inlays[a] & inlays[b]).volume
            if clash >= 0.01:
                print(f"  inlays {a} and {b} overlap by {clash:.3f} mm3")
                FAIL.append(f"logo {a}/{b} overlap")
    save(lid_logo, "logo", "lid-logo")
    for name, part in inlays.items():
        save(part, "logo", f"logo-{name}")
        print(f"  {'inlay ' + name:32s} {part.volume:8.1f} mm3")

    # Plain-nut variant of the base. Only the base carries the nut pocket, so the
    # lid is shared. A shallower pocket is strictly more material than the part
    # checked above, so it gets the two checks that could still fail.
    base_pn, _ = m.build(nut_depth=p.nut_depth_plain)
    print(f"\nplain-nut variant   DIN 934, pocket {p.nut_depth_plain:.2f}")
    n = len(base_pn.solids())
    clash = (base_pn & lid).volume
    print(f"  {'base solids':32s} {n:8d}      want 1      {'ok' if n == 1 else 'DETACHED ISLAND'}")
    print(f"  {'closed interference':32s} {clash:8.3f} mm3  want 0.00   "
          f"{'ok' if clash < 1.0 else 'COLLISION'}")
    if n != 1:
        FAIL.append("plain-nut base is not one solid")
    if clash >= 1.0:
        FAIL.append("plain-nut closed interference")
    cb_pn, _ = m.coupon(base_pn, lid)
    for name, part in (("base-plainnut", base_pn), ("coupon21-base-plainnut", cb_pn)):
        save(part, "plainnut", name)
    print(f"  exported to {m.OUT / 'plainnut'}")

    bezel_variant(base)
    # ADR-0013 is parked (2026-10-23): no USB-C extender for now. adapter_variant() and
    # export/adapter/ stay as they were; switch the call back on to rebuild them.
    # adapter_variant(base)
    switch_window_variant()
    import bambu_project
    where = bambu_project.write_plates(
        m.OUT / "skladen2-2.1-plates.3mf", PARTS["lid"], PARTS["inlay"],
        [[("Frame", PARTS["frame"], 3)],
         [("Base, switch window", PARTS["base"], 3)]
         + [(n, sh, 3) for n, sh in PARTS["plugs"]],
         # plates 5 to 8, after the through-logo lid (plate 4)
         [("Frame, closed over the buttons", PARTS["frame_closed"], 3)],
         ],
        through=(PARTS["lid_through"], PARTS["inlay_through"]), through_index=3,
        # plates 6 to 10: the whole lid in five variants, dog cut through, one to a plate
        extra=[("Lid " + n, PARTS["variants"][n], PARTS["inlay_through"], pi, dy)
               for n, pi, dy in (("Ribs 0.50, tab 1.0", 5, 0.0), ("Ribs 0.60, tab 1.0", 6, 0.0),
                                 ("Ribs 0.70, tab 1.0", 7, 0.0), ("Ribs 0.60, tab 0.8", 8, 0.0),
                                 ("Ribs 0.60, tab 1.2", 9, 0.0))],
        plate_names=["1 Lid, logo", "2 Frame", "3 Base, switch window + plugs",
                     "4 Lid, through logo", "5 Frame, closed over buttons",
                     "6 Lid ribs 0.50 tab 1.0", "7 Lid ribs 0.60 tab 1.0",
                     "8 Lid ribs 0.70 tab 1.0", "9 Lid ribs 0.60 tab 0.8",
                     "10 Lid ribs 0.60 tab 1.2"])
    print("\nall plates in one project:", ", ".join(f"{n} -> plate {i}" for n, i in where.items()))

    # Keep docs/parameters.md from drifting: regenerate it every build.
    import gen_params_doc
    gen_params_doc.main()

    if FAIL:
        print(f"\nFAILED: {', '.join(FAIL)}")
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
