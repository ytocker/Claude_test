# SHOES roster expansion — 5 new escalating shoes

Goal: extend the SHOES tab UP the rarity ladder. Current roster is grounded
real-sneaker homages topping out at RETRO 1 (epic, 850). These 5 new shoes are
**top-heavy** — 1 rare, 2 epic, 2 legendary — and get **wilder + more unique as
the tier climbs** (grounded mass → translucent candy → emissive neon → winged
gold → flaming rocket).

Each candidate is a single side-profile `draw_shoe(surf, x, y, w, h, facing)`
(canonical shoe contract — same call feeds the 104×58 store product-shot AND the
17×11 worn-foot render). Proportional geometry, `max(1, …)` stroke clamps so cues
survive the 40px foot read. Template: `game/shoe_retro1.py`. Numbers map
design_1…5.

---

## design_1 — MEGA DAD · rare · ~780
**Theme:** oversized "dad shoe" chunky runner. The loudest *grounded* sneaker —
no glow, no fantasy, pure mass.
- **Hero silhouette:** bulbous triple-stacked foam midsole, exaggerated bulk;
  reads as a fat wedge of sole even at 16px.
- **Objects + placement:** stacked white/grey midsole layers (bottom ⅓);
  mesh+suede colour-blocked upper (grey body, teal toe overlay, orange mudguard);
  reflective lace-cage straps across the throat; fat heel pull-loop at the back.
- **Palette:** `#E8E6E0` off-white · `#B9C0C4` cool grey · `#2AA6A0` teal pop ·
  `#F0792E` orange pop · `#2B2E33` dark seams.
- **Distinct:** the only shoe that reads as pure *bulk/stack height*; a hype
  homage that stays believable footwear.

## design_2 — JELLYCORE · epic · ~1200
**Theme:** translucent gel runner. First shoe to introduce glow — a see-through
candy sole you can read the ground through.
- **Hero silhouette:** glossy jelly upper over a clear gradient sole, rounded and
  wet-looking.
- **Objects + placement:** translucent gradient outsole (pink→cyan, ground faintly
  visible through it); glossy jelly upper with visible inner gel bubbles; frosted
  semi-clear lace loops; soft inner bloom/glow along the midsole.
- **Palette:** `#FF8FD0` pink · `#66E6FF` cyan · `#C9A8FF` lilac · translucent
  whites · `#3A2E55` deep contrast.
- **Distinct:** translucency + candy gradient + first soft glow; a gummy/gel look
  no grounded shoe has.

## design_3 — NEON CIRCUIT · epic · ~1800
**Theme:** LED light-up cyber high-top. Emissive — reads as LIGHT at 40px.
- **Hero silhouette:** dark tech high-top with a bright glowing sole light-strip
  + lit collar; the glow is the silhouette read.
- **Objects + placement:** near-black tech upper; electric-blue→magenta LED sole
  strip with a glow halo; circuit-trace lines climbing the side panel; glowing
  lace eyelets; light-up heel chevron.
- **Palette:** `#0E1018` near-black · `#19E0FF` cyan glow · `#FF3CC7` magenta glow
  · `#7A48FF` violet · `#DDF6FF` hot light.
- **Distinct:** emissive neon glow lines on a dark base — cyberpunk; the only
  "lit-up" shoe, reads as light rather than colour.

## design_4 — WING BOOTS · legendary · ~3200
**Theme:** Hermes winged boots. First true fantasy boot — the silhouette breaks
the shoe box outward with wings.
- **Hero silhouette:** gold greave boot with feathered ankle wings spreading out
  to both sides — an unmistakable winged outline.
- **Objects + placement:** gold metal greave/boot shell; white-gold feathered
  ankle wings flaring back from the heel/ankle; laurel ankle wrap; a gemmed clasp
  at the cuff; faint sparkle motes.
- **Palette:** `#F4D77A` gold · `#FBF0C4` light gold · `#C99A3A` deep gold ·
  `#FFFFFF` feather white · `#6FE3FF` sparkle.
- **Distinct:** WINGS break the silhouette outward; mythic gold; the first piece
  that stops looking like a sneaker and becomes a relic.

## design_5 — AFTERBURNER · legendary · ~4800 · THE showpiece
**Theme:** rocket thruster boots. Loudest, most spectacle — active flame + chrome
mecha, an energy/motion cue no other shoe has.
- **Hero silhouette:** chrome mecha boot with a rear exhaust nozzle and a flame
  plume trailing behind it — unmistakably a rocket.
- **Objects + placement:** chrome/steel armoured boot shell with riveted plating;
  rear thruster nozzle at the heel; a layered flame plume (white core → orange →
  red) streaming back; heat-glow vents; a few ember sparks.
- **Palette:** `#C9D2DB` chrome · `#6E7A88` steel · `#FFE27A` flame core ·
  `#FF7A1A` orange · `#E22810` red · `#2A2E36` dark plating.
- **Distinct:** active flaming exhaust + chrome armour; reads as thrust/motion;
  the top-of-ladder grail.
