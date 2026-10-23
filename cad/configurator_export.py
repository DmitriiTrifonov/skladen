"""Every part the web configurator can offer, as a compact mesh in its printing pose.

Run: .venv/bin/python cad/configurator_export.py [--assembled]
(--assembled rebuilds only the device in place, for the page's model view.)

Writes configurator/public/parts/*.bin.gz and manifest.json. Nothing here is a new
design: each part comes from the same model.build() calls as cad/build.py, so the
configurator can only hand out geometry that build.py knows how to check. Run
build.py first if you changed the model; this script does not repeat its checks.

Mesh format (little-endian, gzipped): u32 vertex count, u32 triangle count,
f32 xyz per vertex, u32 index triple per triangle.
"""

import gzip
import json
import struct
import sys
from math import atan, degrees
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import numpy as np
from build123d import Pos, Rot

import bambu_project
import logo
import model as m
import params as p

OUT = Path(__file__).parent.parent / "configurator" / "public" / "parts"
RIBS = (0.50, 0.60, 0.70)
TABS = (0.8, 1.0, 1.2)

manifest = {"parts": {}}


def write(key, shape, role):
    """One part to <key>.bin.gz; the manifest keeps its bounding box for the layout."""
    if isinstance(shape, (list, tuple)):      # several solids, one mesh (keycaps, text lines)
        vs, ts, off = [], [], 0
        for sh in shape:
            v1, t1 = bambu_project.welded(sh)
            vs.append(v1)
            ts += [tuple(i + off for i in tri) for tri in t1]
            off += len(v1)
        v, t = np.concatenate(vs), ts
    else:
        v, t = bambu_project.welded(shape)
        if bambu_project.open_edges(t):
            raise ValueError(f"open edges in {key}")
    raw = (struct.pack("<II", len(v), len(t)) + v.astype("<f4").tobytes()
           + np.array(t, dtype="<u4").tobytes())
    (OUT / f"{key}.bin.gz").write_bytes(gzip.compress(raw, 9, mtime=0))
    manifest["parts"][key] = {
        "role": role,
        "min": v.min(0).round(3).tolist(),
        "max": v.max(0).round(3).tolist(),
        "triangles": len(t),
    }
    print(f"  {key:34s} {len(t):7d} tri")


def union(parts):
    out = None
    for part in parts:
        out = part if out is None else out + part
    return out


def assembled():
    """The device in place, for the page's model view: lid parts in the CLOSED pose (the page
    swings them about the hinge), phone and keyboard as the stand-ins render.py draws."""
    import render

    base = m.build()[0]
    lid = m.build(bezel=True, rib_h=0.60, tab_t=1.0)[1]
    recess = union(logo.inlays().values())
    kbd, caps = render.keyboard()
    ph, glass, text = render.phone()
    prompt = [t for t, c in text if c is render.TXT_PROMPT]
    out = [t for t, c in text if c is not render.TXT_PROMPT]
    print("assembled")
    write("asm-base", base, "base")
    write("asm-lid", lid - recess, "lid")
    write("asm-inlay", recess, "inlay")
    write("asm-frame", m.bezel_ring(), "frame")
    write("asm-kbd", kbd, "kbd")
    write("asm-caps", list(caps), "caps")
    write("asm-phone", ph, "phone")
    write("asm-glass", glass, "glass")
    write("asm-text", out, "text")
    write("asm-prompt", prompt, "prompt")
    manifest["hinge"] = {"y": p.hinge_axis_y, "z": p.hinge_axis_z, "close_tilt": p.close_tilt}


def main():
    only = "--assembled" in sys.argv
    OUT.mkdir(parents=True, exist_ok=True)
    if only:      # keep the parts already built, add the assembled device to them
        manifest.update(json.loads((OUT / "manifest.json").read_text()))
        assembled()
        (OUT / "manifest.json").write_text(json.dumps(manifest, indent=1))
        return
    for old in OUT.glob("*"):
        old.unlink()

    tilt = degrees(atan((p.rim_rear - p.rim_front) / p.base_depth_to_axis))

    def pose(shape):
        """Rear wall on the bed, screen side up, as the adapter coupon is laid."""
        return Rot(Y=180) * (Rot(X=-tilt) * shape)

    # One drop for every lid and inlay, so the inlay still sits in its recess.
    ref_lid = m.build(bezel=True)[1]
    drop = -pose(ref_lid).bounding_box().min.Z

    def lay(shape):
        return Pos(0, 0, drop) * pose(shape)

    print("lids")
    recess = union(logo.inlays().values())
    through = union(logo.inlays(p.lid_rear_wall).values())
    write("inlay-recess", lay(recess), "inlay")
    write("inlay-through", lay(through), "inlay")
    for rib in RIBS:
        for tab in TABS:
            lid = m.build(bezel=True, rib_h=rib, tab_t=tab)[1]
            for logo_key, cut in (("none", None), ("recess", recess), ("through", through)):
                part = lid if cut is None else lid - cut
                n = len(part.solids())
                # The through cut leaves islands inside the dog by design (plate 4 has them
                # too); they print held by the inlay.
                if n != 1 and logo_key != "through":
                    raise ValueError(f"lid rib {rib} tab {tab} logo {logo_key}: {n} solids")
                write(f"lid-r{rib:.2f}-t{tab:.1f}-{logo_key}", lay(part), "lid")

    print("frames")

    def flat(shape):
        shape = Rot(X=-tilt) * shape
        return Pos(0, 0, -shape.bounding_box().min.Z) * shape

    write("frame-open", flat(m.bezel_ring()), "frame")
    write("frame-closed", flat(m.bezel_frame(closed=True)), "frame")

    print("bases")
    for nut, depth in (("din934", None), ("plain", p.nut_depth_plain)):
        for sw, window in (("shuttle", False), ("window", True)):
            base = m.build(nut_depth=depth, switch_window=window)[0]
            if len(base.solids()) != 1:
                raise ValueError(f"base {nut}/{sw} is not one solid")
            write(f"base-{nut}-{sw}", base, "base")

    print("switch parts")
    for finger in p.sw_finger_len:
        for proud in p.sw_stem_proud:
            write(f"shuttle-f{finger:.1f}-p{proud:.1f}",
                  m.switch_shuttle(proud=proud, finger=finger), "small")
    for clr in p.sw_plug_clr:
        plug = Rot(X=90) * m.switch_plug(clr)
        write(f"plug-c{clr:.2f}", Pos(0, 0, -plug.bounding_box().min.Z) * plug, "small")

    assembled()
    manifest["options"] = {
        "rib": [f"{r:.2f}" for r in RIBS], "tab": [f"{t:.1f}" for t in TABS],
        "finger": [f"{f:.1f}" for f in p.sw_finger_len],
        "proud": [f"{x:.1f}" for x in p.sw_stem_proud],
        "clr": [f"{c:.2f}" for c in p.sw_plug_clr],
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=1))
    total = sum(f.stat().st_size for f in OUT.glob("*.gz"))
    print(f"\n{len(manifest['parts'])} parts, {total / 1e6:.1f} MB in {OUT}")


if __name__ == "__main__":
    main()
