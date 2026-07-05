# Coin Store redesign — Round 1

## Goal
Elevate the COIN STORE from a functional proof-of-concept to an awesome,
polished, AAA-quality casual-game store, while staying unmistakably in Skybit's
visual family (tropical macaw "Pip", warm-gold, night-sky, casual-arcade — NOT
generic sci-fi). All art is procedural / pygame-only and readable at 360x640
phone scale. Five genuinely distinct full-screen directions, plus a larger
detail-callout strip so the small stuff (rarity gems, chips, balance, modal) can
be judged up close.

Render harness: `docs/store_redesign/render.py` (headless, `SDL_VIDEODRIVER=dummy`).
Combined sheet: `docs/store_redesign/round_1.png` (1944x1332). Real catalog
items, real procedural thumbnails (`parrot.get_skin_icon` / `get_skin_frame`),
the real price->rarity ladder, real equipped/secret states.

## The premium rarity language (shared across all 5)
The current store encodes rarity as a flat 2px outline. Every direction replaces
that with a real, faceted **rarity gem badge** (`_gem`): a diamond cut with a lit
top-left facet, a shaded bottom-right facet, a white specular pip, and an
additive tier glow — the established casual-game gem ladder (white/gray common →
blue rare → purple/pink epic → orange legendary), re-warmed toward Skybit's gold
world. Equipped cards still override to the bright-gold rim so the active look
reads at a glance; secrets stay masked (`???` + `_draw_qmark`) with the price chip
showing, exactly as today.

## The 5 directions

1. **GEM VITRINE** — museum display-case treatment. Each card is glass with a
   top sheen, a brushed two-ply metallic rim in the rarity colour, an inner
   bevel, and a soft per-rarity **floor-glow pedestal** under the thumbnail so
   the item reads as lit on a stand. Faceted gem badge top-right. Rich indigo
   sky. *(This is also the language used for the detail-strip single cards.)*

2. **FOIL CARDS** — trading-card treatment. A full rarity **colour banner** runs
   across the top of each card (the gem language as a ribbon, name printed on
   it), a clean product-shot thumbnail sits on a darker inset, and epic/legendary
   cards get an animated **holographic diagonal foil sweep**. Underlined tab
   strip. Teal-to-plum sky.

3. **TROPICAL TICKET** — warm arcade-ticket treatment, the most distinctly
   Skybit-tropical break from the dark family. Cream/sand cards with punched
   ticket **notches**, a corner-fold **dog-ear rarity tab** with a mini gem, leafy
   gold corner flourishes, a dashed tear line, and bold dark ink type on a
   sandstone banner header. Sunset-band sky.

4. **OBSIDIAN & GOLD** — restrained luxury-jeweller treatment, the most AAA-mobile
   minimal. Near-black obsidian cards with a fine gold inner bezel, a confident
   large thumbnail, a small gem dot, and a thin rarity **shelf-light bar glowing
   along the card's base**. Hairline-framed wordmark + dot-marker tab strip. Deep
   cool sky, sparse stars.

5. **AURORA SHELF** — atmospheric boutique-shelf treatment, the most "alive".
   Soft **aurora ribbons** wash behind the grid; each card is a **frosted-glass**
   panel (translucent cool body, frost speckle, top sheen) with a corner gem and
   a matching per-rarity **aura bloom** behind it. Aurora teal-green-violet sky.

## Palette / treatment notes
- Each direction picks its own multi-stop background gradient (`_bg`) so palette
  richness genuinely differs, all within the night-sky/tropical/gold world.
- Rarity tints (`RARITY`): gem face + additive glow + deep-facet shade per tier.
- Depth kit applied everywhere: soft drop shadows (`_drop_shadow`), vertical-
  gradient lit panel bodies (`_vgrad_panel`), diagonal-split inner bevels
  (`_inner_bevel`), layered additive blooms (`_soft_glow`).
- **Luxe coin balance** (`_balance_bar`): recessed dark-gold capsule, glowing
  coin, gold-gradient digits (`_gradient_text`), and a `+` add-coins affordance.
- **Beautiful modal** (`_modal_closeup`): dimmed scrim, double gold frame, bevel,
  rarity aura behind the item, gem + rarity word, glowing coin price chip, and
  gradient BUY / brushed CANCEL buttons.
- Chips (`_coin_chip`): gradient pill body, hairline gold rim, optional coin and
  under-glow; states EQUIPPED (green) / EQUIP (deep gold) / price (afford) /
  locked (grey).

## Helpers used
- Reused from the project: `rounded_rect`, `lerp_color`, `UI_CREAM`,
  `NEAR_BLACK`, `WHITE` (`game/draw`); `_font`, `_coin_icon`,
  `_draw_overlay_stars`, `_GOLD_BRIGHT`, `_GOLD_PALE`, `_GOLD_DEEP`,
  `_RED_OUTLINE`, `_ORANGE_BORDER` (`game/hud`); `_seeded_stars`
  (`game/powerup_help`); `parrot.get_skin_icon`/`get_skin_frame`,
  `store_catalog` (ids/cost/rarity/name/secret), `store_data`, `_draw_qmark`
  (`game/surprise_box_variants`).
- New procedural primitives defined in the harness (all pygame-only, both-target
  safe): `_soft_glow`, `_vgrad_panel`, `_drop_shadow`, `_inner_bevel`, `_gem`,
  `_coin_chip`, `_gradient_text`, `_balance_bar`, plus per-direction card +
  tab-strip + header functions and `_modal_closeup`.

All primitives use only standard pygame surface ops (gradients, polygons,
`BLEND_ADD`/`BLEND_RGBA_MIN`/`BLEND_RGBA_MULT`, smoothscale) — nothing
desktop- or browser-only — so they port straight into the live store draw path.
