"""The Mitya Computer logo, inlaid in the lid's outer face.

The logo itself is not under the design's licence - see the README.

The artwork is logo/mitya-shiba-green.svg, the dog traced from a printed test
inlay: head, body and ring tail in one green, with the eye, the nut and the leg
lines as holes in it. Fills come through import_svg as faces, but strokes come
through as bare centrelines - the leg lines are strokes - so they are thickened
here.

The result is one flat green region, with the holes taken out. It becomes a body
logo_depth thick, sitting flush in a recess of the same shape.
"""

import re
import sys
from pathlib import Path

from build123d import *

sys.path.insert(0, str(Path(__file__).parent))
import params as p

SVG = Path(__file__).parent / "logo" / "mitya-shiba-green.svg"

# Colours in the artwork, and the stroke width each colour's strokes use there,
# in the artwork's own units. White is not a colour of the part but the holes in
# it; only the leg lines are strokes.
COLOURS = {
    "green": ((0x4C, 0xC9, 0x5C), 0.0),
    "hole": ((0xFF, 0xFF, 0xFF), 14.0),
}


def _colour_of(shape):
    rgb = tuple(round(c * 255) for c in tuple(shape.color)[:3])
    for name, (want, _) in COLOURS.items():
        if max(abs(a - b) for a, b in zip(rgb, want)) <= 2:
            return name
    raise ValueError(f"logo: colour {rgb} is not in the palette")


def _thicken(wire, width):
    return Face(wire.offset_2d(width / 2, kind=Kind.ARC, side=Side.BOTH, closed=True))


def _union(faces):
    out = faces[0]
    for f in faces[1:]:
        out = out + f
    return out


def regions():
    """{colour: 2D shape}, centred on the origin, logo_height tall, Y up."""
    # Imported as drawn, Y down: flip_y hides the flip in each face's location,
    # which scale() then misplaces. The flip is done explicitly at the end.
    shapes = import_svg(SVG, align=None, flip_y=False)
    # An invalid face does not mesh, and leaves a hole in every STL cut from it.
    # A self-crossing outline does this - it is how variable-font lettering
    # arrived here once - so refuse the artwork rather than export a broken part.
    bad = [s for s in shapes if isinstance(s, Face) and not s.is_valid]
    if bad:
        raise ValueError(f"logo: {len(bad)} invalid shape(s) in {SVG.name}, "
                         f"first at {bad[0].bounding_box().center()}")
    canvas = max(s.bounding_box().size.X for s in shapes)
    fills = {k: [] for k in COLOURS}
    strokes = {k: [] for k in COLOURS}
    for s in shapes:
        if isinstance(s, Face) and s.bounding_box().size.X >= canvas - 1e-6:
            continue   # the white background
        (fills if isinstance(s, Face) else strokes)[_colour_of(s)].append(s)

    holes = _union(fills["hole"] + [_thicken(w, COLOURS["hole"][1] * canvas / _viewbox_w())
                                    for w in strokes["hole"]])
    green = _union(fills["green"]) - holes

    out = {"green": green}
    bb = _union(list(out.values())).bounding_box()
    k = p.logo_height / bb.size.Y
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
