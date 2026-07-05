# BINKY — Diaper Redo Concepts

Five distinct, buildable takes on how a baby **diaper** should sit **naturally**
on BINKY (powder-blue cartoon-baby Pip, faces RIGHT, pink pacifier is the single
bright-pink hero). The bug being fixed: the current nappy reads as a tub Pip
*sits in* down at his legs. Every concept below wraps the **lower belly + rump
band (y52–63)** and sits **ABOVE the legs** (legs poke out at x26–36, y65–69).

## Geometry recap (composite pixel space)

- Body ellipse centre (32,52), x13–51 / y38–66; belly lobe centre (28,58),
  x16–40 / y52–64; lower-body bottom edge ~y64–66.
- Legs: (28,65)→(26,69) and (34,65)→(36,69), x26–36, **y65–69** — must stay
  visible below the nappy.
- Rump/tail (bird's "bottom"): back-left, x2–22, y44–56.
- Pacifier (pink hero): x33–40, y44–48. Cream bib: x27–36, y47–51 — keep a
  **powder-blue body gap** between bib and nappy.
- Natural nappy band: curves from back-left rump (x16–22) around the underside
  to the front hip (x38–42), top edge ~y52, bottom edge ~y63.

## Shared palette (cream cloth family — NO bright pink in the cloth)

- `#FBF4DA` cream (main body of the nappy)
- `#FFFFFF` lit top edge / waistband highlight
- `#C9D9DE` powder shadow (underside, leg-cuff shade — this is what holds value
  on navy night sky)
- `#ABA282` seam / fold line / stitch
- Sub-pixel pin head MAY be pink (≤2px) only where a concept calls for a pin.
  The pacifier stays the one true pink.

**Value rule for night sky:** the cream lobe must always carry a `#C9D9DE`
powder-shadow underside arc (y60–63) + at least one `#ABA282` seam so the shape
doesn't void to a flat blob against navy. Lit `#FFFFFF` waistband edge gives the
day-sky top read.

---

## DESIGN 1 — "SNUG CLOTH" (→ design_1)

- **How it sits:** A trim, close-fitting cloth nappy hugging the rump and crotch
  in a smooth band y53–62, contour-following the belly ellipse so it reads as
  worn, not bulky; legs emerge cleanly below at y65.
- **Object/shape stack:**
  - Waistband: thin `#FFFFFF`-topped band, x18–40, y53–55, following the belly
    curve (lit top edge, one `#ABA282` seam line just under it at y55).
  - Rear wrap: cream lobe sweeping the rump back-left, x16–24, y52–60, tucked
    snug (no overhang).
  - Crotch fold: a single cream gusset narrowing between the legs, x27–35,
    y60–64, with one centred `#ABA282` fold line.
  - Leg-cuff shade: short `#C9D9DE` arcs hugging each leg root at (26,64) and
    (36,64), 2–3px, so legs read as poking *through*.
  - Underside: `#C9D9DE` shadow arc along y61–63.
- **Distinctness:** The TRIM/minimal one — lowest profile, smoothest contour,
  no bulk or droop. The baseline "this is obviously a worn nappy" read.

## DESIGN 2 — "PUFFY DISPOSABLE" (→ design_2)

- **How it sits:** A bulky padded disposable with an obvious raised waistband and
  pronounced leg-cuff gathers; sits proud of the body in band y51–63, rounded and
  full, but still clearly above the legs.
- **Object/shape stack:**
  - Waistband: chunky 3px `#FFFFFF`/`#ABA282` ribbed band, x17–41, y51–54, with
    2–3 tiny vertical `#ABA282` ribbing ticks for the stretchy-tape read.
  - Padded body: fat rounded cream lobe bulging out past the belly contour,
    x16–42, y54–63 (silhouette puffs slightly beyond y64 visually but the
    *opening* is above the legs).
  - Leg-cuff gathers: scalloped `#C9D9DE` ruffle arcs around each leg opening,
    (25,63)→(28,65) and (34,63)→(37,65), 2px scallops — the signature tell.
  - Front tape tab: small `#FFFFFF` rectangle at the front hip x38–41, y55–57,
    one `#ABA282` edge (the resealable tab).
  - Underside: deep `#C9D9DE` shadow y60–63 to sell the bulk.
- **Distinctness:** The BULKY/modern one — raised ribbed waistband + scalloped
  leg-cuff ruffles. Fullest silhouette of the five.

## DESIGN 3 — "PINNED TERRY" (→ design_3)

- **How it sits:** The classic folded terry-cloth triangle, points brought up
  over the rump and front hips and pinned at the sides; a flat-front, pointed-
  underside look sitting y52–63 with hip tabs at the waist.
- **Object/shape stack:**
  - Triangle body: cream wrap with a visible diagonal fold — flat top waist edge
    x18–40 at y53, tapering to a point at the crotch x30, y63.
  - Fold diagonals: two `#ABA282` fold lines running from the back-left rump
    (x18,y54) and front hip (x40,y54) down to the crotch point (30,63) — the
    folded-triangle signature.
  - Hip pin tabs: a small `#FFFFFF` tab at each hip, back (x19,y53) and front
    (x39,y53); **one sub-pixel pink pin head (≤2px)** allowed on the front tab
    only (the lone exception to one-pink-budget; keep it tiny).
  - Leg gap: legs emerge at the wide base corners, y65, framed by `#C9D9DE`
    shade at (26,63) and (35,63).
  - Underside: `#C9D9DE` along the lower fold edges y61–63.
- **Distinctness:** The HERITAGE/folded one — visible diagonal fold lines + hip
  pins + a pointed crotch. The only concept with a fastening pin.

## DESIGN 4 — "SAGGY LOAD" (→ design_4)

- **How it sits:** A low-rise nappy that droops a touch at the back rump for a
  cute "heavy" read; waistband stays up front (y53) but the rear lobe sags lower
  and rounder behind, still clearing the legs.
- **Object/shape stack:**
  - Front waistband: snug `#FFFFFF`-lit band across the front hip/belly,
    x24–41, y53–55 (stays high).
  - Drooping rear lobe: cream pouch sagging down-and-back at the rump, x14–26,
    y55–64, bulging lowest at (18,63) — the heavy droop. Rounds well above the
    leg roots so legs still read.
  - Sag crease: one `#ABA282` curved crease across the droop x16–24, y60, plus a
    `#C9D9DE` deep-shadow pool under the heaviest point (18,62).
  - Crotch fold: short cream gusset x28–34, y61–64, one seam line.
  - Leg-cuff shade: `#C9D9DE` arcs at the leg roots y64.
- **Distinctness:** The COMEDY/heavy one — asymmetric rear droop + shadow pool.
  Reads "full nappy" and gives BINKY personality; the only off-balance silhouette.

## DESIGN 5 — "FOLD-OVER FRONT" (→ design_5)

- **How it sits:** A structured nappy with a turned-down front waistband panel
  (like a folded-over towel cuff) giving a crisp horizontal seam line across the
  belly; clean architectural band y52–63, legs out below.
- **Object/shape stack:**
  - Rear wrap: cream lobe around the rump back-left, x16–24, y53–61 (plain,
    smooth — the panel detail is all up front).
  - Fold-over front panel: a `#FFFFFF`-topped cream flap turned down across the
    front belly, x24–42, y53–58, its bottom edge a crisp `#ABA282` horizontal
    seam at y58 — the structural signature tell at 40px.
  - Tape strip: a 2px `#ABA282` vertical tab centred on the panel at x32, y54–57
    (the closure stripe).
  - Lower body: cream below the panel x26–38, y58–63, with a centred crotch seam.
  - Leg-cuff shade + underside: `#C9D9DE` arcs at leg roots (26,64)/(35,64) and
    shadow along y61–63.
- **Distinctness:** The STRUCTURED/architectural one — the crisp turned-down
  front panel with a hard horizontal seam is unique; cleanest geometric read of
  the five, best high-contrast tell on busy backgrounds.

---

## Ranking (most natural + readable first)

1. **DESIGN 1 — SNUG CLOTH.** The truest fix: contour-hugging band that
   unmistakably reads as a *worn* nappy with legs poking through. Lowest risk,
   reads cleanest at 40px on both skies. The safe hero.
2. **DESIGN 2 — PUFFY DISPOSABLE.** The most "baby diaper" instantly-legible
   shape — ribbed waistband + leg-cuff ruffles are a universal diaper tell.
   Slightly fuller silhouette but still clearly above the legs.
3. **DESIGN 5 — FOLD-OVER FRONT.** Best high-contrast structural seam for the
   40px read; crisp and characterful without bulk. Strongest value hold on navy.
4. **DESIGN 3 — PINNED TERRY.** Charming heritage look and the only fastening
   detail, but the diagonal fold lines + sub-pixel pin risk muddying at 40px —
   needs the fold lines kept to hard ≥2px or it softens.
5. **DESIGN 4 — SAGGY LOAD.** Most personality and funniest, but the asymmetric
   droop is the highest risk of reading as "tub/basket" again if the rear lobe
   creeps toward the legs — ship only if the droop stays well clear of y65.

**Best showpiece for charm:** DESIGN 4 (comedy). **Safest natural-nappy
read:** DESIGN 1. **Best 40px clarity:** DESIGN 5.
