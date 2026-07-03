# THUNDERBIRD — Round 2 (converged: STORM-RAPTOR)

VERDICT to address: **ITERATE**, winner = v1 STORM-RAPTOR, graft v4's signature.

Round 1 explored 5 takes; round 2 collapses to ONE production design:
`build_thunderbird` = perfected v1 raptor carrying v4's cultural under-wing
lightning. The 4 other variants are retired from the file.

Sheet: `docs/animals/thunderbird/round_2.png` — the single design on BOTH a
**bright-day** sky (mandatory legendary proof) and a **night** sky, each at hero
130px (clap), 40px smooth, and 40px NEAREST x3 (clap / up-dive).

## Punch list — what changed

1. **Asymmetric under-wing fork (the #1 change).** Replaced v1's symmetric
   both-wingtip forks with a SINGLE fork crackling from beneath the near wing's
   trailing edge, grafted from v4. It's a zig-zag where each segment drifts
   further LEFT than it drops, so it angles diagonally OUTWARD into the sky and
   can never read as legs/talons. One short crackle branch peels off the same
   side for legendary spectacle. This is the distinctiveness vs dragon/phoenix.

2. **Thunderclap locked to lightning SCALE, not body mass.** Body ellipses,
   tail, head and plumes are drawn at FIXED size every frame. Only the aura and
   the fork vary: full branching fork on the clap (frame 3, down-stroke), a
   short single zig-zag mid-stroke, a faint stub on the up-pose (frame 0). No
   silhouette-jump flicker (the v5 problem is gone).
   - Note: `_WING_ANGLES = (50,20,-10,-40)` is *up → down*, so the clap is
     **frame 3**. Round 1's harness mislabeled frame 0 as the clap; round 2's
     harness renders the correct frame for each pose.

3. **Pushed the eye.** One storm-blue eye built as the brightest single point on
   the sprite: dark socket → blue halo → white-hot core → a 1px pure-white
   glint. It is the guaranteed 40px tell on both skies.

4. **Fixed the up-pose tail/fork collision.** The fork origin moved forward to
   mid-wing (x≈18) and the up-pose only draws a short forward stub — verified
   NEAREST at dive tilt: nothing trailing the body reads as a tail spike.

5. **Sharpened the twin plumes.** New `PLUME_HH` highlight (+~15% value) plus a
   hard 1px tip stroke per plume so the back-swept crest survives bright-day.

6. **Glow restraint held at v1 level.** Only the single body aura halo; no extra
   halos, no wing-veins. The yellow fork + blazing eye are the spectacle.

7. **Colorblind read.** The fork's yellow mid pass (`BOLT` / `BOLT_HOT`) carries
   the lightning on the dark body even if the storm-blue desaturates.

## Contract (unchanged)
64×84 canvas, body (32,44), head (44,34), 4 poses, procedural-only, WHY-only
comments. Exposes `build_thunderbird(wing_angle_deg)`,
`get_thunderbird = _make_prebuilt_skin(build_thunderbird)`, and
`BUILDERS = {"skin_thunderbird": get_thunderbird}` — liftable into
`game/animal_skins.py`. No live particles; all glow/lightning baked into the
4 frames.
