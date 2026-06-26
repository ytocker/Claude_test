"""DESIGN 4 — THE MUMMY: the bandaged risen king (scratch exploration).

Value-inverted from the gold/black pharaoh concepts: a pale linen-wrapped
bird whose only colour notes are a deep-blue scarab amulet on the chest, a
slim gold brow-band, and faint glowing eye-pinpoints in the hollow sockets.
The body palette re-plumages the whole macaw to aged cream so the costume can
paint over it as overlapping horizontal BANDAGE BANDS (cream main, grey-grime
seams) — the bird reads as wrapped, not just recoloured.

Footprint discipline (gameplay hitbox is a fixed ~10px circle): every body
element — bands, scarab, slung bandage end, frayed foot tips — stays WITHIN
the base bird footprint; nothing dips below the feet line (~HY+24..28) and
nothing balloons the body. Only the head-wrap + one flicking bandage tail
rise above CROWN_Y.

Scratch only — NOT registered in store_skins.BUILDERS.
"""
import pygame

from game import store_skins
from game.store_skins import HX, HY, CROWN_Y, _poly
from game.dollar_parrot_ghost import _pal, _build_parrot_with_palette


# ── colour constants ─────────────────────────────────────────────────────────
# Three linen values (band body / seam shadow / grime) carry the wrap texture;
# the deep-blue scarab + gold band are the two lone colour splashes, and the
# socket void + faint amber pinpoint own the hollow-eye horror tell.
_MU_LINEN    = (237, 228, 207)     # #EDE4CF aged linen band body
_MU_LINEN_H  = (250, 244, 228)     # brightest linen highlight (top of a band)
_MU_SEAM     = (200, 182, 144)     # #C8B690 shadow seam between bands
_MU_GRIME    = (138, 122, 85)      # #8A7A55 grime in the deepest folds
_MU_BLUE     = (30, 95, 176)       # #1E5FB0 scarab glazed blue
_MU_BLUE_D   = (18, 60, 120)       # scarab shadow / carapace seams
_MU_BLUE_H   = (96, 168, 240)      # scarab glaze highlight (night glow core)
_MU_GOLD     = (232, 181, 58)      # #E8B53A gold brow-band
_MU_GOLD_H   = (255, 232, 150)     # gold glint
_MU_VOID     = (24, 22, 24)        # sunken eye-socket void
_MU_PIN      = (255, 196, 120)     # warm amber eye-pinpoint (the alive note)


# Aged-cream re-plumage of the whole macaw so the costume paints bandage bands
# over it. Every slot is a linen value; the seam tone does the line work; the
# beak is bleached bone so nothing warm survives, and lenses are dropped so the
# hollow sockets own the face.
_MU_BODY = _pal(
    tail=[(200, 188, 162), (214, 202, 176), (226, 215, 190), (237, 228, 207)],
    tail_line=_MU_GRIME,
    body_shadow=(198, 184, 154),
    body_main=_MU_LINEN,
    body_chest=(244, 236, 216),
    body_belly=(228, 218, 196),
    sheen=(255, 252, 244, 70),
    wing_main=(224, 214, 188),
    wing_dark=_MU_SEAM,
    wing_tip=(244, 236, 216),
    wing_secondary=None,
    wing_highlight=_MU_LINEN_H,
    head_shadow=(198, 184, 154),
    head_main=_MU_LINEN,
    head_cheek=(240, 232, 212),
    head_crown=(232, 222, 200),
    lens_frame=(210, 198, 170),
    lens_body=_MU_VOID,
    lens_tint=None,
    lens_glint=None,
    beak_main=(214, 204, 178),
    beak_dark=(168, 152, 116),
    beak_gloss=(240, 232, 212),
    foot=(196, 182, 150),
)


_MU_RIM = (120, 106, 72)           # darker-linen rim on the OUTER body contour


def _mu_base(angle_deg):
    # Linen-cream bird, no aviators — the sunken hollow sockets own the head.
    body = _build_parrot_with_palette(angle_deg, _MU_BODY, draw_lenses=False)
    # The cream body sits at near-identical VALUE to the bright day sky, so the
    # left wing / tail / head-dome edge dissolves at 40px. A darker-linen rim
    # hugging the OUTER silhouette (drawn UNDER the body so it shows only as a
    # 1px edge, never over the interior bands) gives the day read an edge to
    # hold without touching the night structure.
    return _rim_outer(body, _MU_RIM)


def _rim_outer(src, color):
    """Stamp a 1px `color` rim hugging the source silhouette's OUTER edge by
    growing the alpha mask one pixel and laying the original sprite back on
    top — only the contour ring survives, never the interior."""
    w, h = src.get_size()
    out = pygame.Surface((w, h), pygame.SRCALPHA)
    mask = pygame.mask.from_surface(src, threshold=8)
    ring = mask.to_surface(setcolor=color, unsetcolor=(0, 0, 0, 0))
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        out.blit(ring, (dx, dy))
    out.blit(src, (0, 0))
    return out


def _band(surf, y, x0, x1, dip=0):
    """One horizontal bandage band wrapping the body: a grime seam under a
    cream strip with a top highlight, the ends pinched so the wrap reads as
    cloth crossing the body, not a flat stripe. `dip` slants the band to follow
    the chest curve so the stack reads as wound linen."""
    pygame.draw.line(surf, _MU_GRIME, (x0, y + 2), (x1, y + 2 + dip), 4)
    pygame.draw.line(surf, _MU_SEAM, (x0, y + 1), (x1, y + 1 + dip), 4)
    pygame.draw.line(surf, _MU_LINEN, (x0, y), (x1, y + dip), 3)
    pygame.draw.line(surf, _MU_LINEN_H, (x0 + 1, y - 1), (x1 - 2, y - 1 + dip), 1)


def _paint(surf, _a):
    # Body centre in composite space (parrot body centre (32,32) + PARROT_DY).
    BCX, BCY = 32, 52

    # ── Loose bandage end slung in the wing ──────────────────────────────────
    # Drawn FIRST so the body/bands cover its root and only the trailing strip
    # reads as a flapping end. It sweeps DOWN-and-back across the wing but is
    # pulled up well clear of the feet line — a mummy's unwound strip, tucked
    # inside the silhouette so it never enlarges the body or dangles past feet.
    le = [(BCX + 9, BCY - 2), (BCX + 17, BCY + 2), (BCX + 19, BCY + 8),
          (BCX + 15, BCY + 9), (BCX + 14, BCY + 4), (BCX + 7, BCY + 2)]
    _poly(surf, _MU_GRIME, [(x, y + 1) for x, y in le])
    _poly(surf, _MU_SEAM, le)
    _poly(surf, _MU_LINEN, [(BCX + 10, BCY - 1), (BCX + 16, BCY + 2),
                            (BCX + 17, BCY + 7), (BCX + 13, BCY + 7),
                            (BCX + 12, BCY + 3), (BCX + 8, BCY + 1)])
    pygame.draw.line(surf, _MU_LINEN_H, (BCX + 11, BCY), (BCX + 16, BCY + 3), 1)
    # Frayed tip ticks so the loose end reads as torn cloth, not a paddle.
    for fx, fy in ((BCX + 18, BCY + 8), (BCX + 16, BCY + 9), (BCX + 14, BCY + 9)):
        pygame.draw.line(surf, _MU_SEAM, (fx, fy), (fx + 1, fy + 2), 1)

    # ── Body wrap: overlapping horizontal bandage bands ──────────────────────
    # A clean stack of wide bands (3px cloth over a grime seam) crossing the
    # whole torso, slightly slanted to follow the chest so the bird reads as
    # WRAPPED. Kept few + wide so they survive the 40px downscale instead of
    # turning to 1px mud, and held strictly inside the body footprint.
    _band(surf, BCY - 9, BCX - 15, BCX + 13, dip=1)
    _band(surf, BCY - 4, BCX - 17, BCX + 15, dip=1)
    _band(surf, BCY + 1, BCX - 17, BCX + 16, dip=1)
    _band(surf, BCY + 6, BCX - 16, BCX + 15, dip=1)
    _band(surf, BCY + 11, BCX - 14, BCX + 13, dip=0)
    # Two short diagonal cross-wraps hint the ARMS-CROSSED mummy pose over the
    # chest — the classic folded-linen X without breaking the footprint.
    pygame.draw.line(surf, _MU_GRIME, (BCX - 11, BCY - 5), (BCX + 9, BCY + 9), 4)
    pygame.draw.line(surf, _MU_LINEN, (BCX - 11, BCY - 6), (BCX + 9, BCY + 8), 2)
    pygame.draw.line(surf, _MU_GRIME, (BCX + 9, BCY - 5), (BCX - 11, BCY + 9), 4)
    pygame.draw.line(surf, _MU_LINEN, (BCX + 9, BCY - 6), (BCX - 11, BCY + 8), 2)

    # ── Scarab amulet on the chest — the lone colour splash ──────────────────
    # A single large deep-blue glazed beetle dead-centre on the crossed wraps;
    # an oval carapace split by a centre seam, a small head node, and two leg
    # ticks, ringed in gold. On day the blue pops on cream; on night the glaze
    # highlight + gold ring keep it glowing.
    sx, sy = BCX - 1, BCY + 2
    pygame.draw.ellipse(surf, _MU_GOLD, (sx - 6, sy - 7, 13, 15))        # gold mount ring
    pygame.draw.ellipse(surf, _MU_BLUE_D, (sx - 5, sy - 6, 11, 13))
    pygame.draw.ellipse(surf, _MU_BLUE, (sx - 4, sy - 5, 9, 11))
    pygame.draw.line(surf, _MU_BLUE_D, (sx, sy - 5), (sx, sy + 6), 1)     # carapace seam
    pygame.draw.line(surf, _MU_BLUE_D, (sx - 4, sy - 1), (sx + 4, sy - 1), 1)
    pygame.draw.ellipse(surf, _MU_BLUE, (sx - 3, sy - 8, 7, 5))           # head node
    pygame.draw.ellipse(surf, _MU_BLUE_D, (sx - 3, sy - 8, 7, 5), 1)
    for lx in (sx - 6, sx + 5):                                           # leg ticks
        pygame.draw.line(surf, _MU_BLUE_D, (lx, sy - 2), (lx, sy + 4), 1)
    pygame.draw.circle(surf, _MU_BLUE_H, (sx - 2, sy - 3), 2)             # glaze glint / night-glow core
    pygame.draw.circle(surf, (220, 240, 255), (sx - 2, sy - 3), 1)
    pygame.draw.line(surf, _MU_GOLD_H, (sx - 5, sy - 6), (sx - 2, sy - 7), 1)

    # ── Wrapped feet with frayed tips AT the feet line ───────────────────────
    # Each foot is a small linen knot capped by torn ticks sitting ON the feet
    # line (~HY+24), never below it, so the bird stays its true size.
    for fx in (28, 35):
        pygame.draw.ellipse(surf, _MU_SEAM, (fx - 3, HY + 22, 7, 5))
        pygame.draw.ellipse(surf, _MU_LINEN, (fx - 3, HY + 21, 7, 4))
        pygame.draw.line(surf, _MU_LINEN_H, (fx - 2, HY + 21), (fx + 2, HY + 21), 1)
        for tx in (fx - 2, fx, fx + 2):
            pygame.draw.line(surf, _MU_SEAM, (tx, HY + 25), (tx, HY + 27), 1)

    # ── Head wrapped in linen ────────────────────────────────────────────────
    # A linen skull-wrap domes over the crown leaving a horizontal GAP where the
    # hollow eyes show — the horror/comedy tell. Wide cream bands with grime
    # seams keep the wrap reading as cloth at 40px.
    pygame.draw.ellipse(surf, _MU_SEAM, (HX - 13, CROWN_Y - 4, 27, 24))
    pygame.draw.ellipse(surf, _MU_LINEN, (HX - 12, CROWN_Y - 3, 25, 22))
    # Wrap seams arcing over the skull-cap.
    for wy in (CROWN_Y, CROWN_Y + 4, CROWN_Y + 8):
        pygame.draw.line(surf, _MU_SEAM, (HX - 11, wy), (HX + 12, wy - 1), 1)
    pygame.draw.ellipse(surf, _MU_LINEN_H, (HX - 7, CROWN_Y - 2, 11, 4))

    # Slim GOLD brow-band across the wrap — the one metallic note up top. Dropped
    # 1px so it sits in the wrap shadow (not the bright highlight crest) and the
    # solid 3px _MU_GOLD stays a hard horizontal gold line at 40px on day; the
    # glint is a thin secondary so gold, not the pale glint, dominates.
    pygame.draw.line(surf, _MU_GOLD, (HX - 12, CROWN_Y + 7), (HX + 13, CROWN_Y + 6), 3)
    pygame.draw.line(surf, _MU_GOLD_H, (HX - 9, CROWN_Y + 6), (HX + 3, CROWN_Y + 6), 1)

    # One bandage tail flicking UP off the back of the wrap, into open sky above
    # CROWN_Y — the only element (with the wrap) allowed to break upward.
    tail = [(HX - 9, CROWN_Y - 1), (HX - 14, CROWN_Y - 8),
            (HX - 11, CROWN_Y - 9), (HX - 6, CROWN_Y - 2)]
    _poly(surf, _MU_SEAM, tail)
    pygame.draw.line(surf, _MU_LINEN, (HX - 9, CROWN_Y - 2), (HX - 12, CROWN_Y - 8), 2)
    pygame.draw.line(surf, _MU_LINEN_H, (HX - 9, CROWN_Y - 2), (HX - 11, CROWN_Y - 6), 1)

    # ── Face: a gap in the wrap with two sunken hollow eyes ───────────────────
    # A dark wrap-gap band crosses the face; inside it sit two hollow sockets —
    # dark voids each with a faint amber pinpoint glow so the mummy reads as
    # alive-but-dead on both day and night (the pinpoint is the night tell).
    pygame.draw.rect(surf, _MU_GRIME, (HX - 8, HY - 4, 24, 8), border_radius=3)
    # Two sockets, spaced ~1px wider apart, with a NEAR-BLACK dominant fill so
    # at 40px they survive as TWO distinct dark dots instead of merging with the
    # grime wrap-gap band into one smear.
    for ex in (HX - 1, HX + 10):
        pygame.draw.circle(surf, (8, 7, 9), (ex, HY), 4)
        pygame.draw.circle(surf, (8, 7, 9), (ex, HY + 1), 4)
        pygame.draw.circle(surf, _MU_VOID, (ex, HY - 2), 2)   # faint upper rim of the hollow
        pygame.draw.circle(surf, _MU_PIN, (ex, HY), 1)        # inner pinpoint glow
    # A torn upper-wrap edge over the eyes so the gap reads as unravelled cloth.
    pygame.draw.line(surf, _MU_LINEN, (HX - 8, HY - 4), (HX + 15, HY - 5), 2)
    pygame.draw.line(surf, _MU_SEAM, (HX - 7, HY + 4), (HX + 14, HY + 4), 1)


build = store_skins._make_skin(_paint, base_fn=_mu_base)
