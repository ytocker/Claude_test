"""design_2 · JADE-CARVING MACAW — EPIC parrot-wave2 exploration (scratch only).

A cool museum-object Pip: the whole bird re-plumaged as one piece of polished
translucent nephrite, finished by a tail re-cut into a single bold RUYI
cloud-scroll — the auspicious comma/spiral whose hooked tip jets up and out
past the tail silhouette like the carved tip of a jade pendant. That scroll is
the read; everything else (relief grooves moulding the body as sculpted stone,
one cinnabar seal-mark, smoky-jade aviators) supports it.

North star is "lives or dies at 40px". The signature is bought as VALUE on a
warm-leaning mint stone, NOT as glass: a darker carve-groove line paired with a
pale mint rim is the one contrast that survives downscale, and the ruyi tip is
edged with a single cinnabar-red lacquer line so the warm pop separates the
scroll from the cool body on both day and night sky. Deliberately the opposite
of GLASS (no panes, no lead, no back-light) and of ICE (warm mint, not cold
blue) so the carved-stone read is unmistakable.

The cloud-scroll paints OVER the body's existing tail — it EXTENDS the tail
silhouette rather than sitting behind the body — so no back-layer is needed and
the standard _make_skin (body → paint_fn → outline) compose order holds.

Exploration only — NEVER registered in store_skins.BUILDERS.
"""
import math

import pygame

from game import store_skins
from game.store_skins import HX, HY, CROWN_Y
from game.dollar_parrot_ghost import _pal, _build_parrot_with_palette


# ── palette (brief) ───────────────────────────────────────────────────────────
# Warm-leaning milky jade, NOT cold ice-blue: the body green carries a touch of
# yellow so it reads as nephrite stone, and every bright is the pale-mint POLISH
# highlight (the one sub-white that sells carved stone catching light). Value is
# carried by GROOVE_DK — a near-black teal that lines every relief cut — paired
# against MINT, because dark-cut + pale-rim is the contrast that holds at 40px.
# Cinnabar is the lone warm note, reserved for the scroll edge + the seal-mark.
_JADE      = (95, 181, 140)        # #5FB58C jade body
_JADE_DK   = (46, 110, 85)         # #2E6E55 deep jade shadow
_MINT      = (207, 240, 220)       # #CFF0DC mint polish highlight
_CINNABAR  = (200, 54, 43)         # #C8362B cinnabar accent
_CINNAB_D  = (150, 34, 28)         # cinnabar shadow (seal/scroll under-edge)
_GROOVE_DK = (26, 58, 48)          # #1A3A30 carve-groove dark (the value)
_JADE_MID  = (70, 148, 114)        # mid jade — between body and shadow


# Full nephrite re-plumage. The body is milky warm-green with a genuinely dark
# teal-jade shadow owning the line work so the stone already carries a dark→
# light gradient before the overlay cuts grooves into it; the polish highlight
# rides the crown/chest/belly so the carving reads as catching a single light.
# Aviators RETAINED, retinted smoky jade (Pip's signature stays) — the scroll
# tail owns the silhouette so the glasses can stay on the face. Beak goes a
# pale carved-jade so nothing warm survives except the one cinnabar seal.
P_JADE = _pal(
    tail=[(40, 96, 74), (58, 130, 100), (84, 166, 128), (140, 200, 170)],
    tail_line=_GROOVE_DK,
    body_shadow=(40, 100, 78),         # deep so the stone underside reads dark
    body_main=_JADE,
    body_chest=(150, 212, 178),
    body_belly=(120, 196, 158),
    sheen=(220, 248, 232, 150),        # pale-mint polished sheen on the chest
    wing_main=(78, 160, 122),
    wing_dark=_JADE_DK,
    wing_tip=(168, 218, 188),
    wing_secondary=None,               # one-stone read — no contrast feather
    wing_highlight=_MINT,
    head_shadow=(40, 100, 78),
    head_main=_JADE,
    head_cheek=(150, 212, 178),
    head_crown=(168, 218, 188),
    lens_frame=(150, 200, 176),        # pale-jade frame so the carving catches light
    lens_body=(22, 50, 42),            # smoky-jade lens body
    lens_tint=(90, 170, 140, 130),     # smoky-jade tint band
    lens_glint=(218, 246, 230),        # mint glint
    beak_main=(150, 200, 170),
    beak_dark=_JADE_DK,
    beak_gloss=_MINT,
    foot=(60, 120, 96),
)


# ── shared carving helpers ────────────────────────────────────────────────────

def _groove(surf, pts):
    """One carved relief groove: a dark cut line with a pale-mint rim riding just
    ABOVE it, so the pairing reads as a bevel chiselled into stone (light catching
    the upper lip of the cut) rather than a flat drawn scratch. Dark-cut + pale-
    rim is the one value contrast that survives the 40px downscale, so it is the
    grammar repeated for every groove."""
    pygame.draw.lines(surf, _GROOVE_DK, False, pts, 2)
    rim = [(x, y - 1) for x, y in pts]
    pygame.draw.lines(surf, _MINT, False, rim, 1)


def _ruyi_scroll(surf, ox, oy, sway):
    """The hero: the tail-fan re-cut into a single bold RUYI cloud-scroll — a fat
    comma whose body sweeps down-back off the tail root then HOOKS up and out into
    open sky, the tip spiralling inward into the auspicious cloud-head. It extends
    the existing tail silhouette so it breaks the egg with a shape no other skin
    has. The whole comma is built as ONE log-spiral spine (so the curve tightens
    smoothly into the cloud-head with no detached blob), sculpted in three values
    (deep jade core → jade body → mint rim-light on the outer/leading edge) and
    edged with ONE cinnabar lacquer line in the inner throat so a warm pop lifts
    the scroll off the cool body on every sky. `sway` flexes the hook a touch with
    the wing beat so the baked stone still feels alive across the 4 frames."""
    # The comma spine as a single cubic Bézier: it leaves the tail root sweeping
    # DOWN-and-back into open sky, then curves UP-and-out past the tail line, the
    # control points pulling the far end back inward so the tip hooks toward the
    # body — the auspicious ruyi cloud-head, drawn as ONE open curve (no full
    # revolution, so the ribbon never wraps behind the body or self-intersects).
    p0 = (ox + 1,  oy + 1)          # tail root
    p1 = (ox - 17, oy + 13)         # pull down-back: the belly of the comma
    p2 = (ox - 34, oy - 12 + sway)  # pull up-out past the tail silhouette
    p3 = (ox - 19, oy - 21 + sway)  # hook the tip back inward (cloud-head)
    n = 30
    spine = []
    for i in range(n + 1):
        t = i / n
        u = 1 - t
        x = (u**3 * p0[0] + 3 * u*u*t * p1[0] + 3 * u*t*t * p2[0] + t**3 * p3[0])
        y = (u**3 * p0[1] + 3 * u*u*t * p1[1] + 3 * u*t*t * p2[1] + t**3 * p3[1])
        spine.append((x, y))

    # Ribbon body — perpendicular offset tapering from a fat root to a fine tip,
    # so the scroll reads as a solid carved volume, not a stroke. Built as a
    # filled polygon (outer edge + inner edge) in three value passes.
    outer, inner = [], []
    for i, (x, y) in enumerate(spine):
        t = i / n
        if i == 0:
            dx, dy = spine[1][0] - x, spine[1][1] - y
        elif i == n:
            dx, dy = x - spine[-2][0], y - spine[-2][1]
        else:
            dx, dy = spine[i + 1][0] - spine[i - 1][0], spine[i + 1][1] - spine[i - 1][1]
        L = math.hypot(dx, dy) or 1.0
        px, py = -dy / L, dx / L
        hw = 6.0 * (1.0 - t) ** 0.7 + 1.8                 # fat root → rounded tip
        outer.append((x + px * hw, y + py * hw))
        inner.append((x - px * hw, y - py * hw))
    body_poly = outer + inner[::-1]

    # deep core (the recessed underside of the carving)
    pygame.draw.polygon(surf, _JADE_DK, [(x, y + 1) for x, y in body_poly])
    # jade body fill
    pygame.draw.polygon(surf, _JADE, body_poly)
    # mint rim-light down the OUTER (leading) edge — the polished stone catching
    # light; 2px near the root so it survives downscale, thinning toward the tip.
    pygame.draw.lines(surf, _MINT, False, outer[:24], 2)
    # deep groove down the INNER edge so the volume reads as a thick scroll and the
    # cloud-head's hollow is a real carved recess.
    pygame.draw.lines(surf, _GROOVE_DK, False, inner, 1)
    # bright mint dot capping the very tip of the cloud-head curl.
    pygame.draw.circle(surf, _MINT, (int(spine[-1][0]), int(spine[-1][1])), 1)

    # ONE cinnabar lacquer line inlaid down the spine of the hooked cloud-head —
    # the single warm note that lifts the cool scroll off the cool body on both
    # skies. Run along the SPINE of the tip so a sliver of jade edges it on both
    # sides (an inlaid red band, not a recolour of the whole tip), seated where the
    # hook breaks the silhouette so the warm pop carries the read at 40px.
    pygame.draw.lines(surf, _CINNAB_D, False, [(x, y + 1) for x, y in spine[19:30]], 3)
    pygame.draw.lines(surf, _CINNABAR, False, spine[19:30], 2)


# ── front overlay: grooves, seal-mark, scroll tail, relit aviators ────────────

def _paint_jade(surf, wing_angle_deg):
    # Tail-hook flexes a touch with the wing beat so the carved scroll still feels
    # alive; the base wing angles run negative-on-downbeat so a share reads as the
    # cloud-tail trailing the dive.
    sway = wing_angle_deg * 0.04

    # 1 · HERO — the ruyi cloud-scroll, painted OVER the body's tail root so it
    #     EXTENDS the tail (no back-layer). Rooted at the existing tail mass
    #     (~(10,55) in composite space) so the carving grows out of the bird.
    _ruyi_scroll(surf, 13, 52, sway)

    # 2 · BODY RELIEF GROOVES — 2-3 carved cuts sweeping the back/chest so the body
    #     reads as sculpted nephrite catching one light, not a flat green blob.
    #     Each is a dark cut + pale-mint upper rim (the bevel grammar). Kept to a
    #     few bold sweeps so they never busy the 40px read.
    _groove(surf, [(20, 44), (28, 41), (37, 43)])          # shoulder/back ridge
    _groove(surf, [(22, 52), (31, 50), (40, 53)])          # chest contour
    _groove(surf, [(20, 59), (29, 61), (38, 59)])          # belly contour

    # 3 · CINNABAR SEAL-MARK — one small lacquer-red square stamped on the shoulder,
    #     the single warm pop on the body. A red field with a thin mint inner border
    #     and a tiny carved glyph notch so it reads as an engraved seal, not a dot.
    sx, sy = 35, 47
    pygame.draw.rect(surf, _CINNAB_D, (sx - 4, sy - 4, 8, 8), border_radius=1)
    pygame.draw.rect(surf, _CINNABAR, (sx - 3, sy - 3, 6, 6), border_radius=1)
    pygame.draw.rect(surf, (235, 150, 140), (sx - 3, sy - 3, 6, 6), 1, border_radius=1)
    # carved glyph: a tiny stylised stroke cut into the seal face
    pygame.draw.line(surf, _CINNAB_D, (sx - 1, sy - 2), (sx - 1, sy + 2), 1)
    pygame.draw.line(surf, _CINNAB_D, (sx - 2, sy), (sx + 1, sy), 1)

    # 4 · POLISH HIGHLIGHTS — two hard mint glints (crown + chest) where the
    #     polished stone catches the key light, each butting a deep-jade shadow
    #     just below so the value JUMPS and the surface reads as glossy mineral.
    pygame.draw.line(surf, _MINT, (HX - 7, HY - 9), (HX + 3, HY - 11), 2)
    pygame.draw.line(surf, _JADE_DK, (HX - 7, HY - 6), (HX + 4, HY - 8), 1)
    pygame.draw.line(surf, _MINT, (26, 45), (34, 43), 2)
    pygame.draw.line(surf, _JADE_DK, (26, 49), (35, 47), 1)

    # 5 · BOTTOM RIM-LIGHT — a thin mint stroke tracing the underside silhouette
    #     (belly + lower wing) that faces open sky, so the cool lower mass keeps a
    #     crisp lit edge against dark night sky instead of dissolving. Held one step
    #     above the shadow floor so it's a rim, not a glow; bright-day read intact.
    pygame.draw.lines(surf, _MINT, False,
                      [(17, 56), (24, 61), (32, 63), (40, 61), (46, 56)], 1)

    # 6 · AVIATORS RELIT — the smoky-jade lenses get a pale mint top-rim + glint so
    #     Pip's signature glasses read as polished jade catching the carving light,
    #     tying the face into the museum-object material.
    pygame.draw.line(surf, _MINT, (40, 44), (46, 43), 2)
    pygame.draw.line(surf, _MINT, (49, 43), (55, 44), 2)
    pygame.draw.circle(surf, _MINT, (44, 45), 1)
    pygame.draw.circle(surf, _MINT, (53, 45), 1)


# Body recolour through the palette system + the carving overlay, wrapped by the
# house _make_skin contract (lazy flat build + per-(frame, 3°) rotation cache).
# The cloud-scroll extends the existing tail (front overlay), so no custom
# back-layer getter is needed.
build = store_skins._make_skin(
    _paint_jade,
    base_fn=lambda a: _build_parrot_with_palette(a, P_JADE),
)
