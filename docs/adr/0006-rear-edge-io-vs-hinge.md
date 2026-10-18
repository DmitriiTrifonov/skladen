# ADR-0006: Keyboard I/O on the hinge edge

> **Skladen 2:** written for Mk3 and the Pixel 3a XL. Its numbers are inherited, not re-derived; what the Pocophone F1 changes is in [ADR-0011](0011-phone-swap-pocophone-f1.md).

- **Status:** Rejected — the premise was a misreading
- **Date:** 2026-09-20
- **Decides:** nothing. F5 turned out not to be contested.

> **This ADR addressed a conflict that does not exist.** The keyboard's USB-C is
> on its **right side face**, not on the rear edge. It is kept rather than
> deleted because the reasoning it drove — discrete hinge stations, the I/O
> shelf idea, the height analysis — shaped ADR-0005 and is worth being able to
> re-read. See *What actually happened* at the end.

## Context

The keyboard carries **all** of its I/O on one long edge: an OFF/ON slide switch,
four status LEDs (charge, caps lock, two wireless) and the USB-C charging port.
See `reference/photos/keyboard-rear-edge-switch-leds.jpg` and
`reference/photos/keyboard-rear-edge-usb-c.jpg`.

Two things then dissolved this, one after the other.

**First**, the owner's decision: the power switch stays permanently ON and the
LEDs are not needed. F5 was relaxed, leaving one feature — the USB-C port.

**Second**, and fatally: **the USB-C is not on the rear edge at all.** It is on
the keyboard's right side face. The premise above is simply wrong — the two
photographs show two different edges, and the second was read as the first seen
at an angle.

That edge is also the **thick** edge of the 2.64 deg wedge (9.52 vs 5.54), and
the wedge rises front-to-rear, so the I/O edge is the rear edge — which is
exactly where the hinge goes.

This looked like a genuine conflict: the hinge wants the full width of the rear
edge for stiffness, the I/O wants the same width to stay reachable, and F5
requires the I/O to work without disassembly.

[ADR-0005](0005-hinge-mechanism.md) has since made it much less sharp. The two
can occupy the same width at **different heights**: the keyboard's rear face is
9.52 mm tall, while the hinge axis sits naturally on the parting plane at
~12.5 mm — above it. A full-width barrel runs over the keyboard, and the port
tunnels run underneath it through the 15 mm tail. What remains is a
cross-section problem rather than a contest for the same space.

## What actually happened

The keyboard's rear edge carries the switch and the LEDs, neither of which needs
access. The USB-C is on the **right side face**, 8 mm back from the rear edge,
its opening 3.94 mm tall centred at Z 6.17.

So the rear edge carries nothing that needs a hole, and the hinge has all
193 mm of it. The consequences:

| | Under the misreading | Actually |
|---|---|---|
| Rear-edge features needing access | 1 (thought: 6) | **0** |
| Hinge station placement | right one pushed inboard to +70 | **symmetric, ±88** |
| Span between outermost stations | 159.3 mm, 10.8% short | **176.0 mm, 1.5% short** |
| USB-C tunnel | a funnel through 15 mm of tail | a hole through 1.9 mm of side wall |
| Risk R1 | live, quantified | **gone** |

The 15 mm rear setback stands unchanged, but it is now earned entirely by
[ADR-0003](0003-lid-balance-strategy.md) — the worst mass case needs 14.6 mm on
its own. This ADR was never really paying for any of it.

## What survives

Not nothing. Two decisions made under the wrong premise turned out to be right
for other reasons and are kept:

- **Discrete hinge stations** rather than a continuous full-width barrel
  ([ADR-0005](0005-hinge-mechanism.md)). Chosen here to leave gaps for port
  tunnels; kept because a 193 mm continuous knuckle array demands a straightness
  no PETG part that size will hold.
- **The height analysis of the rear edge**, which fed directly into discovering
  that the hinge axis cannot sit on the parting plane at all.

## Lesson for the record

The measurement that would have caught this cost nothing and was never asked
for: *which face is the port on*. Tasks 0.1 and 0.1b both asked how far along an
edge and how high up, and neither asked which edge. A datum is not a datum until
it names the surface.
