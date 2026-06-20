# KITSUNE (`skin_kitsune`, LEGENDARY) — Round 2

Art-director returned **VERDICT: ITERATE**, winner = **v3 CURLED ORACLE**, with
the directive to graft v5's gold→violet palette + v1's brow blaze and make it
the crown jewel. Round 2 converges to **ONE production build** — `build_kitsune`
— and addresses every punch-list item.

Sheet: `round_2.png` — the single design at **hero 130px** (with the store-card
gold aura ring) + **40px level/dive (smooth)** + **40px NEAREST x3** (the honest
gameplay-pixel read), shown on **BOTH a night AND a bright-day backdrop**.

Contract unchanged: 64×84, fox body at `(32,44)` for the fixed 14px collision
circle, head near `(44,34)`, nine-tail fan spreads behind, 4 poses, procedural-
only, WHY-only comments. The spectacle (foxfire + aura) is baked into the
frames — no live particles.

Production API (liftable into `game/animal_skins.py`):
`build_kitsune(wing_angle_deg)` + `get_kitsune = _make_prebuilt_skin(build_kitsune)`
+ `BUILDERS = {"skin_kitsune": get_kitsune}`. `build_kitsune_aura()` returns the
hero-only aura ring on its own surface (composited behind the outlined fox for
the store card; never in the 40px frames).

---

## What changed, per the punch list

1. **Gold→violet banded fan.** The vertical nine-tail fan now runs warm GOLD at
   the base/inner plumes, cooling to a bright VIOLET crown at the tips. `_band()`
   resolves to **three discrete value STEPS** (gold / mid / violet), not a smooth
   ramp — banding is what survives 40px and reads "most expensive." The violet
   band was widened (outer ~45% of the fan) and the crown tips pushed brighter
   (`TIP_VIOLET` + a near-white `TIP_VIOLET_H` hotspot) so the violet edge holds
   at gameplay scale. Plumes are drawn outer→inner so gold sits ON TOP, locking
   the gold-base / violet-crown read.

2. **Signature moon-disc blaze.** v1's brow placement, rendered as a small pure-
   WHITE moon-disc with a tight violet glow ring and one crisp center dot. It
   pops on BOTH the night and bright-day panels; head + blaze alone read
   "kitsune."

3. **Dive-pose mass solved.** The fan gathers **back-and-up** on the up-pose
   (`centre` rotates back-left as it lifts; `fan` arc narrows hard), so the
   collision-centred body stays the dominant mass on the dive frame. The
   vertical-spread delta between frame 0 (down, wide low fan) and frame 3 (up,
   gathered) is large and obvious — that's the visible "flap" (see the
   "flap: down / up" pair on the sheet).

4. **Open eyes + catchlight.** Replaced v3's serene closed arcs (which read dead
   at 40px) with open oracle eyes plus a bright catchlight pixel — the charm half
   of prestige+cute.

5. **Internal fan structure preserved.** Each plume gets a baked 1px dark
   separator (drawn as a `RIM` outline under the fill) so the eye counts distinct
   tails — the "nine" tell — and a lighter spine highlight. Tip flames are tight
   (1–2px violet glow on crown tips only), not a soft halo that bleeds tails
   together.

6. **Day-sky rim.** A baked dark/violet `RIM` is laid under the body, head, and
   every plume so the silhouette survives the bright-day sky (verified on the
   day panel).

7. **Distinctiveness vs phoenix.** Gold is confined to the BASE/inner third;
   violet owns the CROWN. Warm gold never dominates the whole fan — the cool
   violet edge is the kitsune's own signature.

8. **Hero aura ring.** A baked radiant gold aura ring sits BEHIND the body for
   the store card, on its own surface so the sprite-outline pass doesn't trace
   the soft halo. It is kept entirely OUT of the 40px gameplay frames so it never
   costs legibility.

LEGENDARY spectacle constraint honored: no live particles — foxfire tips, body
warmth, and the hero aura are all baked into the 4 frames; the flicker is the
per-frame tail-spread delta.
