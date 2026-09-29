"""Build, check and export. Run: .venv/bin/python cad/build.py"""

import sys
from math import asin, degrees, radians, sin
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from build123d import export_step, export_stl

import model as m
import params as p

FAIL = []


def check(label, got, want, tol=0.01, unit="mm"):
    ok = abs(got - want) <= tol
    print(f"  {label:32s} {got:8.2f} {unit}   want {want:.2f}   {'ok' if ok else 'MISMATCH'}")
    if not ok:
        FAIL.append(label)


def save(part, sub, name):
    """STEP and STL side by side, one folder per thing you would print together."""
    d = m.OUT / sub
    d.mkdir(exist_ok=True)
    export_step(part, str(d / f"mk3-{name}.step"))
    export_stl(part, str(d / f"mk3-{name}.stl"))


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

    cb, cl = m.coupon(base, lid)
    print(f"\ncoupon 2.1   base {cb.volume/1000:.1f} cm3   lid {cl.volume/1000:.1f} cm3")

    for sub, name, part in (("device", "base", base), ("device", "lid", lid),
                            ("coupon21", "coupon21-base", cb),
                            ("coupon21", "coupon21-lid", cl)):
        save(part, sub, name)
    print(f"exported to {m.OUT}")

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
