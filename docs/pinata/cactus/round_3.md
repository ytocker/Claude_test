# CACTUS PINATA — round 3

Verdict to clear from round 2: **ITERATE**. The grayscale saguaro read was won
in round 2 (carved arm notches) — KEPT untouched. Round 3 fixes the four notes,
judged on the **DAY/NIGHT gameplay frames at play-size** (where the game
composites Pip's fixed brown parcel), not the isolated hero.

## What changed

### 1. Parcel fusion fixed IN-CONTEXT (the blocker)
Pip's parcel is fixed by the game (~21px, centred ~12px below bird centre →
skin-space ≈ (32, 56), top edge ≈ y45, flanks at x≈21 / x≈43). I can't move it,
so the **cactus was adapted around it**:

- The green trunk mass is **pulled UP** into a rounded **shoulder** that
  terminates at `base_y = PARCEL_TOP - 1` (≈ y44), so a clear cool-green band
  shows **ABOVE** the parcel's top edge in the composite. The trunk no longer
  trails down behind the gift.
- The two saguaro **arm risers now drop DOWN the parcel flanks** (`foot_y =
  PARCEL_TOP + 7`), with their outer walls sitting just outside the parcel span,
  so a column of green **brackets the gift left and right**.
- `ARM_SPAN` tightened 15→13 and `NOTCH` 4→3 so the risers hug the trunk and
  read as upturned **arms with an elbow**, not two free-floating posts, while
  still flanking the parcel.

Net read in both gameplay frames: **green over the gift + green either side of
it** → "a cactus the gift sits in front of/below", not "hat + arms + brown
torso". Confirmed on the zoomed DAY and NIGHT composites — the brown parcel is
bracketed by green on three sides and is no longer the centre of mass.

### 2. Fringe flutter pushed so it reads at 40px
- Per-band horizontal amplitude **1.7 → 2.8 px (~+65%)**.
- Per-band spatial phase step **0.9 → 1.45 rad/band**, so adjacent bands lean
  opposite ways and a crest visibly travels DOWN the trunk.
- The small hat tilt is kept (`_HAT_TILT` unchanged).

Frame 1 vs frame 3 (sampled offsets, px):

| band | frame 1 | frame 3 |
|------|---------|---------|
| 0    | +2.80   | −2.80   |
| 1    | +0.34   | −0.34   |
| 2    | −2.72   | +2.72   |
| 3    | −0.99   | +0.99   |

Every band leans the **opposite way** frame 1 vs frame 3, and the strongest
crest sits at a **different height** (band 0 in frame 1, band 2 in frame 3) — a
visible wave down the trunk, not a whole-body micro-tip.

### 3. Mid-band studs simplified to crepe blocks
The tiny gray belt studs (drifting to screw-thread noise at 40px) are gone.
`_crepe_blocks()` now stamps **2 fat hi/lo value blocks** per band — a clear
paper-fold rhythm so each band reads as a crepe-paper ring.

### 4. Night legibility
- Trunk low-value green lifted ~10% (`GREEN_LO` (38,112,50) → (44,126,58);
  `GREEN_EDGE` lifted too).
- A faint cool rim (`GREEN_RIM` #78D696) is baked on **both** trunk edges and
  down each arm riser's outer wall.

Confirmed on the NIGHT gameplay frame: the silhouette holds against the
deep-purple sky and no longer merges.

## Kept from round 2 (per brief)
Carved trunk/arm negative space (the saguaro read), the narrower brim, the
cool-green vs warm-brown hue logic, the green/straw palette + pink flower dots.
No parcel is drawn by this skin — the game composites Pip's own.

## Artifact
`docs/pinata/cactus/round_3.png` — DAY gameplay | NIGHT gameplay |
reference column (3x / play-size day+night / grayscale). The two gameplay frames
are the verdict; both read at play-size with the parcel composited and bracketed
by green.

Rendered with:
```sh
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python docs/pinata/cactus/render.py
```
