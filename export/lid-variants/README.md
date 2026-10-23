# lid-variants/

The whole bezel lid, with the dog cut through the rear wall (as plate 4's lid), in five variants, to print and choose by feel which crush ribs
and button tongues work (ADR-0015, ADR-0016). The same five are plates 6 to 10 of
`../skladen2-2.1-plates.3mf`, laid in their printing pose; the STLs here are in the
lid's own pose, like the other lids. Each is printed with the same inlay,
`skladen2-logo-through-inlay.stl` (filament 4 on the plates, the lid is 3).

| File | Rib height | Tongue | On plate |
|---|---|---|---|
| `skladen2-lid-bezel-rib0.50-tab1.0-through.stl` | 0.50 mm | 1.0 mm | 6 |
| `skladen2-lid-bezel-rib0.60-tab1.0-through.stl` | 0.60 mm | 1.0 mm | 7 |
| `skladen2-lid-bezel-rib0.70-tab1.0-through.stl` | 0.70 mm | 1.0 mm | 8 |
| `skladen2-lid-bezel-rib0.60-tab0.8-through.stl` | 0.60 mm | 0.8 mm | 9 |
| `skladen2-lid-bezel-rib0.60-tab1.2-through.stl` | 0.60 mm | 1.2 mm | 10 |

Rib height is how far a rib stands off the pocket wall; the pocket leaves 0.3 mm per side,
so the squeeze is the height less 0.3 (0.2 / 0.3 / 0.4). Start with 0.60. A tongue is the
thin flexure that presses a key: 0.8 is about 10 N/mm at the tip, 1.0 about 19, 1.2 about
33 (a beam estimate, not a measurement). Use the closed frame
(`../bezel/skladen2-bezel-closed*`) with these lids.

Then set `phone_rib_h` and `button_tab_t` in `cad/params.py` to the winners.
