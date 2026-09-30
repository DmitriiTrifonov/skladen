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


def save(part, sub, name):
    """STEP and STL side by side, one folder per thing you would print together."""
    d = m.OUT / sub
    d.mkdir(exist_ok=True)
    export_step(part, str(d / f"mk3-{name}.step"))
    export_stl(part, str(d / f"mk3-{name}.stl"))
    bad = open_edges(d / f"mk3-{name}.stl")
    if bad:
        print(f"  mk3-{name}.stl: {bad} non-manifold edges")
        FAIL.append(f"mk3-{name}.stl mesh")


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
    print(f"  assembly              {tot_s:7.1f}  {tot_p:9.1f} g    N4 budget 400")
    if tot_p > 400:
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
            push = m.switch_shuttle(x + (p.sw_clr + 0.05) * (1 if label == "ON" else -1))
            drives = (knob & push).volume > 0.01
            ok = hit < 0.01 and drives
            print(f"  {f'knob {label}, centre Z {z:.2f}':32s} {hit:8.3f} mm3  "
                  f"{'drives' if drives else 'MISSES'}      {'ok' if ok else 'FAIL'}")
            if not ok:
                FAIL.append(f"knob {label} at Z {z:.2f}")
    sh = m.switch_shuttle()
    pulled = (base & Pos(0, 1.0, 0) * sh).volume
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
    for f in (m.OUT / "switch").glob("mk3-switch-shuttle*"):
        f.unlink()
    for proud in p.sw_stem_proud:
        sh = m.switch_shuttle(proud=proud)
        sh_print = Pos(-round(p.sw_knob_x_on), -round(p.sw_head_y0), -round(p.sw_z0)) * sh
        save(sh_print, "switch", f"switch-shuttle-proud{proud:.1f}")
    print(f"  exported stems proud by {', '.join(f'{v:.1f}' for v in p.sw_stem_proud)}")

    cb, cl = m.coupon(base, lid)
    print(f"\ncoupon 2.1   base {cb.volume/1000:.1f} cm3   lid {cl.volume/1000:.1f} cm3")

    for sub, name, part in (("device", "base", base), ("device", "lid", lid),
                            ("coupon21", "coupon21-base", cb),
                            ("coupon21", "coupon21-lid", cl)):
        save(part, sub, name)
    print(f"exported to {m.OUT}")

    # Logo: the lid with a recess, and one inlay per colour to fill it. The
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
    check("recess taken vs inlays", lid.volume - lid_logo.volume, filled, tol=0.05, unit="mm3")
    names = list(inlays)
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            clash = (inlays[a] & inlays[b]).volume
            if clash >= 0.01:
                print(f"  inlays {a} and {b} overlap by {clash:.3f} mm3")
                FAIL.append(f"logo {a}/{b} overlap")
    # Engraved, for one filament: only the black is cut, so the collar, nut, eye
    # and legs stay at the surface and read inside the engraving. Cutting the
    # whole recess instead merges them into one plain silhouette.
    lid_engraved = lid - inlays["black"]
    n = len(lid_engraved.solids())
    print(f"  {'engraved lid solids':32s} {n:8d}      want 1      {'ok' if n == 1 else 'DETACHED ISLAND'}")
    if n != 1:
        FAIL.append("engraved lid is not one solid")
    check("engraving taken vs black", lid.volume - lid_engraved.volume,
          inlays["black"].volume, tol=0.05, unit="mm3")
    save(lid_logo, "logo", "lid-logo")
    save(lid_engraved, "logo", "lid-logo-engraved")
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

    # Keep docs/parameters.md from drifting: regenerate it every build.
    import gen_params_doc
    gen_params_doc.main()

    if FAIL:
        print(f"\nFAILED: {', '.join(FAIL)}")
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
