# UFO Store skin (`skin_ufo`) — Round 2

**Sheet:** `docs/animals/ufo/round_2.png`
**Build:** `docs/animals/ufo/ufo_skins.py` → `build_ufo(wing_angle_deg)`,
`get_ufo = _make_prebuilt_skin(build_ufo)`, `BUILDERS = {"skin_ufo": get_ufo}`.

Round 1 VERDICT was **ITERATE**: winner **V3 Matte Stealth (amber)** with
**V1's disc geometry grafted on**. This round converges the five explorations
into ONE production skin and addresses every must-fix note.

## What converged
V3's amber matte "night-ops" palette + V1's wide disc-to-dome ratio, so the
saucer **ellipse** is the dominant mass — not the dome. Cyan and magenta
colorways are preserved as a commented alt block (amber is canonical).

## Must-fix → how it was addressed
1. **Day-sky death — baked keyline (FIXED FIRST).** A 1px pale-amber lip
   (`KEYLINE = (214,196,150)`) is baked along the UPPER rim of the disc and
   across the top of the dome glass via `_keyline_arc`. Tested specifically
   against the brightest day-biome band (`biome.py` DAY `sky_bot ≈
   (170,220,245)`), which is the render's top hero/strip background — the
   silhouette holds without dimming the night "glow out of black".
2. **Disc dominance restored.** Disc widened to V1's `rx,ry = 26,9`; dome
   shrunk + lowered to `12×9` at `DOME_Y = BCY-8` (was a tall `12×13` stacked
   high). The disc now reads as a disc even with dome + beam removed.
3. **Rim-chase contrast for legible motion.** Lit dots carry an additive bloom
   + hot white pip (~30–40% visually larger/brighter than the flat dim pips);
   the lit pair advances one clearly visible notch left→right across the FRONT
   lip per frame. Dim dots are now contoured + visible so the eye tracks the
   pair *travelling against* them — rotation, not twinkle.
4. **Low rim-light count.** 8 dots (the cap), spaced across the full leading
   lip so they don't granulate into a band at 40px.
5. **Beam capped.** Kept the widen/narrow pulse (phase 0/2 widen, 1/3 narrow —
   the clearest "alive" tell, now a bigger ±swing) but ramped the additive
   alpha in from zero over the top ~30% of the cone, so the bloom never washes
   up over the disc's lower lip and erodes the night silhouette.
6. **Dome reworked.** The legible alien face is gone. The dome is now a single
   bright specular glint (high-left) over a dark occupant pupil-shape — reads
   "occupied glass orb" at 40px without resolving to noisy facial detail.
7. **Colorblind / day safety.** Each lit rim dot gets a thin dark contour, so
   the chase holds on BOTH skies and doesn't rely on amber hue alone.

## Contract (unchanged)
64×84 SRCALPHA canvas, saucer mass centred at `(32,44)`, beam below, glow
baked into the 4 frames, no live particles. Verified: `build_ufo()` returns
`(64,84)`; content bbox `(6,28)–(58,78)` (disc mass at the body anchor, beam
trailing below); outlined getter frame `(68,88)`; `BUILDERS == {"skin_ufo"}`.

## Sheet contents
Hero 130px + 40px NEAREST×3 (all 4 chase frames + a dive tilt) on the
**BRIGHTEST DAY** sky AND a **NIGHT** sky.
