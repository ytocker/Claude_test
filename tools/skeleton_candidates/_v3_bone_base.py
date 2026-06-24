"""Shared bone-recoloured base for the v3 SKELETON candidates.

The v3 fix: instead of inventing skeleton proportions from scratch (the v2
`_make_prebuilt_skin` redraw, whose beak became a down-hook and whose tail swept
off the sprite edge), build the skeleton ON the REAL original parrot silhouette.

`_bone_parrot(angle)` recolours the actual `parrot._build_frame` geometry — via
`dollar_parrot_ghost._build_parrot_with_palette` — into a dark "flesh" bird whose
BEAK and TAIL sit at their original locations/shapes. Each candidate then wraps it
with `store_skins._make_skin(paint_fn, base_fn=_bone_parrot)` and paints the white
skeletal detail INSIDE that silhouette, so beak shape/location + tail location +
overall proportions all match Pip automatically.

Paint happens in COMPOSITE space = original sprite coords + (0, PARROT_DY=20):
- head centre  = (HX, HY)        = (47, 41)         crown top = CROWN_Y = 31
- body centre  = (32, 52)
- ORIGINAL beak quad (composite)  = (55,41)(61,44)(58,48)(52,46)
- ORIGINAL tail fan (composite)   ≈ x2–23, y44–62  (fans left-and-down)
- ORIGINAL feet (composite)       = (28,65)->(26,69) and (34,65)->(36,69)

Scratch only — never registered in `store_skins.BUILDERS`.
"""
from game.store_skins import HX, HY, CROWN_Y, PARROT_DY  # noqa: F401 (re-export)
from game.dollar_parrot_ghost import _pal, _build_parrot_with_palette


# ── bone palette ─────────────────────────────────────────────────────────────
# White bone is the brightest element; the bird "flesh" is recoloured near-black
# so the painted skeleton reads as bright bone on a dark void (design_1's value
# split). The BEAK and FEET are recoloured to bone directly so the original-
# location bill + leg bones read skeletal without any extra paint; the dark body/
# head/wing/tail are the void the painter traces white bone onto.
_FLESH    = (24, 26, 32)          # near-black flesh
_FLESH_D  = (13, 14, 19)          # deepest flesh / shadow
_FLESH_H  = (33, 36, 45)          # faint flesh form
_BONE     = (236, 238, 244)       # bone (base beak/feet)
_BONE_KEY = (92, 96, 110)         # cool bone keyline edge

P_BONE = _pal(
    # Tail: dark fan at the ORIGINAL location, faint bone edge lines — the
    # painter lays white tail-feather bone(s) on top.
    tail=[(28, 30, 38), (24, 26, 33), (20, 22, 28), (16, 18, 24)],
    tail_line=_BONE_KEY,
    body_shadow=_FLESH_D,
    body_main=_FLESH,
    body_chest=_FLESH_H,
    body_belly=(20, 22, 28),
    sheen=None,
    wing_main=_FLESH,
    wing_dark=_FLESH_D,
    wing_tip=(38, 41, 50),
    wing_secondary=None,
    wing_highlight=None,
    head_shadow=_FLESH_D,
    head_main=_FLESH,
    head_cheek=_FLESH_H,
    head_crown=_FLESH_H,
    # Lenses are not drawn (draw_lenses=False) — neutral fillers.
    lens_frame=_FLESH, lens_body=_FLESH_D, lens_tint=None, lens_glint=None,
    # Beak recoloured to bone at its ORIGINAL shape/location.
    beak_main=_BONE, beak_dark=_BONE_KEY, beak_gloss=(255, 255, 255),
    # Feet recoloured to bone — the original leg lines read as leg bones.
    foot=_BONE,
)


def _bone_parrot(angle_deg):
    """The original Pip silhouette recoloured to dark bone-flesh, no aviators —
    the skull face is the painter's; the beak/tail/feet keep their real geometry."""
    return _build_parrot_with_palette(angle_deg, P_BONE, draw_lenses=False)
