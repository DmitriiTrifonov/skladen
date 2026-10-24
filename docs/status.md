# Where we stopped — 2026-10-23

The phone-fit round on the bezel lid. Nothing here is confirmed on a print yet except the first
coupon's result.

## What was done

- **Coupon `-ribs-h0.60` confirmed (2026-10-23):** ribs 0.60 and tongue 1.0 with the moved tongues and 2.5 nubs work. `phone_rib_h` is now 0.60 by default; plate 4 and the rest are built with it. Next: print one whole lid (plate 4 or 7) with the closed frame.

- **Crush ribs on the pocket walls** ([ADR-0015](adr/0015-phone-crush-ribs.md)). The phone
  floated 0.3 per side. First coupon, ribs 0.40 (0.1 squeeze per side): **the phone was still
  loose.** Variants 0.50 / 0.60 / 0.70 are modelled (`phone_rib_h`, default still 0.40).
- **Button tongues** ([ADR-0016](adr/0016-button-tabs.md)) replace the open button window in
  the bezel lid. First coupon (tongue 1.0, no nubs): **the volume tongue nearest the power key
  pressed both volume keys**, because the split between the two keys was a guess. Fixed in the
  model with 4 x 4 nubs at X -45.0 and -32.5. Second print: still pressed both, and the volume tongues stood 1.5-2 mm toward the top end. Now moved +1.75 with 2.5-wide nubs at the outer ends (ADR-0016); **not printed**. Power works.
- **Closed frame** (`export/bezel/skladen2-bezel-closed*`): the plate with no cut-out over the
  buttons; for use with the tongues.
- **USB-C extender parked** ([ADR-0013](adr/0013-usbc-extender.md)): build step off, files in
  `export/adapter/` untouched.
- READMEs in every `export/` folder; `skladen2-2.1-plates.3mf` now has ten named plates.

## On the printer / to print next

- **Printing now:** `export/coupon-phone/skladen2-coupon-phone-lid-ribs-h0.60.3mf` (ribs 0.60,
  tongue 1.0, with nubs).
- **Not printed yet:** `export/coupon-phone/skladen2-coupon-phone-plates.3mf`, two plates of two
  coupons: 1 = ribs 0.50 + 0.70; 2 = tongue 0.8 + 1.2 (ribs 0.60).
- **Whole lids** with the dog cut through, one variant per plate: plates 6-10 of
  `export/skladen2-2.1-plates.3mf`. Wait for the coupons; print one lid once the parameters are
  chosen, with the closed frame (plate 5).

## What to check on the coupons

- The phone goes in with a little force and does not move. Too tight: lower `phone_rib_h`; still
  loose: raise it.
- Each volume key is pressed by its own tongue; the power key still works.
- The tongues are neither too soft (the lid's weight presses a key) nor too stiff (the key does
  not move). 0.8 / 1.0 / 1.2 are about 10 / 19 / 33 N/mm at the tip by a beam estimate.

## Open questions

- Which coupon was printed first: the file name is the same as the rebuilt one; the committed
  one (before the nubs) is the one without nubs.
- The real spans of the two volume keys and their height (assumed split X -39.15, height 3.0).
  The nubs work for a split anywhere from -43 to -34.5.
- Whether the phone's rear edge is rounded; if so, the ribs touch only near the glass. A
  straightedge on the back, and a caliper at the edge, would say.
- A 0.2 mm play over the glass remains, and the ribs do not touch it. If it clicks in Z, a
  0.3 mm self-adhesive felt strip under the plate's overlap (not 0.5 or 1 mm: it cannot
  compress into 0.2).

## Next

1. Read the three coupon results; set `phone_rib_h` and `button_tab_t` in `cad/params.py`.
2. Rebuild, print one whole lid with the closed frame; tick the checks in ADR-0015 and 0016.
3. The first frame's clips still need their reprint (ADR-0012), and the earlier items in
   [plan.md](plan.md) stand.
