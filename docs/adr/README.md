# Architecture decision records

One file per structural decision, written before the geometry is committed to
CAD. See [ADR-0001](0001-record-architecture-decisions.md) for why.

| # | Decision | Status | Blocked on |
|---|---|---|---|
| [0001](0001-record-architecture-decisions.md) | Record design decisions as ADRs | Accepted | — |
| [0002](0002-keyboard-integration-depth.md) | How deeply to integrate the keyboard | **Accepted** — stays sealed, stripping deferred to Mk4 | — |
| [0003](0003-lid-balance-strategy.md) | Keeping the device from tipping backwards | **Accepted** — 15 mm rear setback + empty ballast pocket |
| [0004](0004-phone-retention.md) | How the phone is held in the lid | **Accepted** — closed pocket with a rear wall | — |
| [0005](0005-hinge-mechanism.md) | Hinge mechanism | Proposed | Coupon 2.2 — measured torque of a printed bolted hinge |
| [0006](0006-rear-edge-io-vs-hinge.md) | Keyboard I/O on the hinge edge | **Rejected** — the premise was a misread photograph | — |
| [0007](0007-cad-toolchain.md) | CAD toolchain | **Accepted** — build123d, model is Python in `cad/` |
| [0008](0008-base-floor.md) | Base floor | **Accepted** — full 1.2 mm floor kept; Option E open | Task 0.4 (Option E only) |
| [0009](0009-closure-retention.md) | Keeping the device shut when closed | Proposed | Coupon 2.2 — does hinge torque survive 100 cycles |
| [0010](0010-hinge-station-count.md) | How many hinge stations, and how a bolt reaches its pocket | Proposed — two stations, heads outboard | First article — does the lid sag at mid-span |

## Dependency order

```
0002 (keyboard sealed, ACCEPTED)
   |
   +--> only two 1.2 mm skins left as thickness levers, both now spent:
   |        0008 (base floor, ACCEPTED: kept)
   |        0004 (lid rear wall, ACCEPTED: kept)   --> 22.24 mm
   |            +--> tape behind the phone (0004, 2026-09-29) --> 23.24 mm
   |            |
   |            +--> 0008 Option E (0.8 ribbed floor) is the last 0.4 mm
   |
   +--> 0006 (rear I/O stays a live problem)
            |
   0005 (hinge) <--> 0003 (setback) <--> 0006 (rear I/O)
        all three resolve into one rear-edge cross-section
            |
            +--> 0009 (stays shut) rides on 0005's measured torque

0007 (toolchain) gates everything but depends on nothing
```

## The shape of the design as it stands

0002 fixed the keyboard as an untouchable 9.52 mm block, leaving two 1.2 mm skins
as the only thickness levers. 0008 spent one on an enclosed base; 0004 spent the
other on a protected phone back, the fingerprint reader it covers being unused.

The result is **22.24 mm** — a 30% reduction over Mk2 with both components fully
enclosed, rather than the 38% that was available with both exposed. That was the
trade, made twice and deliberately.

**It left 0.26 mm of margin against N1's hard limit of 22.5, which was not a
margin.** The limit has since been restated to 24.5, and 1.0 of it went to tape
behind the phone (0004), putting the device at **23.24 mm**. Two things follow: 0008 Option E (a 0.8 ribbed floor, stiffer than the
flat 1.2 it replaces) is now the project's only remaining reduction and should be
resolved early; and the hard limit itself needs restating, since 22.5 was derived
from an early estimate of this very scenario.

On balance, the two decisions nearly cancelled: 0008 added 26 g low, 0004 added
25 g high, and the device tips at 127 deg. A **15 mm** rear setback eliminates
tipping at any angle across the whole plausible mass bracket — 11 mm covered only
the expected case — and 0006 uses that tail as a shelf for the keyboard's
rear-edge I/O.

So the three open structural ADRs remain one problem: **the rear-edge
cross-section**, where the hinge, the setback and the keyboard's switch, LEDs and
USB-C all have to share the same 15 mm of depth.

0005 has since made that section easier in two ways. Its printed knuckles on
bolted stations have **no lead time**, so they no longer block the drawing; and
because the stations occupy points rather than the whole rear line, the gaps
between them are free for port tunnels. What is left blocking the cross-section
is a single measurement, task 0.1.

0009 turned out to need no hardware of its own. Holding the lid shut while
inverted takes the same 0.091 N*m as holding it at 90 deg — the moment arm is the
same in both cases — so the hinge torque F3 already demands satisfies F8 with
margin. Magnets stay recorded as insurance, with a note to check the phone's
magnetometer first.

One more consequence surfaced along the way and is written up in
[clamshell-geometry.md](../analysis/clamshell-geometry.md): with an inboard axis,
a lid the same depth as the base **does not open at all** — its rear overhang
drives straight into the setback tail. The lid is therefore 197 x 90 and the base
197 x 105, with the tail exposed even when shut, exactly as a laptop's hinge
region is. Full 0-180 deg remains available.

0010 came out of a question asked while looking at an assembly drawing: would the
bolt actually go in? It would not. The lid's rounded rear is a solid cylinder
coaxial with the hinge, so it blocks the bolt's path equally at every opening
angle, and the centre station had no path at all. Neither the interference check
nor the 0-180 deg sweep could see it — an unassemblable joint overlaps nothing.
The station count dropped to two and `build.py` gained a corridor check, next to
the connectivity check added the same day for the same class of blindness.
