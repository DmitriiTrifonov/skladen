# ADR-0014: Power switch by hand, through a window with a plug

- **Status:** Proposed — modelled as a separate export (`export/switch-window/`), not printed
- **Date:** 2026-10-19
- **Decides:** replaces the shuttle (Mk3) for builds that want a simpler base; touches nothing else

## Context

The keyboard's slide switch sits in a niche on its rear face. Mk3 reaches it with a
printed shuttle: a fork on the knob, a stem through the tail to a thumb end in the
rear face, a set of finger and stem lengths to choose from because the niche was never
measured. It works, but it is a moving part with three dimensions that were only
settled by printing. The switch is touched rarely: on, then off, a few times a
week at most.

The owner's proposal: no moving part. A window in the base's rear face, closed by a
plug; take the plug out and push the knob with a toothpick or tweezers.

## Decision

Option B below, as a proposal and a separate export; the shuttle base stays.

| Option | + | − |
|---|---|---|
| A. Shuttle (Mk3, as printed) | Works by thumb, no tool | Three unmeasured lengths, a printed set, fork can slip off the 0.75 mm of knob |
| **B. Window and plug** | One cut, one tiny part, nothing to size against the knob; the tail is only cut 7.0 x 4.0 | A tool is needed; the plug can be lost |
| C. No access | Nothing to build | The device cannot be switched off without lifting the keyboard out |

## As modelled

| | |
|---|---|
| Slot through the wall | 9.4 wide (the knob's travel + the knob + 2 mm each side), Z 3.6-8.2: room to open tweezers on the knob |
| Tunnel through the tail | 7.0 x 4.0 to the rear face |
| Plug | an 8 mm peg in the tunnel, a 9 x 6 x 1 flange against the face and a 4 mm nipple to pull it by; printed nipple up |
| Fit | three plugs, 0.05, 0.10 and 0.15 mm per side: print the set and keep what holds |

Checked in `build.py`: one solid, no interference with the lid, a 2 mm toothpick
reaches the knob at both ends of its travel and between, each plug fits the base with
no overlap. **Not checked:** the retention of the plug (friction only), and whether
tweezers can pinch the 0.75 mm of knob that stands proud; the owner's measurements say
0.75, the owner reckons 1.0.

## Consequences

- The base for this variant is a separate file, `skladen2-base-switchwindow`; the
  shuttle sets in `export/switch/` stay for the other.
- The plug's flange and nipple stand 2.5 mm proud of the tail's face; the lid's rear
  cylinder is 9 mm clear of it at every opening angle.
