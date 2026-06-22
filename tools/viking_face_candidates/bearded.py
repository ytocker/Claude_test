"""Viking refinement — "BEARDED" (replaces the rejected design_2 BERSERKER).

The user's correction was three concrete moves, all aimed at making the bird
read as a NORMAL macaw wearing Viking gear rather than a custom-faced brute:

1. REGULAR PARROT FACE. The base macaw eye (a pale bare-skin patch + dark
   pupil + white glint, exactly parrot._draw_eye) and the hooked beak stay
   VISIBLE. The frozen base helm in P['front'] dropped its dome over the eye
   and buried the beak under a long nasal, so it is NOT used as-is here; a
   RAISED variant of the same horned spangenhelm is drawn instead — dome and
   brow lifted ~4px, nasal shortened and narrowed — so the bare eye + beak sit
   in the open under the brow like any other costume.

2. BEADED MOUSTACHE + BEARD. A long braided moustache sweeps down past both
   sides of the beak, each end capped with a metal BEAD; a modest beard hangs
   onto the chest below it. The whole facial-hair mass is value-separated from
   the body with a 1px keyline edge so it reads even in IRONCLAD's
   brown-on-brown. Mass + bead accents only — no per-strand noise.

3. DOUBLE-BIT AXE STOWED ON THE BACK. The BERSERKER twin-crescent double-bit
   head is reused, but the axe is no longer HELD — it is slung diagonally
   across the back the way skin_ninja stows its ninjato: butt low past the
   tail, twin-blade head poking up past the back shoulder, the haft running
   down behind the body with the round shield sitting IN FRONT of its middle so
   the axe reads as carried/stowed, not wielded. No grip, no claw.

Custom compose (NOT S.make_build) because the axe must sit BEHIND the body:
    axe -> body -> back(shield+fur) -> raised helm+boots -> face -> outline.
Scratch exploration only — nothing here registers in store_skins.BUILDERS and
the live skin_viking is untouched.
"""
import math

import pygame

from game import store_skins
from game.store_skins import HX, HY, CROWN_Y, _poly, _compose
from game.parrot import _add_outline, _aaellipse, _WING_ANGLES
from tools.viking_face_candidates import _shared as S


# ─────────────────────────────────────────────────────────────────────────────
# 1 · RAISED HORNED HELM (+ boots) — the frozen spangenhelm, dome & brow lifted
#     ~4px and the nasal shortened/narrowed so the bare macaw eye (≈(50,40)) and
#     hooked beak (≈(55-61,41-48)) read in the open underneath. The horns,
#     dome, brow band, rivets and boot cuffs are otherwise the verbatim base
#     pieces from _shared._iron_front / _blood_front so it still matches v1/v2.
# ─────────────────────────────────────────────────────────────────────────────
def _raised_helm(surf, P):
    iron = P["name"] == "IRONCLAD"
    cy = CROWN_Y
    # Palette aliases mirroring the two frozen *_front blocks.
    if iron:
        beard, fur_hi, bone = S.I_BEARD, S.I_FUR_HI, S.I_BONE
        helm, helm_dk, helm_hi = S.I_HELM, S.I_HELM_DK, S.I_HELM_HI
        rivet = S.I_BRONZE
        boot_dk, boot_hi = S.I_FUR, S.I_FUR_HI
        horn_tip = S.I_BONE
        horn_glint = S.I_HELM_HI
    else:
        beard, fur_hi, bone = S.B_BEARD, S.B_FUR_HI, S.B_BONE
        helm, helm_dk, helm_hi = S.B_IRON, S.B_IRON_DK, S.B_IRON_HI
        rivet = S.B_IRON_HI
        boot_dk, boot_hi = S.B_BEARD, S.B_FUR_HI
        horn_tip = S.B_BONE
        horn_glint = (244, 234, 210)

    # ── HORNS (verbatim flare/curl, only their root y is unchanged so they keep
    # springing from the dome crown that has been lifted with them). ──────────
    for sgn, hx0 in ((-1, HX - 9), (1, HX + 9)):
        tipx = hx0 + sgn * 6
        mid = (hx0 + sgn * 5, cy - 6)
        _poly(surf, beard, [(hx0 - 4, cy + 2), (hx0 + 4, cy + 2), mid, (tipx + sgn * 2, cy - 16)])
        _poly(surf, fur_hi, [(hx0 + sgn * 3, cy + 1), (hx0 + sgn * 4, cy + 1),
                             (mid[0] + sgn, mid[1] + 1), (tipx + sgn * 2, cy - 15)])
        pygame.draw.circle(surf, fur_hi, (tipx + sgn, cy - 15), 3)
        pygame.draw.circle(surf, horn_tip, (tipx + sgn, cy - 15), 2)
        pygame.draw.circle(surf, horn_glint, (tipx + sgn - 1, cy - 16), 1)

    # ── DOME + BROW BAND lifted ~4px (dy = -4) so its lower rim clears the eye.
    # The frozen dome bottomed at cy+12 (y43) which clipped the eye at y40; here
    # it bottoms at cy+8 (y39), opening the bare face below the band. ──────────
    dy = -4
    pygame.draw.ellipse(surf, helm_dk, (HX - 12, cy - 6 + dy, 25, 18))
    pygame.draw.ellipse(surf, helm, (HX - 11, cy - 6 + dy, 23, 8))
    pygame.draw.ellipse(surf, helm_hi, (HX - 6, cy - 5 + dy, 9, 4))
    # Brow band (the dark rim + lit edge), also lifted, sitting just above the eye.
    pygame.draw.line(surf, helm_dk, (HX - 11, cy + 5 + dy), (HX + 12, cy + 4 + dy), 4)
    pygame.draw.line(surf, helm_hi if not iron else helm,
                     (HX - 11, cy + 4 + dy), (HX + 12, cy + 3 + dy), 1)
    for rx in (HX - 8, HX - 1, HX + 6):
        pygame.draw.circle(surf, rivet, (rx, cy + 5 + dy), 1)

    # ── SHORT NASAL — narrowed to 2px and stopped at the brow band so it no
    # longer runs down over the beak. A stub of the spangenhelm nasal, present
    # for the period read but clear of the hooked beak at (55-61,41-48). ───────
    nx = HX + 1
    pygame.draw.rect(surf, helm_dk, (nx, cy + 4 + dy, 2, 5))
    pygame.draw.line(surf, helm, (nx, cy + 4 + dy), (nx, cy + 8 + dy), 1)

    # ── BOOT CUFFS (verbatim) ────────────────────────────────────────────────
    for fx, fy in ((27, 65), (35, 65)):
        pygame.draw.circle(surf, boot_dk, (fx, fy + 1), 3)
        pygame.draw.circle(surf, boot_hi, (fx, fy), 2)


# ─────────────────────────────────────────────────────────────────────────────
# 2 · BEADED MOUSTACHE + BEARD — the bare macaw eye is drawn first (so it always
#     shows), then a long braided moustache sweeping down past both sides of the
#     beak with a metal bead at each tip, then a modest beard onto the chest.
#     Every facial-hair edge carries a 1px keyline so the mass separates from the
#     body even in IRONCLAD. NO custom/fierce eye — this is parrot._draw_eye.
# ─────────────────────────────────────────────────────────────────────────────
def _face(surf, wing_angle, P):
    beard, beard_hi = P["beard"], P["beard_hi"]
    ring, white, bone = P["ring"], P["white"], P["bone"]
    key = P["keyline"][:3]
    # IRONCLAD's chin beard sat too close to the brown body; drop the chin tone
    # a notch darker than the 'stache beard so it doesn't melt into the chest.
    iron_face = P["name"] == "IRONCLAD"
    chin_tone = (40, 28, 18) if iron_face else beard

    # The facial-hair value plan: a DARK narrow CHIN BEARD (bottom of the stack)
    # under a LIGHTER walrus MOUSTACHE with two long braids dropping to metal
    # beads. Stacking light-on-dark — not piling one dark mass — is what keeps
    # the 'stache and beads legible even in IRONCLAD's brown-on-brown.

    # ── REGULAR MACAW EYE at (50,40) — verbatim parrot._draw_eye look so the
    # bird reads as a normal macaw under the helm. The base body is built with
    # draw_lenses=False and no eye, so the eye is painted here. ────────────────
    ex, ey = 50, 40
    _aaellipse(surf, (250, 243, 236), (ex, ey), 6, 5)
    pygame.draw.line(surf, (236, 210, 205), (ex - 5, ey - 2), (ex + 5, ey - 2), 1)
    pygame.draw.line(surf, (236, 210, 205), (ex - 5, ey + 2), (ex + 5, ey + 2), 1)
    pygame.draw.circle(surf, (40, 26, 30), (ex + 1, ey), 3)
    pygame.draw.circle(surf, (15, 10, 12), (ex + 1, ey), 3, 1)
    pygame.draw.circle(surf, (255, 255, 255), (ex, ey - 1), 1)

    # ── CHIN BEARD (bottom of the stack) — a NARROW rounded tuft hanging
    # straight down from the chin onto the chest BETWEEN the two braids, so the
    # beaded braids drop against the lighter body on either side of it (not over
    # it) and stay legible. Dark `beard` tone, keyline ring + one side light. ──
    cx0, cy0 = 47, 53
    chin = [
        (cx0 - 4, cy0),           # chin, below the eye
        (cx0 - 5, cy0 + 6),
        (cx0 - 2, cy0 + 11),      # rounded bottom onto the chest
        (cx0 + 3, cy0 + 11),
        (cx0 + 5, cy0 + 6),
        (cx0 + 4, cy0),           # right edge, body-side of the beak
        (cx0,     cy0 - 1),
    ]
    # A doubled keyline (offset 1px down + the rim) strengthens the chin edge
    # so it reads against the body brown even before the darker fill helps.
    _poly(surf, key, [(x, y + 2) for x, y in chin])
    _poly(surf, key, [(x, y + 1) for x, y in chin])
    _poly(surf, chin_tone, chin)
    _poly(surf, beard_hi, [
        (cx0 - 4, cy0 + 1), (cx0 - 1, cy0 + 1),
        (cx0 - 2, cy0 + 8), (cx0 - 5, cy0 + 6),
    ])

    # ── WALRUS MOUSTACHE — a COMPACT lighter band slung directly under the beak
    # (drawn separately from the two braids so the silhouette reads as a clear
    # 'stache, not a wide blob). Filled at `beard_hi` over a keyline outline so
    # it lifts off the body and the darker chin beard. ───────────────────────
    mx, my = 50, 45          # band centre, just under the eye/nose
    band = [
        (mx - 8, my - 1),         # left cheek swell
        (mx - 9, my + 3),         # left corner droop
        (mx - 5, my + 4),
        (mx - 1, my + 2),         # dip under the nose between the halves
        (mx + 4, my + 2),
        (mx + 8, my + 4),         # right corner droop (beak side)
        (mx + 9, my + 1),
        (mx + 7, my - 1),         # far-right swell
        (mx,     my - 2),         # top centre, just under the cheek/eye
    ]
    _poly(surf, key, [(x, y + 1) for x, y in band])
    _poly(surf, beard_hi, band)
    # A brighter top-light line along the band's upper sweep so the lighter mass
    # separates even where beard_hi is close to the body tone (IRONCLAD).
    pygame.draw.lines(surf, P["bone"], False,
                      [(mx - 7, my - 1), (mx - 1, my - 2), (mx + 4, my - 2), (mx + 7, my)], 1)

    # ── TWO BRAIDS — slim tapering tails dropping from each corner of the band
    # down past the beak, each a distinct keyed column so the beaded ends read
    # as braids hanging clear on the body to the sides of the chin beard. ─────
    for sgn, bx0 in ((-1, mx - 8), (1, mx + 8)):
        braid = [
            (bx0,            my + 2),       # root at the band corner
            (bx0 + sgn,      my + 5),
            (bx0 + sgn,      my + 12),      # long drop (bead anchor)
            (bx0 - sgn * 2,  my + 12),
            (bx0 - sgn * 2,  my + 4),       # inner side, slim
        ]
        _poly(surf, key, [(x, y + 1) for x, y in braid])
        _poly(surf, beard_hi, braid)
        # one darker comb line so the slim tail still reads hairy.
        pygame.draw.line(surf, beard, (bx0, my + 5), (bx0, my + 11), 1)

    # ── REDRAW THE HOOKED BEAK on top so it always pokes through between the
    # braids — verbatim beak geometry from _build_parrot_with_palette (+PARROT_DY
    # on y), recoloured per palette so the macaw's signature hook stays legible. ─
    iron = P["name"] == "IRONCLAD"
    if iron:
        beak_main, beak_dk, beak_gloss = (150, 120, 80), S.I_BODY_SHAD, (190, 160, 116)
    else:
        beak_main, beak_dk, beak_gloss = (196, 150, 96), (120, 84, 44), (228, 200, 150)
    beak_pts = [(55, 41), (61, 44), (58, 48), (52, 46)]
    pygame.draw.polygon(surf, beak_main, beak_pts)
    pygame.draw.polygon(surf, beak_dk, beak_pts, 1)
    pygame.draw.line(surf, beak_gloss, (55, 42), (59, 44), 1)
    pygame.draw.line(surf, beak_dk, (52, 44), (58, 45), 1)

    # ── METAL BEADS capping each braided tip — a ring stud + a bone/white glint
    # so each end reads as clasped metal (the only ornament). ─────────────────
    for bdx, bdy in ((mx - 9, my + 14), (mx + 9, my + 14)):
        pygame.draw.circle(surf, key, (bdx, bdy), 3)
        pygame.draw.circle(surf, ring, (bdx, bdy), 2)
        pygame.draw.circle(surf, P["white"], (bdx - 1, bdy - 1), 1)


# ─────────────────────────────────────────────────────────────────────────────
# 3 · DOUBLE-BIT AXE STOWED ON THE BACK — the BERSERKER twin-crescent head, but
#     the whole axe is slung diagonally across the back like skin_ninja's
#     ninjato (lo≈(HX-31,HY+28) up to hi≈(HX+19,CROWN_Y-18)). Drawn BEFORE the
#     body so the haft runs behind it; the back shield (painted after the body)
#     covers the haft's middle, so it reads as STOWED. No grip / no claw — the
#     twin-blade head simply pokes up past the back shoulder.
# ─────────────────────────────────────────────────────────────────────────────
def _carried_axe(surf, P):
    iron = P["name"] == "IRONCLAD"
    haft, haft_hi = P["haft"], P["haft_hi"]
    ring, white, bone = P["ring"], P["white"], P["bone"]
    key = P["keyline"][:3]

    # IRONCLAD's grey blade fused with the grey helm steel, so here the blade
    # tone is WARMED + DARKENED a notch toward gunmetal/iron away from the
    # cool helm steel (P['blade']); BLOODAXE's blade already contrasts the
    # rust body, so it keeps the frozen steel tone. The hot outer-arc edge
    # highlight is what still sells "blade" once the silhouette is fixed.
    if iron:
        blade, blade_dk, blade_hi = (92, 96, 104), (52, 54, 62), (176, 182, 192)
    else:
        blade, blade_dk, blade_hi = P["blade"], P["blade_dk"], P["blade_hi"]

    # Back-slung pose: butt LOW past the tail (left), head HIGH up past the
    # back shoulder so it clears the crown into OPEN SKY (not tucked on the
    # helm). The diagonal is steepened vs round-1 and the head pulled higher
    # and back-of-crown so its outer bits silhouette against sky on the
    # tail/crown side, and a run of wrapped haft shows on the tail-side body
    # between the shield bottom and the butt-cap.
    lo = (HX - 30, HY + 30)        # haft butt, low past the tail
    hi = (HX - 3, CROWN_Y - 23)    # axe-head centre, high above the back crown

    dx, dy = hi[0] - lo[0], hi[1] - lo[1]
    blen = math.hypot(dx, dy)
    ux, uy = dx / blen, dy / blen          # along the haft (lo->hi)
    px, py = -uy, ux                       # perpendicular

    # ── HAFT running the whole diagonal (a dark core + wood + lit edge). It
    # stops a touch short of the head centre so the bits sit on its end. ───────
    hx0, hy0 = lo
    hx1 = hi[0] - ux * 8
    hy1 = hi[1] - uy * 8
    pygame.draw.line(surf, key, (hx0, hy0), (hx1, hy1), 6)
    pygame.draw.line(surf, haft, (hx0, hy0), (hx1, hy1), 4)
    pygame.draw.line(surf, haft_hi, (hx0 + px, hy0 + py), (hx1 + px, hy1 + py), 1)
    # Whipping bands so the haft reads as wrapped wood.
    for t in (0.30, 0.55, 0.80):
        wx = hx0 + (hx1 - hx0) * t
        wy = hy0 + (hy1 - hy0) * t
        pygame.draw.line(surf, blade_dk, (wx - px * 2, wy - py * 2),
                         (wx + px * 2, wy + py * 2), 1)
    # A small steel butt-cap glint at the LOW tip past the tail.
    pygame.draw.circle(surf, blade_dk, (int(lo[0]), int(lo[1])), 3)
    pygame.draw.circle(surf, blade_hi, (int(lo[0]), int(lo[1])), 2)

    # ── TWIN-CRESCENT DOUBLE-BIT HEAD at hi, aligned to the haft so both bits
    # flank the shaft. Built in haft-local axes (u along the haft, p across) so
    # the crescent shape rides the diagonal instead of sitting flat. ──────────
    tx, ty = hi

    def L(a, b):
        # a = offset along the haft (toward the tip is +), b = offset across.
        return (tx + ux * a + px * b, ty + uy * a + py * b)

    # Each bit is a true CRESCENT held off the haft by a SLIM socket, joined to
    # it only by thin necks at the socket's top and bottom — so a wedge of OPEN
    # SKY (transparent) bites in between the bit's inner arc and the socket on
    # each side. That negative-space notch, not a painted line, is what splits
    # the head into a clean "><" twin-crescent instead of one solid block. The
    # outer cutting edge bulges to b=±13 with SHARP horn points; the inner arc
    # caves back to b=±8, leaving the daylight gap to the b=±2 socket. The bit
    # WAIST + the daylight notch are what carry the read at 40px.
    for side in (-1, 1):
        bit = [
            L(8,  side * 4),      # upper neck — thin join to the socket top
            L(8,  side * 8),      # upper horn POINT — sharp, little flare
            L(4,  side * 12),
            L(0,  side * 13),     # cutting-edge waist (widest, outermost)
            L(-4, side * 12),
            L(-8, side * 8),      # lower horn POINT — sharp
            L(-8, side * 4),      # lower neck — thin join to the socket bottom
            L(-5, side * 7),      # inner arc caves back in...
            L(0,  side * 8),      # ...deepest of the concave inner edge
            L(5,  side * 7),
        ]
        _poly(surf, blade_dk, bit)
        # Brighter inner bevel facet on each bit.
        facet = [
            L(6,  side * 6), L(6, side * 9), L(0, side * 11),
            L(-6, side * 9), L(-6, side * 6), L(0, side * 9),
        ]
        _poly(surf, blade, facet)
        # Hot cutting-edge highlight along the outer arc.
        pygame.draw.lines(surf, blade_hi, False,
                          [L(8, side * 8), L(0, side * 13), L(-8, side * 8)], 2)
        pygame.draw.line(surf, white, L(0, side * 13), L(0, side * 12), 1)
    # Slim socket column hugging the haft (much narrower than the bit reach so
    # the daylight notches stay open), one ring stud at the centre.
    pygame.draw.line(surf, key, L(8, 0), L(-8, 0), 5)
    pygame.draw.line(surf, blade_dk, L(8, 0), L(-8, 0), 3)
    pygame.draw.line(surf, blade, L(7, 0), L(-7, 0), 1)
    pygame.draw.circle(surf, ring, (int(tx), int(ty)), 1)


# ─────────────────────────────────────────────────────────────────────────────
# Custom compose — axe must sit BEHIND the body, so the frozen S.make_build
# draw order (which blits the body first) can't be used. Order:
#   axe -> body -> back(shield+fur) -> raised helm+boots -> face -> outline.
# Mirrors store_skins._make_skin's lazy-flat-build + per-(frame,3° tilt) cache.
# ─────────────────────────────────────────────────────────────────────────────
def _make(P):
    state = {"frames": None, "rot": {}}

    def _flat(wing_angle):
        comp = pygame.Surface((store_skins.COMPOSITE_W, store_skins.COMPOSITE_H),
                              pygame.SRCALPHA)
        _carried_axe(comp, P)                                   # behind everything
        comp.blit(P["base_fn"](wing_angle), (0, store_skins.PARROT_DY))  # body on top
        P["back"](comp)                                         # shield + fur cover the haft
        _raised_helm(comp, P)                                   # raised helm + boots
        _face(comp, wing_angle, P)                              # beaded 'stache + beard
        return _add_outline(comp, outline_color=P["keyline"])

    def getter(frame_idx, tilt_deg):
        if state["frames"] is None:
            state["frames"] = [_flat(a) for a in _WING_ANGLES]
        frames = state["frames"]
        frame_idx %= len(frames)
        key = (frame_idx, int(round(tilt_deg / 3.0)) * 3)
        s = state["rot"].get(key)
        if s is None:
            s = pygame.transform.rotozoom(frames[frame_idx], key[1], 1.0)
            state["rot"][key] = s
        return s

    return getter


build_ironclad = _make(S.IRONCLAD)
build_bloodaxe = _make(S.BLOODAXE)
