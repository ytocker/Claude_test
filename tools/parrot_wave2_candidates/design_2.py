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
    """One carved relief groove: a single CLEAN dark-jade chisel stroke with the
    pale-mint catch-light on ONE side only (a real chisel only catches light on
    one face). Mint above the dark cut = a wide value gap that reads as a carved
    bevel at 40px without fragmenting the body — depth, not quantity. Used for at
    most two grooves, both routed to follow the body form and to cross NEITHER the
    face, so the head stays the cleanest, densest shape."""
    pygame.draw.lines(surf, _GROOVE_DK, False, pts, 2)
    rim = [(x, y - 1) for x, y in pts]            # catch-light on the upper face only
    pygame.draw.lines(surf, _MINT, False, rim, 1)


def _ruyi_scroll(surf, ox, oy, sway):
    """The hero, and the ONLY place the detail budget is spent: the tail re-cut
    into ONE bold ruyi comma-hook that clearly LEAVES the body and curls up into
    open sky — the tail-break that makes the skin un-confusable with the
    crest-break of THORNCREST. A single clean hook (fat root → tapering out-and-up
    tip) beats a mushy double-spiral at 40px, so this commits to one comma. The
    carved-stone read is bought as VALUE: a deep-jade core, a jade body, and a fat
    ≥3px pale-MINT rim down the OUTER (sky-facing) edge running the full length
    through the tip, so the hook reads against BOTH skies. No cinnabar here — the
    shoulder seal is the sole warm note. `sway` flexes the tip a touch with the
    wing beat (kept subtle — baked stone)."""
    # The hook is built as a true CRESCENT — the region between an OUTER arc and an
    # INNER arc that share a centre. A crescent is mathematically guaranteed to be
    # an open C with an island of OPEN SKY in its mouth, so the negative-space notch
    # that makes a 40px viewer read "hook" (not "tapered lump") can never fill in.
    # The two arcs MEET at the tip (crescent tapers to a point there) and are held
    # APART at the root (the comma is fat where it joins the body), and the whole
    # curl is seated just off the lower tail so the C clears the body silhouette.
    cx, cy = ox - 3, oy + 8 + sway      # curl centre, off the lower-left tail
    a0 = math.radians(-58)             # mouth opens up-left into open sky
    a1 = math.radians(-58 + 250)       # ~250° of crescent — a bold open C
    R_out, R_in = 11.5, 5.0            # gap = fat belly; both arcs meet at the tip
    n = 30
    outer, inner = [], []
    for i in range(n + 1):
        t = i / n
        a = a0 + (a1 - a0) * t
        # the inner radius climbs to MEET the outer one near the tip (t→1) so the
        # crescent tapers to a carved point instead of a blunt ring end.
        ri = R_in + (R_out - R_in) * (t ** 1.5)
        ro = R_out + 1.0 * math.sin(math.pi * t)          # slight belly bulge
        outer.append((cx + math.cos(a) * ro, cy + math.sin(a) * ro))
        inner.append((cx + math.cos(a) * ri, cy + math.sin(a) * ri))
    body_poly = outer + inner[::-1]

    # deep core (offset down 1px — the recessed underside; also closes the
    # silhouette against bright sky)
    pygame.draw.polygon(surf, _JADE_DK, [(x, y + 1) for x, y in body_poly])
    # jade body fill
    pygame.draw.polygon(surf, _JADE, body_poly)
    # FAT pale-mint rim down the OUTER sky-facing arc, full length through the tip
    # — the hook's read on BOTH biomes. 3px so it survives the 40px downscale.
    pygame.draw.lines(surf, _MINT, False, outer, 3)
    # a rounded mint cap where the crescent tapers to its point, so the hook
    # terminates cleanly (not a ragged pixel) when small.
    pygame.draw.circle(surf, _MINT, (int(outer[-1][0]), int(outer[-1][1])), 2)
    # a single deep-jade groove down the INNER arc (the dark concave throat facing
    # the sky-gap) so the carved hollow of the C reads as a real recess — one clean
    # line, not noise.
    pygame.draw.lines(surf, _GROOVE_DK, False, inner, 2)


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

    # 2 · BODY RELIEF GROOVES — exactly TWO clean chisel cuts that FOLLOW the body
    #     form and cross NEITHER the face, so the body reads as sculpted nephrite
    #     without fragmenting into speckle at 40px. One sweeps the back-shoulder,
    #     one the lower chest/belly; both kept well below and behind the head block.
    _groove(surf, [(19, 45), (27, 42), (36, 44)])          # back-shoulder ridge
    _groove(surf, [(20, 57), (29, 59), (39, 56)])          # lower chest/belly

    # 3 · CINNABAR SEAL-MARK (KEEP — exact size/placement) — one small lacquer-red
    #     square stamped on the shoulder, the SOLE warm note on the whole skin and
    #     the one thing anchoring the eye to the body. A red field with a thin mint
    #     inner border + a tiny carved glyph so it reads as an engraved seal.
    sx, sy = 35, 47
    pygame.draw.rect(surf, _CINNAB_D, (sx - 4, sy - 4, 8, 8), border_radius=1)
    pygame.draw.rect(surf, _CINNABAR, (sx - 3, sy - 3, 6, 6), border_radius=1)
    pygame.draw.rect(surf, (235, 150, 140), (sx - 3, sy - 3, 6, 6), 1, border_radius=1)
    # carved glyph: a tiny stylised stroke cut into the seal face
    pygame.draw.line(surf, _CINNAB_D, (sx - 1, sy - 2), (sx - 1, sy + 2), 1)
    pygame.draw.line(surf, _CINNAB_D, (sx - 2, sy), (sx + 1, sy), 1)

    # 4 · BOTTOM RIM-LIGHT — a 2px mint stroke tracing the underside silhouette
    #     (belly + lower wing) facing open sky, so the cool lower mass keeps a crisp
    #     lit edge and the silhouette CLOSES against the navy night sky / store card
    #     instead of melting in. Thickened to 2px (from 1) so it survives downscale
    #     on near-black; the bright-day read is untouched.
    pygame.draw.lines(surf, _MINT, False,
                      [(17, 56), (24, 61), (32, 63), (40, 61), (46, 55)], 2)

    # 5 · FACE — kept deliberately CLEAN of all groove/rim detail so the head +
    #     dark aviator block stays the densest, sharpest shape and the eye lands
    #     there first. The only head note is ONE thin mint top-rim across the
    #     smoky-jade lenses so the aviators read as a crisp dark block catching a
    #     single carving light — no speckle, no body grooves crossing the face.
    pygame.draw.line(surf, _MINT, (41, 44), (55, 43), 1)


# Body recolour through the palette system + the carving overlay, wrapped by the
# house _make_skin contract (lazy flat build + per-(frame, 3°) rotation cache).
# The cloud-scroll extends the existing tail (front overlay), so no custom
# back-layer getter is needed.
build = store_skins._make_skin(
    _paint_jade,
    base_fn=lambda a: _build_parrot_with_palette(a, P_JADE),
)
