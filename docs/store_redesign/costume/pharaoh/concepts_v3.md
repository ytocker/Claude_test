# PHARAOH — "richer classic pharaoh" concepts (v3)

Brief: the current `skin_pharaoh` is essentially head-only — a gold+lapis striped
**nemes** headdress with a gold **uraeus** cobra at the brow on the plain scarlet
macaw. The user likes the pharaoh; they just want it **RICHER**. So this is an
ENRICH pass (like the shipped pirate / top-hat redesigns), NOT a re-theme. Two
earlier batches were rejected for going off into different characters (Anubis,
Ra, Mummy, Cleopatra, Horus, Khepri, Osiris…). **This batch does the opposite:**

**CORE IDENTITY — present in ALL 5, unchanged:** the gold+lapis striped nemes
headdress with flaring side lappets + the gold uraeus cobra at the brow. Every
design keeps this so it reads unmistakably as the SAME pharaoh. Each design only
ADDS a different set of bold Egyptian ornaments to make it richer.

## Hard rules (learned this session)
- **Stay the classic pharaoh.** Build ON the existing nemes; don't redesign it.
- **40px-in-motion read, day AND night.** Add BOLD, clean ornaments — gold-on-
  scarlet is the strongest contrast; avoid fussy 1px detail that muds at 40px.
  ONE clear hero element per design.
- **Footprint law (gameplay):** the collision hitbox is a fixed ~10px circle and
  never changes. Keep ALL body ornaments INSIDE the base bird footprint — body
  centre ~(32,52), feet line ~y65-69 (HY+24..28). Nothing hangs below the feet;
  nothing balloons the body. Only the nemes/headgear rises above CROWN_Y=31.
- **Mostly paint-over the scarlet body** (the user is ADDING to the existing
  costume) — only design 4 recolors the body (gold), as the one "divine" option.

Coord anchors: canvas 64×100; head HX=47 HY=41; crown CROWN_Y=31; body centre
~(32,52); feet ~(28,65)/(34,65). Numbers map to v3_design_1…v3_design_5.

---

## 1. THE GOLD KING — full royal regalia (the classic, maximised)
- **Hero:** the **crook & flail** crossed high on the chest over a broad gold collar.
- **Adds (on top of the core nemes+uraeus):**
  - broad **usekh collar** — 3 concentric bead rows (gold / lapis / turquoise)
    arcing across the upper breast, inside the body footprint;
  - plaited **false beard** straight down from the chin;
  - **crook & flail** crossed and held over the chest (the authority hero);
  - thin gold **anklets** at the feet line.
- **Palette:** `#F4C430` gold, `#1B3A8C` lapis, `#2FB8A6` turquoise, scarlet body,
  `#7A4A12` bronze shadow.
- **Body:** paint over scarlet.
- **Distinct:** the complete "king holding crook & flail" — maximal authority regalia.

## 2. THE JEWELED PHARAOH — inlaid treasure (bling)
- **Hero:** a big **jeweled pectoral** medallion on the chest — a central scarab
  flanked by carnelian + turquoise inlay, hung on a gold chain.
- **Adds:**
  - the pectoral necklace (chest centre);
  - gold **armlet / wing-band** + **wrist cuff** on the near wing;
  - a gem-studded **brow band** lifting the nemes front;
  - gold **anklets**.
- **Palette:** `#F4C430` gold, `#C1453B` carnelian, `#2FB8A6` turquoise, `#1B3A8C`
  lapis, scarlet body.
- **Body:** paint over scarlet.
- **Distinct:** jewelry-forward — the bejeweled pectoral + armlets read as treasure;
  the richest "wearing the museum" look.

## 3. THE DIVINE PRIEST — ceremonial (textile + glyph)
- **Hero:** an upright **ankh** held in the wing + a spotted **leopard-skin sash**
  draped diagonally across the body.
- **Adds:**
  - **leopard mantle/sash** over one shoulder, tan with black rosettes (the only
    patterned textile in the set), crossing the chest within the footprint;
  - a simple gold collar;
  - the gold **ankh** held upright in the near wing;
  - anklets.
- **Palette:** `#F4C430` gold, `#C9A24B` leopard tan + `#1A1410` spots, `#1B3A8C`
  lapis, scarlet body.
- **Distinct:** priestly/ceremonial — the only one with a patterned animal-skin
  textile + a held sacred glyph.

## 4. THE SUN-GILDED — divine gold-flesh (the one recolor)
- **Hero:** the whole bird **gilded gold** (eternal god-flesh) with a small
  **winged-sun** disk motif on the brow above the uraeus.
- **Adds:**
  - **gold body recolor** (warm gold with amber shadow) via a base palette — the
    nemes stripes + a COOL lapis/turquoise usekh collar pop against the warm body;
  - the **winged-sun** brow emblem (small gold disk + two short out-swept wings)
    above the uraeus;
  - gold anklets.
- **Palette:** `#F4C430`/`#FFE9A8` gold body, `#1B3A8C` lapis, `#2FB8A6` turquoise,
  `#9A6B1E` amber shadow.
- **Body:** **gold recolor via base palette** (the single divine variant).
- **Distinct:** the only gilded-body "god-flesh" pharaoh — richness via the gold
  skin + cool-collar contrast, not added props.

## 5. THE ADORNED SOVEREIGN — royal heraldry (Two Ladies + cartouche)
- **Hero:** **twin brow emblems** — the uraeus cobra AND a vulture head side by
  side (the "Two Ladies" nebty) — plus a **cartouche** name-ring on a chest sash.
- **Adds:**
  - the vulture head beside the uraeus at the brow (gold + white);
  - a deep **shebyu collar** — rings of fat gold discs across the chest;
  - a **sash** down the body bearing a small oval **cartouche** (gold ring with
    2-3 glyph ticks);
  - gold anklets.
- **Palette:** `#F4C430` gold, `#1B3A8C` lapis, `#2FB8A6` turquoise, `#EDE9DD`
  vulture white, scarlet body.
- **Distinct:** royal heraldry — the only one with the twin "Two Ladies" emblems
  + a cartouche; the most "titled/named" sovereign.

---

## Ranking (best first → maps to v3_design_1…5)
1. **THE GOLD KING** — the safest, most iconic "richer pharaoh"; crook & flail +
   collar + beard is the textbook upgrade everyone reads instantly.
2. **THE JEWELED PHARAOH** — bold single hero (gem pectoral); maximal "rich" read.
3. **THE ADORNED SOVEREIGN** — heraldic twin-emblem + cartouche; regal and distinct.
4. **THE SUN-GILDED** — the gilded-body divine option; one recolor for variety.
5. **THE DIVINE PRIEST** — characterful leopard-sash + ankh; subtlest silhouette,
   so ranked last but the most thematically different addition.
