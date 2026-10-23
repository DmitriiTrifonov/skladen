# ADR-0016: Flexure tabs for the phone's buttons in the bezel lid

- **Status:** Proposed — modelled, not printed
- **Date:** 2026-10-23
- **Decides:** what replaces the open 45 mm button window in the bezel lid ([ADR-0004](0004-phone-retention.md), [ADR-0012](0012-removable-front-bezel.md))

## Decision

Three tongues in the front wall, one per key (volume down, volume up, power), each
fixed to a post at one end and free at the other, 1.0 thick (`button_tab_t`) and 7.6
long. A finger pushes the tongue's outer face, recessed 2.7 from the lid's front edge;
its inner face stops 0.10 short of the key (`button_tab_pre`). Printed in one piece with
the lid, nothing to buy.

- The tongues are cut free through the rear skin as well, so on the bed they stand from
  the first layer with no bridge, and they bend in the plane of their layers (not across
  them, which is what limits the snap clips, R8).
- Stiffness goes with the cube of the thickness. A rough beam estimate, with PETG at 2 GPa and a
  10 mm tall tongue: 0.8 -> ~10 N/mm, 1.0 -> ~19, 1.2 -> ~33 at the tip. The coupons
  carry **0.8 / 1.0 / 1.2** (`export/coupon-phone/`, `...-ribs-tab0.8` / `-tab1.2`
  and the 1.0 default) so the push is picked by feel, not by this estimate.
- The frame can stay as it is: it still has its cut-out over the window span and its two legs
  at the span's ends, and the end gaps (X -52.5..-51.1 and -8.9..-7.5) are kept open for them.
  `bezel_frame(closed=True)` (`export/bezel/skladen2-bezel-closed*`) is the same plate with
  no cut-out and no legs, roofing the tongues; the tongues are still pressed from the
  front edge, under it (the opening there is 10 mm tall below the plate's 0.8). Checked:
  one solid, no contact with the lid.
- `button_tabs = False` in `params.py` brings the old open window back.

## Assumed, to measure

- The rocker is two keys split at its middle (X -39.15); the F1's actual split and the
  keys' height (3.0 assumed, in the check only) are not in `measurements.md`.
- **First print (2026-10-23): the volume-up tongue pressed both volume keys.** The split
  at the rocker's middle was a guess, and a tongue touching along its length overlapped
  the neighbour. The two volume tongues now touch through a 4 x 4 nub each, near the
  outer ends and 12.5 apart (X -45.0 and -32.5, `button_tab_beams`), the rest of the
  tongue standing 0.3 back. The split can then lie anywhere from X -43 to -34.5; `build.py`
  checks keys stretched to those limits. The power tongue, known to work, is unchanged.
  Still wanted: the two keys' measured spans.
- A tongue without a nub touches along its length, so pressing near its fixed end is stiffer.
- The key's own travel and force (a few N, a few tenths of a millimetre) are not
  measured; if a tongue is too soft the key is pressed by the lid's weight, too stiff
  and it does nothing.
