"""Skladen 2 geometry.

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


def lid_shell(bezel=False):
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
    # With the bezel there is no tape: the phone sits on the rear wall, its glass
    # p.bezel_phone_off behind the rim plane, and the ring fills the gap.
    tape = 0.0 if bezel else p.tape_t
    phone_off = p.bezel_phone_off if bezel else 0.0
    ph_x = p.phone_x + 2 * (p.clr_phone + tape)   # tape lives in this gap
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
    if bezel:
        # Printed on its outer face, the cylinder's first 45 deg of arc hang in the
        # air and need supports that PETG welds to. Fill that corner with a flat
        # ramp from the tangent point to the arc's 45 deg point instead; the ramp's
        # foot sits p.lid_ramp_out outside the cylinder, which the base's tail can
        # spare (checked by the opening sweep, worst at 150 deg).
        r, ay, az = p.lid_rear_radius, p.hinge_axis_y, p.hinge_axis_z
        k = 2 ** -0.5
        foot = (2 * r * p.lid_ramp_out + p.lid_ramp_out ** 2) ** 0.5
        s += yz_prism([(ay, az + r), (ay + foot, az + r), (ay + r * k, az + r * k)],
                      p.lid_x)

    # Button window through the front wall: one opening over power and volume
    # together, spanning the phone's full thickness. Mk2's geometry.
    bw_y0, bw_y1 = -1.0, ph_y0 + 0.5
    s -= yz_prism(
        [
            (bw_y0, z_at(ph_y0, -1.0)),
            (bw_y1, z_at(ph_y0, -1.0)),
            (bw_y1, z_at(ph_y0, phone_off + p.phone_z)),
            (bw_y0, z_at(ph_y0, phone_off + p.phone_z)),
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
    top = z_at(uy, phone_off + p.phone_z / 2) + p.phone_usbc_cut_h / 2
    bot = z_at(uy, 0.0) - 3.0   # well past the screen face, tilt included
    s -= Pos(p.lid_x / 2 - (p.lid_x - ph_x) / 4, uy, (top + bot) / 2) * Box(
        (p.lid_x - ph_x) / 2 + 2.0, p.phone_usbc_cut_w, top - bot
    )

    # Headphone jack through the left wall, the same open slot on the other end.
    # The phone's top edge is the lid's -X end; the jack is measured from the
    # button-side edge, which is the pocket's front.
    jy = phone_y0 + p.phone_jack_from_edge
    top = z_at(jy, phone_off + p.phone_z / 2) + p.phone_jack_cut_h / 2
    bot = z_at(jy, 0.0) - 3.0
    s -= Pos(-(p.lid_x / 2 - (p.lid_x - ph_x) / 4), jy, (top + bot) / 2) * Box(
        (p.lid_x - ph_x) / 2 + 2.0, p.phone_jack_cut_w, top - bot
    )
    if bezel:
        s -= front_rebate()
        s -= lightening(ph_x, ph_y0, ph_y)
        for clip in clips():
            s -= clip[1]
        s -= pry_notch()
    return s


def lightening(ph_x, ph_y0, ph_y):
    """Hollow the lid's two ends from the screen side, as the Reddit build did.

    The end blocks (21 mm each) are dead material in the worst place for it
    (ADR-0003: hollow the lid, leave the base solid). What stays: the outer wall,
    on top of the base's own wall, one rib across each end, walls either side of the
    USB-C and jack channels (they carry the plug), and under the ears and screws.
    Open to the face, so it prints without bridges, the lid face-up.
    """
    t = p.wall_t
    xi, xo = ph_x / 2 + t, p.lid_x / 2 - t
    y0, y1 = t, ph_y0 + ph_y - t
    top = p.pocket_z                       # the 1.2 rear skin stays
    outline = rounded_outline(2 * xo, y1 - y0, y0, max(p.corner_r - t, 1.0), 1.0)
    uy = ph_y0 + p.clr_phone + p.phone_y / 2
    jy = ph_y0 + p.clr_phone + p.phone_jack_from_edge
    out = None
    for sign in (-1, 1):
        a, b = (xi, xo) if sign > 0 else (-xo, -xi)
        cav = _slab(a, b, y0, y1, -1.0, top) & outline
        # a rib across the middle of the end
        xm = sign * (xi + xo) / 2
        keep = _slab(xm - t / 2, xm + t / 2, y0, y1, -2.0, top + 1.0)
        # walls beside the plug's channel
        yc, w = (uy, p.phone_usbc_cut_w) if sign > 0 else (jy, p.phone_jack_cut_w)
        for lo, hi in ((yc - w / 2 - t, yc - w / 2), (yc + w / 2, yc + w / 2 + t)):
            keep += _slab(a, b, lo, hi, -2.0, top + 1.0)
        # a solid block round each end clip: its arm and the recess it snaps into sit
        # in the block, as the front clips sit in the 4.0 front wall. Standing in the
        # hollow, with only the 1.6 outer wall behind the barb, they held nothing.
        c, pad = p.clip_slot_clr, p.clip_pad
        for axis, along, origin, d in _clip_places():
            if axis != "x" or d != sign:
                continue
            x_in = origin - d * (c + pad)        # the block's inner face, past the arm's
            keep += _slab(min(x_in, sign * xo), max(x_in, sign * xo),
                          along - p.clip_w / 2 - c - pad, along + p.clip_w / 2 + c + pad,
                          -2.0, top + 1.0)
        cav -= keep
        out = cav if out is None else out + cav
    return out


# --- removable front bezel (ADR-0012) ---------------------------------------
# Same sloped frame as the lid: an offset is measured from the lid's face plane,
# which follows the keyboard's wedge, into the lid.

def _face_z(y, off):
    slope = (p.rim_rear - p.rim_front) / p.base_depth_to_axis
    return p.rim_front + slope * y + off


def _slab(x0, x1, y0, y1, off0, off1):
    return yz_prism(
        [(y0, _face_z(y0, off0)), (y1, _face_z(y1, off0)),
         (y1, _face_z(y1, off1)), (y0, _face_z(y0, off1))],
        x1 - x0, (x0 + x1) / 2)


def _xz_prism(points, span_y, y_centre):
    sk = Plane(origin=(0, 0, 0), x_dir=(1, 0, 0), z_dir=(0, -1, 0)) * Polygon(*points, align=None)
    solid = extrude(sk, amount=span_y / 2, both=True)
    return Pos(0, y_centre, 0) * solid


def front_rebate():
    """The lid's own face layer, under the plate: gone from the whole front."""
    return _slab(-p.lid_x / 2 - 1.0, p.lid_x / 2 + 1.0, -1.0, p.bezel_y_end + p.bezel_gap,
                 -1.0, p.bezel_t)


def pry_notch():
    """A nick under the front edge, so a fingernail can lift the plate."""
    x0, x1 = p.pry_notch
    return _slab(x0, x1, -1.0, 1.2, p.bezel_t - 0.01, p.bezel_t + 1.5)


def _clip_places():
    """(axis, along, origin, direction) for every clip. The axis is the one the arm's
    thickness lies along; `origin` is the arm's inner face on that axis, `along`
    where it stands on the other, and `direction` the way the barb points."""
    out = []
    for x in p.clip_front_xs:
        out.append(("y", x, 2.9, -1))                       # front wall, barb outward
    for x in p.clip_rear_xs:
        out.append(("y", x, p.bezel_y_end - 3.0, +1))       # rear wall, barb inward
    xo = p.lid_x / 2 - p.wall_t - 0.2 - p.clip_t            # arm just inside the outer wall
    for y in p.clip_end_left_ys:
        out.append(("x", y, -xo, -1))
    for y in p.clip_end_ys:
        out.append(("x", y, xo, +1))
    return out


def clips():
    """[(arm with barb, void for it in the lid)] for each clip. Arms are vertical,
    not along the face's normal: the 2.6 deg difference is 0.3 over their length,
    and the slots are cut the same way, so they agree."""
    t, b, w, c = p.clip_t, p.clip_barb, p.clip_w, p.clip_slot_clr
    top = p.clip_arm_top
    # (u, v): u along the arm's thickness from its inner face toward the barb, v up
    # from the face plane. The barb has a long lead-in and a steeper catch.
    arm = [(0, p.bezel_t - 0.4), (t, p.bezel_t - 0.4), (t, top), (0, top)]
    barb = [(t, top), (t + b, top - 0.7), (t + b, top - 1.4), (t, top - 2.0)]
    slot = [(-c, -1.0), (t + c, -1.0), (t + c, top + 0.4), (-c, top + 0.4)]
    recess = [(t + c - 0.01, top - 2.3), (t + b + 0.3, top - 2.3),
              (t + b + 0.3, top + 0.4), (t + c - 0.01, top + 0.4)]
    out = []
    for axis, along, origin, d in _clip_places():
        y_ref = origin if axis == "y" else along
        z0 = _face_z(y_ref, 0.0)

        def place(prof, wide):
            span = w + (2 * c if wide else 0.0)
            if axis == "y":
                return yz_prism([(origin + d * u, z0 + v) for u, v in prof], span, along)
            return _xz_prism([(origin + d * u, z0 + v) for u, v in prof], span, along)

        arm_solid = place(arm, False) + place(barb, False)
        void = place(slot, True) + place(recess, True)
        out.append((arm_solid, void))
    return out


def bezel_frame():
    """The plate over the whole front, flush with the lid's face, with its clips."""
    g = p.bezel_gap
    ph_y0 = p.phone_front_wall
    outer = _slab(-p.lid_x / 2 + g, p.lid_x / 2 - g, g, p.bezel_y_end, 0.0, p.bezel_t) \
        & rounded_outline(p.lid_x - 2 * g, p.bezel_y_end - g, g,
                          p.corner_r - g, 0.6)
    win_x = p.phone_x - 2 * p.bezel_overlap_end
    win_y = p.phone_y - 2 * p.bezel_overlap_side
    window = rounded_outline(win_x, win_y, ph_y0 + p.clr_phone + p.bezel_overlap_side,
                             p.bezel_window_r, p.bezel_window_r)
    # The notch (the phone's top edge is the lid's -X end): a tab of the plate reaches
    # into the window and covers it down to the picture, centred on the phone.
    uy = ph_y0 + p.clr_phone + p.phone_y / 2
    x_edge = -win_x / 2
    tab = _slab(x_edge - 1.0, x_edge + p.bezel_notch_d_ASSUMED,
                uy - p.bezel_notch_w_ASSUMED / 2, uy + p.bezel_notch_w_ASSUMED / 2,
                -1.0, p.bezel_t + 1.0)
    frame = outer - (window - tab)
    # The buttons are pressed from the front edge, through the lid's window. The
    # plate would roof it, so it is cut away over the same span, joining the screen
    # window: fingers and a thumbnail reach the buttons as they do on the open lid.
    win_y_front = ph_y0 + p.clr_phone + p.bezel_overlap_side
    frame -= _slab(p.button_win_x0, p.button_win_x1, -1.0, win_y_front + 0.5,
                   -1.0, p.bezel_t + 1.0)
    for arm, _ in clips():
        frame += arm
    return frame


bezel_ring = bezel_frame



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
                       p.kbd_rear_y - 0.5, p.sw_head_y1 + c + p.sw_retract,
                       p.sw_z0 - c, p.sw_head_z1 + c)
    tunnel = box_between(lo - p.sw_stem_w / 2 - c, hi + p.sw_stem_w / 2 + c,
                         p.sw_head_y1 - 0.5, p.base_y + 1.0,
                         p.sw_z0 - c, p.sw_z0 + p.sw_stem_h + c)
    return slot + tunnel


def switch_window_cut():
    """The hand-operated version of switch_cut(): a slot through the rear wall wide
    enough to open tweezers on the knob, and a narrower tunnel back through the
    tail to the rear face."""
    c = p.sw_clr
    slot = box_between(p.sw_win_xc - p.sw_win_w / 2, p.sw_win_xc + p.sw_win_w / 2,
                       p.kbd_rear_y - 0.5, p.sw_head_y1 + c,
                       p.sw_win_z0, p.sw_win_z1)
    tunnel = box_between(p.sw_win_xc - p.sw_tun_w / 2, p.sw_win_xc + p.sw_tun_w / 2,
                         p.sw_head_y1 - 0.5, p.base_y + 1.0,
                         p.sw_win_zc - p.sw_tun_h / 2, p.sw_win_zc + p.sw_tun_h / 2)
    return slot + tunnel


def switch_plug(clr):
    """The plug, in place: a peg in the tunnel's rear end, a flange against the
    rear face and a nipple to pull it by."""
    x, z = p.sw_win_xc, p.sw_win_zc
    peg = box_between(x - p.sw_tun_w / 2 + clr, x + p.sw_tun_w / 2 - clr,
                      p.base_y - p.sw_plug_len, p.base_y,
                      z - p.sw_tun_h / 2 + clr, z + p.sw_tun_h / 2 - clr)
    fx, fz, fy = p.sw_plug_flange
    flange = box_between(x - fx / 2, x + fx / 2, p.base_y, p.base_y + fy,
                         z - fz / 2, z + fz / 2)
    nipple = Pos(x, p.base_y + fy + p.sw_plug_nipple_h / 2, z) * Rot(90, 0, 0) * Cylinder(
        p.sw_plug_nipple_d / 2, p.sw_plug_nipple_h)
    return peg + flange + nipple


def switch_shuttle(x=None, proud=None, finger=None, back=0.0):
    """The pusher, in place, its fork centred on X (the knob's ON position by
    default), its stem standing PROUD out of the rear face and its fingers
    FINGER into the niche (the longest of each by default), pulled BACK from
    home. Prints flat on its underside: head and stem share that face."""
    x = p.sw_knob_x_on if x is None else x
    proud = max(p.sw_stem_proud) if proud is None else proud
    finger = max(p.sw_finger_len) if finger is None else finger
    head_y0 = p.kbd_rear_y + p.sw_tip_gap
    head_y1 = p.sw_head_y1 + p.sw_clr - p.sw_back_play
    head = box_between(x - p.sw_head_w / 2, x + p.sw_head_w / 2,
                       head_y0, head_y1, p.sw_z0, p.sw_head_z1)
    gap = p.kbd_sw_knob_w + 2 * p.sw_fork_clr
    head -= box_between(x - gap / 2, x + gap / 2,
                        p.kbd_rear_y - 1.0, p.sw_notch_y1, p.sw_z0 - 1.0, p.sw_head_z1 + 1.0)
    # Fingers: inner face flush with the prong's, tapering on the outer.
    root, tip, y1 = gap / 2, p.kbd_rear_y - finger, head_y0 + 0.10
    for side in (-1, 1):
        pts = [(x + side * root, y1), (x + side * (root + p.sw_finger_root), y1),
               (x + side * (root + p.sw_finger_tip), tip), (x + side * root, tip)]
        # Upward whichever way the outline winds: the two sides wind oppositely.
        head += Pos(0, 0, p.sw_finger_z0) * extrude(Polygon(*pts, align=None),
                                                    p.sw_finger_z1 - p.sw_finger_z0,
                                                    dir=(0, 0, 1))
    y_end = p.base_y + proud
    stem = box_between(x - p.sw_stem_w / 2, x + p.sw_stem_w / 2,
                       head_y1 - 0.5, y_end, p.sw_z0, p.sw_z0 + p.sw_stem_h)
    stem -= box_between(x - p.sw_nail_groove / 2, x + p.sw_nail_groove / 2,
                        y_end - 0.8, y_end + 1.0, p.sw_z0 - 1.0, p.sw_z0 + p.sw_stem_h + 1.0)
    return Pos(0, back, 0) * (head + stem)


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


def build(fillets=True, nut_depth=None, bezel=False, switch_window=False):
    base, lid = base_shell(), lid_shell(bezel)
    for x0 in p.station_x:
        base = base - lid_knuckle(x0, p.knuckle_clr) + base_station(x0)
        base = base - bore(x0) - fasteners(x0, nut_depth)
        lid = lid - station_envelope(x0) + lid_knuckle(x0) - bore(x0)
        lid -= head_access(x0)
    base -= usbc_cut()
    base -= switch_window_cut() if switch_window else switch_cut()
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


def phone_coupon(lid, x0=-p.lid_x / 2, x1=-4.0):
    """The lid's phone end: the jack slot, the camera cutout, the button window
    and the pocket's corner, in the one piece, to try the real phone in before
    the whole lid is printed. Left end of the lid, X from the end to just past
    the button window (which stops at -7.5)."""
    box = Pos((x0 + x1) / 2, p.lid_y / 2, p.closed_h_rear / 2) * Box(
        x1 - x0, p.lid_y + 20, p.closed_h_rear + 10
    )
    return lid & box
