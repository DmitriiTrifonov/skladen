"""The Mitya Computer logo, inlaid in the lid's outer face.

The logo itself is not under the design's licence - see the README.

The artwork is logo/mitya-computer.svg, a copy of the brand's master. Fills come
through import_svg as faces, but strokes come through as bare centrelines - and
the tail ring, the collar and the leg lines are all strokes - so they are
thickened here. The collar is also clipped to the dog in the artwork, which
import_svg ignores, so that is redone here too.

The result is one flat region per colour. Each becomes a body logo_depth thick,
sitting flush in a recess cut to the union of all of them.
"""

import re
import sys
from pathlib import Path

from build123d import *

sys.path.insert(0, str(Path(__file__).parent))
import params as p

SVG = Path(__file__).parent / "logo" / "mitya-computer.svg"

# Colours in the artwork, and the stroke width each colour's strokes use there,
# in the artwork's own units. One stroke width per colour holds for this logo:
# black is only the tail, teal only the collar, white only the leg lines.
COLOURS = {
    "black": ((0x11, 0x11, 0x11), 14.0),
    "teal": ((0x1F, 0xB5, 0xA0), 9.0),
    "white": ((0xFF, 0xFF, 0xFF), 3.5),
}


def _colour_of(shape):
    rgb = tuple(round(c * 255) for c in tuple(shape.color)[:3])
    for name, (want, _) in COLOURS.items():
        if max(abs(a - b) for a, b in zip(rgb, want)) <= 2:
            return name
    raise ValueError(f"logo: colour {rgb} is not in the palette")


def _thicken(wire, width):
    if wire.is_closed:   # a ring: the tail
        return Face(wire.offset_2d(width / 2)) - Face(wire.offset_2d(-width / 2))
    return Face(wire.offset_2d(width / 2, kind=Kind.ARC, side=Side.BOTH, closed=True))


def _union(faces):
    out = faces[0]
    for f in faces[1:]:
        out = out + f
    return out


def regions():
    """{colour: 2D shape}, centred on the origin, logo_width across, Y up."""
    # Imported as drawn, Y down: flip_y hides the flip in each face's location,
    # which scale() then misplaces. The flip is done explicitly at the end.
    shapes = import_svg(SVG, align=None, flip_y=False)
    canvas = max(s.bounding_box().size.X for s in shapes)
    fills = {k: [] for k in COLOURS}
    strokes = {k: [] for k in COLOURS}
    for s in shapes:
        if isinstance(s, Face) and s.bounding_box().size.X >= canvas - 1e-6:
            continue   # the white background
        (fills if isinstance(s, Face) else strokes)[_colour_of(s)].append(s)

    thick = {k: [_thicken(w, COLOURS[k][1] * canvas / _viewbox_w()) for w in ws]
             for k, ws in strokes.items()}
    black = _union(fills["black"] + thick["black"])
    # The collar is clipped to the dog's filled body in the artwork - not to the
    # tail, which is a stroke, and not to the lettering, which starts right of
    # the collar's far end.
    collar = _union(thick["teal"])
    dog = _union([f for f in fills["black"]
                  if f.bounding_box().min.X < collar.bounding_box().max.X])
    teal = collar & dog
    white = _union(fills["white"] + thick["white"])
    # A white shape with a black one inside it (the nut and its hole) keeps the
    # black: black fills that lie wholly inside white are holes in the white.
    holes = [f for f in fills["black"] if (f - white).area < 1e-6]
    if holes:
        white = white - _union(holes)
    black = black - teal - white

    out = {"black": black, "teal": teal, "white": white}
    bb = _union(list(out.values())).bounding_box()
    k = p.logo_width / bb.size.X
    # Scale about the origin first, then move: scale() drops a location that
    # Pos() has only recorded, rather than applied, on a boolean result.
    move = Pos(-bb.center().X * k, -bb.center().Y * k)
    return {name: mirror(move * scale(r, by=k), about=Plane.XZ)
            for name, r in out.items()}


def _viewbox_w():
    """import_svg works in the document's px, not viewBox units; strokes are
    given in the latter."""
    vb = re.search(r'viewBox="([^"]+)"', SVG.read_text()).group(1).split()
    return float(vb[2])


def place(shape2d):
    """Extrude a flat region logo_depth down into the lid's outer face."""
    solid = Pos(0, 0, -p.logo_depth) * extrude(shape2d, amount=p.logo_depth)
    if p.logo_reads_open:
        solid = Rot(0, 0, 180) * solid
    slope = (p.rim_rear - p.rim_front) / p.base_depth_to_axis
    z = p.rim_front + p.lid_t + slope * p.logo_centre_y
    return Pos(0, p.logo_centre_y, z) * Rot(p.close_tilt, 0, 0) * solid


def inlays():
    """{colour: solid}, in device coordinates, flush with the lid's face."""
    return {name: place(r) for name, r in regions().items()}
