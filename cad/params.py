"""Driving dimensions for Palmtop Mk3.

Mirrors docs/parameters.md, which is the human-readable source of truth.
Keep the two in step: a number that changes here changes there.

All lengths mm, masses g, angles deg.
"""

from math import atan, degrees

# --- sentinel -------------------------------------------------------------
# Values still blocked on a measurement. Massing uses the ASSUMED twin below;
# nothing that matters structurally may depend on one.
BLOCKED = {
    "kbd_rim_recess": "task 0.4",
    "phone_camera_bump": "task 0.6",
}

# --- 1. keyboard (measured) ----------------------------------------------
kbd_span_x = 194.00  # re-measured 2026-09-25 against a printed base; was 193.00
kbd_depth_y = 86.25
kbd_h_rear = 9.52
kbd_h_front = 5.54
kbd_keycap_rear = 1.82
kbd_keycap_front = 1.82  # owner: same as rear
kbd_mass = 95.0
kbd_rim_width = 1.68

# --- USB-C, on the keyboard's RIGHT SIDE face -----------------------------
# NOT on the rear edge. Earlier drafts put it there from a misread photograph,
# which invented the whole hinge-versus-I/O conflict in ADR-0006.
# Datum: distance back from the keyboard's REAR (high) edge; Z from the plane
# the keyboard rests on.
kbd_usbc_rear_inset = 8.00    # rear edge to the near end of the connector
kbd_usbc_z_bottom = 3.00      # opening's lower edge above the rest plane
kbd_usbc_z_top_inset = 2.00   # opening's upper edge below the top of that face
kbd_usbc_w_ASSUMED = 9.0      # along the keyboard's depth; receptacle is 8.34
# CONFIRMED BY FIT 2026-09-22: the printed coupon's window lines up with the real
# keyboard's port. The width itself is still not measured, but it no longer needs
# to be - the opening clears it, which is the only thing the number was for.

# How much that assumption can be wrong, from the cut geometry further down:
# the opening through the wall spans 6.0 to 19.0 mm back from the keyboard's
# rear edge, while the connector's near end sits at the MEASURED 8.00. Any true
# width up to 11.0 mm is therefore cleared, with 2.0 mm spare at the rear end.
# The receptacle itself is 8.34 and a bezel around it still fits, so the
# assumption is not on the critical path - coupon 2.1 confirms it against the
# real keyboard before anything large is printed.

# The side face is a wedge, so its local height depends where you are along it.
def _kbd_side_h(from_rear):
    return kbd_h_rear - (from_rear / kbd_depth_y) * (kbd_h_rear - kbd_h_front)

kbd_usbc_face_h = _kbd_side_h(kbd_usbc_rear_inset + kbd_usbc_w_ASSUMED / 2)
kbd_usbc_z_top = kbd_usbc_face_h - kbd_usbc_z_top_inset
kbd_usbc_h = kbd_usbc_z_top - kbd_usbc_z_bottom
kbd_wedge_angle = degrees(atan((kbd_h_rear - kbd_h_front) / kbd_depth_y))

# --- 2. phone (spec) ------------------------------------------------------
phone_x = 160.1
phone_y = 76.1
phone_z = 8.20
phone_mass = 167.0
# Plan-view corner radii, from Mk2's pocket sketch (9.362 / 10.904 at a 0.5
# gap) less that gap; the Mk2 phone STL's outline agrees. Front = button edge.
phone_corner_r_front = 8.86
phone_corner_r_rear = 10.40

# --- 3. materials and clearances -----------------------------------------
mat_density = 1.27e-3  # g/mm3, PETG, SOLID

# `volume * mat_density` is the 100%-infill upper bound, not what comes off the
# printer. Thin walls (1.2-1.6) print essentially solid; chunky blocks - the
# lid's side spacers, the tail - take infill and land near 40%. Treating solid
# mass as printed mass once produced a spurious "over budget" flag and made the
# tipping margins look better than they are. Both figures are reported; the
# authoritative one comes from slicing the STL.
infill_chunky = 0.42
wall_t = 1.60
clr_kbd = 0.30
# Across the span the pocket needs more than clr_kbd. The first full base
# printed its pocket 193.0 wide against 193.6 modelled - 0.6 of shrinkage and
# elephant's foot over a 194 mm run, which a 0.3 per-side gap cannot absorb.
# Depth is short enough (86 mm) that clr_kbd still holds there.
clr_kbd_x = 0.60
clr_phone = 0.30

# The phone is held by double-sided tape, as Mk2's was - no retention lips, so
# the pocket is a plain recess. The tape goes on the pocket's FLOOR, behind the
# phone, and the pocket is that much deeper. It was first put on the side walls
# to save the 1.0 of height, but the assembled device got floor tape anyway: the
# phone stood 1 mm proud, landed on the keycaps, and held the lid ~4 mm open at
# the front. The owner took the height instead (N1 restated to 24.5). The side
# widening is kept, so tape on the ends still fits. Holding an inverted phone
# takes 1.64 N, so adhesion is not the constraint anywhere.
tape_t = 1.00
# Gap between the keycap tops and the lid. The lid lands on the base's RIM, not
# on the keys: the base's walls stand this much proud of the keycap plane, so
# pressing a closed lid loads the walls instead of typing. The tail does NOT
# rise with them - it keeps clear of the lid's swept cylinder by exactly this.
keycap_gap = 0.30

# --- 4. base --------------------------------------------------------------
base_floor_t = 1.20  # ADR-0008
hinge_setback = 15.00  # ADR-0003

base_x = kbd_span_x + 2 * (wall_t + clr_kbd_x)
base_depth_to_axis = wall_t + clr_kbd + kbd_depth_y + clr_kbd + wall_t
base_y = base_depth_to_axis + hinge_setback

# --- 5. lid ---------------------------------------------------------------
lid_rear_wall = 1.20  # ADR-0004, closed pocket
lid_x = base_x
lid_y = base_depth_to_axis  # ends at the hinge axis; see clamshell-geometry.md
pocket_z = phone_z + tape_t  # phone flush with the lid's face, tape behind it
lid_t = lid_rear_wall + pocket_z

lid_lip_depth_ASSUMED = 2.50  # task 0.8

# The phone is biased FORWARD in the lid, not centred: thin wall where the power
# and volume buttons need reaching, thick wall on the hinge side where the
# station reliefs live. Mk2 did the same - 4.70 front, 9.60 rear, measured off
# its STL. Mk3 uses a little more bias because Mk2's full-width hinge barrel
# needed no station reliefs and Mk3's stations do.
phone_front_wall = 4.00

# Button window, taken from Mk2 rather than measured fresh: same phone, same
# orientation, centred in X in both lids, so its span transfers directly.
# One opening over both buttons, as Mk2 has - not two holes.
button_win_x0, button_win_x1 = -48.60, 5.00

# --- camera cutout, also transferred from Mk2 -----------------------------
# Measured off palmtop_weighted_mk2-top_part.stl. X transfers unchanged since
# both lids centre the same phone on X=0. Y is referenced to the phone's own
# button-side edge, because the two lids differ in depth and in how the phone
# sits in them.
_mk2_phone_y0 = -38.05          # phone's button-side edge in Mk2's lid
mk2_cam_x0, mk2_cam_x1 = -69.80, -58.60
mk2_cam_y0, mk2_cam_y1 = -29.20, -6.00

cam_x0, cam_x1 = mk2_cam_x0, mk2_cam_x1
cam_from_edge0 = mk2_cam_y0 - _mk2_phone_y0   # 8.85
cam_from_edge1 = mk2_cam_y1 - _mk2_phone_y0   # 32.05

# Phone USB-C cutout. Position follows from the fixed orientation (ADR-0004):
# the phone's bottom edge becomes the lid's RIGHT short edge, +X. Assumed centred
# along that edge - standard for this phone, but unverified.
phone_usbc_centred = True  # A
phone_usbc_cut_w = 12.0  # along Y, sized for a cable overmould not just the plug
phone_usbc_cut_h = 7.0   # along Z: sets the FLOOR side only - the slot is open
                         # to the screen side, so 3.5 below the port centre is
                         # the one limit left on overmould thickness

# --- 6. derived stack -----------------------------------------------------
parting_rear = base_floor_t + kbd_h_rear + kbd_keycap_rear
parting_front = base_floor_t + kbd_h_front + kbd_keycap_front
rim_rear = parting_rear + keycap_gap     # where the lid lands
rim_front = parting_front + keycap_gap
closed_h_rear = rim_rear + lid_t
closed_h_front = rim_front + lid_t
close_tilt = degrees(atan((parting_rear - parting_front) / base_depth_to_axis))

N1_TARGET = 20.00
N1_HARD_LIMIT = 24.50  # restated 2026-09-29 by the owner, see requirements.md

# --- 7. hinge -------------------------------------------------------------
# The axis sits at the lid's MID-THICKNESS, not on the parting plane. With it on
# the parting plane the lid's rear-top corner is 9.7 mm from the axis and sweeps
# down into the tail past ~90 deg of opening - caught by the opening sweep in
# build.py. At mid-thickness the furthest corner is only half the lid thickness
# away, and the swept cylinder clears the tail entirely.
hinge_axis_y = base_depth_to_axis
lid_bottom_rear = rim_rear
hinge_axis_z = (lid_bottom_rear + closed_h_rear) / 2
lid_rear_radius = (closed_h_rear - lid_bottom_rear) / 2  # lid's rounded rear edge
hinge_torque_req = 0.091  # N*m at 90 deg

# Knuckle OD is set by packaging, not by load: it must fit between the lid's
# faces at the axis. The lid weighs ~2 N, so even a small annulus is ample.
knuckle_od = 9.0   # must fit inside the lid's thickness at the axis
knuckle_id = 3.50
knuckle_clr = 0.20  # per face, between interleaved knuckles

# One station: base | lid | base, interleaved. The outer knuckles are 6.0 rather
# than the 4.4 that packaging alone would need, so each can host a fastener
# pocket without being reduced to a shell.
station_outer_w = 6.00   # each base knuckle

# The lid's relief at a station is larger than its own rear radius. It has to be:
# at 180 deg the lid's underside behind the axis sits at (axis - lid_rear_radius),
# so no base material may rise above that line except inside this relief. The
# knuckle posts reach the axis through the relief, directly underneath it.
# Tied to the lid's radius, not fixed: a fixed 5.70 left the posts' front faces
# clipping the lid's underside once the lid thickened for floor tape.
station_relief_r = lid_rear_radius + 1.00
post_half_y = 2.50
station_inner_w = 5.80   # the lid knuckle
station_w = 2 * station_outer_w + station_inner_w + 2 * 0.20

# M3 through all three knuckles: head one side, nut the other, so tightening
# squeezes the stack. The friction surfaces are the PETG knuckle end faces; the
# compliant element sits under the head, OUTSIDE the stack, so the spring and
# the sliding surface are separate parts each doing one job.
nut_af = 5.70            # across flats, M3 nut 5.5 plus fit
# DIN 985 nylon-insert nut, 4.00 tall, not a plain DIN 934 with threadlocker.
# The joint runs at low preload - the O-ring sets 22-25 N - which is exactly
# where plain threads walk loose, and the nut faces inboard where no one can
# reach it to re-apply a locker. The wall left behind the pocket is 1.70; at
# 25 N over the 24 mm2 under the hex that is 1 MPa, against PETG's ~50.
# The nut's outer face stays at -8.80, so the M3 x 16 still runs 1.10 past it:
# two threads into the insert. Nylon side OUT, metal face on the pocket floor.
nut_depth = 4.30
# Plain DIN 934 (2.40 tall) kept as a second base while the nylon nuts are on
# order: export/*-plainnut.*. It wants threadlocker, which cannot be re-applied
# once the lid is nested - fine for a coupon, not what the device should ship with.
nut_depth_plain = 2.70
head_dia = 5.80          # M3 socket cap 5.5 plus fit
head_depth = 3.80        # head 3.0 plus a wave washer

corner_r = 3.0   # outer vertical corners

# --- feet ------------------------------------------------------------------
# Locating recesses for stick-on bumpons. The REAR pair sets the tipping contact
# line, which the whole balance analysis measures the setback from: move them
# 5 mm inboard and the effective setback drops 15 -> 10 and the device tips.
# They sit as far back as a pad can go.
foot_dia = 10.0
foot_recess = 0.40
foot_inset_x = 12.0
foot_y_front = 8.0
foot_y_rear = None   # set below, hard against the tail's rear edge

# --- ballast ---------------------------------------------------------------
# No pocket. ADR-0003 carried one as insurance against a mass *bracket* that has
# since been replaced by measured geometry, and the margins now pass on the
# pessimistic printed estimate. Hosting a pocket would mean thickening the front
# wall by ~6 mm, since the keyboard fills the base almost edge to edge.
# If the built device ever needs ballast, a steel strip tapes to the UNDERSIDE of
# the base at the front, between the feet - free in closed height, because the
# front is the thin end of the wedge.

# Station X positions. The rear edge carries nothing else, so these are placed
# purely for anti-racking span: as far apart as the side walls allow.
# Two stations, not three. The centre one cannot be assembled: the lid's rounded
# rear is a solid cylinder about the hinge axis running the full 196.8, so no
# axial path exists from outside the device to a bolt head at X=0. Rotating the
# lid does not help - the obstruction is coaxial with the rotation. Both survivors
# open OUTBOARD, where only 1.6 mm of lid stands in the way. See ADR-0010; whether
# two stations are stiff enough across the span is what the first article decides.
station_x = (-87.5, 87.5)

# Clearance bored through the lid outboard of each station so the Ø5.5 head can
# travel down the axis into its pocket. Ø3.5 - the bolt's own bore - will not.
head_access_dia = 6.40
foot_y_rear = base_y - foot_dia / 2 - 1.0

# The tunnel is now a plain opening through the base's right wall - 1.9 mm of
# material, not 15 mm of tail. Sized for a cable overmould, not just the plug.
usbc_cut_w, usbc_cut_h = 13.0, 7.5   # along Y and Z
usbc_centre_y = (wall_t + clr_kbd + kbd_depth_y) - (
    kbd_usbc_rear_inset + kbd_usbc_w_ASSUMED / 2
)
usbc_centre_z = base_floor_t + (kbd_usbc_z_bottom + kbd_usbc_z_top) / 2

# --- 8. masses and balance (ALL ESTIMATES - risk R3) ----------------------
# Bracketed, not guessed. The lower bound was the original hand estimate; the
# upper bound is what massing.py measures with both halves fully solid. The real
# part sits between, depending on how much of the lid's dead side material is
# hollowed out. See docs/analysis/balance.md.
lid_shell_mass_min, lid_shell_mass_max = 40.0, 83.0
base_shell_mass_min, base_shell_mass_max = 42.0, 72.0

lid_shell_mass = 60.0   # working value: side regions partly hollowed
base_shell_mass = 55.0  # working value
lid_mass_total = lid_shell_mass + phone_mass
base_mass_total = base_shell_mass + kbd_mass
r_lid = 45.0
d_base = 41.0


def tipping_margin(s=hinge_setback, opening=180.0, lid_shell=None, base_shell=None):
    """Ratio of restoring to overturning moment at a given opening angle.

    >= 1.0 means the device cannot be tipped backwards at that angle.
    opening=180 is the theoretical worst case; 150 is a realistic maximum.
    See docs/analysis/balance.md.
    """
    from math import radians, sin

    L = (lid_shell if lid_shell is not None else lid_shell_mass) + phone_mass
    B = (base_shell if base_shell is not None else base_shell_mass) + kbd_mass
    restoring = B * d_base + s * (B + L)
    overturning = L * r_lid * sin(radians(opening - 90.0))
    return restoring / overturning


def setback_for_no_tip(lid_shell=None, base_shell=None):
    """Rear setback at which tipping becomes impossible at any angle."""
    L = (lid_shell if lid_shell is not None else lid_shell_mass) + phone_mass
    B = (base_shell if base_shell is not None else base_shell_mass) + kbd_mass
    return (L * r_lid - B * d_base) / (B + L)


def balance_sweep(s=hinge_setback):
    """Print tipping margin across the plausible mass bracket."""
    cases = [
        (lid_shell_mass_min, base_shell_mass_min, "both light"),
        (lid_shell_mass_max, base_shell_mass_max, "both solid"),
        (lid_shell_mass, base_shell_mass, "working values"),
        (lid_shell_mass_max, base_shell_mass_min, "heavy lid, light base  <-- worst"),
        (lid_shell_mass_min, base_shell_mass_max, "light lid, heavy base"),
    ]
    print(f"  {'lid':>5} {'base':>5} {'@180':>6} {'@150':>6} {'s_req':>6}   case")
    for ls, bs, note in cases:
        print(f"  {ls:5.0f} {bs:5.0f}"
              f" {tipping_margin(s, 180, ls, bs):6.3f}"
              f" {tipping_margin(s, 150, ls, bs):6.2f}"
              f" {setback_for_no_tip(ls, bs):6.1f}   {note}")


def report():
    print(f"base           {base_x:.2f} x {base_y:.2f}")
    print(f"lid            {lid_x:.2f} x {lid_y:.2f} x {lid_t:.2f}")
    print(f"parting plane  {parting_front:.2f} front -> {parting_rear:.2f} rear")
    print(f"closed height  {closed_h_front:.2f} front -> {closed_h_rear:.2f} rear")
    print(f"close tilt     {close_tilt:.2f} deg  (keyboard wedge {kbd_wedge_angle:.2f})")
    margin = N1_HARD_LIMIT - closed_h_rear
    print(f"N1             target {N1_TARGET}, limit {N1_HARD_LIMIT}, margin {margin:+.2f}")
    print(f"blocked        {len(BLOCKED)} parameters")
    print(f"\nbalance sweep at s={hinge_setback:.0f} mm  (margin >= 1.0 means it cannot tip)")
    balance_sweep()


if __name__ == "__main__":
    report()
