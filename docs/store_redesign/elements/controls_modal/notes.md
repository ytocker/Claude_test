# CONSTELLATION store — CONTROLS + BUY MODAL (round 1)

Element 8 of 8. Covers the action/nav chrome: the **BACK pill**, the
`< PAGE 1/3 >` **page controls**, and the buy-confirmation **MODAL**. Built on
the locked `constellation_hi/render_hi.py` pipeline (SS = 4 author canvas, one
smoothscale down) and its material primitives — `vgrad`, `bevel_rim`,
`gloss_sweep`, `drop_shadow`, `coin_glyph`, `cabochon`, `facet_gem`,
faux-bold type — so this reads as the same screen as its siblings. Real epic
item used throughout: **skin_phoenix** (PHOENIX, epic, 1,500).

Render: `python render.py` → `round_1.png`. Pure pygame, both targets safe.

## Shared chrome (top row)
- **BACK pill** — fully-rounded premium pill with a left chevron, the locked
  defined edge (dark outer keyline UNDER a bright top-left gold bevel), top
  gloss + bottom-right AO. Shown in both finishes: the default dark-indigo
  gradient (quiet, sits at the store's bottom margin) and an optional warm-gold
  finish. Generous bottom margin is expressed by the caller's placement.
- **Page controls** — `< PAGE n/total >` with a loud gold-pale label flanked by
  two beveled arrow buttons sized ~40×30 logical (≈ a 44px physical tap target,
  per Apple/Material), each double-rimmed and lit top-left. Two spreads shown.

## Modal hierarchy (shared across all variants)
~70% flat dark scrim → panel with a **defined double-gold edge** (bevel + a
concentric inset gold rule) → heading "CONFIRM PURCHASE" + soft gold rule →
glass-cabochon stage with the rarity gem **seated ON the dome rim** (centre on
the bezel circle, never floating) → item NAME (bold) → rarity word → a single
**single-gradient gold** price chip (per THEME directive) → BUY / CANCEL row.
BUY is the primary CTA (right side per CTA convention): bright gold body, gloss
sweep, outer halo + subtle inner top glow, dark label. CANCEL is one value step
lighter than the panel (slate) so it's clearly separate but never competes.
≥8px gap between buttons. Nothing clipped or cramped.

## Variants (pick one panel/CTA treatment)
- **V1 ROYAL** — canonical centered panel, symmetric equal-width BUY/CANCEL
  pair. Cleanest, most neutral; the safe default.
- **V2 WEIGHTED** — CTA-best-practice 60/40 row (BUY dominant, CANCEL a quiet
  40% pill), heading on a recessed gold ribbon plate, BUY carries a coin glyph
  for an explicit "spend" read. Most commercially aggressive.
- **V3 CABOCHON-FORWARD** — enlarged/raised hero dome (R 50 vs 44), gem seated
  higher on the rim, gold-bevel-wordmark heading, and a faint footer rule that
  turns the action zone into a distinct shelf. Most "hero item" feel.

Review PNG is 392 KB under `docs/` — clear of the 5 MB CI ceiling and excluded
from the shipped bundle.

Sources (CTA / modal conventions): LogRocket CTA best practices; DesignStudio
CTA UX; Apple HIG / Material 44px tap target + 8px separation guidance.
