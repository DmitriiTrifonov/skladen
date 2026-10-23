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


PLATE = 256.0            # the A1's bed
PLATE_STRIDE = PLATE * 1.2   # Bambu Studio lays plates out a fifth of a bed apart


def _flat(M):
    return " ".join(f"{x:.9g}" for x in np.asarray(M).flatten())


def write_plates(out, lid, inlay, plates, through=None, through_index=None, extra=(),
                 plate_names=()):
    """A multi-plate project: plate 1 is the lid with its logo exactly as write() lays
    it out; every other plate is a list of (name, shape, filament) lying as exported,
    each shape on its own plate, centred. Printer and filament settings come from the
    template. Plates are placed on Bambu's grid (a column count of ceil(sqrt(n)),
    rows going toward -Y), so a slice with the real slicer is the check that matters.
    `through` = (lid, inlay) of the through-logo variant: one more plate, the same lid
    in the same pose as plate 1, so the two cannot drift apart. It is the last plate
    unless `through_index` (0-based) puts it earlier; `plates` then continue after it.
    `extra` = [(name, lid, inlay, plate, dy)], more through-logo lids in the same pose on
    their own plates (0-based, after the others), `dy` mm along the plate's Y, so two can
    share one. All of them print lid in filament 3, inlay in 4."""
    import uuid
    from math import ceil, sqrt

    z = zipfile.ZipFile(TEMPLATE)
    files = {n: z.read(n) for n in z.namelist()}
    cfg = files["Metadata/model_settings.config"].decode()
    mats = [np.array(x.split(), float).reshape(4, 4)
            for x in re.findall(r'key="matrix" value="([^"]+)"', cfg)]
    M_logo, M_lid = mats
    item_lid = re.search(r'<item [^>]*transform="([^"]+)"',
                         files["3D/3dmodel.model"].decode()).group(1).split()
    R, t = M_lid[:3, :3], M_lid[:3, 3]
    first = 1 if lid is not None else 0     # lid=None: a project of plain plates, no lid plate
    if lid is not None:
        v_lid, c_lid, t_lid = _local(lid)
        v_logo, c_logo, t_logo = _local(inlay)
        new_logo = np.eye(4)
        new_logo[:3, :3] = R
        new_logo[:3, 3] = R @ (c_logo - c_lid) + t
    M_lid = np.array(M_lid)

    n_plates = first + len(plates) + (1 if through else 0) + len({e[3] for e in extra})
    cols = ceil(sqrt(n_plates))

    def origin(i):
        return (i % cols) * PLATE_STRIDE, -(i // cols) * PLATE_STRIDE

    meshes = [(v_logo, t_logo), (v_lid, t_lid)] if first else []    # mesh ids 1 and 2
    # objects: (id, name, extruder, [(mesh id, part matrix, part name, extruder)], item)
    objs = [(3, "Lid with logo", 3,
             [(1, new_logo, "inlay", 4), (2, M_lid, "lid", 3)],
             " ".join(item_lid))] if first else []
    plate_of = {3: 0} if first else {}
    nxt = 4
    for i, plate in enumerate(plates):
        pi = i + first
        if through and through_index is not None and pi >= through_index:
            pi += 1
        ox, oy = origin(pi)
        for name, shape, fil in plate:
            v, c, ts = _local(shape)
            if open_edges(ts):
                raise ValueError(f"open edges in {name}")
            meshes.append((v, ts))
            mid = len(meshes)
            # The shape keeps its exported position; centre it on the plate.
            h = (v[:, 2].max() - v[:, 2].min()) / 2
            xy = np.array([PLATE / 2 + ox, PLATE / 2 + oy])
            objs.append((nxt, name, fil, [(mid, np.eye(4), name, fil)],
                         f"1 0 0 0 1 0 0 0 1 {xy[0]:.6f} {xy[1]:.6f} {h:.6f}"))
            plate_of[nxt] = pi
            nxt += 1
    fixed = {0} if first else set()
    if through:
        lid2, inlay2 = through
        v_l2, c_l2, t_l2 = _local(lid2)
        v_i2, c_i2, t_i2 = _local(inlay2)
        if open_edges(t_l2) + open_edges(t_i2):
            raise ValueError("open edges in the through-logo meshes")
        if not np.allclose(c_l2, c_lid, atol=1e-3):
            raise ValueError("the through lid is not centred like plate 1's")
        logo2 = np.eye(4)
        logo2[:3, :3] = R
        logo2[:3, 3] = R @ (c_i2 - c_lid) + t
        meshes += [(v_i2, t_i2), (v_l2, t_l2)]
        pi = n_plates - 1 if through_index is None else through_index
        ox, oy = origin(pi)
        tf2 = list(item_lid)
        tf2[9], tf2[10] = f"{float(item_lid[9]) + ox:.6f}", f"{float(item_lid[10]) + oy:.6f}"
        objs.append((nxt, "Lid with through logo", 3,
                     [(len(meshes) - 1, logo2, "inlay", 4), (len(meshes), M_lid, "lid", 3)],
                     " ".join(tf2)))
        plate_of[nxt] = pi
        fixed.add(pi)
        nxt += 1
    for name, lid2, inlay2, pi, dy in extra:
        v_l2, c_l2, t_l2 = _local(lid2)
        v_i2, c_i2, t_i2 = _local(inlay2)
        if open_edges(t_l2) + open_edges(t_i2):
            raise ValueError(f"open edges in {name}")
        if not np.allclose(c_l2, c_lid, atol=1e-3):
            raise ValueError(f"{name} is not centred like plate 1's lid")
        logo2 = np.eye(4)
        logo2[:3, :3] = R
        logo2[:3, 3] = R @ (c_i2 - c_lid) + t
        meshes += [(v_i2, t_i2), (v_l2, t_l2)]
        ox, oy = origin(pi)
        tf2 = list(item_lid)
        tf2[9], tf2[10] = f"{float(item_lid[9]) + ox:.6f}", f"{float(item_lid[10]) + oy + dy:.6f}"
        objs.append((nxt, name, 3,
                     [(len(meshes) - 1, logo2, "inlay", 4), (len(meshes), M_lid, "lid", 3)],
                     " ".join(tf2)))
        plate_of[nxt] = pi
        fixed.add(pi)
        nxt += 1
    # Spread each plate's objects along X so they do not overlap. Done after sizing.
    by_plate = {}
    for o in objs:
        by_plate.setdefault(plate_of[o[0]], []).append(o)
    placed = []
    for pi, group in by_plate.items():
        if pi in fixed:
            placed += group
            continue
        ox, oy = origin(pi)
        widths = []
        for o in group:
            v = meshes[o[3][0][0] - 1][0]
            widths.append((v[:, 0].max() - v[:, 0].min(), v[:, 1].max() - v[:, 1].min()))
        # Everything sits clear of the plate edge, where the bed heats worst. Small
        # "Plug" parts go in a row at the back (north), 15 mm apart; the rest is
        # laid out in rows, each centred in X and the block centred in Y.
        plug = [k for k, o in enumerate(group) if o[1].startswith("Plug")]
        main = [k for k in range(len(group)) if k not in plug]
        rows, cur, cw = [], [], 0.0
        for k in main:
            w = widths[k][0]
            if cur and cw + w > PLATE - 12:
                rows.append(cur)
                cur, cw = [], 0.0
            cur.append(k)
            cw += w + 6.0
        rows.append(cur)
        row_w = [sum(widths[k][0] for k in r) + 6.0 * (len(r) - 1) for r in rows]
        row_d = [max(widths[k][1] for k in r) for r in rows]
        total_h = sum(row_d) + 6.0 * (len(rows) - 1)
        pos = {}
        y = (PLATE - total_h) / 2
        for r, rw, rd in zip(rows, row_w, row_d):
            x = (PLATE - rw) / 2
            for k in r:
                w, d = widths[k]
                pos[k] = (ox + x + w / 2, oy + y + rd / 2)
                x += w + 6.0
            y += rd + 6.0
        if plug:
            gap = 15.0
            pw = sum(widths[k][0] for k in plug) + gap * (len(plug) - 1)
            pd = max(widths[k][1] for k in plug)
            x = (PLATE - pw) / 2
            py = PLATE - 30.0 - pd / 2
            if (PLATE + total_h) / 2 + 6.0 > py - pd / 2:
                raise ValueError("plugs do not fit north of the main part")
            for k in plug:
                w, d = widths[k]
                pos[k] = (ox + x + w / 2, oy + py)
                x += w + gap
        for k, o in enumerate(group):
            tf = o[4].split()
            tf[9], tf[10] = f"{pos[k][0]:.6f}", f"{pos[k][1]:.6f}"
            placed.append(o[:4] + (" ".join(tf),))

    # Objects file: every mesh
    body = []
    for i, (v, ts) in enumerate(meshes, start=1):
        body.append(f' <object id="{i}" p:UUID="{uuid.uuid4()}" type="model">\n'
                    + _mesh_xml(v, ts).replace("   <mesh>", "  <mesh>", 1) + " </object>\n")
    head = files["3D/Objects/Assembly_11.model"].decode()
    head = head[:head.index("<resources>") + len("<resources>")] + "\n" + "".join(body) \
        + " </resources>\n <build/>\n</model>\n"
    files["3D/Objects/Assembly_11.model"] = head.encode()

    # Main model
    top = files["3D/3dmodel.model"].decode()
    res, items = [], []
    for oid, name, ext, parts, item in placed:
        comps = "".join(
            f'<component p:path="/3D/Objects/Assembly_11.model" objectid="{mid}" '
            f'p:UUID="{uuid.uuid4()}" transform="{_comp(M)}"/>'
            for mid, M, pname, pext in parts)
        res.append(f'  <object id="{oid}" p:UUID="{uuid.uuid4()}" type="model">'
                   f'<components>{comps}</components></object>\n')
        items.append(f'  <item objectid="{oid}" p:UUID="{uuid.uuid4()}" transform="{item}" '
                     f'printable="1"/>\n')
    top = re.sub(r"<resources>.*</resources>", lambda m_: "<resources>\n" + "".join(res)
                 + " </resources>", top, flags=re.S)
    top = re.sub(r"<build [^>]*>.*</build>", lambda m_: f'<build p:UUID="{uuid.uuid4()}">\n'
                 + "".join(items) + " </build>", top, flags=re.S)
    files["3D/3dmodel.model"] = top.encode()

    # model_settings: objects, then plates
    ms = ['<?xml version="1.0" encoding="UTF-8"?>\n<config>\n']
    for oid, name, ext, parts, item in placed:
        ms.append(f'  <object id="{oid}">\n    <metadata key="name" value="{name}"/>\n'
                  f'    <metadata key="extruder" value="{ext}"/>\n')
        for k, (mid, M, pname, pext) in enumerate(parts, start=1):
            ms.append(f'    <part id="{k}" subtype="normal_part">\n'
                      f'      <metadata key="name" value="{pname}"/>\n'
                      f'      <metadata key="matrix" value="{_flat(M)}"/>\n'
                      f'      <metadata key="extruder" value="{pext}"/>\n'
                      f'    </part>\n')
        ms.append("  </object>\n")
    for pi in range(n_plates):
        ms.append(f'  <plate>\n    <metadata key="plater_id" value="{pi + 1}"/>\n'
                  f'    <metadata key="plater_name" value="{plate_names[pi] if pi < len(plate_names) else ""}"/>\n'
                  f'    <metadata key="locked" value="false"/>\n'
                  f'    <metadata key="filament_map_mode" value="Auto For Flush"/>\n'
                  f'    <metadata key="filament_maps" value="1 1 1 1 1"/>\n')
        if pi == 0 and first:
            ms.append('    <metadata key="thumbnail_file" value="Metadata/plate_1.png"/>\n'
                      '    <metadata key="thumbnail_no_light_file" value="Metadata/plate_no_light_1.png"/>\n'
                      '    <metadata key="top_file" value="Metadata/top_1.png"/>\n'
                      '    <metadata key="pick_file" value="Metadata/pick_1.png"/>\n')
        for o in placed:
            if plate_of[o[0]] == pi:
                ms.append(f'    <model_instance>\n      <metadata key="object_id" value="{o[0]}"/>\n'
                           f'      <metadata key="instance_id" value="0"/>\n'
                           f'      <metadata key="identify_id" value="{400 + o[0]}"/>\n'
                           f'    </model_instance>\n')
        ms.append("  </plate>\n")
    ms.append("  <assemble>\n")
    for o in placed:
        ms.append(f'   <assemble_item object_id="{o[0]}" instance_id="0" transform="{o[4]}" offset="0 0 0" />\n')
    ms.append("  </assemble>\n</config>\n")
    files["Metadata/model_settings.config"] = "".join(ms).encode()

    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zo:
        for n, b in files.items():
            zo.writestr(n, b)
    return {o[1]: plate_of[o[0]] + 1 for o in placed}


def _comp(M):
    """A 4x4 matrix as the 3MF component transform: columns of R, then translation."""
    M = np.asarray(M)
    return " ".join(f"{x:.9g}" for x in [*M[:3, 0], *M[:3, 1], *M[:3, 2], *M[:3, 3]])


def write_single(shape, out, name):
    """One part as a plain 3MF, as placed: no slicer settings, just the mesh."""
    vs, ts = welded(shape)
    assert not open_edges(ts), f"open edges in {name}"
    v = "".join(f'<vertex x="{x:.5f}" y="{y:.5f}" z="{z:.5f}"/>' for x, y, z in vs.tolist())
    t = "".join(f'<triangle v1="{a}" v2="{b}" v3="{c}"/>' for a, b, c in ts)
    xml = ('<?xml version="1.0" encoding="UTF-8"?><model unit="millimeter" xml:lang="en-US" '
           'xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02"><resources>'
           f'<object id="1" name="{name}" type="model"><mesh><vertices>{v}</vertices>'
           f'<triangles>{t}</triangles></mesh></object></resources>'
           '<build><item objectid="1"/></build></model>')
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", '<?xml version="1.0" encoding="UTF-8"?><Types '
                   'xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
                   '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
                   '<Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>')
        z.writestr("_rels/.rels", '<?xml version="1.0" encoding="UTF-8"?><Relationships '
                   'xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                   '<Relationship Target="/3D/3dmodel.model" Id="rel0" '
                   'Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
        z.writestr("3D/3dmodel.model", xml)
