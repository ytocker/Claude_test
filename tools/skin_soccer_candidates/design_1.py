"""SOCCER redesign — design_1 THE STRIKER (exploration only).

A Brazil-style canary-yellow striker kit on Pip the macaw. The whole bird is
re-plumaged through the palette system to a single solid canary-yellow jersey
so the body reads as one bright kit, not bare scarlet and not a green-splattered
mess. Green is the team trim and lives ONLY in four deliberate bands — neck
collar, wingtip cuff, tail-base waistband, socks — so it frames the kit instead
of scattering across it. An oversized white "10" owns the chest as the single
hero read at 40px, built from chunky white blocks so the bold digits survive
downscale where a thin outlined glyph would smear.

R2 fix-list (each tied to an art-director note at 40px):
  * Green confined to FOUR bands only — collar ring, wing cuff, waistband, socks.
    The tail is no longer green (it was the main splatter source); the whole
    body/back/belly/flanks are now solid canary yellow.
  * Hair tuft rebuilt as ONE cohesive forward-swept mass leaning toward the
    beak, instead of two symmetric horn-like spikes.
  * Cleats simplified to a white toe-box with a single black sole line and NO
    stud row — studs were sub-pixel noise at 40px.
  * The "10" recentred on the chest mass with ≥1px breathing room from any
    green on every side and a dark keyline all around.
  * The collar drawn as a crisp closed dark-green ring at the neck, framing the
    number from above.

Scratch builder — NOT registered in store_skins.BUILDERS. Production art is
untouched until a winner is picked.
"""
import pygame

from game import store_skins
from game.store_skins import HX, HY, CROWN_Y, COMPOSITE_W, COMPOSITE_H, PARROT_DY
from game.dollar_parrot_ghost import _pal, _build_parrot_with_palette


# ── palette ──────────────────────────────────────────────────────────────────
_CANARY     = (245, 208, 0)        # #F5D000 jersey yellow
_CANARY_H   = (255, 232, 90)       # jersey highlight
_CANARY_D   = (196, 162, 0)        # jersey shadow / seam
_GREEN      = (10, 122, 60)        # #0A7A3C dark-green trim
_GREEN_H    = (40, 168, 95)
_GREEN_D    = (8, 88, 44)
_WHITE      = (255, 255, 255)      # boots / number
_WHITE_SH   = (214, 220, 226)
_BLACK      = (26, 26, 26)         # #1A1A1A hair / sole
_OUTLINE    = (11, 58, 30)         # #0B3A1E green outline under the number

# Full canary-yellow kit re-plumage. EVERY plumage slot — body, chest, belly,
# wings AND tail — is a canary value so the bird is one solid bright kit; the
# deepest CANARY_D owns the line work. Green is deliberately kept OUT of the
# palette so the only green on the bird is the four painted trim bands. Lenses
# off — the chest number, not the face, owns the read. Beak stays a warm macaw
# orange so Pip still reads as a parrot under the kit. Feet read white as the
# boot base.
_STRIKER_PAL = _pal(
    tail=[(196, 162, 0), (232, 196, 0), (245, 208, 0), (255, 224, 70)],
    tail_line=_CANARY_D,
    body_shadow=_CANARY_D,
    body_main=_CANARY,
    body_chest=(255, 220, 40),
    body_belly=(235, 198, 10),
    sheen=(255, 255, 255, 90),
    wing_main=(232, 196, 0),
    wing_dark=_CANARY_D,
    wing_tip=(255, 224, 70),
    wing_secondary=None,
    wing_highlight=_CANARY_H,
    head_shadow=(200, 166, 0),
    head_main=_CANARY,
    head_cheek=(255, 224, 80),
    head_crown=(255, 220, 60),
    lens_frame=(200, 166, 0),
    lens_body=(150, 124, 0),
    lens_tint=None,
    lens_glint=None,
    beak_main=(255, 168, 40),
    beak_dark=(176, 100, 18),
    beak_gloss=(255, 214, 130),
    foot=_WHITE,
)


def _striker_base(angle_deg):
    # Canary-kit bird, no aviators — the chest "10" owns the read.
    return _build_parrot_with_palette(angle_deg, _STRIKER_PAL, draw_lenses=False)


def _digit_one(surf, x, y, w, h):
    """Chunky white '1' — a bold vertical bar on a wide serif foot so it never
    reads as a stray line at 40px. (x,y) is the top-left of the vertical bar."""
    foot_h = max(3, h // 5)
    foot_w = w * 2 + 2
    # outline underlay (one dark keyline so white holds on yellow)
    pygame.draw.rect(surf, _OUTLINE, (x - 1, y - 1, w + 2, h + 2))
    pygame.draw.rect(surf, _OUTLINE, (x - w + 1, y + h - foot_h - 1, foot_w, foot_h + 2))
    # white fills
    pygame.draw.rect(surf, _WHITE, (x, y, w, h))
    pygame.draw.rect(surf, _WHITE, (x - w + 2, y + h - foot_h, foot_w - 2, foot_h))


def _digit_zero(surf, x, y, w, h):
    """Chunky white '0' — a bold ring (outer white block minus an inner punch)
    so the hole survives downscale without smearing shut."""
    pygame.draw.rect(surf, _OUTLINE, (x - 1, y - 1, w + 2, h + 2), border_radius=4)
    pygame.draw.rect(surf, _WHITE, (x, y, w, h), border_radius=4)
    inset = max(3, w // 3)
    # Punch the hole back to the jersey yellow so the ring reads as a "0".
    pygame.draw.rect(surf, _CANARY, (x + inset, y + inset,
                                     w - inset * 2, h - inset * 2), border_radius=2)


def _paint(surf, wing_angle_deg):
    BCX, BCY = 32, 52       # body centre in composite space (32,32)+PARROT_DY

    # ── BAND (b): single green cuff at the wing tip — one clean ring, no spray ─
    pygame.draw.line(surf, _GREEN_D, (45, 44), (52, 41), 5)
    pygame.draw.line(surf, _GREEN, (45, 43), (52, 40), 3)
    pygame.draw.line(surf, _GREEN_H, (46, 42), (51, 40), 1)

    # ── BAND (d): green socks above the cleats + white cleats at the feet ─────
    # Drawn first so the body sits in front. Each foot is a green sock band, a
    # white toe-box, and ONE hard black sole line — no stud row (studs are
    # sub-pixel noise at 40px). The white toe-box against the body's lower
    # outline gives a clean two-foot read.
    for fx in (BCX - 7, BCX + 4):
        # green sock band above the cleat
        pygame.draw.rect(surf, _GREEN_D, (fx - 1, BCY + 9, 8, 7), border_radius=2)
        pygame.draw.rect(surf, _GREEN, (fx, BCY + 9, 6, 6), border_radius=2)
        pygame.draw.line(surf, _GREEN_H, (fx + 1, BCY + 10), (fx + 5, BCY + 10), 1)
        # white cleat (toe-box angled forward)
        boot = [(fx - 2, BCY + 15), (fx + 6, BCY + 15),
                (fx + 9, BCY + 18), (fx - 2, BCY + 18)]
        pygame.draw.polygon(surf, _WHITE_SH, [(px, py + 1) for px, py in boot])
        pygame.draw.polygon(surf, _WHITE, boot)
        # ONE hard black sole as the literal bottom of the boot
        pygame.draw.line(surf, _BLACK, (fx - 2, BCY + 18), (fx + 9, BCY + 18), 2)

    # ── BAND (c): green waistband at the tail/hip junction — one closed band ──
    pygame.draw.line(surf, _GREEN_D, (15, BCY + 6), (26, BCY + 10), 5)
    pygame.draw.line(surf, _GREEN, (15, BCY + 5), (26, BCY + 9), 3)
    pygame.draw.line(surf, _GREEN_H, (16, BCY + 4), (25, BCY + 8), 1)

    # ── BAND (a): crisp closed dark-green crew collar RING at the neck ────────
    # A proper closed ring at the head/chest junction — the one shape that
    # instantly says "team jersey" and frames the "10" from above. The yellow
    # neck hole is punched back so it reads as a ring, never a smear or bib.
    # Drawn before the number; kept high and slim so it never crowds the digits.
    cnx, cny = HX - 3, HY + 10
    pygame.draw.ellipse(surf, _GREEN_D, (cnx - 11, cny - 4, 24, 11))
    pygame.draw.ellipse(surf, _GREEN, (cnx - 10, cny - 3, 22, 9))
    # punch the neck hole back to yellow so the band reads as a closed ring
    pygame.draw.ellipse(surf, _CANARY, (cnx - 6, cny - 1, 14, 5))
    pygame.draw.line(surf, _GREEN_H, (cnx - 8, cny - 2), (cnx + 9, cny - 3), 1)

    # ── the hero: oversized white "10" centred on the chest mass ──────────────
    # Sized so the pair owns the chest at 40px and recentred under the collar
    # with ≥1px clearance from the collar above and the waistband below. Built
    # from chunky white blocks over a green keyline so the digits hold on yellow.
    num_h = 17
    digit_w = 5
    nx, ny = BCX - 10, BCY - 6
    _digit_one(surf, nx, ny, digit_w, num_h)
    _digit_zero(surf, nx + digit_w + 4, ny, 10, num_h)

    # ── ONE cohesive forward-swept black hair tuft over the crown ─────────────
    # A single mass leaning toward the beak with the flight tilt — not two
    # symmetric spikes. A rounded base anchors it to the crown and a single
    # swept triangular peak gives the forward flick.
    tx, ty = HX, CROWN_Y
    pygame.draw.ellipse(surf, _BLACK, (tx - 7, ty - 1, 15, 6))
    tuft = [(tx - 6, ty + 2), (tx + 8, ty + 1),
            (tx + 7, ty - 4), (tx + 2, ty - 3)]
    pygame.draw.polygon(surf, _BLACK, tuft)
    # subtle sheen line along the swept top edge so the single mass reads
    pygame.draw.line(surf, (70, 70, 70), (tx - 3, ty - 1), (tx + 6, ty - 2), 1)


build = store_skins._make_skin(_paint, base_fn=_striker_base)
