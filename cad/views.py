"""Assembled views of Mk3, as SVG line drawings with hidden lines removed."""

import sys
from pathlib import Path

from build123d import *

sys.path.insert(0, str(Path(__file__).parent))
import model as m
import params as p

OUT = Path(__file__).parent.parent / "export" / "drawings"
OUT.mkdir(parents=True, exist_ok=True)
CENTRE = (0, p.base_y / 2, p.closed_h_rear / 2)


def render(shape, name, eye, up=(0, 0, 1), scale=4.0):
    vis, hid = shape.project_to_viewport(eye, up, look_at=CENTRE)
    ex = ExportSVG(scale=scale, margin=12)
    ex.add_layer("hidden", line_color=(150, 150, 150), line_type=LineType.DASHED,
                 line_weight=0.15)
    ex.add_layer("visible", line_weight=0.32)
    ex.add_shape(hid, layer="hidden")
    ex.add_shape(vis, layer="visible")
    path = OUT / f"view-{name}.svg"
    ex.write(str(path))
    print(f"  {path.name:28s} {len(vis)} visible, {len(hid)} hidden edges")


def main():
    base, lid = m.build()
    axis = Axis((0, p.hinge_axis_y, p.hinge_axis_z), (1, 0, 0))

    def assembly(opening):
        return base + lid.rotate(axis, -(opening + p.close_tilt))

    D = 900
    iso = (-D * 0.8, -D, D * 0.55)
    print("views:")
    render(assembly(0), "closed-iso", iso)
    render(assembly(120), "open120-iso", iso)
    render(assembly(120), "open120-side", (D, p.base_y / 2, p.closed_h_rear / 2))
    render(assembly(0), "closed-side", (D, p.base_y / 2, p.closed_h_rear / 2))
    render(assembly(180), "open180-side", (D, p.base_y / 2, p.closed_h_rear / 2))
    render(base, "base-iso", iso)
    render(lid, "lid-iso", (-D * 0.8, -D, -D * 0.55))
    render(lid, "lid-back", (0, p.base_depth_to_axis / 2, D), up=(0, 1, 0))


if __name__ == "__main__":
    main()
