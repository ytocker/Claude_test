# PIRATE costume redesign — 5 concepts (richer, multi-item look)

**Item:** `skin_pirate` / "PIRATE" (280 coins, `group: "costume"`).
**Brief:** The user likes today's pirate and wants it to carry **more themed
items for a richer look**. Keep the **pirate identity** (still a
tricorn-and-skull pirate) — designers may **restyle existing elements** while
adding new ones. New items spread across **all body zones**: head, body
(coat/sash/chains), shoulder/back (companion, slung steel), and hand/wing props.

**Current pirate (the ORIGINAL):** head-area only on the untouched scarlet macaw
body — slate tricorn (`_PIR_FELT (74,78,96)`) with a continuous bright-gold brim
band (`(255,205,70)`), a big white skull cockade dead-centre-front
(`(244,246,240)`), a black eyepatch over the near eye with a crown strap, and a
gold hoop earring. See `game/store_skins.py:131-167` (`_paint_pirate`).

## Shared build facts (all designs)
- Composite anchors (COMPOSITE_W=64, COMPOSITE_H=100, PARROT_DY=20):
  head centre **HX=47, HY=41**, crown top **CROWN_Y=31**, beak tip ~**(61,41)**,
  body centre ~**(32,52)**, tail behind/left, near (right) eye faces the viewer.
- Each `tools/pirate_candidates/design_N.py` exposes `build (frame_idx, tilt_deg)
  -> Surface` wrapped by `store_skins._make_skin(paint_fn, base_fn=...)`.
- **Preserve the scarlet macaw** where possible: paint coats/sashes/chains as
  OVERLAYS on top of the scarlet base. Use a full-body recolor via
  `dollar_parrot_ghost._build_parrot_with_palette` + `_pal` (model `P_NINJA` /
  `_VK_PAL`) ONLY if the concept genuinely needs a recoloured body.
- The bar is the **40px-in-motion truth read** on day AND night: every signature
  shape must break the silhouette (push past the crown / past the back/tail),
  keep ≥2px strokes, and avoid near-black on a dark store card. Skull + gold
  brim stay as the anchor read; everything else is layered density around it.

---

## DESIGN 1 — "CAPTAIN'S COMMAND" (the officer)
**Goal:** Promote the buccaneer to a ship's captain — richer hat, a brocade coat,
and naval finery widening the silhouette.
**Hero silhouette:** broad gold-laced tricorn up off the crown + squared,
gold-buttoned coat shoulders that visibly widen the body outline.
**Layered objects + placement:**
- Head: keep the tricorn but richer — deeper navy-slate felt, a DOUBLE gold lace
  band on the brim, the white skull cockade re-trimmed with a tiny gold edge.
- Neck: white lace cravat/jabot tucked under the beak (`(61,41)` down to chest).
- Body: captain's coat overlay over the lower body/chest — deep red-wine panels
  with a gold-button row down the centre and turned-back gold cuffs at the wings.
- Shoulder (back/right): a gold bullion epaulette breaking the back outline.
**Palette:** felt `#2E3346`, gold-lace `#FFCD46`, gold-hi `#FFF0A0`, coat-wine
`#7A1F28`, coat-shadow `#511019`, lace-white `#F4F6F0`.
**Distinctness:** the only "dressed-up officer" — coat + epaulette + jabot read as
formal naval rank, not a deckhand.

## DESIGN 2 — "PARROT'S PARROT" (shoulder-companion buccaneer)
**Goal:** The iconic pirate-with-a-parrot — a tiny companion bird on the back,
bandana, and a cross-body strap.
**Hero silhouette:** a small second-parrot lump perched high on the back breaking
the rear outline + a red bandana knot under the hat.
**Layered objects + placement:**
- Shoulder/back: a tiny 8–10px companion parrot (green/yellow macaw) perched on
  the back-left so it clears the wing — beak, eye dot, folded wing, stubby tail.
- Head: a red headscarf/bandana wrapping the crown UNDER the tricorn, with two
  short knot tails trailing behind the head.
- Chest: a brown leather bandolier strap crossing the body with a small brass
  buckle + one or two stitched musket-cartridge loops.
- Keep: tricorn, gold brim, skull, eyepatch, earring.
**Palette:** companion-green `#2FA85A`, companion-gold `#F2C53D`, bandana-red
`#C0392B`, bandana-shadow `#7E2018`, leather `#5A3A22`, brass `#D9A441`.
**Distinctness:** the only one with a living companion — the second creature is
the signature, unmistakable even at 40px.

## DESIGN 3 — "SWASHBUCKLER" (armed for a fight)
**Goal:** A fighting pirate bristling with steel — slung cutlass, baldric, and a
flintlock at the belt.
**Hero silhouette:** a cutlass blade crossing behind the body with its tip
breaking the tail/back outline + a chunky buckled belt across the chest.
**Layered objects + placement:**
- Back: a cutlass slung diagonally behind — curved steel blade + brass guard +
  grip, tip clearing the tail so it reads against the sky.
- Body: a baldric/wide belt across the chest with a big square brass buckle.
- Belt/wing: a flintlock pistol grip + curved butt tucked at the waist near the
  near wing.
- Keep: tricorn + gold brim + skull + eyepatch; add a tiny scar hint on the cheek.
**Palette:** steel `#C7D0DA`, steel-shadow `#7C8794`, brass `#D9A441`, grip-wood
`#5A3A22`, belt-leather `#3E2A1A`, buckle-hi `#FFE9A8`.
**Distinctness:** the only weaponised set — crossed steel behind the bird is the
read, aggressive and kinetic.

## DESIGN 4 — "OLD SEA-DOG" (the grizzled veteran)
**Goal:** A weathered old salt — braided beard, headscarf with tails, a clay pipe,
and stacked gold hoops.
**Hero silhouette:** a braided beard mass hanging under the beak + a knotted
headscarf with trailing tails; a pipe poking forward off the beak.
**Layered objects + placement:**
- Face: a grey braided beard under/around the beak with 2–3 small gold bead rings
  on the braids.
- Beak: a short clay pipe held in the beak with a tiny smoke wisp curl.
- Head: a deep-red headscarf knotted at the side with two trailing tails behind;
  the tricorn sits battered/worn on top (keep the gold brim + skull).
- Ear: DOUBLE stacked gold hoop earrings.
**Palette:** beard-grey `#C9CBD2`, beard-shadow `#878A95`, scarf-red `#A23026`,
scarf-shadow `#6C1C16`, pipe-clay `#D8C3A0`, bead-gold `#FFCD46`.
**Distinctness:** the only "aged character" build — beard + pipe + scarf tails give
a face full of personality nobody else has.

## DESIGN 5 — "GOLD-LADEN" (the treasure raider)
**Goal:** A plunderer dripping with loot — jewel-studded hat, coin chains across
the chest, a coin pouch, and a gold hook.
**Hero silhouette:** cascading gold coin-chains down the chest + a gem-studded,
coin-trimmed tricorn that sparkles at the crown.
**Layered objects + placement:**
- Head: tricorn upgraded — gold brim PLUS a row of tiny coins/gems on the band and
  a small red gem set into the skull cockade's brow.
- Chest: two or three draped gold necklaces/coin-chains arcing across the body
  (the hero density), each a beaded line of 2px gold dots.
- Belt: a bulging coin pouch on the waist with a few spilling coins.
- Wing/foot: a curved gold hook hint replacing/over one foot.
**Palette:** gold `#FFCD46`, gold-deep `#C8922A`, gold-hi `#FFF0A0`, gem-red
`#D2353A`, gem-green `#36B26B`, pouch-leather `#5A3A22`.
**Distinctness:** the only "wealth" build — sheer mass of gold across the body is
the read; maximalist where the others are characterful.
