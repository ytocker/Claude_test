# MESSAGE BOTTLE — Round 2

Round 1 verdict was ITERATE: the tilt row read beautifully, but in the actual
CARRY pose the cork pointed INTO Pip and the bottle collapsed to a round teal
lozenge (read as a gem/orb). Round 2 fixes the carry orientation and the
in-hand proportions so the carried glyph reads as a message-in-a-bottle.

## What changed (per critique)

1. **Carry ORIENTATION — the blocker.** The cork now lives on the LEFT of the
   bottle and the whole sprite is baked with a `LEAN_DEG = 45` tip. The parcel
   anchor sits right at Pip's belly-bottom (bird-centre y≈269, parcel-centre
   y≈281, BIRD_R 14), so the bottle's upper half always tucks under Pip and
   only the lower half shows. Leaning the cork-left bottle DOWN means the cork
   tip + neck hang clear of Pip's silhouette into OPEN SKY below him — the
   broken outline that converts "orb" → "bottle". (Round 1's cork pointed right,
   straight into Pip's body, and never broke the outline.)
2. **Exaggerated horizontal proportion.** Belly half-height dropped to 9 and the
   belly stretched to ~25px long at 2× — a ~17×9 lying-down vessel instead of
   round 1's near-square belly. The long axis now survives the downscale rather
   than rounding off into a lozenge.
3. **Bigger, higher-contrast CORK.** The cork is a fatter warm nub
   (`#CF9A4E`, punchier than round 1's `#C9A368`) with a lit `#F0CE8E` top and
   a dedicated DARK seam ring (`#5A3E1E`) at the cork→neck join so it stays a
   distinct cap and never smears into the neck — it's the iconic tell.
4. **Translucency tell that survives 22px.** Two additions: a bright top-edge
   glass keyline (`#E6FBF4`, 2px specular rim along the belly shoulder) and a
   sky-value sliver (`#C9E8DC` at lower alpha) bled into the lower belly so the
   glass reads see-through rather than fully opaque.
5. **DAY contrast.** The glass wall was deepened from `#5FA88C` to `#3E866E` and
   the outline darkened to `#102A22`, so the glyph holds against the bright
   upper sky band instead of melting into it.

KEPT: tilt-row clarity (the baked 45° lean lands the carry pose on the same
strong lying-down diagonal the row showed), the cream scroll core as the
brightest value (`#F6ECCE`), and the grayscale pass.

## Carry-pose confirmation (day + night, 22px)

On the DAY and NIGHT gameplay crops the bottle now hangs below Pip with the
warm cork + neck poking past his lower-left body outline into open sky, the
cream scroll-belly visible above it, and the elongated glass body reading as a
vessel rather than a round orb. The cork's warm hue + dark seam separate it
from the green glass at true size; the cream scroll carries the read on the
dark night sky. It reads as a message-in-a-bottle in the carry pose on both
day and night, not a gem.

## Residual notes

The parcel anchor (`PARCEL_Y_OFFSET = 12`) is a shared game constant, so Pip's
body always occludes the bottle's upper half — that's true of every parcel
cosmetic. The round-2 framing makes the part that DOES show (cork, neck, scroll-
belly) the unambiguously bottle-shaped part, hanging into sky.
