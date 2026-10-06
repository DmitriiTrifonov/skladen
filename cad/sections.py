"""Rear-edge sections, as SVG, at a hinge station and at the USB-C tunnel."""

import sys
from pathlib import Path

from build123d import *

sys.path.insert(0, str(Path(__file__).parent))
import model as m
import params as p

OUT = Path(__file__).parent.parent / "export" / "drawings"
OUT.mkdir(parents=True, exist_ok=True)


def section_at(part, x, half=0.05):
    """Thin slab at plane X=x, rotated so its YZ profile lands in XY."""
    bb = part.bounding_box()
    slab = Pos(x, (bb.min.Y + bb.max.Y) / 2, (bb.min.Z + bb.max.Z) / 2) * Box(
        2 * half, bb.size.Y + 10, bb.size.Z + 10
    )
    sl = part & slab
    if sl.volume == 0:
        return None
    return Rot(0, -90, 0) * sl  # X -> -Z, so the YZ profile faces the viewer


def main():
    base, lid = m.build()
    axis = Axis((0, p.hinge_axis_y, p.hinge_axis_z), (1, 0, 0))

    for tag, x in (("station", p.station_x[-1]),):
        for opening in (0, 90, 180):
            turn = -(opening + p.close_tilt)
            shapes = [s for s in (section_at(base, x),
                                  section_at(lid.rotate(axis, turn), x)) if s]
            if not shapes:
                continue
            ex = ExportSVG(scale=6, margin=10, line_weight=0.3)
            for s in shapes:
                ex.add_shape(s)
            name = OUT / f"section-{tag}-{opening:03d}.svg"
            ex.write(str(name))
            print(f"  {name.name}")


if __name__ == "__main__":
    print("sections:")
    main()
