# RINGSHIP (Torus) — Round 1

## Read (the instant 40px tell)
A spinning donut/halo craft: a thick cyan torus with a **visible see-through
hole** straight through the middle and a small hot-amber bead suspended in the
dead centre — a unique **"O with a dot"** silhouette. The negative-space hole is
unlike any solid saucer/wedge/pod in the set, so even in pure silhouette it can
only be the Ringship. The propulsion IS the ring; there is no hull, dome, or
wings.

## Palette
- Torus body: `#3AA0C9` lit (upper-left) → `#16465E` shaded (lower-right), with a
  deeper `#0E2E3E` inner-shadow band so the tube reads round.
- Travelling spin highlight: `#CFF6FF` near-white crest + a desaturated wake.
- Centre bead: `#FFE25A` core, white-hot `#FFF8D6` pip, `#FFD660` night bloom.
- Keylines: a dark `#081A24` hairline on BOTH the outer rim and the inner-hole
  rim — this is what holds the donut against a bright day sky.

## Spin tell — how the arc maps across the 4 frames
The brief's life-cycle is a bright highlight arc that orbits the torus.
`_phase()` maps `_WING_ANGLES = (50, 20, -10, -40)` to phases 0→3, and each phase
parks the arc centre one quarter-turn around the ring via
`_ARC_CENTER_DEG = (90, 0, -90, 180)`:

| phase | wing angle | arc position | bead pulse |
|------:|-----------:|--------------|-----------|
| 0 | 50 | **12 o'clock** (top) | large |
| 1 | 20 | **3 o'clock** (right) | small |
| 2 | -10 | **6 o'clock** (bottom) | large |
| 3 | -40 | **9 o'clock** (left) | small |

12→3→6→9 reads as a clockwise spin. The arc is a ~78° bright crest riding the
MID line of the tube, plus a lower-value trailing wake one step behind the crest
so the eye reads a single light **travelling** (comet-like), not a strobe. The
centre bead pulses steadily (bigger on even phases) so the craft's heart feels
alive independent of the ring's rotation. Because the tell is a high-value arc
sweeping a mid-value ring, it survives the grayscale / colourblind strip.

## The donut-hole-closing risk at 40px — and how I kept it open
This is the make-or-break risk: below ~35% inner/outer radius the hole closes at
40px and the craft collapses into a plain disc (exactly the failure that sank the
previous round of indistinct domed saucers).

Mitigations baked in:
1. **Generous hole ratio.** `IN_RX/OUT_RX = 12/26 ≈ 0.46`, comfortably above the
   0.35 floor, so the hole survives the downscale with margin.
2. **A TRUE transparent hole, not a dark inner fill.** `_punch_hole()` multiplies
   a zero-alpha inner-ellipse mask into the ring surface, so the sky shows
   *through* the hole in play (visible in both gameplay frames). A solid inner
   fill would have read as a disc with a painted spot.
3. **An inner-rim keyline.** A 1px dark hairline rings the hole itself, hard-edging
   the negative space so it doesn't bleed into a pale day sky.
4. **The bead is composited AFTER the punch**, floating in the open hole rather
   than plugging it — and it's small (r≈5) so the hole stays clearly annular
   around it.

Note for the parcel: Pip's parcel hangs just below centre in play, so the ring is
centred at (32,44) with the hole + bead + arc reading above/around the parcel; in
the gameplay frames the parcel tucks into the lower hole without erasing the "O".

## Files
- `build.py` — `build(wing_angle_deg)` + helpers/palette.
- `render.py` — exact boilerplate; outputs `round_1.png`.
- `round_1.png` — DAY gameplay | NIGHT gameplay | reference (3x / play-size / grayscale).

## Verification
Rendered headless. The donut hole stays **open** at 40px on both skies; the
travelling-arc spin reads clockwise across the 4 frames (confirmed at 4x and at
play-size); the bead bloom carries the legendary glow at night and the dark
keylines hold the ring against the bright day sky.
