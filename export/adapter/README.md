# adapter/

**Parked 2026-10-23.** ADR-0013: a seat in the bezel lid's USB-C slot for a short
male-to-female USB-C extender left in the phone. The extender is dropped for now and
`build.py` no longer rebuilds these files; they are as they were on 2026-10-21 and do
not have the crush ribs or the button tongues.

| File | What it is |
|---|---|
| `skladen2-lid-bezel-adapter.stl`, `.step` | The bezel lid with the seat |
| `skladen2-coupon-usbc-lid.stl`, `.step`, `.3mf` | The lid's right end, to try the real adapter in; the 3MF is in its printing pose |

The seat is sized for an **assumed** body of 10.5 x 6.0 x 18.5 mm, read off photos;
caliper the real adapter first. To rebuild, turn the `adapter_variant(base)` call in
`cad/build.py` back on.
