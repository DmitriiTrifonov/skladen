"""Shaded renders for the README. A small numpy rasteriser; no OpenGL, no VTK.

    .venv/bin/python cad/render.py   ->  docs/img/skladen2-open.png, docs/img/skladen2-closed.png

The printed shells come straight from model.build(). The phone and keyboard are
stand-ins built from their measured envelopes in params.py - there only so the
picture reads as a device rather than two empty shells, and placed exactly where
the pockets put the real ones.

Pipeline: tessellate each B-rep face on its own, so normals are smooth within a
face and crisp across edges; light per vertex; z-buffer at 2x; outline wherever
the part changes, depth jumps, or the surface creases; a soft contact shadow and
a longer cast shadow on the ground; downsample; crop to content.
"""

import sys
from math import cos, radians, tan
from pathlib import Path

import numpy as np
from build123d import Axis
from PIL import Image, ImageFilter

sys.path.insert(0, str(Path(__file__).parent))
import logo
import model as m
import params as p

IMG = Path(__file__).parent.parent / "docs" / "img"
W, H, SS = 1600, 1050, 2           # output size and supersampling factor
w, h = W * SS, H * SS


def hexcol(s):
    return np.array([int(s[i:i + 2], 16) for i in (1, 3, 5)], float) / 255


# Colours as printed (photo of 2026-10-24): lid and base are translucent clear PETG, the
# bezel frame and the logo inlay on the lid are translucent teal.
CLEAR_PETG = hexcol("#D6E2E2")
TEAL_PETG = hexcol("#4DC4C0")
KBD_BODY = hexcol("#1D1F24")
KBD_CAP = hexcol("#2B2E35")
PHONE = hexcol("#24262B")
GLASS = hexcol("#0A0C10")
TXT_OUT = hexcol("#BFC6D0")
TXT_PROMPT = hexcol("#86D49A")

KEY = np.array([-0.45, -0.60, 0.66]); KEY /= np.linalg.norm(KEY)     # to the key light
FILL = np.array([0.85, -0.15, 0.35]); FILL /= np.linalg.norm(FILL)


# --- stand-ins ------------------------------------------------------------
def keyboard():
    y0 = p.wall_t + p.clr_kbd
    y1 = y0 + p.kbd_depth_y
    z0 = p.base_floor_t

    def top(y):
        return z0 + p.kbd_h_front + (y - y0) / p.kbd_depth_y * (p.kbd_h_rear - p.kbd_h_front)

    body = m.yz_prism([(y0, z0), (y1, z0), (y1, top(y1)), (y0, top(y0))], p.kbd_span_x)

    # A plausible compact layout, front row first. Units of one key pitch.
    rows = [
        [1, 1, 1, 1, 4, 1, 1, 1, 1],
        [2, 1, 1, 1, 1, 1, 1, 1, 1, 2],
        [1.75, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1.25],
        [1.5, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1.5],
        [1] * 12,
    ]
    pitch_x, pitch_y, gap = 15.55, 15.3, 2.3
    field_y0 = y0 + 4.4
    caps = []
    for r, row in enumerate(rows):
        ya = field_y0 + r * pitch_y + gap / 2
        yb = ya + pitch_y - gap
        x = -sum(row) * pitch_x / 2
        for u in row:
            wx = u * pitch_x - gap
            caps.append(m.yz_prism(
                [(ya, top(ya) - 0.2), (yb, top(yb) - 0.2),
                 (yb, top(yb) + p.kbd_keycap_rear), (ya, top(ya) + p.kbd_keycap_front)],
                wx, x + u * pitch_x / 2))
            x += u * pitch_x
    return body, caps


def phone():
    """Phone, screen and a few lines of terminal, in the lid's CLOSED frame.

    The screen is the LOW face there: it looks down at the keyboard when shut.
    Its top edge, once open, is the lid's front edge - small Y.
    """
    bot_f = p.rim_front
    slope = (p.rim_rear - p.rim_front) / p.base_depth_to_axis

    def z(y, off):
        return bot_f + slope * y + off

    y0 = p.phone_front_wall + p.clr_phone
    y1 = y0 + p.phone_y
    body = m.yz_prism([(y0, z(y0, 0)), (y1, z(y1, 0)),
                       (y1, z(y1, p.phone_z)), (y0, z(y0, p.phone_z))], p.phone_x)

    sx, sy0, sy1 = p.phone_x - 15.0, y0 + 3.2, y1 - 3.2
    glass = m.yz_prism([(sy0, z(sy0, -0.15)), (sy1, z(sy1, -0.15)),
                        (sy1, z(sy1, 0.05)), (sy0, z(sy0, 0.05))], sx)

    lines = [(0.34, TXT_PROMPT), (0.86, TXT_OUT), (0.71, TXT_OUT), (0.52, TXT_OUT),
             (0.0, None), (0.40, TXT_PROMPT), (0.93, TXT_OUT), (0.64, TXT_OUT),
             (0.27, TXT_OUT), (0.0, None), (0.12, TXT_PROMPT)]
    text = []
    x_left, usable = -sx / 2 + 4.0, sx - 8.0
    for i, (frac, col) in enumerate(lines):
        if not frac:
            continue
        ya = sy0 + 4.0 + i * 3.1
        yb = ya + 1.25
        wx = frac * usable
        text.append((m.yz_prism([(ya, z(ya, -0.30)), (yb, z(yb, -0.30)),
                                 (yb, z(yb, -0.10)), (ya, z(ya, -0.10))],
                                wx, x_left + wx / 2), col))
    # block cursor after the last prompt
    ya = sy0 + 4.0 + 10 * 3.1
    cx = x_left + 0.12 * usable + 2.2
    text.append((m.yz_prism([(ya - 0.3, z(ya - 0.3, -0.30)), (ya + 1.55, z(ya + 1.55, -0.30)),
                             (ya + 1.55, z(ya + 1.55, -0.10)), (ya - 0.3, z(ya - 0.3, -0.10))],
                            1.6, cx), TXT_PROMPT))
    return body, glass, text


# --- mesh -----------------------------------------------------------------
class Mesh:
    def __init__(self):
        self.V, self.N, self.C, self.F, self.I = [], [], [], [], []
        self.gloss, self.n = [], 0

    def add(self, shape, colour, part_id, gloss=0.0, tol=0.06, ang=0.18):
        for face in shape.faces():
            verts, tris = face.tessellate(tol, ang)
            if not tris:
                continue
            V = np.array([(v.X, v.Y, v.Z) for v in verts], float)
            F = np.array(tris, int)
            tn = np.cross(V[F[:, 1]] - V[F[:, 0]], V[F[:, 2]] - V[F[:, 0]])
            ref = face.normal_at(face.center())
            if (tn.sum(0) @ np.array([ref.X, ref.Y, ref.Z])) < 0:
                F = F[:, ::-1]
                tn = -tn
            vn = np.zeros_like(V)
            for k in range(3):
                np.add.at(vn, F[:, k], tn)
            vn /= np.linalg.norm(vn, axis=1, keepdims=True) + 1e-12
            self.V.append(V); self.N.append(vn)
            self.C.append(np.repeat(colour[None], len(V), 0))
            self.gloss.append(np.full(len(V), gloss))
            self.F.append(F + self.n)
            self.I.append(np.full(len(F), part_id))
            self.n += len(V)

    def arrays(self):
        return (np.vstack(self.V), np.vstack(self.N), np.vstack(self.C),
                np.concatenate(self.gloss), np.vstack(self.F), np.concatenate(self.I))


# --- camera and raster ----------------------------------------------------
class Camera:
    def __init__(self, eye, target, fov):
        self.eye = np.array(eye, float)
        f = np.array(target, float) - self.eye
        self.f = f / np.linalg.norm(f)
        r = np.cross(self.f, (0, 0, 1))
        self.r = r / np.linalg.norm(r)
        self.u = np.cross(self.r, self.f)
        self.focal = (w / 2) / tan(radians(fov) / 2)

    def project(self, P):
        d = P - self.eye
        z = d @ self.f
        return (d @ self.r) / z * self.focal + w / 2, -(d @ self.u) / z * self.focal + h / 2, z


def light(V, N, C, G, cam):
    view = cam.eye - V
    view /= np.linalg.norm(view, axis=1, keepdims=True)
    hemi = 0.30 + 0.12 * N[:, 2]
    d = 0.72 * np.clip(N @ KEY, 0, None) + 0.26 * np.clip(N @ FILL, 0, None)
    half = KEY + view
    half /= np.linalg.norm(half, axis=1, keepdims=True)
    spec = G * np.clip((N * half).sum(1), 0, None) ** 48
    rim = 0.10 * np.clip(1 - (N * view).sum(1), 0, 1) ** 3
    return np.clip(C * (hemi + d)[:, None] + (spec + rim)[:, None], 0, 1)


def rasterise(cam, V, N, VC, F, I):
    X, Y, Z = cam.project(V)
    zbuf = np.full((h, w), np.inf, np.float32)
    cbuf = np.zeros((h, w, 3), np.float32)
    nbuf = np.zeros((h, w, 3), np.float32)
    ibuf = np.full((h, w), -1, np.int32)
    for (a, b, c), pid in zip(F, I):
        za, zb, zc = Z[a], Z[b], Z[c]
        if min(za, zb, zc) <= 1:
            continue
        xa, xb, xc, ya, yb, yc = X[a], X[b], X[c], Y[a], Y[b], Y[c]
        den = (yb - yc) * (xa - xc) + (xc - xb) * (ya - yc)
        if abs(den) < 1e-9:
            continue
        x0 = max(int(min(xa, xb, xc)), 0); x1 = min(int(max(xa, xb, xc)) + 1, w - 1)
        y0 = max(int(min(ya, yb, yc)), 0); y1 = min(int(max(ya, yb, yc)) + 1, h - 1)
        if x0 > x1 or y0 > y1:
            continue
        px, py = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
        l1 = ((yb - yc) * (px - xc) + (xc - xb) * (py - yc)) / den
        l2 = ((yc - ya) * (px - xc) + (xa - xc) * (py - yc)) / den
        l3 = 1 - l1 - l2
        inside = (l1 >= -1e-5) & (l2 >= -1e-5) & (l3 >= -1e-5)
        if not inside.any():
            continue
        iz = l1 / za + l2 / zb + l3 / zc
        z = 1 / iz
        sub = zbuf[y0:y1 + 1, x0:x1 + 1]
        hit = inside & (z < sub)
        if not hit.any():
            continue
        w1, w2, w3 = (l1 / za * z)[hit], (l2 / zb * z)[hit], (l3 / zc * z)[hit]
        sub[hit] = z[hit]
        cbuf[y0:y1 + 1, x0:x1 + 1][hit] = (w1[:, None] * VC[a] + w2[:, None] * VC[b]
                                           + w3[:, None] * VC[c])
        nbuf[y0:y1 + 1, x0:x1 + 1][hit] = (w1[:, None] * N[a] + w2[:, None] * N[b]
                                           + w3[:, None] * N[c])
        ibuf[y0:y1 + 1, x0:x1 + 1][hit] = pid
    return zbuf, cbuf, nbuf, ibuf


def outlines(zbuf, nbuf, ibuf):
    obj = ibuf >= 0
    e = np.zeros((h, w), bool)
    iz = np.where(obj, 1 / np.where(obj, zbuf, 1), 0)
    nn = nbuf / (np.linalg.norm(nbuf, axis=2, keepdims=True) + 1e-9)
    for dy, dx in ((0, 1), (1, 0)):
        A = (slice(0, h - dy), slice(0, w - dx))
        B = (slice(dy, h), slice(dx, w))
        cut = (ibuf[A] != ibuf[B])
        crease = (nn[A] * nn[B]).sum(2) < cos(radians(38))
        e[A] |= (cut | crease) & obj[A]
        e[B] |= (cut | crease) & obj[B]
    # depth discontinuities: 1/z is linear across a plane, so its second
    # difference is ~0 on surfaces and large where one surface hides another
    for ax in (0, 1):
        d2 = np.abs(np.roll(iz, 1, ax) + np.roll(iz, -1, ax) - 2 * iz)
        e |= obj & (d2 > 0.012 * iz)
    return e


def shadow(V, F, extent, res, direction, blur_mm):
    gx0, gx1, gy0, gy1 = extent
    gw, gh = int((gx1 - gx0) / res), int((gy1 - gy0) / res)
    t = V[:, 2] / direction[2]
    SX = (V[:, 0] - t * direction[0] - gx0) / res
    SY = (V[:, 1] - t * direction[1] - gy0) / res
    img = np.zeros((gh, gw), np.uint8)
    for a, b, c in F:
        xa, xb, xc, ya, yb, yc = SX[a], SX[b], SX[c], SY[a], SY[b], SY[c]
        den = (yb - yc) * (xa - xc) + (xc - xb) * (ya - yc)
        if abs(den) < 1e-9:
            continue
        x0 = max(int(min(xa, xb, xc)), 0); x1 = min(int(max(xa, xb, xc)) + 1, gw - 1)
        y0 = max(int(min(ya, yb, yc)), 0); y1 = min(int(max(ya, yb, yc)) + 1, gh - 1)
        if x0 > x1 or y0 > y1:
            continue
        px, py = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
        l1 = ((yb - yc) * (px - xc) + (xc - xb) * (py - yc)) / den
        l2 = ((yc - ya) * (px - xc) + (xa - xc) * (py - yc)) / den
        inside = (l1 >= 0) & (l2 >= 0) & (1 - l1 - l2 >= 0)
        img[y0:y1 + 1, x0:x1 + 1][inside] = 255
    blurred = Image.fromarray(img).filter(ImageFilter.GaussianBlur(blur_mm / res))
    return np.asarray(blurred, np.float32) / 255


def ground_alpha(cam, zbuf, V, F):
    extent, res = (-330, 330, -260, 420), 0.6
    key = KEY.copy()
    contact = shadow(V, F, extent, res, np.array([0.0, 0.0, 1.0]), 1.6)
    cast = shadow(V, F, extent, res, key, 9.0)
    gx0, gx1, gy0, gy1 = extent
    px, py = np.meshgrid(np.arange(w) + 0.5, np.arange(h) + 0.5)
    d = (cam.f[None, None] + ((px - w / 2) / cam.focal)[..., None] * cam.r
         - ((py - h / 2) / cam.focal)[..., None] * cam.u)
    t = -cam.eye[2] / np.where(d[..., 2] < -1e-6, d[..., 2], -1e-6)
    gx = ((cam.eye[0] + t * d[..., 0]) - gx0) / res
    gy = ((cam.eye[1] + t * d[..., 1]) - gy0) / res
    ok = (d[..., 2] < -1e-6) & (t < zbuf) & (gx >= 0) & (gy >= 0) \
        & (gx < contact.shape[1] - 1) & (gy < contact.shape[0] - 1)
    ix = np.clip(gx.astype(int), 0, contact.shape[1] - 1)
    iy = np.clip(gy.astype(int), 0, contact.shape[0] - 1)
    a = 1 - (1 - 0.62 * contact[iy, ix]) * (1 - 0.30 * cast[iy, ix])
    return np.where(ok, a, 0)


def render(parts, cam, out):
    mesh = Mesh()
    for pid, (shape, colour, gloss) in enumerate(parts):
        mesh.add(shape, colour, pid, gloss)
    V, N, C, G, F, I = mesh.arrays()
    VC = light(V, N, C, G, cam)
    zbuf, cbuf, nbuf, ibuf = rasterise(cam, V, N, VC, F, I)
    edge = outlines(zbuf, nbuf, ibuf)
    edge = np.asarray(Image.fromarray(edge.astype(np.uint8) * 255)
                      .filter(ImageFilter.MaxFilter(3)), bool) & (ibuf >= 0)
    rgb = np.where(edge[..., None], cbuf * 0.35 + 0.02, cbuf)

    ga = ground_alpha(cam, zbuf, V, F)
    obj = ibuf >= 0
    rgba = np.zeros((h, w, 4), np.float32)
    rgba[..., :3] = np.where(obj[..., None], rgb, hexcol("#0E1424"))
    rgba[..., 3] = np.where(obj, 1.0, ga)

    im = Image.fromarray((np.clip(rgba, 0, 1) * 255).astype(np.uint8), "RGBA")
    im = im.convert("RGBa").resize((W, H), Image.LANCZOS).convert("RGBA")
    box = im.getchannel("A").point(lambda v: 255 if v > 6 else 0).getbbox()
    pad = 24
    im = im.crop((max(box[0] - pad, 0), max(box[1] - pad, 0),
                  min(box[2] + pad, W), min(box[3] + pad, H)))
    IMG.mkdir(parents=True, exist_ok=True)
    im.save(out, optimize=True)
    print(f"  {out.relative_to(IMG.parent.parent)}   {im.size[0]} x {im.size[1]}"
          f"   {len(F)} triangles")


def union(parts):
    out = None
    for part in parts:
        out = part if out is None else out + part
    return out


def main():
    base = m.build()[0]
    lid = m.build(bezel=True, rib_h=p.phone_rib_h, tab_t=p.button_tab_t)[1]
    inlay = union(logo.inlays().values())
    lid = lid - inlay
    frame = m.bezel_ring()
    kbd, caps = keyboard()
    ph, glass, text = phone()
    axis = Axis((0, p.hinge_axis_y, p.hinge_axis_z), (1, 0, 0))

    def lid_parts(turn):
        rot = (lambda s: s.rotate(axis, turn)) if turn else (lambda s: s)
        return ([(rot(lid), CLEAR_PETG, 0.35), (rot(inlay), TEAL_PETG, 0.35), (rot(frame), TEAL_PETG, 0.35), (rot(ph), PHONE, 0.2), (rot(glass), GLASS, 0.9)]
                + [(rot(t), c, 0.0) for t, c in text])

    below = [(base, CLEAR_PETG, 0.35), (kbd, KBD_BODY, 0.15)] + [(c, KBD_CAP, 0.25) for c in caps]

    print("renders:")
    opening = 112
    render(below + lid_parts(-(opening + p.close_tilt)),
           Camera(eye=(-377, -531, 306), target=(2, 45, 42), fov=24),
           IMG / "skladen2-open.png")
    render(below + lid_parts(0),
           Camera(eye=(400, -511, 187), target=(0, 52, 10), fov=24),
           IMG / "skladen2-closed.png")


if __name__ == "__main__":
    main()
