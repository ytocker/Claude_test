# KIDDIE CAR-CART — Round 2

Round 1 got `VERDICT: ITERATE`: the candy-red car nose read beautifully, but
the rear "basket" rendered as an oversized gray WEDGE/slab that out-weighed the
red hero (worse at night) and Pip's parcel fused into the body flank. Round 2
keeps the win — bubble cabin + candy-red capsule hull + fat keyline-rimmed
wheels — and fixes the rear mass, the value hierarchy, the parcel, and the
bounce.

## What changed (against the punch list)

1. **Rear basket: shrunk + reads as a BASKET, not a slab.** Cut ~35% of its
   visual area — box height 20px→13px, top width 18→11, bottom 14→9 — and
   squared it UPRIGHT instead of the back-tipped wedge. The wire-mesh now reads
   as a real mesh: a **3-vertical + 2-horizontal cross-hatch** plus a **bright
   top rail keyline**. It is clearly the smaller, secondary mass.

2. **RED leads on BOTH skies.** Re-tuned the steel to a muted **warm-grey**
   (`#84868E`) nudged toward the red family and darkened (shade `#565A64`) so it
   RECEDES; combined with the ~35% size cut the candy-red cabin+hull is now the
   unambiguous focal mass at 40px day and night. Body red nudged a touch hotter
   (`#E63A3A`). The only bright bit left on the basket is its top rail keyline,
   which holds the rim without out-weighing the hull.

3. **Parcel collision solved.** The car body is lifted 2px (`body_cy` from
   `BCY+4` to `BCY+2`) and the lower edge is now a **clean unbroken candy-red
   shelf** running the full hull width (replacing the old dark lower shade). The
   car/basket dark seam is pulled HIGH on the hull so it no longer cuts the
   shelf. Pip's parcel (composited by the game at +12px below centre) now reads
   as distinct cargo BELOW a solid red car, not fused into the flank.

4. **Bounce legible at 40px.** Pushed width squash/stretch to **+4px / −3px**
   (was +2 / −1) and real vertical body-travel to **+4px drop / −3px lift**
   against the FIXED ground line — so the springs read as a clear 4-beat
   compress→rebound. The **handle nub and basket are now FIXED** (no swing), so
   that motion can't masquerade as wobble; only the car body deforms.

5. **Night tightened.** Cabin glint brightened (`#FAFEFF`) and the white
   wheel-rim keyline pushed to `#F8FAFC`; the basket top rail keyline holds the
   lower silhouette out of the dark hull. Headlight halo unchanged (restrained,
   blinks only on the squash beat).

6. **Front 60% stays unmistakably a toy race car** — bubble cabin, red roof
   cap, chrome bumper keyline, hood scoop, fat hubcap wheels — and the rear no
   longer dominates.

## 40px verdict

`round_2.png` rendered via the shared helper on DAY and NIGHT gameplay frames:

- **RED leads on both skies** — the warm-dark, smaller basket recedes; the
  candy-red cabin+hull is read-first at 40px day and night.
- **Rear reads as a basket, not a slab** — small upright box with visible
  cross-hatch mesh + bright top rail; the grayscale strip confirms it stays
  distinct from the car rather than blobbing into the tail.
- **Parcel separates below** — the clean lower-centre red shelf gives Pip's
  composited parcel a solid car underside to hang beneath.
- **Bounce reads at 40px** — the 4-frame play-size strips show clear
  width + vertical deformation against the fixed wheels/ground gap; basket and
  handle hold still.
