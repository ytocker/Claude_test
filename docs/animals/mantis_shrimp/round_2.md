# MANTIS SHRIMP — Round 2 (`skin_mantis_shrimp`)

**Verdict to address:** ITERATE, winner = **v3 DUOTONE BRUISER**. This round
converges the five round-1 explorations into ONE ship candidate and clears the
full punch list. The module now exposes the single primary production build.

Sheet: `docs/animals/mantis_shrimp/round_2.png` — the design on a **bright-day**
card (flat duotone) and a **night** card (glow build), each with hero 130px
(cocked/level + punch) and the 40px → NEAREST x3 truth read (cock / punch+dive).

## Contract / API (liftable into `game/animal_skins.py`)
- `build_mantis_shrimp(wing_angle_deg)` — single primary production build.
- `get_mantis_shrimp = _make_prebuilt_skin(build_mantis_shrimp)`.
- `BUILDERS = {"skin_mantis_shrimp": get_mantis_shrimp}`.
- Plus `build_mantis_shrimp_night` / `get_mantis_shrimp_night` — same
  silhouette, glow on eye-jewels + club-tips only, for the night biome and for
  review parity. Same 64×84 canvas, body (32,44), 4 poses, procedural-only,
  WHY-only comments.

## What changed, per the punch list
1. **Clubs separated in EVERY pose (ship-blocker).** Rewrote `_club_arm` with
   a `lead`/rear split. The lead fist cocks **down + outward** so it never
   occludes the snout or merges with the rear fist; the rear fist is parked
   low + back for the double-fist read. Every fist carries a dark heel rim so
   the two keep a 1px dark separation even when they overlap in depth — and a
   sky-gap between them otherwise.
2. **Unmistakable punch.** Exaggerated cock-back vs punch-forward: the lead
   elbow drives up and the lead club rises ~18px to clearly **cross past the
   snout line** on the up-pose, with the whole body **recoiling** (shifts back
   + down with the strike) so the haymaker has weight.
3. **Controlled technicolor that keeps the duotone read.** The teal body +
   **two bold orange load-bearing stripes** stay the structure. Added a single
   **thin banded mid-stripe** (alternating gold/cyan ticks) as the third
   accent, plus **iridescent eye-jewels** that blue-shift toward the rim.
   Colour = structure, not noise.
4. **Periscope eye-stalks.** Thickened to a **3px core + dark outline** (5px
   rim line under a 3px stalk), **jewel tip ≈ 2× stalk width** (r=6 on a 3px
   stalk), each with **one bright specular pixel** and the equatorial ommatidia
   midband, so the twins read on both skies.
5. **1px dark body contour for day-sky** via the house `_add_outline` applied
   to every frame in `_make_prebuilt_skin`.
6. **Night glow on eye-jewels + club-tips ONLY** (not the body). The glow build
   adds a tight additive halo seeded smaller than the jewel so the close-set
   twins stay two distinct lamps, plus a halo on the lead club-tip.

## Read at 40px (truth test)
Cock pose: clear twin jewel periscopes, striped teal shield, two distinct
orange fists low-front/low-back. Punch+dive: lead orange club snaps up across
the snout — the strike is legible in the magnified gameplay pixels on both day
and night.
