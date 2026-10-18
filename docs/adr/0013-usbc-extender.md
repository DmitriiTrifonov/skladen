# ADR-0013: A short USB-C extender left in the phone

- **Status:** Proposed
- **Date:** 2026-10-17
- **Decides:** how F6 is met; sizes the lid's right-end slot

## Context

The same Reddit build shows a small USB-C adapter plugged into the phone's port and
seated in a notch in the lid's end wall, so the port the user touches is the adapter's,
not the phone's.

Today the phone's USB-C faces the lid's right end through a 12.0 wide, 7.0 deep slot,
open on the screen side, cut through a wall about 20 mm thick
([ADR-0011](0011-phone-swap-pocophone-f1.md)). A plug therefore lies in the slot for
most of its length, so a right-angle or short-overmould cable is the practical choice.
`build.py` checks that a 3.5 mm rod clears, not that a real cable does.

## Options

### Option A — plug the cable straight into the phone (current)

| Pros | Cons |
|---|---|
| No extra part | Cable overmould must fit a 12 x 7 slot over ~20 mm |
| | Every insertion wears the phone's own port, the usual failure on an old phone |
| | Side load from the cable goes onto the phone's board |

### Option B — a short male-to-female extender, left in

The adapter stays in the phone. Its female end sits in the slot; the cable plugs into it.

| Pros | Cons |
|---|---|
| The adapter takes the wear; a 3 EUR part replaces a phone's port | A part to buy and measure before the slot can be sized |
| Shorter plug travel into the slot (adapter ~10-15 mm, plug only the remainder) | Cheap adapters can cap charging speed through contact resistance |
| The slot's walls can carry side load instead of the port | Phone leaves the lid with a stub on it |
| The slot is open on the screen side, so the phone still lifts out | |

### Option C — right-angle extender

Same as B, turned so the cable leaves along the lid's end face.

| Pros | Cons |
|---|---|
| Cable path is clear of the wall | Taller: must fit the slot's 7.0 and the 9.25 pocket |

## Decision

**Not decided, pending a measured adapter.** Leaning to **Option B**. The slot is
then sized from the adapter's body, with 0.5 clearance, rather than from a cable
overmould.

## What size of extender to buy

Derived from the current model (`cad/params.py`, `cad/model.py`), not from a datasheet.
These are the limits of the existing slot, so a different adapter means recutting it.

| | Limit | Where it comes from |
|---|---|---|
| Width | **<= 11.5** (slot is 12.0, 0.25 a side); a cable overmould wider than 12 stays outside the slot | `phone_usbc_cut_w` |
| Height, centred on the port axis | **<= 8.5** (slot floor is now 4.5 below the axis, `phone_usbc_cut_h` 9.0; was 3.5 and 7.0 on 2026-10-17, a plug had to be worked in at an angle) | the screen side is open, so only the floor side limits it |
| Height, deeper still | up to ~9.5 | 2.3 of the lid's rear skin remains under the slot now; below ~1.2 it would break through |
| Length, plug tip to socket face | **~28** | phone edge to the lid's end face is 21.45, plus ~6.65 of plug shell inside the phone |
| Shortest useful | ~25 | the socket may sit 3 mm inside the lid face, so the cable's overmould enters the slot; over 3 mm and only slim overmoulds (< 12 wide) seat |
| Longer than 28 | not acceptable | the socket would stand proud of the lid's end, which snags in a bag and loads the phone's port |

- A **straight** male-to-female extender is the fit. A right-angle one points the cable
  along the lid's end face, into the hinge side or the keyboard's rim.
- A shorter extender (under ~20) is still usable, but then the lid's end face gets a
  counterbore around the slot (about 14 x 9, `phone_usbc_*`) so the cable's overmould
  can reach the socket. That is a CAD change, not a limit.
- Passive, rated 3 A or more. The F1 charges at 18 W, and a thin adapter is where that
  is lost. Data does not matter for F6.
- Dimensions of any real adapter go into `docs/measurements.md` before the slot is
  recut; the numbers above are the envelope, not a part.

## Consequences

- **Buy and measure an adapter first** (new task 0.12), at least two shapes, and
  check each on a USB power meter for charging current against the bare cable.
- `phone_usbc_cut_w` and `phone_usbc_cut_h` become the adapter's, and the slot grows a
  shoulder that bears the side load, which wants a thicker wall around the slot.
- `build.py`'s rod check should become the adapter's actual outline, not a 3.5 mm rod.
- With [ADR-0012](0012-removable-front-bezel.md) the adapter also locates the phone in
  X, so the pocket's end clearance can be smaller.
- Treat the adapter as sacrificial, and fit it dry before any tape or bezel is fixed.
