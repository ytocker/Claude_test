# Coin Store redesign — Round 3 (FINAL, locked B+)

## Direction
The art-director LOCKED the chassis to **"B+"** and handed a 6-point
punch-list. Round 3 builds the single shippable design at that locked spec —
no sub-variants. Harness: `docs/store_redesign/render_r3.py` (headless,
`SDL_VIDEODRIVER=dummy`, repo root on `sys.path`). Combined sheet:
`docs/store_redesign/round_3.png` (1192x1198). Real catalog items, real
procedural thumbnails (`parrot.get_skin_icon` / `get_skin_frame`), the real
price->rarity ladder, real equipped / secret / can't-afford states.

The sheet is ONE full-screen 360x640 mockup of the locked B+ store (left)
beside a DETAIL-CALLOUT band (right): the five distinct rarity reads on
shelf-bar + gem, a grayscale proof strip, the unified chip family with the new
coin glyph, the balance header, the tab strip, the four tier cards + equipped +
mystery + can't-afford at scale, and the rebuilt cohesive buy-confirm modal.

## Locked B+ chassis (built exactly)
- **Obsidian near-black body**, subtle top-lit gradient (`_OBS_TOP (26,24,32)`
  -> `_OBS_BOT (9,8,15)` via `_vgrad_panel`) + a faint top sheen. **Never tinted
  by rarity.**
- **2px fine gold inner bezel** (`_GOLD_DEEP@210` inset stroke).
- **Rarity SHELF-LIGHT BAR at the card base @1.0 intensity** (`_shelf_bar`,
  PRIMARY cue) — a crisp 3px tier-colour bar with a hot centre + dark ends and a
  shallow additive up-wash that glows UP into the body like a vitrine light.
- **Inset faceted GEM badge in the TOP-RIGHT corner** (`_gem`, SECONDARY cue),
  seated in a dark keyline well.
- **Thumbnail on a clean dark inset disc** (`_inset_disc`) — never rarity-tinted.
- **Equipped = full-card gold rim + edge halo** (additive edge-only, not a fill
  bloom).
- **Aurora wash OFF by default** — the `_bg(aurora=...)` code path is kept but
  `render_store` calls it with `aurora=False`.
- **Legendary gold-leaf sprig** kept, faint, legendary cards only (`_gold_leaf`,
  top-left, opposite the TR gem).

## Punch-list — what changed (ordered by impact)

### 1. Tier-colour collisions fixed (hue AND value, colorblind-safe)
Re-hued the four tiers + mystery so no two collide on either the shelf-bar or
the gem, and so they ladder in grayscale value. The "lum" below is the Rec.601
grayscale value of the gem face (`0.299R+0.587G+0.114B`):

| state      | gem RGB         | hue            | lum  | grayscale role        |
|------------|-----------------|----------------|------|-----------------------|
| COMMON     | `(208,178,132)` | warm sand      | ~178 | a real, lit tier — **not** gray-on-obsidian. Warm, clearly different from mystery's cool silver. |
| RARE       | `(96,196,240)`  | cyan-blue      | ~178 | pushed cooler/greener so it cannot be the neutral silver mystery. |
| EPIC       | `(190,104,236)` | magenta-violet | ~135 | **darkest** tier value. |
| LEGENDARY  | `(255,168,56)`  | hot orange     | ~178 | the deliberate standout (brightest warm). |
| MYSTERY    | `(214,218,224)` | neutral silver | ~218 | **brightest, no saturated hue** — claims NO tier; re-hued OFF blue so it no longer collides with RARE. |

The decisive grayscale separation lives in the **shelf-bar** (the primary cue):
the strip's value clearly ladders epic(dark) < common/rare(mid) <
legendary(bright) < mystery(brightest) — visible in the GRAYSCALE PROOF strip on
the sheet. Hue does the rest (warm-sand vs cyan vs violet vs orange vs neutral
silver are four separable hue families + one neutral). COMMON and LEGENDARY sit
at a similar grayscale value but are unmistakable by hue (cool-warm sand vs hot
orange) and never appear adjacent without the tier word. Helpers: `RARITY` /
`MYSTERY` dicts, `_shelf_bar`, `_gem`.

### 2. Coin glyph redrawn ONCE, applied everywhere
New `_coin_glyph` (cached per radius): a flat-gold disc with a **single diagonal
bevel** (bright top-left `(255,230,150)` ramping to deep bottom-right
`(188,132,30)` along the TL->BR axis), a thin `_GOLD_DEEP` rim keyline, one
specular arc hugging the top-left edge, and a simple stamped **`$`**. NO
gear/sunburst teeth (they muddied at small size). It reads cleanly from the 9px
chip coin up to the 30px modal coin. Used in: the price chip (`_chip` coin path),
the balance capsule (`_balance_header`), and the modal price chip (`_modal`). It
replaces every prior `_coin_icon` call in the store harness.

### 3. Can't-afford vs EQUIP chips separated
The "locked" chip is pushed **dark + cool**: fill `(40,46,62)` slate-blue, text
`(150,166,190)`, rim `(88,102,132)`, and a damped sheen (`peak 28` vs `46`) so it
reads flat and recessed — unmistakably distinct from the warm EQUIP chip
(`(96,74,24)` gold) at 360px. The small `_lock_glyph` stays a confirming (not
sole) cue. All chips keep the unified pill silhouette + hairline rim + sheen
(`_chip` / `_CHIP_STATES`). Proven on the sheet: price / EQUIP / EQUIPPED /
can't-afford side by side, plus a forced can't-afford card in both the grid and
the tier-card row.

### 4. Chassis locked to B+
Built exactly per spec above: obsidian body, **2px** bezel, shelf-bar @**1.0**,
gem in the **TOP-RIGHT** corner, aurora **off**, legendary sprig kept. No
sub-variants rendered. (`_card`, `render_store`.)

### 5. Modal cohesion
- The thumbnail disc and its shelf strip are now **ONE seated element**: the
  disc sits in a dark inset **stage panel** (`_vgrad_panel`) with the rarity
  shelf-light bar seated FLUSH at the stage base (the same `_shelf_bar` routine
  the cards use) and the gem badge seated into the stage's top-right corner —
  exactly the card's language, so nothing floats as a detached pill.
- The hard header hairline under "CONFIRM PURCHASE" is replaced by a **soft gold
  GRADIENT rule** (`_gold_rule`: bright `_GOLD_BRIGHT` centre fading to nothing
  at both ends), matching the capsule's lit language.

### 6. Gem cut depth
`_gem` now cuts with **three facet values** plus the recovered specular:
- bright top-left facet `lerp(base, WHITE, 0.5)`,
- mid top-right facet `base`,
- shaded bottom-left facet `lerp(base, deep, 0.5)`,
- **darker bottom-right SHADOW facet** `lerp(deep, NEAR_BLACK, 0.3)`,
- a crisp girdle keyline around the stone, and
- a **white specular pip** (additive, on the lit facet) so the cut catches light
  at 360px instead of reading as a flat 2-tone chevron. The mystery gem uses the
  same four-facet structure on a neutral iridescent base.

## Palette / treatment values
- Obsidian body: `(26,24,32)` -> `(9,8,15)`; 2px `_GOLD_DEEP@210` bezel.
- Rarity gem / glow / deep:
  common `(208,178,132)/(196,162,110)/(96,74,44)`;
  rare `(96,196,240)/(64,172,230)/(20,78,116)`;
  epic `(190,104,236)/(170,78,232)/(70,28,104)`;
  legendary `(255,168,56)/(255,138,30)/(132,64,10)`;
  mystery `(214,218,224)/(176,196,214)/(78,84,98)`.
- Chip states: price `bg _GOLD_DEEP`; equip `bg (96,74,24)`; equipped
  `bg (84,196,112)`; locked `bg (40,46,62)` (dark cool).
- Coin glyph: disc `(255,230,150)`->`(188,132,30)` diagonal, `$` stamp.
- Modal scrim `(4,4,10,180)` (~70%); panel `(28,24,38)`->`(12,10,22)`, double
  gold frame; stage `(18,16,26)`->`(8,7,14)`.

## Helpers used (per effect)
- **Reused from the project**: `rounded_rect`, `lerp_color`, `UI_CREAM`,
  `NEAR_BLACK`, `WHITE` (`game/draw`); `_font`, `_draw_overlay_stars`,
  `_GOLD_BRIGHT`, `_GOLD_PALE`, `_GOLD_DEEP`, `_RED_OUTLINE` (`game/hud`);
  `_seeded_stars` (`game/powerup_help`); `parrot.get_skin_icon` /
  `get_skin_frame`, `store_catalog` (ids/cost/rarity/name), `store_data`,
  `_draw_qmark` (`game/surprise_box_variants`). NOTE: `_coin_icon` is
  intentionally NOT used — the store now draws the dedicated `_coin_glyph`.
- **Harness primitives** (all pygame-only, both-target safe — gradients,
  polygons, `BLEND_ADD`/`BLEND_RGBA_MIN`/`BLEND_RGBA_MULT`, `PixelArray`,
  smoothscale; no numpy, no desktop-/browser-only API):
  - coin glyph: `_coin_glyph`
  - obsidian body + chip/button bodies: `_vgrad_panel`
  - shelf-light bar: `_shelf_bar`; gem (3-value cut + pip): `_gem`
  - legendary flourish: `_gold_leaf`; thumbnail disc: `_inset_disc`
  - unified chips: `_chip` / `_CHIP_STATES` / `_state_chip` / `_lock_glyph`
  - balance header: `_balance_header` (+ `_gradient_text`, `_drop_shadow`)
  - soft gold rule: `_gold_rule`; tab strip: `_tabstrip`
  - modal: `_modal`; tier callouts: `_big_card`; rarity reads:
    `_rarity_chip_row`; grayscale proof: `_grayscale` (PixelArray luma)
  - depth/glow: `_drop_shadow`, `_soft_glow`

All primitives use only standard pygame surface ops — nothing desktop- or
browser-only — so they port straight into the live store draw path.
