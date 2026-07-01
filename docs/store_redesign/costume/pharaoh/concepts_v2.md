# PHARAOH — Concepts v2 (RE-ROLL)

Premium 700-coin store costume. Replaces the current head-only nemes. The
first batch (Golden Nemes, Anubis, Ra sun-disk, Cleopatra, Mummy) was judged
too weak/fussy at 40px — this batch pushes for **bolder, cleaner, more iconic
silhouettes**, maximal distinctness in head shape + body zone + palette + hero
prop, and a lavish/legendary feel worthy of a premium slot.

**Hard constraints honored by every concept below:**
- Hitbox is a FIXED ~10px circle at body centre — so NO body-ballooning. All
  collar/regalia/recolor stays **inside the base bird footprint**.
- Only HEADGEAR rises above CROWN_Y=31. Nothing hangs below feet line (~y65).
- Slung props read diagonally **across** the body, tucked inside the silhouette.
- Composite facts: canvas 64×100; head centre HX=47, HY=41; CROWN_Y=31; body
  centre ~(32,52); feet ~(28,65)/(34,65).
- All-procedural (pygame polygons/lines/circles/ellipses) — no photo/sprite.

Numbers map to **v2_design_1 … v2_design_5** in rank order (best first).

---

## 1. HORUS — the Falcon-God King  *(v2_design_1)*

Falcon-god of sky & kingship. The boldest re-silhouette in the set: it changes
the *head shape itself*, not just adds a hat. Reads as a sharp predator profile
under a tall crown — unmistakable at 40px and totally unlike a parrot.

- **Hero silhouette:** a sleek, downturned **falcon head/beak** crowned by the
  tall stacked **Pschent (double crown)** — a hard, angular profile spike over
  a hooked dark beak. Two shapes, both reading at 40px.
- **Object list + placement:**
  - *Headgear (above CROWN_Y):* Pschent — bulbous **white Hedjet** cone (Upper
    Egypt) nested inside the flared **red Deshret** basket (Lower Egypt) with a
    front curl wire; a tiny gold **uraeus cobra** bump at the brow.
  - *Face:* recolor the head to slate-grey **falcon** with a clean white cheek
    blaze and a single bold **Eye-of-Horus (wedjat)** stroke — one teardrop line
    + brow, drawn LARGE as the face's hero mark; sharp black **hooked beak**
    replacing the parrot beak; a yellow cere dot.
  - *Neck/chest (in footprint):* a slim turquoise+gold **broad collar** arc,
    2–3 banded rings only (kept thin so it never reads as body mass).
  - *Body:* **paint-over** — keep Pip's body but add a few grey falcon
    chest-feather chevrons so head and body agree; scarlet wings stay as the
    flap so the bird still feels like Pip in costume.
  - *Limbs (slung prop):* a gold **was-scepter** laid diagonally across the
    body, tucked inside the silhouette.
  - *Feet:* dark talon recolor at the feet line.
- **Palette:** `#3A4A5C` slate falcon · `#F2EFE6` Hedjet white · `#C0392B`
  Deshret red · `#E8B23A` gold · `#1FA39A` wedjat turquoise. Day: dark falcon
  head pops on bright sky. Night: white Hedjet + gold uraeus carry the read.
- **Body treatment:** paint-over (head fully recolored falcon-grey; body keeps
  Pip with grey accents).
- **Distinctness:** the ONLY concept that swaps the head's *shape* (hooked
  falcon beak vs parrot) — instant, iconic, royal. The wedjat is the single
  hero face-mark.

---

## 2. KHEPRI — the Scarab Sun-Bearer  *(v2_design_2)*

Sun-beetle god of rebirth. The most *surprising* and the only concept that
claims the BACK zone: an iridescent beetle carapace shell riding the bird with
a rolled sun-disk above. Premium shimmer baked in — feels legendary.

- **Hero silhouette:** a fat **scarab carapace shell** domed over the back +
  the glowing **sun-disk ball** lifted at the head — a beetle rolling the sun.
  Round-on-round, super legible.
- **Object list + placement:**
  - *Headgear (above CROWN_Y):* a radiant **sun-disk** orb (layered gold→amber
    gradient + soft glow ring) held just above the brow — the rolled sun.
  - *Face:* keep Pip's face; add a small dark **scarab-head plate** crest at the
    hairline (segmented notch) so the beetle theme reaches the head.
  - *Neck/chest (in footprint):* a thin gold collar band to seat the shell.
  - *Body — back zone:* the hero — an **iridescent scarab elytra shell**: two
    teardrop wing-cases meeting in a center seam, blue→green→violet sheen with
    a bright specular highlight streak. Kept **within the body footprint** (a
    shell ON the back, not enlarging the body).
  - *Limbs (slung prop):* none needed; the rolled sun-disk above + shell read is
    already two strong shapes. (Optional: tiny beetle-leg ticks at the body edge,
    inside silhouette.)
  - *Feet:* dark recolor at feet line.
- **Palette:** `#16263B` deep beetle-blue (shadow) · `#1E8E7E` scarab teal ·
  `#7FE3B0` iridescent highlight · `#E9B72E` sun gold · `#FFF1B8` sun core.
  Day: dark shell + bright sun-disk = max contrast. Night: glowing sun-disk and
  teal sheen luminesce against the dark sky — true premium flex.
- **Body treatment:** paint-over (shell painted onto the back; head stays Pip
  + crest).
- **Distinctness:** only BACK-zone hero, only insect, only built-in
  iridescent/glow shimmer — the legendary showpiece of the batch.

---

## 3. OSIRIS — the Green Lord of the Afterlife  *(v2_design_3)*

God of resurrection — the only **full body recolor** in the set (Nile-green
skin) and the only one whose hero is a tall pale crown with twin plumes. Regal,
eerie, instantly distinct in palette from every gold pharaoh.

- **Hero silhouette:** a tall white **Atef crown** — Hedjet cone flanked by two
  curling **ostrich plumes** — over a **green** bird. Pale spike + green body =
  unmistakable two-value read.
- **Object list + placement:**
  - *Headgear (above CROWN_Y):* **Atef** — white Hedjet cone center, a tall
    curving **ostrich plume** each side, a small gold sun-disk + red uraeus at
    the base. Tall, clean, symmetrical.
  - *Face:* green head; add a long thin **divine false-beard** bar straight down
    under the chin (kept inside silhouette, NOT below feet) — a crisp vertical
    tell.
  - *Neck/chest (in footprint):* slim gold-and-lapis collar arc.
  - *Body — recolor:* **RECOLOR the whole bird Nile-green** via the palette
    (skin of rebirth) with subtle pale **mummy-wrap bands** painted across the
    lower body (thin horizontal lines, within footprint) so it reads mummiform-
    regal without adding mass.
  - *Limbs (slung prop):* the **crook & flail crossed** diagonally over the
    chest — two short gold staffs in an X, tucked inside the body silhouette
    (the signature Osiris gesture).
  - *Feet:* pale wrap recolor at feet line.
- **Palette:** `#2E7D4F` Osiris green · `#1B4D32` green shadow · `#F2EFE6` Atef
  white · `#E8B23A` gold crook/flail · `#27408B` lapis collar. Day: pale crown
  pops, green body distinct from sky. Night: white Atef + gold X carry it.
- **Body treatment:** **RECOLOR** (whole bird turns green — the palette flex
  no other concept uses).
- **Distinctness:** only green-skin recolor + only crossed crook-and-flail X +
  only twin-plume crown — a different color story entirely from the gold kings.

---

## 4. WAR PHARAOH — the Khepresh Conqueror  *(v2_design_4)*

The martial pharaoh. A bold **rounded blue dome** crown — a soft bulbous
silhouette that contrasts hard-edged against every conical crown in the set —
plus a slung sickle-sword. Reads as "king at war."

- **Hero silhouette:** the round **Khepresh (blue war crown)** — a smooth
  helmet dome studded with disc dots, golden uraeus striking forward — over the
  bird, with a curved **khopesh** sword slung across the body.
- **Object list + placement:**
  - *Headgear (above CROWN_Y):* **Khepresh** — a deep blue rounded dome (single
    clean polygon/ellipse cap), a sparse grid of small gold **disc bosses** for
    the scaled shimmer (kept sparse so it never muddies), and a forward **gold
    uraeus cobra** at the brow as the hero accent.
  - *Face:* keep Pip's face; a thin gold brow-band where dome meets head.
  - *Neck/chest (in footprint):* a **golden scale-armor pectoral** — an arc of
    2–3 rows of small gold scale-flecks across the upper chest, thin, inside the
    footprint (armored but not bulky).
  - *Body:* **paint-over** — a faint blue-and-gold royal sash diagonal to echo
    the crown.
  - *Limbs (slung prop):* a curved gold **khopesh sickle-sword** laid diagonally
    across the body, blade tucked inside the silhouette — the war tell.
  - *Feet:* dark sandal recolor at feet line.
- **Palette:** `#1E3A8A` khepresh blue · `#142A63` blue shadow · `#E8B23A` gold
  uraeus/khopesh · `#F4D67A` gold highlight · `#9FB4E8` disc-boss sheen. Day:
  saturated blue dome stands clean. Night: gold uraeus + khopesh glint against
  blue carry the silhouette.
- **Body treatment:** paint-over (head keeps Pip under the dome).
- **Distinctness:** only ROUND/soft crown silhouette (every other is a cone or
  organic head) + only weapon prop + only blue-dome palette — a martial flex.

---

## 5. THE SARCOPHAGUS KING — the Living Death-Mask  *(v2_design_5)*

The funerary golden death-mask — a *living coffin lid*. The face itself becomes
the hero: a flat gold mask with bold lapis stripes. Most graphic, most
high-contrast face read; eerie-premium.

- **Hero silhouette:** the iconic **nemes-framed golden death-mask face** —
  broad gold cheeks, blue-and-gold striped lappets falling beside the head, a
  single long divine beard bar. A solid gold shield of a face.
- **Object list + placement:**
  - *Headgear (above CROWN_Y):* the **nemes** headcloth crest with bold
    alternating **gold + lapis stripes** rising to a low peak; gold-and-red
    **uraeus + vulture** brow band (kept to two clean bumps, not fussy).
  - *Face:* the hero — **paint the head as a flat golden death-mask:** smooth
    gold face plane, big calm **lapis-rimmed eyes** (almond outline + dark
    pupil, drawn large), straight gold nose ridge. High-contrast, graphic, reads
    as a mask at 40px.
  - *Neck/chest (in footprint):* a wide **inlaid broad-collar** of concentric
    lapis/gold/turquoise band arcs — but kept as 3 thin arcs so it stays in
    footprint.
  - *Body:* **paint-over** — lower body painted as **coffin-lid panel:** vertical
    gold center band flanked by thin lapis stripes (the sarcophagus inlay),
    within footprint.
  - *Limbs (slung prop):* **crossed arms holding mini crook+flail** painted flat
    across the upper chest — the death-mask's crossed-arms pose, inside the
    silhouette (echoes Osiris pose but rendered as flat gold mask art, not 3D
    staffs).
  - *Feet:* gold-banded recolor at feet line.
- **Palette:** `#E8B23A` mask gold · `#C8902A` gold shadow · `#1F3A93` lapis
  blue · `#1FA39A` turquoise inlay · `#F4D67A` gold highlight. Day: gold + lapis
  stripe contrast is loud and clean. Night: gold face glows, lapis stripes
  anchor the value — pure treasure read.
- **Body treatment:** paint-over (head becomes flat gold mask; body painted as
  coffin lid).
- **Distinctness:** only "mask-as-face" concept (the face *is* the hero, not a
  hat) + only flat coffin-lid inlay body + the loudest gold/lapis stripe
  graphic — reads as living treasure, distinct from the rejected realistic
  golden-nemes by being a stylized FLAT graphic mask, not a soft portrait.

---

## Ranking rationale

1. **HORUS** — strongest, most iconic re-silhouette (changes the head shape,
   not just a hat); the wedjat is a perfect single hero mark.
2. **KHEPRI** — best legendary showpiece: only back-zone hero, only built-in
   iridescent shimmer + glowing sun-disk; the premium flex.
3. **OSIRIS** — best palette differentiation (full green recolor + crossed
   crook/flail), regal and eerie, distinct from every gold king.
4. **WAR PHARAOH** — only soft round crown + weapon; clean martial read,
   great value contrast, but closer to "pharaoh-in-a-hat" than 1–3.
5. **SARCOPHAGUS KING** — most graphic face, but highest risk of reading
   "fussy/gold-on-gold" at 40px and nearest in spirit to the rejected nemes;
   ranked last as the safety pick, carried by its flat-mask stylization.

**Best legendary showpiece:** KHEPRI (#2) — iridescence + glow baked into the
art justify the 700-coin price tag.
