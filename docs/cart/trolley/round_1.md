# CLASSIC TROLLEY — round 1

Secret flyer skin concept: the player's bird becomes a flying supermarket
trolley. One of 5 independent cart concepts. The verdict frame is the staged
gameplay frame at true scale (`round_1.png`, DAY | NIGHT | reference column).

## The read (what makes it a shopping trolley at 40px)

- **Flared-open trapezoid basket** — wide at the top, narrow at the bottom.
  This is the dominant filled mass and the load-bearing silhouette.
- **Two wheels** under the narrow base, on short steel struts.
- **A single curved push-handle** hooking UP off the back-right corner.
- A warm-orange **cargo block** sits inside the basket so it reads as a cart
  carrying goods (and gives Pip's parcel a home below centre).

The flared mouth + rear handle-hook is the universal cart read; both are
drawn at full weight so neither drops out at small scale.

## Palette (chrome steel + near-black wheels + warm cargo)

| Role | Colour | Hex |
|------|--------|-----|
| Steel highlight band | `(232,237,242)` | `#E8EDF2` |
| Steel mid band | `(159,176,190)` | `#9FB0BE` |
| Steel shadow band | `(91,107,120)` | `#5B6B78` |
| Steel hard edge/contour | `(60,74,86)` | — |
| Wheel tyre (near-black) | `(43,49,56)` | `#2B3138` |
| Wheel keyline | `(242,245,248)` | `#F2F5F8` |
| Cargo accent | `(240,162,58)` | `#F0A23A` |

The body uses **vertical value banding** (hi→mid→lo top to bottom, clamped to
the trapezoid silhouette) to sell polished metal.

- **DAY** (`sky_bot ≈ (170,220,245)`): the near-black wheels + the dark steel
  edge contour carry the silhouette against a bright sky; the wheel keyline
  rings the tyres so they don't muddy into the basket.
- **NIGHT** (`phase 0.52`): the light steel highlight band IS the silhouette
  against the dark sky, and the bright `#F2F5F8` wheel keyline makes the two
  wheels pop out of black.

## Wheel-spin frame map (the 4-frame tell — NO wings, NO particles)

`_WING_ANGLES = (50, 20, -10, -40)` → `_phase()` → spoke-cross orientation + bob:

| Frame | wing° | phase | spoke cross | bob |
|-------|-------|-------|-------------|-----|
| 0 | 50 | 0 | `+` upright | 0 |
| 1 | 20 | 1 | `×` diagonal | −1px (up) |
| 2 | −10 | 2 | `+` upright | 0 |
| 3 | −40 | 3 | `×` diagonal | +1px (down) |

Each wheel is a near-black tyre with a **bright hub plate**; the spoke cross
is cut into that plate as a **value flip** (dark spokes on a light disc). The
cross alternates `+ → × → + → ×` while the whole cart bobs 1px, so it reads as
rolling through the air. Because the tell is a value flip inside a solid disc
(not a hue change), it **survives grayscale** — confirmed in the reference
column's grayscale strip.

## 40px wire-risk + how it was solved

The prior-failure trap: a true wire trolley is thin diagonal grid lines that
vanish at 40px and turn to mush.

Solution — **lead with mass, only suggest the wire:**
1. The basket is a **bold filled chrome trapezoid** (vertical value band +
   hard contour), not an outline. That mass alone reads as a basket.
2. The **flared top rim** is a fat 3px bright bar — the single most cart-
   defining line — so it never drops.
3. The wire grid is **only 3 fat verticals + one fat mid rail** (no thin
   diagonals). They are heavy enough to suggest a basket grid, but the cart
   read does not depend on them — if they blur away at true 40px the filled
   mass + flared mouth + two wheels + handle still say "shopping trolley."
4. The **two wheels + curved handle** are drawn bold and are the secondary
   load-bearing read, confirmed legible in the DAY/NIGHT play-size strips.

## Contract

64×84 SRCALPHA canvas; basket mass centred at `(BCX,BCY)=(32,44)`
(`COMPOSITE_W=64, COMPOSITE_H=84, DY=12`). 14px collision circle at (32,44)
sits inside the trapezoid mass; the cargo block + Pip's parcel hang just below
centre. `build(wing_angle_deg) -> Surface`, drawn UPRIGHT (velocity tilt
applied later by the getter cache). Procedural pygame only; reuses
`game/parrot.py` (`_aaellipse`, `_WING_ANGLES`) and the
`game/animal_ufo._make_prebuilt_skin` getter pattern via the gameplay lib.
