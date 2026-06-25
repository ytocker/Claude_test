"""HIKER CANTEEN — vintage scout field-flask parcel cosmetic.

A round, slightly flattened canvas-OLIVE canteen carried below Pip. The IDENTITY
is the SILHOUETTE: a near-circular, squat body (a field canteen, not an upright
bottle) topped by a short steel NECK + a chunky steel screw CAP, with a STRAP
loop arcing off the cap. The round flattened mass + cap + strap is a wholly
different outline from the shipped tall straight-walled squeeze bottle, so the
swap reads at a glance before colour even registers.

22px read tradeoffs (WHY): a real canteen carries stitching, ridges and buckles
that all dissolve at this size, so the body is reduced to ONE bold olive disc
with a single dark stitched SEAM running just inside the rim and ONE rivet — more
detail than that just muddies the disc under the rotozoom. The body is drawn
slightly WIDER than tall (a flattened canteen, not a ball) because a true circle
reads as a generic blob while the squashed disc keeps the canteen character. The
steel cap is kept high-value and a touch oversized so it stays the metal accent
against the olive even when banked to 90deg, and the strap loop is drawn as a
solid filled arc (not a thin line) so it survives the downscale instead of
vanishing. Built on a 44px work surface then smoothscaled to 22 so the disc rim,
seam and strap antialias cleanly. A baked dark OUTLINE (inflated, drawn first)
carries the shape on bright DAY sky; a warm keyline rim inside is the NIGHT
lifeline; everything is held off the surface edges so the gameplay rotozoom never
clips the cap or the strap loop.
"""
import pygame

# Tight palette: canvas olive body with a darker shade for the lower volume, a
# cool steel cap/neck (the grayscale-safe metal accent against the warm olive),
# a dark leather strap, a dark outline for day, and a warm keyline for night.
OLIVE = (126, 138,  78)        # canvas-olive body (upper, lit)
OLIVE_SH = ( 86,  94,  50)     # olive shade — lower body volume
SEAM = ( 70,  76,  42)         # stitched seam just inside the rim
STEEL = (174, 182, 192)        # steel screw cap + neck
STEEL_HI = (216, 222, 230)     # cap top highlight
STEEL_SH = (120, 128, 140)     # cap groove / underside
STRAP = ( 74,  58,  40)        # leather strap loop
RIVET = (150, 158, 168)        # single metal rivet
OUTLINE = ( 42,  46,  28)      # dark, high-value: reads on bright day sky
KEYLINE = (196, 204, 150)      # warm olive rim — the NIGHT lifeline


def build(mode="normal") -> pygame.Surface:
    # Mode-agnostic: one static canteen sprite for every Pip skin.
    S = 44
    surf = pygame.Surface((S, S), pygame.SRCALPHA)
    cx = S // 2

    # Body: a flattened disc — wider than tall so it reads as a canteen, not a
    # ball. Centre dropped slightly to leave room for the cap + strap above,
    # held well off the edges so the rotozoom never clips.
    BW, BH = 30, 26               # body width / height (flattened ellipse)
    body_cy = 27
    body_rect = pygame.Rect(cx - BW // 2, body_cy - BH // 2, BW, BH)

    # Neck: a short steel step bridging the body top and the cap.
    NW, NH = 9, 5
    neck_rect = pygame.Rect(cx - NW // 2, body_rect.top - NH + 2, NW, NH)

    # Cap: a chunky steel screw cap, slightly wider than the neck, sitting above.
    CW, CH = 15, 8
    cap_rect = pygame.Rect(cx - CW // 2, neck_rect.top - CH + 1, CW, CH)

    # Strap loop: a stout ring off the cap's shoulder. Drawn beside the cap (not
    # hidden behind the body) and as a fat ring so it survives the downscale as
    # an unmistakable carry-loop — the cue that separates a canteen from a flask.
    strap_c = (cap_rect.left - 4, cap_rect.centery + 1)

    # --- Baked dark OUTLINE (drawn first, slightly inflated) for the DAY read.
    pygame.draw.ellipse(surf, OUTLINE, body_rect.inflate(4, 4))
    pygame.draw.rect(surf, OUTLINE, neck_rect.inflate(4, 2), border_radius=1)
    pygame.draw.rect(surf, OUTLINE, cap_rect.inflate(4, 4), border_radius=2)
    # Strap loop outline: a fat dark ring on the cap's shoulder.
    strap_out = pygame.Rect(0, 0, 16, 16)
    strap_out.center = strap_c
    pygame.draw.ellipse(surf, OUTLINE, strap_out)

    # --- STRAP loop body: leather ring on its own surface so the centre hole is
    # punched to true transparency (BLEND_RGBA_MULT by a transparent disc), then
    # composited (reads as a carry loop, not a solid blob).
    sl = pygame.Surface((16, 16), pygame.SRCALPHA)
    pygame.draw.ellipse(sl, STRAP, pygame.Rect(1, 1, 13, 13))
    punch = pygame.Surface((16, 16), pygame.SRCALPHA)
    punch.fill((255, 255, 255, 255))
    hole = pygame.Rect(0, 0, 7, 7)
    hole.center = (8, 8)
    pygame.draw.ellipse(punch, (0, 0, 0, 0), hole)
    sl.blit(punch, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(sl, (strap_c[0] - 8, strap_c[1] - 8))

    # --- BODY: olive disc with a vertical shade so it reads as a round volume.
    body = pygame.Surface((body_rect.w, body_rect.h), pygame.SRCALPHA)
    for y in range(body_rect.h):
        t = y / max(1, body_rect.h - 1)
        c = (
            int(OLIVE[0] + (OLIVE_SH[0] - OLIVE[0]) * t),
            int(OLIVE[1] + (OLIVE_SH[1] - OLIVE[1]) * t),
            int(OLIVE[2] + (OLIVE_SH[2] - OLIVE[2]) * t),
        )
        body.fill(c + (255,), pygame.Rect(0, y, body_rect.w, 1))
    mask = pygame.Surface((body_rect.w, body_rect.h), pygame.SRCALPHA)
    pygame.draw.ellipse(mask, (255, 255, 255, 255), mask.get_rect())
    body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(body, body_rect.topleft)

    # --- Stitched SEAM: one dark ring just inside the rim — the canvas-canteen
    # cue. A single inset ellipse, no more, so the disc stays clean at 22px.
    seam_rect = body_rect.inflate(-7, -7)
    pygame.draw.ellipse(surf, SEAM, seam_rect, width=1)

    # --- One metal RIVET on the upper body — a single bright dot, the only
    # hardware detail the disc can carry without muddying.
    rivet_c = (body_rect.centerx + 6, body_rect.top + 8)
    pygame.draw.circle(surf, OUTLINE, rivet_c, 2)
    pygame.draw.circle(surf, RIVET, rivet_c, 1)

    # --- Soft top-left sheen on the disc so it reads as a curved canvas volume.
    pygame.draw.ellipse(surf, OLIVE,
                        pygame.Rect(body_rect.x + 4, body_rect.y + 3, 9, 7))

    # --- NECK fill (steel, between body and cap).
    pygame.draw.rect(surf, STEEL, neck_rect)
    pygame.draw.line(surf, STEEL_SH,
                     (neck_rect.x, neck_rect.bottom - 1),
                     (neck_rect.right - 1, neck_rect.bottom - 1), 1)

    # --- CAP: chunky steel screw cap with a flat top highlight + a hard groove
    # at the cap/neck join so it reads as a screw-on lid, not a painted band.
    pygame.draw.rect(surf, STEEL, cap_rect, border_radius=2)
    pygame.draw.line(surf, STEEL_HI,
                     (cap_rect.x + 2, cap_rect.y + 1),
                     (cap_rect.right - 3, cap_rect.y + 1), 1)
    pygame.draw.line(surf, STEEL_SH,
                     (cap_rect.x + 1, cap_rect.bottom - 2),
                     (cap_rect.right - 2, cap_rect.bottom - 2), 1)
    # Hard cap/neck groove — a dark line so the lid screws on.
    pygame.draw.line(surf, OUTLINE,
                     (cap_rect.x, cap_rect.bottom),
                     (cap_rect.right - 1, cap_rect.bottom), 1)

    # --- Warm keyline rim INSIDE the outline — the NIGHT lifeline that glows on
    # dark sky while staying subtle on day. Traces the disc + cap.
    pygame.draw.ellipse(surf, KEYLINE, body_rect, width=1)
    pygame.draw.rect(surf, KEYLINE, cap_rect, width=1, border_radius=2)

    return pygame.transform.smoothscale(surf, (22, 22))
