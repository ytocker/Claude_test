"""SOCCER costume — design_5 THE DEFENDER (exploration only).

A blaugrana centre-back kit on Pip: a claret-and-blue vertical-halves jersey
split down the centre by a thin gold seam, a gold round collar with one bold
gold chest bar and a clean white squad-number hint, claret sleeves with a blue
cuff, blue shorts waistband, and — the hero tell — a pair of chunky pale shin
guards strapped over the lower legs, bridged up into the body by a claret sock
so they read as worn kit, with black cleats and gold studs below. The macaw is
re-plumaged so the body reads as a CLARET jersey and the wing as a BLUE sleeve,
so the two-tone identity holds at 40px instead of fighting the scarlet bird.

R2 fix-list (each tied to the 40px read):
  * FACE RESCUE — the head was a dark claret mass with no eye. A pale-claret
    cheek oval + a dark eye dot with a white catchlight are painted back in,
    the beak stays warm orange-yellow, and the sweatband is lifted clear of
    the eye so Pip still reads as a friendly macaw wearing a kit.
  * BLUE THAT READS — the navy half was collapsing into body shadow, so the
    blue is pushed to a brighter, more saturated #1E4FA8 and a THIN gold seam
    runs down the body centre so the claret/blue split survives downsampling.
  * LIFTED TORSO — a procedural rim-light on the back and crown (lighter
    claret on the left edge, lighter blue on the right edge) so the upper body
    isn't a flat dark silhouette under the bright shin guards.
  * SIMPLER GOLD — two shapes that survive 40px: ONE bold collar ring + ONE
    hard-edged horizontal gold chest bar. The blurry "4" is replaced by a
    clean white number rectangle; the brown sponsor smudge is dropped.
  * FEET CONNECTED — a claret sock segment bridges the shin-guard plates up
    into the body so the plates read as strapped-on armour, not floating blobs.

Scratch builder — NOT registered in store_skins.BUILDERS. Production art is
untouched until a winner is picked.
"""
import pygame

from game import store_skins
from game.store_skins import HX, HY, CROWN_Y, COMPOSITE_W, COMPOSITE_H, PARROT_DY
from game.dollar_parrot_ghost import _pal, _build_parrot_with_palette


# ── palette ──────────────────────────────────────────────────────────────────
_CLARET    = (140, 38, 72)         # #8C2648 claret jersey body (lifted ~15%)
_CLARET_D  = (96, 24, 50)
_CLARET_H  = (192, 78, 116)        # rim-light / cheek claret
_CLARET_HH = (224, 120, 156)       # brightest claret edge
_BLUE      = (30, 79, 168)         # #1E4FA8 brighter blaugrana blue
_BLUE_D    = (20, 52, 116)
_BLUE_H    = (86, 134, 214)        # rim-light blue
_BLUE_HH   = (140, 180, 240)
_GOLD      = (232, 184, 75)        # #E8B84B gold trim / number
_GOLD_D    = (176, 132, 40)
_GOLD_H    = (255, 224, 150)
_SEAM      = (244, 206, 120)       # pale-gold centre seam line
_BOOT      = (26, 26, 26)          # #1A1A1A boots
_BOOT_H    = (70, 70, 74)
_OUTLINE   = (12, 8, 32)           # #0C0820 deep outline value
_PLATE     = (232, 232, 222)       # pale shin-guard armour
_PLATE_D   = (186, 186, 176)
_PLATE_H   = (255, 255, 252)
_WHITE     = (245, 246, 250)
_SKIN_DK   = (40, 26, 18)          # dark hair / sweatband
_EYE       = (24, 16, 22)          # dark eye on the pale cheek

# Full claret-and-blue re-plumage: the body slots become claret so the chest
# reads as the jersey, the wing slots become blue so the sleeve carries the
# second kit colour, and the tail alternates claret/blue. Lenses are dropped so
# the bare macaw face sits under the hair + sweatband; the cheek + eye are
# painted back in _paint so Pip keeps a friendly read, and the beak stays warm
# so he reads as a parrot wearing a kit, not a recoloured blob.
_DEF_PAL = _pal(
    tail=[_CLARET_D, _BLUE_D, _CLARET, _BLUE],
    tail_line=_OUTLINE,
    body_shadow=_CLARET_D,
    body_main=_CLARET,
    body_chest=_CLARET_H,
    body_belly=(120, 32, 64),
    sheen=(255, 255, 255, 80),
    wing_main=_BLUE,
    wing_dark=_BLUE_D,
    wing_tip=_BLUE_H,
    wing_secondary=None,
    wing_highlight=_BLUE_HH,
    head_shadow=_CLARET_D,
    head_main=_CLARET,
    head_cheek=_CLARET_H,
    head_crown=(120, 32, 64),
    lens_frame=(120, 40, 60),
    lens_body=(40, 20, 28),
    lens_tint=None,
    lens_glint=None,
    beak_main=(240, 176, 74),      # warm light orange-yellow macaw beak
    beak_dark=(168, 108, 36),
    beak_gloss=(255, 230, 168),
    foot=_BOOT,
)


def _defender_base(angle_deg):
    # Claret body / blue sleeve bird, no aviators — the brow + hair own the
    # head, with the eye + cheek repainted in _paint for the friendly read.
    return _build_parrot_with_palette(angle_deg, _DEF_PAL, draw_lenses=False)


def _rim_light(surf):
    """Lift the upper-body value with hand-drawn edge highlights.

    The torso was reading as one dark mass under the bright shin guards. Rather
    than a mask trick that floods the interior, a few thin bright arcs trace
    the lit edges: a lighter-claret sweep on the upper-LEFT back + crown, and a
    lighter-blue sweep on the upper-RIGHT of the body, so the two halves each
    catch a rim of light and the upper body holds shape at 40px. Clipped to the
    painted silhouette so the strokes never spill past the bird's contour.
    """
    bcx, bcy = 32, 32 + PARROT_DY     # body ellipse centre in composite space
    light = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    # Upper-left claret back rim (the bird's "back").
    pygame.draw.lines(light, _CLARET_HH, False, [
        (bcx - 16, bcy + 2), (bcx - 14, bcy - 8), (bcx - 6, bcy - 13)], 2)
    # Crown rim over the head, claret into the parting.
    pygame.draw.lines(light, _CLARET_HH, False, [
        (HX - 9, CROWN_Y + 4), (HX - 3, CROWN_Y + 1)], 2)
    # Upper-right blue rim along the blue half's shoulder.
    pygame.draw.lines(light, _BLUE_HH, False, [
        (HX + 2, HY - 5), (HX + 12, HY - 1), (HX + 16, HY + 6)], 2)
    # Clip every stroke to the body so it hugs the silhouette.
    mask = pygame.mask.from_surface(surf, 8).to_surface(
        setcolor=(255, 255, 255, 255), unsetcolor=(0, 0, 0, 0))
    light.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(light, (0, 0))


def _paint(surf, wing_angle_deg):
    # ── vertical halves: brighter blue over the RIGHT half so the jersey is
    #     split claret(left) / blue(right). Clipped to the painted body
    #     silhouette so the colour stops at the bird's edge. ─────────────────
    right = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    pygame.draw.rect(right, _BLUE, (HX, HY - 6, 24, 76))
    mask = pygame.mask.from_surface(surf, 8).to_surface(
        setcolor=(255, 255, 255, 255), unsetcolor=(0, 0, 0, 0))
    right.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(right, (0, 0))

    # ── rim-light lift on the back + crown (claret left, blue right) ──────────
    _rim_light(surf)

    # ── THIN gold centre seam down the body so the two-tone split survives
    #     downsampling — clipped to the body so it doesn't overrun the edge ───
    seam = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    pygame.draw.line(seam, _SEAM, (HX, HY - 6), (HX, HY + 30), 1)
    seam.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(seam, (0, 0))

    # ── blue shorts waistband at the tail base (under the chest trim) ─────────
    pygame.draw.rect(surf, _BLUE_D, (16, HY + 22, 30, 6), border_radius=2)
    pygame.draw.rect(surf, _BLUE, (16, HY + 22, 30, 4), border_radius=2)
    pygame.draw.line(surf, _BLUE_H, (18, HY + 23), (44, HY + 23), 1)

    # ── ONE bold gold chest bar: 2px tall, full body width, hard edges, high
    #     saturation — the kit's signature horizontal line, set across the
    #     mid-chest below the collar. Clipped to the body so the bar stops at
    #     the silhouette instead of poking past into the wing. ───────────────
    bar = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    pygame.draw.rect(bar, _GOLD_D, (HX - 16, HY + 15, 32, 4))
    pygame.draw.rect(bar, _GOLD,   (HX - 16, HY + 15, 32, 2))
    bar.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(bar, (0, 0))

    # ── clean WHITE squad-number hint on the back jersey (claret half) — a
    #     simple bold rectangle, no blurry glyph to smear at thumbnail ────────
    pygame.draw.rect(surf, _OUTLINE, (HX - 16, HY + 6, 7, 8))
    pygame.draw.rect(surf, _WHITE,   (HX - 15, HY + 7, 5, 6))

    # ── ONE bold gold collar: a tight ARC at the neckline right under the head
    #     so it reads as a round collar, not a free-floating hoop ─────────────
    pygame.draw.arc(surf, _GOLD_D, (HX - 8, HY + 4, 17, 14), 3.40, 6.02, 3)
    pygame.draw.arc(surf, _GOLD,   (HX - 8, HY + 4, 17, 14), 3.40, 6.02, 2)
    pygame.draw.line(surf, _GOLD_H, (HX - 4, HY + 6), (HX + 3, HY + 6), 1)

    # ── blue cuff band on the (near) right wing so the blue sleeve reads as a
    #     kitted arm, not bare plumage ───────────────────────────────────────
    cuffx, cuffy = 48, HY + 2
    pygame.draw.line(surf, _BLUE_D, (cuffx - 5, cuffy + 4), (cuffx + 4, cuffy - 2), 5)
    pygame.draw.line(surf, _BLUE_HH, (cuffx - 4, cuffy + 3), (cuffx + 3, cuffy - 3), 1)

    # ── FACE: pale-claret cheek oval + dark eye + white catchlight so Pip
    #     reads as a friendly macaw; the beak (warm orange-yellow) is left as
    #     drawn by the base. The eye sits clear of the lifted sweatband. ───────
    eye_cx, eye_cy = HX + 3, HY - 2
    pygame.draw.ellipse(surf, _CLARET_HH, (eye_cx - 5, eye_cy - 3, 9, 8))    # cheek patch
    pygame.draw.ellipse(surf, (242, 200, 218), (eye_cx - 4, eye_cy - 2, 6, 6))
    pygame.draw.circle(surf, _EYE,   (eye_cx, eye_cy), 2)                    # eye
    pygame.draw.circle(surf, _WHITE, (eye_cx - 1, eye_cy - 1), 1)           # catchlight

    # ── short hair tuft hugging the crown: small rounded clumps clipped to the
    #     head so it reads as hair, not a dark slab floating over the bird ────
    hair = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    for hcx, hr in ((HX - 6, 3), (HX - 1, 4), (HX + 4, 3), (HX + 8, 2)):
        pygame.draw.circle(hair, _SKIN_DK, (hcx, CROWN_Y + 1), hr)
    for hcx in (HX - 3, HX + 3):
        pygame.draw.circle(hair, (84, 58, 42), (hcx, CROWN_Y), 1)   # strand sheen
    hair.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(hair, (0, 0))

    # ── thin sweatband lifted ABOVE the eye so it never merges with the face ──
    band = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    pygame.draw.rect(band, _SKIN_DK, (HX - 8, CROWN_Y + 4, 18, 3), border_radius=1)
    pygame.draw.line(band, (112, 82, 60), (HX - 7, CROWN_Y + 4), (HX + 8, CROWN_Y + 4), 1)
    band.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(band, (0, 0))

    # ── LEGS — the hero stack: a claret SOCK that bridges the body down into
    #     the shin guards (so the plates read as worn kit), chunky pale shin
    #     guards, then black cleats with gold studs ──────────────────────────
    for legx in (22, 35):
        # Claret sock segment connecting the body to the guard — a continuous
        # band so the bright plate is clearly strapped on a leg, not floating.
        pygame.draw.rect(surf, _CLARET_D, (legx - 1, 52, 10, 10), border_radius=3)
        pygame.draw.rect(surf, _CLARET,   (legx, 53, 8, 8), border_radius=3)
        pygame.draw.line(surf, _CLARET_H, (legx + 1, 54), (legx + 1, 60), 1)
        # Rolled-sock cuff just above the guard.
        pygame.draw.rect(surf, _CLARET_H, (legx, 58, 8, 2), border_radius=1)

        # Prominent shin guard: chunky pale rounded plate over the lower leg —
        # the standout tell, thick + bright + clearly armour at 40px.
        pygame.draw.rect(surf, _OUTLINE, (legx - 1, 61, 10, 13), border_radius=4)
        pygame.draw.rect(surf, _PLATE_D, (legx, 62, 8, 12), border_radius=4)
        pygame.draw.rect(surf, _PLATE,   (legx + 1, 62, 6, 10), border_radius=3)
        pygame.draw.line(surf, _PLATE_H, (legx + 2, 63), (legx + 2, 70), 1)  # ridge
        pygame.draw.line(surf, _PLATE_D, (legx, 65), (legx + 7, 65), 1)      # strap
        pygame.draw.line(surf, _PLATE_D, (legx, 70), (legx + 7, 70), 1)      # strap

        # Black cleat under the plate with two gold stud dots.
        pygame.draw.rect(surf, _BOOT, (legx - 1, 73, 11, 5), border_radius=2)
        pygame.draw.line(surf, _BOOT_H, (legx, 73), (legx + 8, 73), 1)
        pygame.draw.circle(surf, _GOLD, (legx + 1, 77), 1)
        pygame.draw.circle(surf, _GOLD, (legx + 7, 77), 1)


build = store_skins._make_skin(_paint, base_fn=_defender_base)
