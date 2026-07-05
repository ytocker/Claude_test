# Coin Store redesign — Round 2 (converged)

## Direction
The art-director converged on ONE chassis: **OBSIDIAN & GOLD body + rarity
SHELF-LIGHT BAR + inset GEM BADGE.** Round 2 builds that single design at
near-shippable quality with three within-chassis SUB-VARIANTS (A/B/C that change
only the bar intensity, gem corner, bezel weight, and an optional aurora wash),
plus a large DETAIL-CALLOUT band.

Render harness: `docs/store_redesign/render_r2.py` (headless,
`SDL_VIDEODRIVER=dummy`, repo root on `sys.path`). Combined sheet:
`docs/store_redesign/round_2.png` (1176x1472). Real catalog items, real
procedural thumbnails (`parrot.get_skin_icon` / `get_skin_frame`), the real
price->rarity ladder, real equipped/secret states.

## The converged card (chassis)
- **Obsidian body** — near-black vertical gradient `(_OBS_TOP (26,24,32)` ->
  `_OBS_BOT (9,8,15))` via `_vgrad_panel`, so it reads as subtly top-lit, plus a
  faint top sheen. Body colour is NEVER tinted by rarity.
- **Fine gold inner bezel** — a single (A/B) or double-weight (C) `1px`
  `_GOLD_DEEP@210` rounded inset stroke. Crisp jeweller line, not a fat outline.
- **Rarity SHELF-LIGHT BAR** (`_shelf_bar`, PRIMARY cue) — a crisp 3px tier-colour
  bar at the card base with a bright hot centre + dark ends, and a SHALLOW
  additive up-wash (`wash_h = 10*intensity+6`, `peak = 22*intensity+8`, falloff
  `f**2.6`, horizontal taper) that glows up like a vitrine light. Tuned so all
  four tiers read at 360px without recolouring the obsidian body.
- **Inset GEM BADGE** (`_gem`, SECONDARY cue) — a faceted diamond (lit TL facet /
  shaded BR facet / white specular pip) ~30% smaller than round 1 (`r=6` grid),
  halo HALVED (`radius r*1.5`, `alpha ~70`), seated in a dark keyline well so it
  reads as inset jewellery, not a floating sticker.
- **Clean dark inset disc** (`_inset_disc`) under the thumbnail — a radial
  light-centre -> dark-rim disc with a thin inner-shadow lip. The round-1 colored
  glow ring is GONE; the procedural macaw/skin is the brightest thing on the card.

## Sub-variant differences (within the chassis only)
- **A — SUBTLE**: `bar_intensity 0.7`, gem top-left, 1px bezel, no aurora. The
  most restrained / AAA-minimal read.
- **B — BALANCED**: `bar_intensity 1.0`, gem top-right, 1px bezel, + a <=15%
  aurora ribbon wash behind the grid. The recommended default.
- **C — VITRINE**: `bar_intensity 1.35`, gem top-left, 2px bezel. The punchiest
  shelf-light / most "lit display case" read.

## Punch-list — what changed vs round 1
1. **Converged** to OBSIDIAN & GOLD; the five families collapsed to one chassis
   with three knob-level sub-variants (bar intensity / gem corner / bezel weight
   / aurora). No new looks.
2. **Buy-confirm modal rebuilt** (`_modal`) on a clean centred grid: header +
   divider -> thumbnail on inset disc with a thin rarity shelf-light strip ->
   name -> tier word -> a SINGLE gold price chip -> a two-button row (BUY
   gradient-gold / CANCEL brushed-dark) with a clear 16px gutter, both fully
   inside the panel. Scrim darkened to ~70% (`(4,4,10,180)`). Double gold frame.
   Nothing clipped.
3. **Thumbnail glow rings killed** — replaced by `_inset_disc` (dark recessed
   disc, inner-shadow lip). Rarity now lives ONLY in the bar + gem.
4. **Chip family unified** (`_chip` + `_CHIP_STATES`) — identical pill silhouette
   + hairline gold rim + top sheen for price / EQUIP / EQUIPPED / can't-afford.
   EQUIPPED stays green for state but same shape/rim. Can't-afford =
   DESATURATED-GOLD `(108,92,56)` fill + `_GOLD`-ish text + a tiny `_lock_glyph`
   (never grey). Chip text bumped one weight notch (`fsz = h*0.56`, bold). Coin
   glyph reuses `_coin_icon` sized to the chip.
5. **Tab strip redesigned** (`_tabstrip`) — one consistent active treatment: gold
   underline (short low under-glow, NOT a sunburst) + brighter label on active,
   dimmed/alpha'd inactive, even edge-to-edge cell spacing, no pills, a right
   chevron for the overflow tabs. Tactile and intentional.
6. **Secret `???` card tamed** — its glow uses the neutral `MYSTERY` palette
   (iridescent cool gem, no tier claim) so it stops out-shouting legendary; the
   `?` stays crisp via `_draw_qmark`; tier label reads "MYSTERY".
7. **Equipped card-rim added** — a thin gold frame around the WHOLE card plus a
   faint EDGE-only additive halo (not a fill bloom), so equipped reads at a glance
   across the grid without washing the card content.
8. **Balance header polished** (`_balance_header`) — "BALANCE" microcopy dropped;
   coin gets 9px breathing room from the digits; the `+` is a clear round tappable
   button with its own small glow. Keeps the luxe recessed gold capsule (inner
   shadow lip + gold rim) and gradient-gold digits (`_gradient_text`).
9. **Glow budget dialled to a hierarchy**: brightest = balance coin
   (`alpha 110`), then equipped rim (edge halo `~20`), then rarity shelf-bar wash
   (`~22-38`), then gem halo (`~70` but tiny radius), then thumbnail (no ring).
   Chips carry NO additive bloom. Modal BUY uses a tight edge glow, not a bloom.
10. **Optional flavor**: a <=15% aurora ribbon wash behind the grid on sub-variant
    B only (`_bg(aurora=True)`, two `_soft_glow` ribbons at `alpha 11`); a tiny
    `_gold_leaf` sprig on LEGENDARY cards only, kept faint so it never lowers
    card/product contrast.

## Palette / treatment values
- Obsidian body: `(26,24,32)` -> `(9,8,15)`.
- Rarity (gem / glow / deep): common `(196,204,218)/(170,182,205)/(74,80,96)`;
  rare `(104,182,255)/(78,158,255)/(26,62,124)`; epic
  `(200,126,250)/(184,100,248)/(74,34,116)`; legendary
  `(255,184,76)/(255,156,46)/(126,68,14)`. Mystery (secret):
  `(206,214,224)/(150,190,220)/(64,70,92)`.
- Gold tokens reused from `game/hud`: `_GOLD_BRIGHT (240,192,64)`,
  `_GOLD_PALE (255,232,168)`, `_GOLD_DEEP (180,130,20)`.
- Chip states: price `bg _GOLD_DEEP`; equip `bg (96,74,24)`; equipped
  `bg (84,196,112)`; locked `bg (108,92,56)`.
- Modal scrim `(4,4,10,180)`; panel `(28,24,38)`->`(12,10,22)`, double gold frame.

## Helpers used (per effect)
- **Reused from the project**: `rounded_rect`, `lerp_color`, `UI_CREAM`,
  `NEAR_BLACK`, `WHITE` (`game/draw`); `_font`, `_coin_icon`,
  `_draw_overlay_stars`, `_GOLD_BRIGHT`, `_GOLD_PALE`, `_GOLD_DEEP`,
  `_RED_OUTLINE` (`game/hud`); `_seeded_stars` (`game/powerup_help`);
  `parrot.get_skin_icon`/`get_skin_frame`, `store_catalog`
  (ids/cost/rarity/name), `store_data`, `_draw_qmark`
  (`game/surprise_box_variants`).
- **Harness primitives** (all pygame-only, both-target safe — gradients,
  polygons, `BLEND_ADD`/`BLEND_RGBA_MIN`/`BLEND_RGBA_MULT`, smoothscale):
  - obsidian body + chip/button bodies: `_vgrad_panel`
  - shelf-light bar: `_shelf_bar` (+ `_soft_glow` for the modal/tab echoes)
  - inset gem badge: `_gem`; legendary flourish: `_gold_leaf`
  - thumbnail disc: `_inset_disc`
  - unified chips: `_chip` / `_CHIP_STATES` / `_state_chip` / `_lock_glyph`
  - balance header: `_balance_header` (+ `_gradient_text`, `_drop_shadow`)
  - tab strip: `_tabstrip`; depth: `_drop_shadow`; glow budget: `_soft_glow`
  - modal: `_modal`; big callout cards: `_big_card`

All primitives use only standard pygame surface ops — nothing desktop- or
browser-only — so they port straight into the live store draw path.
