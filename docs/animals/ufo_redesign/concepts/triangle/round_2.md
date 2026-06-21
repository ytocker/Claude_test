# Concept — THE BLACK TRIANGLE (TR-3B) · round 2

`docs/animals/ufo_redesign/concepts/triangle/round_2.png`
(DAY gameplay | NIGHT gameplay | reference: 4 frames @3x / play-size / grayscale)

Round 1 got `VERDICT: ITERATE`: the wide gradient slab body was good, but the
corner beacons rendered as large DARK bulbs with a brown halo + dark contour,
which fractured the triangle into "three dark knobs / a spider", and the lit
pip was a small fleck lost inside a dark surround. Below is each punch-list note
and what changed.

## What changed (punch list)

1. **Lights ON the wedge, not bulbs replacing the corners.** The beacon glow
   radius dropped hard (`glow_r = 3` clamped, alpha halved). The lit pip + glow
   now fit INSIDE the corner of the slab as a ~2–3px hot dot, and the beacon
   anchors were pulled further inboard (`_corners()`: apex +5, base ±7/-3) so
   the wedge's straight 2px keyline edge passes cleanly behind each pip. The
   triangle outline is the dominant shape; the lights are small accents on it.

2. **Beacon value inverted: bright core, no dark surround.** `_glow_dot` was
   replaced by `_pip()`. The lit pip is a pure-white center on a `#FF5C3A`
   warm-red ring with a thin additive warm glow — the BRIGHT thing. The dark
   contour and the brown bloom are GONE entirely. An unlit corner is now just a
   single recessed dark dot (`PIP_DARK`), no halo, so it never reads as a bulb.
   The lit core was made a hair larger + near-white specifically so it beats the
   pale keyline in grayscale — verified the lit corner is the single brightest
   value in the craft in every frame on the grayscale strip.

3. **Corners stay genuinely hard.** The keyline now carries the ENTIRE wedge
   outline (all six bevel edges), not just the lower edges, at 2px — so the
   straight hard edges win at play-size and the corners are flat-clipped bevels
   that don't halo or round. The lights no longer own the corners; the keyline
   does.

4. **Apex reads as a triangle POINT, not a head/cockpit.** The apex carries only
   a small rim pip (same tiny `_pip` as the base corners), pulled inboard so the
   flat-clipped apex bevel stays the read. No blob — at 40px it resolves as a
   clean point.

5. **Separated from the parcel.** In both gameplay frames the wedge base sits
   visibly above Pip's red parcel; the parcel hangs below the base and the two
   bottom-corner pips ride the rim above it. They do not merge into one brown
   lump (the brown that caused the merge in round 1 is gone with the halo).

6. **Chase re-tested at PLAY-SIZE.** Kept the 4-state chase — at 40px the bright
   pip clearly travels apex → bottom-right → bottom-left → dark across the four
   frames on day, night, AND grayscale (a trailing warm pip one step back sells
   a single light travelling, not a blink). No need to drop to 3 states.

7. **Premium pass.** One crisp `#C6CEDC` specular highlight line along the
   upper-left long edge (one bright machined-metal line, not a wash). Panel
   seams were dropped — they vanished at size and only risked muddying.

## Confirm at 40px

- **Clean black triangle:** yes — a dark hard wedge defined by a continuous
  pale 2px keyline; no dark knobs, no spider, no brown halo. Reads as a triangle
  and nothing else on both skies.
- **Lit corner is the brightest value in every frame:** yes — verified on the
  grayscale strip; the white-cored pip out-values the keyline in frames 1–3, and
  frame 4 is uniformly dark (beacon off).
- **Chase reads at play-size:** yes — apex → bottom-right → bottom-left → dark
  is legible at the true ~40px in-play size on day, night, and grayscale.

## Contract

64×84 SRCALPHA canvas, body mass centred at (BCX,BCY)=(32,44), drawn UPRIGHT
(no baked rotation — velocity tilt applied later by the getter).
`build(wing_angle_deg)` returns the Surface; the 14px collision circle at
(32,44) sits inside the wedge mass. Reuses `_make_prebuilt_skin` from
`game/animal_ufo.py` (house `_add_outline`) plus parrot `_add_outline`/
`_aaellipse` parity. Procedural pygame draw calls only.
