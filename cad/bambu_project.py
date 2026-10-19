"""Refill the owner's Bambu Studio project with the current lid and logo inlay.

cad/templates/bezel-lid-logo.3mf is a project saved from the slicer: lid lying on its
back, filaments assigned, process settings. This keeps all of that and swaps in
fresh meshes, with the inlay placed exactly where the CAD puts it (the slicer's
own Assemble had left it 0.2 mm off in X).
"""
import re
import zipfile
from pathlib import Path

import numpy as np

TEMPLATE = Path(__file__).parent / "templates" / "bezel-lid-logo.3mf"


def welded(shape):
    """Tessellated shape with the vertices on shared face edges merged. The raw
    tessellation repeats them per face, which a slicer reads as open edges."""
    vs, ts = shape.tessellate(0.01, 0.1)
    v = np.array([(p.X, p.Y, p.Z) for p in vs])
    uniq, inv = np.unique(np.round(v, 4), axis=0, return_inverse=True)
    inv = inv.reshape(-1)
    tris = [tuple(int(inv[i]) for i in t) for t in ts]
    return uniq, [t for t in tris if len(set(t)) == 3]


def open_edges(ts):
    """Edges not used exactly twice in opposite directions; 0 for a closed mesh."""
    from collections import Counter
    c = Counter()
    for a, b, d in ts:
        for u, w in ((a, b), (b, d), (d, a)):
            c[(u, w)] += 1
    return sum(1 for (u, w), n in c.items() if n != 1 or c.get((w, u), 0) != 1)


def _local(shape):
    """Tessellated shape, centred on its bounding box as the slicer stores it."""
    v, ts = welded(shape)
    c = (v.min(0) + v.max(0)) / 2
    return v - c, c, ts


def _mesh_xml(v, ts):
    vx = "\n".join(f'     <vertex x="{x:.6f}" y="{y:.6f}" z="{z:.6f}"/>' for x, y, z in v)
    tx = "\n".join(f'     <triangle v1="{a}" v2="{b}" v3="{c}"/>' for a, b, c in ts)
    return (f"   <mesh>\n    <vertices>\n{vx}\n    </vertices>\n"
            f"    <triangles>\n{tx}\n    </triangles>\n   </mesh>\n")


def _flat(M):
    return " ".join(f"{x:.9g}" for x in M.flatten())


def write(lid, inlay, out):
    """lid / inlay: build123d shapes in CAD coordinates. Returns the inlay offset error."""
    z = zipfile.ZipFile(TEMPLATE)
    files = {n: z.read(n) for n in z.namelist()}
    cfg = files["Metadata/model_settings.config"].decode()
    mats = [np.array(x.split(), float).reshape(4, 4)
            for x in re.findall(r'key="matrix" value="([^"]+)"', cfg)]
    # template order: part 1 = inlay, part 2 = lid
    M_logo, M_lid = mats
    R, t = M_lid[:3, :3], M_lid[:3, 3]
    v_lid, c_lid, t_lid = _local(lid)
    v_logo, c_logo, t_logo = _local(inlay)
    new_logo = np.eye(4)
    new_logo[:3, :3] = R
    new_logo[:3, 3] = R @ (c_logo - c_lid) + t
    err = np.abs(new_logo[:3, 3] - M_logo[:3, 3]).max()
    bad = open_edges(t_lid) + open_edges(t_logo)
    if bad:
        raise ValueError(f"{bad} open edges in the slicer meshes")

    obj = files["3D/Objects/Assembly_11.model"].decode()
    for oid, (v, ts) in ((1, (v_logo, t_logo)), (2, (v_lid, t_lid))):
        obj = re.sub(rf'(<object id="{oid}"[^>]*>\n).*?(  </object>)',
                     lambda mm, v=v, ts=ts: mm.group(1) + _mesh_xml(v, ts) + mm.group(2),
                     obj, count=1, flags=re.S)
    files["3D/Objects/Assembly_11.model"] = obj.encode()

    # logo's part matrix, in model_settings (row-major 4x4) and the component transform
    old = re.findall(r'key="matrix" value="([^"]+)"', cfg)[0]
    cfg = cfg.replace(old, _flat(new_logo), 1)
    files["Metadata/model_settings.config"] = cfg.encode()
    top = files["3D/3dmodel.model"].decode()
    comp = re.search(r'(<component [^>]*objectid="1"[^>]*transform=")([^"]+)(")', top)
    tf = " ".join(f"{x:.9g}" for x in [*R[:, 0], *R[:, 1], *R[:, 2], *new_logo[:3, 3]])
    top = top[:comp.start(2)] + tf + top[comp.end(2):]
    files["3D/3dmodel.model"] = top.encode()

    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zo:
        for n, b in files.items():
            zo.writestr(n, b)
    return err
