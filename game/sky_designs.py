"""
Dormant registry over the 10 biome sky designs.

A single catalog behind one signature — `render(surf, w, h, ground_y, palette,
phase)` — so a future caller can swap the live sky for any of these designs with
one line. Each design carries its OWN per-biome day/night palette (via its
keyframes) and keys off `phase` (0..1) — the same phase the live biome clock
already produces — so it ignores the live `palette` argument entirely.

NOTE: this module is preview-only. Nothing on the live render path imports it,
exactly like `game/dollar_variants.py` and `game/surprise_box_variants.py`. It
stays inert until someone deliberately sets `ACTIVE_SKY_DESIGN`; while that is
`None`, `render_active` short-circuits to `False` before touching the surface so
gameplay is unchanged.
"""
from game.biome_sky import paint_sky
from game.biome_sky_keyframes import BIOMES, BIOME_NAMES, BIOME_NOTES


# The dormant switch. Set to a CATALOG design id to make that sky active; while
# None the registry contributes nothing to the live render path.
ACTIVE_SKY_DESIGN = None


def _make_render(design_id):
    """Bind one biome spec into the shared render signature. Designs supply
    their own palette, so the live `palette` arg is intentionally ignored."""
    spec = BIOMES[design_id]

    def render(surf, w, h, ground_y, palette, phase):
        paint_sky(surf, spec, w, h, phase, stars=True, ground_y=ground_y)

    return render


def render(surf, w, h, ground_y, palette, phase):
    """Render the currently-active design's sky. Caller must ensure
    `ACTIVE_SKY_DESIGN` is set; use `render_active` for the guarded form."""
    _CATALOG_BY_ID[ACTIVE_SKY_DESIGN](surf, w, h, ground_y, palette, phase)


# (design_id, human_name, note, render_fn) for the 10 biome designs, sheet order.
CATALOG = [
    (bid, BIOME_NAMES[bid], BIOME_NOTES[bid], _make_render(bid))
    for bid in BIOMES
]

_CATALOG_BY_ID = {bid: fn for bid, _name, _note, fn in CATALOG}


def render_active(surf, w, h, ground_y, palette, phase) -> bool:
    """Render the active design if one is selected. Returns True when a design
    painted the sky, False (without touching `surf`) when the registry is
    dormant — so a live caller can fall through to the existing sky path."""
    if ACTIVE_SKY_DESIGN is None:
        return False
    fn = _CATALOG_BY_ID.get(ACTIVE_SKY_DESIGN)
    if fn is None:
        return False
    fn(surf, w, h, ground_y, palette, phase)
    return True
