# Skybit — Costume Category Reference

Everything about the **COSTUMES** store tab: current roster, rarity system,
design history per skin, and tooling notes.

---

## Current Roster

14 skins in the `costume` group, ordered by price.

| ID | Display Name | Cost | Tier | Builder |
|----|--------------|-----:|------|---------|
| `skin_pirate` | PIRATE | 280 | common | `get_pirate_parrot` |
| `skin_cowboy` | COWBOY | 320 | common | `get_cowboy_parrot` |
| `skin_pharaoh` | PHARAOH | 380 | common | `get_pharaoh_parrot` |
| `skin_crown` | CROWN | 450 | common | `get_crown_parrot` |
| `skin_tophat` | GENTLEMAN | 520 | rare | `get_tophat_redraw` |
| `skin_ninja` | NINJA | 560 | rare | `get_ninja_parrot` |
| `skin_viking` | VIKING | 600 | rare | `get_viking_parrot` |
| `skin_wizard` | WIZARD | 720 | rare | `get_wizard_parrot` |
| `skin_baseball` | BASEBALL | 950 | epic | `get_baseball_parrot` |
| `skin_basketball` | BASKETBALL | 950 | epic | `get_basketball_parrot` |
| `skin_tennis` | TENNIS | 1000 | epic | `get_tennis_parrot` |
| `skin_mummy` | MUMMY | 1100 | epic | `get_mummy_parrot` |
| `skin_pilot` | CAPTAIN | 2200 | legendary | `get_pilot_parrot` |
| `skin_astronaut` | ASTRONAUT | 2600 | legendary | `get_astronaut_parrot` |

All builders are registered in `game/store_skins.py → BUILDERS`.

---

## Rarity System

Rarity is computed purely from price in `game/store_catalog.py`. No explicit tier
field exists in the catalog — the `rarity()` function derives it from `_RARITY_BANDS`:

```python
_RARITY_BANDS = ((500, "common"), (900, "rare"), (2000, "epic"))
# anything >= 2000 returns "legendary"
```

| Tier | Price range | Card outline colour |
|------|-------------|---------------------|
| common | < 500 | gray |
| rare | 500 – 899 | blue |
| epic | 900 – 1 999 | purple |
| legendary | >= 2 000 | orange |

**Tier calibration rationale:**
- **Common** (PIRATE, COWBOY, PHARAOH, CROWN): entry-level costumes reachable in a
  few good runs.
- **Rare** (GENTLEMAN, NINJA, VIKING, WIZARD): mid-range character archetypes,
  short-term grind goals.
- **Epic** (BASEBALL, BASKETBALL, TENNIS, MUMMY): sports skins land together so no
  sport feels arbitrarily cheap against another; MUMMY grouped here as the Egyptian
  companion piece.
- **Legendary** (CAPTAIN, ASTRONAUT): the two deepest-designed showpieces, reserved
  for players who have been grinding hard.

---

## Skins Reclassified to Parrot Group

Three skins were moved from `group: "costume"` to `group: "parrot"` because they are
full-body recolours of the macaw, not layered costume objects on top of the base bird:

| ID | Display Name | Cost | Reason |
|----|--------------|-----:|--------|
| `skin_skeleton` | SKELETON | 300 | Full-body bone recolour |
| `skin_zombie` | ZOMBIE | 480 | Full-body recolour |
| `skin_disco` | DISCO | 800 | Full-body palette shift; costume redesign attempted but abandoned |

---

## Design History

Every skin that was explored, created, or redesigned. Scratch builders live under
`tools/<item>_candidates/`; comparison figures under `docs/store_redesign/costume/<item>/`.

### PIRATE
- **Status**: redesigned
- **Concepts explored**: 5 (skull-and-crossbones buccaneer, golden-age privateer,
  Caribbean governor, naval officer, ghost ship captain)
- **Design rounds**: 3
- **Key tells in final build**: tricorn hat, peg leg, cutlass scabbard, eyepatch
- **Files**: `tools/pirate_candidates/design_1..5.py`
- **Comparison**: `docs/store_redesign/costume/pirate/final_comparison.png`

### GENTLEMAN (`skin_tophat`)
- **Status**: redesigned
- **Concepts explored**: 5 Victorian-era gentleman archetypes
- **Design rounds**: 2
- **Key tells in final build**: top hat, monocle, waistcoat, pocket-watch chain
- **Files**: `tools/tophat_candidates/design_1..5.py`
- **Comparison**: `docs/store_redesign/costume/tophat/final_comparison.png`

### PHARAOH
- **Status**: redesigned — most iterated skin; went through 3 full re-roll campaigns
- **Concepts explored**: 15 across v1/v2/v3
- **Design rounds**: 6+ across all campaigns
- **Key tells in final build**: nemes headcloth, crook and flail, gold collar, cartouche
- **Files**: `tools/pharaoh_candidates/design_1..5.py`
- **Comparisons**: `docs/store_redesign/costume/pharaoh/` (v1, v2, v3 figures)

### MUMMY — new item
- **Status**: new skin, created as a companion to the pharaoh exploration
- **Concept**: decaying bandage wrappings over the macaw silhouette; hollow glowing eyes
- **Implementation**: inlined directly into `game/store_skins.py` in a single pass
  (no candidates folder)

### NINJA
- **Status**: redesigned
- **Concepts explored**: 5 (SHADOWSTRIKE, CRIMSON FANG, IRON RONIN, SMOKE PHANTOM,
  NEON SEVER)
- **Design rounds**: 3
- **Key tells in final build**: hood, mask, shuriken on belt, katana scabbard
- **Files**: `tools/ninja_candidates/design_1..5.py`
- **Comparison**: `docs/store_redesign/costume/ninja/final_comparison.png`

### VIKING
- **Status**: redesigned
- **Concepts explored**: 5 main concepts + 5 face-detail variants
- **Design rounds**: 2 main + 1 face pass
- **Key tells in final build**: horned helmet, axe, fur cloak, braided beard
- **Files**: `tools/viking_candidates/design_1..5.py`,
  `tools/viking_face_candidates/design_1..5.py`
- **Comparison**: `docs/store_redesign/costume/viking/final_comparison.png`

### COWBOY
- **Status**: pre-existing, not redesigned in this effort

### CROWN
- **Status**: pre-existing, not redesigned in this effort

### WIZARD
- **Status**: pre-existing, not redesigned in this effort

### BASEBALL / BASKETBALL
- **Status**: designed as part of a sports batch
- **Concepts explored**: 5 per sport (10 total)
- **Design rounds**: 2 + one additional polish pass across all sports
- **Key tells (baseball)**: batting helmet, jersey number, cleats, bat under wing
- **Key tells (basketball)**: headband, jersey stripe, high-tops
- **Files**: `tools/sports_candidates/design_1..5.py`, `tools/basketball_candidates/design_1..5.py`
- **Comparison**: `docs/store_redesign/costume/sports/final_comparison.png`

### TENNIS
- **Status**: dedicated redesign after the sports batch
- **Concepts explored**: 5
- **Design rounds**: 2
- **Winner**: Wimbledon Whites — pristine all-white kit with bright lime ball accent
- **Key tells in final build**: white cap visor, white polo collar, racquet under wing,
  lime ball
- **Files**: `tools/tennis_candidates/design_1..5.py`
- **Comparison**: `docs/store_redesign/costume/tennis/final_comparison.png`

### ASTRONAUT
- **Status**: redesigned (deepest exploration among all costumes: 8 candidates, 2
  comparison figures)
- **Concepts explored**: 8 across two campaigns
- **Design rounds**: 4+
- **Key tells in final build**: EVA helmet dome, gold visor, pressurised suit,
  mission patch on shoulder
- **Files**: `tools/astronaut_candidates/design_1..8.py`
- **Comparisons**: `docs/store_redesign/costume/astronaut/final_comparison.png`,
  `docs/store_redesign/costume/astronaut/v2_comparison.png`

### CAPTAIN (`skin_pilot`) — new item
- **Status**: new skin, added to production
- **Concepts explored**: 5 (THE CAPTAIN, ACE, RED BARON, VIPER, BUSH RUNNER)
- **Design rounds**: 2
- **Winner**: THE CAPTAIN — golden-age airline commander
- **Key tells**: peaked officer's cap with gold cap-badge wings, double-breasted navy
  jacket, four gold sleeve stripes on the wing that animate with each flap, white
  shirt-front + dark tie
- **Palette**: `#14213D` navy / `#F4F1EA` shirt-white / `#F5C542` badge-gold /
  `#0B0F1C` patent-black
- **Files**: `tools/pilot_candidates/design_1..5.py`
- **Comparison**: `docs/store_redesign/costume/pilot/final_comparison.png`

### DISCO — redesign abandoned
- **Status**: moved to `group: "parrot"`; redesign attempted and abandoned after 6
  rounds. The BOOGIE NIGHTS concept (afro, bell-bottom cuff, leisure-suit jacket, gold
  medallion) encountered persistent anatomy-positioning issues and was not shipped.
  The skin remains the original full-body palette shift.
- **Scratch builders**: `tools/disco_candidates/design_1..5.py` (exploration only)

### SKELETON / ZOMBIE
- **Status**: redesigned but reclassified — exploration concluded they are full-body
  recolours, not layered costumes; moved to `group: "parrot"`
- **Files**: `tools/skeleton_candidates/`, `tools/zombie_candidates/`,
  `docs/store_redesign/costume/skeleton/`, `docs/store_redesign/costume/zombie/`

---

## Capture Tools

| Tool | Output | Command |
|------|--------|---------|
| `tools/capture_store_figures.py` | `store_overview.png` (all pages side-by-side) + `gameplay_items.png` (each costume on Pip mid-flight) | `SDL_VIDEODRIVER=dummy python tools/capture_store_figures.py` |
| `tools/render_costumes_all.py` | `docs/store_redesign/all_costumes.png` (5x3 grid of all costumes in gameplay) | `SDL_VIDEODRIVER=dummy python tools/render_costumes_all.py` |

Individual store-page screenshots are saved to `docs/store_redesign/costume/pages/page_N_of_M.png`
by an inline script. **Important**: `StoreScene` defaults to `view="hub"` (the lagoon
stall-picker). Always set `app.store.view = "category"` before rendering to get the
item-card grid the player actually sees after tapping a stall.

---

## Adding a New Costume

1. Write a builder in `game/store_skins.py` and add it to `BUILDERS`.
2. Add a catalog entry to `game/store_catalog.py → CATALOG`:
   `{"name": "...", "cost": N, "kind": "skin", "group": "costume"}`.
3. Run `python -m pytest tests/` — `test_every_skin_resolves_in_renderer` will catch
   any mismatch between the catalog and BUILDERS.
4. Regenerate store screenshots with `tools/capture_store_figures.py`.
