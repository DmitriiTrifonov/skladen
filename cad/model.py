"""Skladen Mk3 geometry.

Coordinates:
    X  span, 0 at centre
    Y  depth, 0 at the FRONT of the device, +Y toward the hinge
    Z  height, 0 at the desk

Still absent, and why: retention lips and button cutouts (tasks 0.8, 0.10),
camera cutout (0.6), ribbed floor variant (0.4), fillets everywhere.
"""

import sys
from pathlib import Path

from math import cos, radians

from build123d import *

sys.path.insert(0, str(Path(__file__).parent))
import params as p

OUT = Path(__file__).parent.parent / "export"
OUT.mkdir(exist_ok=True)


def yz_prism(points, span_x, x_centre=0.0):
    sk = Plane.YZ * Polygon(*points, align=None)
    solid = extrude(sk, amount=span_x / 2, both=True)
    return Pos(x_centre, 0, 0) * solid if x_centre else solid


def x_cyl(d, w, x, y, z):
    """Cylinder with its axis along X."""
    return Pos(x, y, z) * Rot(0, 90, 0) * Cylinder(radius=d / 2, height=w)


def rounded_outline(w, d, y0, r_front, r_rear, z0=-50.0, h=100.0):
    """Vertical prism on a w x d rectangle from Y = y0, corners rounded in plan:
    r_front at the Y = y0 edge, r_rear at the far one."""
    x1, y1 = w / 2, y0 + d
    pts = [
        (-x1 + r_front, y0), (x1 - r_front, y0),
        (x1, y0 + r_front), (x1, y1 - r_rear),
        (x1 - r_rear, y1), (-x1 + r_rear, y1),
        (-x1, y1 - r_rear), (-x1, y0 + r_front),
    ]
    k = 1 - 0.5 ** 0.5
    mids = [
        (x1 - r_front * k, y0 + r_front * k), (x1 - r_rear * k, y1 - r_rear * k),
        (-x1 + r_rear * k, y1 - r_rear * k), (-x1 + r_front * k, y0 + r_front * k),
    ]
    edges = []
    for i in range(4):
        a, b = pts[2 * i], pts[2 * i + 1]
        edges.append(Line(a, b))
        edges.append(ThreePointArc(b, mids[i], pts[(2 * i + 2) % 8]))
    face = make_face(edges)
    return Pos(0, 0, z0) * extrude(face, amount=h)


# --- shells ---------------------------------------------------------------
def base_shell():
    # Walls stand keycap_gap proud of the keycap plane so the lid lands on them.
    # The tail stops at parting_rear: raising it too would close the clearance
    # the lid's swept cylinder needs at 180 deg.
    s = yz_prism(
        [
            (0.0, 0.0),
            (p.base_y, 0.0),
            (p.base_y, p.parting_rear),
            (p.base_depth_to_axis, p.parting_rear),
            (p.base_depth_to_axis, p.rim_rear),
            (0.0, p.rim_front),
        ],
        p.base_x,
    )
    pk_y = p.kbd_depth_y + 2 * p.clr_kbd
    s -= yz_prism(
        [
            (p.wall_t, p.base_floor_t),
            (p.wall_t + pk_y, p.base_floor_t),
            (p.wall_t + pk_y, p.rim_rear + 5),
            (p.wall_t, p.rim_rear + 5),
        ],
        p.kbd_span_x + 2 * p.clr_kbd_x,
    )
    # Foot pads: shallow locating recesses in the underside for bumpons.
    for fx in (-1, 1):
        for fy in (p.foot_y_front, p.foot_y_rear):
            s -= Pos(fx * (p.base_x / 2 - p.foot_inset_x), fy, p.foot_recess / 2) * Cylinder(
                radius=p.foot_dia / 2, height=p.foot_recess
            )
    return s


def lid_shell():
    bot_f, bot_r = p.rim_front, p.rim_rear
    s = yz_prism(
        [
            (0.0, bot_f),
            (p.base_depth_to_axis, bot_r),
            (p.base_depth_to_axis, bot_r + p.lid_t),
            (0.0, bot_f + p.lid_t),
        ],
        p.lid_x,
    )
    ph_x = p.phone_x + 2 * (p.clr_phone + p.tape_t)   # tape lives in this gap
    ph_y = p.phone_y + 2 * p.clr_phone
    ph_y0 = p.phone_front_wall
    slope = (bot_r - bot_f) / p.base_depth_to_axis

    def z_at(y, off):
        return bot_f + slope * y + off

    slab = yz_prism(
        [
            (ph_y0, z_at(ph_y0, -1.0)),
            (ph_y0 + ph_y, z_at(ph_y0 + ph_y, -1.0)),
            (ph_y0 + ph_y, z_at(ph_y0 + ph_y, p.pocket_z)),
            (ph_y0, z_at(ph_y0, p.pocket_z)),
        ],
        ph_x,
    )
    # Plan-view corners follow the phone's, as Mk2's pocket did. The radius
    # takes the smaller (depth) gap, so the long-axis tape gap only widens
    # toward the ends and never goes negative round a corner.
    s -= slab & rounded_outline(ph_x, ph_y, ph_y0,
                                p.phone_corner_r_front + p.clr_phone,
                                p.phone_corner_r_rear + p.clr_phone)
    # rounded rear edge: every point within lid_rear_radius of the hinge axis, so
    # the lid sweeps a clean cylinder and clears the tail at any opening angle
    s += x_cyl(2 * p.lid_rear_radius, p.lid_x, 0, p.hinge_axis_y, p.hinge_axis_z)

    # Button window through the front wall: one opening over power and volume
    # together, spanning the phone's full thickness. Mk2's geometry.
    bw_y0, bw_y1 = -1.0, ph_y0 + 0.5
    s -= yz_prism(
        [
            (bw_y0, z_at(ph_y0, -1.0)),
            (bw_y1, z_at(ph_y0, -1.0)),
            (bw_y1, z_at(ph_y0, p.phone_z)),
            (bw_y0, z_at(ph_y0, p.phone_z)),
        ],
        p.button_win_x1 - p.button_win_x0,
        (p.button_win_x0 + p.button_win_x1) / 2,
    )

    # Camera cutout straight through the rear wall, as Mk2 has it. The bump is
    # roughly as tall as the 1.2 wall, so it passes through rather than needing
    # a recess - which is why task 0.6 stopped being a blocker.
    phone_y0 = ph_y0 + p.clr_phone
    cam_y0, cam_y1 = phone_y0 + p.cam_from_edge0, phone_y0 + p.cam_from_edge1
    s -= Pos(
        (p.cam_x0 + p.cam_x1) / 2,
        (cam_y0 + cam_y1) / 2,
        z_at((cam_y0 + cam_y1) / 2, p.pocket_z + p.lid_rear_wall / 2),
    ) * Box(p.cam_x1 - p.cam_x0, cam_y1 - cam_y0, p.lid_rear_wall + 2.0)

    # Phone USB-C through the right wall, as a slot open on the screen side
    # rather than a closed tunnel. Closed, its screen-side roof was 0.73 mm: a
    # 12 x 18 mm bridge that sagged into the opening when printed face-down and
    # choked the cable. Open, there is no bridge; the plug lays in from the
    # screen side, and with the lid shut the slot faces the keyboard.
    uy = ph_y0 + ph_y / 2
    top = z_at(uy, p.phone_z / 2) + p.phone_usbc_cut_h / 2
    bot = z_at(uy, 0.0) - 3.0   # well past the screen face, tilt included
    s -= Pos(p.lid_x / 2 - (p.lid_x - ph_x) / 4, uy, (top + bot) / 2) * Box(
        (p.lid_x - ph_x) / 2 + 2.0, p.phone_usbc_cut_w, top - bot
    )
    return s


# --- hinge stations -------------------------------------------------------
# The axis is at the lid's mid-thickness, so the base's knuckles are posts rising
# out of the tail rather than bosses on the parting plane. Each half is cut by
# the other's grown solid, which keeps the two automatically complementary.
AY, AZ = p.hinge_axis_y, p.hinge_axis_z
_off = p.station_inner_w / 2 + p.knuckle_clr + p.station_outer_w / 2
_post_z0 = p.parting_rear - 4.0


def base_station(x0, grow=0.0):
    """Two outer knuckles, each on its own post rising out of the tail.

    The posts are separate rather than one full-width block: the centre of the
    station belongs to the lid's knuckle, all the way down.
    """
    d, w = p.knuckle_od + 2 * grow, p.station_outer_w + 2 * grow
    # The post lives BEHIND the axis, over the tail. Straddling the axis puts it
    # into the lid's body below the station relief, which the opening sweep
    # catches immediately.
    py0, py1 = AY - p.post_half_y, AY + p.post_half_y
    out = None
    for sign in (-1, 1):
        x = x0 + sign * _off
        kn = x_cyl(d, w, x, AY, AZ)
        post = Pos(x, (py0 + py1) / 2, (_post_z0 + AZ) / 2) * Box(
            w, py1 - py0 + 2 * grow, AZ - _post_z0 + 2 * grow
        )
        out = kn + post if out is None else out + kn + post
    return out


def station_envelope(x0):
    """Void the lid must provide for the BASE's knuckles and their posts.

    The two OUTER bands only. Cutting the middle band as well severs the lid's
    own knuckle from the lid: the relief radius (5.70) is larger than the
    knuckle's (4.50), so the knuckle added back afterwards touches nothing and
    the lid exports as four solids. It printed exactly that way - the middle
    ring came off the bed as a loose disc - which is how the defect surfaced.

    Radius is the lid's rear radius plus clearance, so the base's knuckles and
    posts have somewhere to be at every opening angle, not only closed.
    """
    w = p.station_outer_w + 2 * p.knuckle_clr
    d = 2 * p.station_relief_r
    return x_cyl(d, w, x0 - _off, AY, AZ) + x_cyl(d, w, x0 + _off, AY, AZ)


def lid_knuckle(x0, grow=0.0):
    return x_cyl(p.knuckle_od + 2 * grow, p.station_inner_w + 2 * grow, x0, AY, AZ)


def bore(x0):
    return x_cyl(p.knuckle_id, p.station_w + 4, x0, AY, AZ)


def outboard(x0):
    """Which way is out of the device from this station."""
    return 1.0 if x0 >= 0 else -1.0


def fasteners(x0, nut_depth=None):
    """Head pocket OUTBOARD, nut pocket inboard.

    The head has to arrive along the axis from outside, so it faces out. The nut
    only has to be dropped into its hex before the lid is nested, so it can face
    in, where the lid's rounded rear blocks the axis completely.
    """
    half, s = p.station_w / 2, outboard(x0)
    nd = p.nut_depth if nut_depth is None else nut_depth
    hexr = p.nut_af / 2 / cos(radians(30))
    nut = Pos(x0 - s * (half - nd / 2), AY, AZ) * Rot(0, 90, 0) * extrude(
        RegularPolygon(radius=hexr, side_count=6), amount=nd / 2, both=True
    )
    head = x_cyl(p.head_dia, p.head_depth,
                 x0 + s * (half - p.head_depth / 2), AY, AZ)
    return nut + head


def head_access(x0):
    """Path for the bolt head through the lid, outboard of the station.

    Without it the head meets 1.6 mm of the lid's rounded rear with only a 3.5
    hole through it, and the joint cannot be assembled at all.
    """
    s = outboard(x0)
    x_from = x0 + s * p.station_w / 2
    x_to = s * (p.lid_x / 2 + 3.0)
    return x_cyl(p.head_access_dia, abs(x_to - x_from), (x_from + x_to) / 2, AY, AZ)


def usbc_cut():
    """Opening through the base's right wall for the keyboard's USB-C."""
    depth = p.wall_t + p.clr_kbd_x + 2.0
    x0 = p.kbd_span_x / 2 + p.clr_kbd_x
    return Pos(x0 + depth / 2 - 1.0, p.usbc_centre_y, p.usbc_centre_z) * Box(
        depth, p.usbc_cut_w, p.usbc_cut_h
    )


def box_between(x0, x1, y0, y1, z0, z1):
    return Pos((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2) * Box(x1 - x0, y1 - y0, z1 - z0)


def switch_cut():
    """Slot in the rear wall for the shuttle's fork, and a tunnel back through
    the tail to the rear face for its stem. Both run under the right station."""
    lo = p.sw_knob_x_on - p.sw_overtravel
    hi = p.sw_knob_x_off + p.sw_overtravel
    c = p.sw_clr
    slot = box_between(lo - p.sw_head_w / 2 - c, hi + p.sw_head_w / 2 + c,
                       p.kbd_rear_y - 0.5, p.sw_head_y1 + c,
                       p.sw_z0 - c, p.sw_head_z1 + c)
    tunnel = box_between(lo - p.sw_stem_w / 2 - c, hi + p.sw_stem_w / 2 + c,
                         p.sw_head_y1 - 0.5, p.base_y + 1.0,
                         p.sw_z0 - c, p.sw_z0 + p.sw_stem_h + c)
    return slot + tunnel


def switch_shuttle(x=None, proud=None):
    """The pusher, in place, its fork centred on X (the knob's ON position by
    default), its stem standing PROUD out of the rear face (the longest variant
    by default). Prints flat on its underside: head and stem share that face."""
    x = p.sw_knob_x_on if x is None else x
    proud = max(p.sw_stem_proud) if proud is None else proud
    head = box_between(x - p.sw_head_w / 2, x + p.sw_head_w / 2,
                       p.sw_head_y0, p.sw_head_y1, p.sw_z0, p.sw_head_z1)
    head -= box_between(x - p.sw_fork_gap / 2, x + p.sw_fork_gap / 2,
                        p.sw_head_y0 - 1.0, p.sw_notch_y1, p.sw_z0 - 1.0, p.sw_head_z1 + 1.0)
    y_end = p.base_y + proud
    stem = box_between(x - p.sw_stem_w / 2, x + p.sw_stem_w / 2,
                       p.sw_head_y1 - 0.5, y_end, p.sw_z0, p.sw_z0 + p.sw_stem_h)
    stem -= box_between(x - p.sw_nail_groove / 2, x + p.sw_nail_groove / 2,
                        y_end - 0.8, y_end + 1.0, p.sw_z0 - 1.0, p.sw_z0 + p.sw_stem_h + 1.0)
    return head + stem


def switch_knob(x, z_centre):
    """The keyboard's switch knob, for fit checks: the part standing proud of the
    rear face, at its most proud reading."""
    return box_between(x - p.kbd_sw_knob_w / 2, x + p.kbd_sw_knob_w / 2,
                       p.kbd_rear_y - 0.5, p.kbd_rear_y + 1.0,
                       z_centre - p.kbd_sw_knob_h / 2, z_centre + p.kbd_sw_knob_h / 2)


def soften(part, radius, name, half_x, y_at):
    """Break the outer vertical corners.

    Selected by position, not by length: the corners differ in height (the base
    tapers front to rear), so a longest-edges filter silently catches only two
    of the four.
    """
    picked = [
        e
        for e in part.edges().filter_by(Axis.Z)
        if abs(abs(e.center().X) - half_x) < 0.1
        and any(abs(e.center().Y - y) < 0.1 for y in y_at)
    ]
    if not picked:
        print(f"  fillet skipped on {name}: no outer corners matched")
        return part
    try:
        return fillet(picked, radius=radius)
    except Exception as exc:
        print(f"  fillet skipped on {name}: {type(exc).__name__}")
        return part


def build(fillets=True, nut_depth=None):
    base, lid = base_shell(), lid_shell()
    for x0 in p.station_x:
        base = base - lid_knuckle(x0, p.knuckle_clr) + base_station(x0)
        base = base - bore(x0) - fasteners(x0, nut_depth)
        lid = lid - station_envelope(x0) + lid_knuckle(x0) - bore(x0)
        lid -= head_access(x0)
    base -= usbc_cut()
    base -= switch_cut()
    if fillets:
        base = soften(base, p.corner_r, "base", p.base_x / 2, (0.0, p.base_y))
        lid = soften(lid, p.corner_r, "lid", p.lid_x / 2, (0.0,))
    return base, lid


def coupon(base, lid, x0=55.0, x1=100.0):
    """Slice containing the right-hand station and the USB-C tunnel."""
    box = Pos((x0 + x1) / 2, p.base_y / 2, p.closed_h_rear / 2) * Box(
        x1 - x0, p.base_y + 10, p.closed_h_rear + 10
    )
    return base & box, lid & box
