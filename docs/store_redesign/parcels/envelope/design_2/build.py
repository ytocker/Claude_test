"""LOVE LETTER — LOW-tier ENVELOPE parcel cosmetic, DESIGN 2.

A sweet sealed billet-doux. Same slab problem as the original mailer: a ~22px
flat object that must survive Pip's bank without collapsing into "a card". The
identity here is the glossy red HEART wax seal dead-centre at the flap point —
so it is drawn BOLD and last, sized to read as a heart (not a round dot) even
after the smoothscale down to 22px. The blush body + darker rose flap V + cream
inner-edge sliver give the envelope read at every angle; the heart carries the
romance. Built on a 44px work surface then smoothscaled to 22 (same scaffold as
the mailer) with a baked dark outline for DAY sky and a warm keyline for NIGHT.
"""
import pygame

from game.draw import lerp_color as _lerp_color

# DAY blush body / rose flap / red heart, plus a warm keyline so the slab still
# reads against a dark sky without changing the sprite per mode.
PINK_HI = (247, 197, 207)      # ~#F7C5CF — top of body gradient
PINK_BASE = (244, 184, 196)    # ~#F4B8C4 — concept body
PINK_SHADE = (224, 156, 170)   # lower body, gives the slab volume
ROSE_FLAP = (217, 126, 146)    # ~#D97E92 — closing flap V
ROSE_FLAP_SHADE = (190, 104, 124)
CREAM = (246, 233, 221)        # ~#F6E9DD — inner letter edge under the flap
HEART = (216, 58, 74)          # ~#D83A4A — wax-seal red
HEART_HI = (240, 120, 132)     # glossy lift
HEART_SHADE = (162, 38, 52)
RIBBON = (200, 92, 112)        # rose ribbon tail, a hair darker than the flap
OUTLINE = (90, 42, 51)         # ~#5A2A33 — dark, reads on bright day sky
KEYLINE = (250, 214, 222)      # warm blush rim — the NIGHT lifeline


def build(mode="normal") -> pygame.Surface:
    # Mode-agnostic: one static slab sprite for every Pip skin.
    S = 44
    surf = pygame.Surface((S, S), pygame.SRCALPHA)

    # Slab body, kept well off the surface edges so the gameplay rotozoom never
    # clips the corners at any bank angle.
    BW, BH = 34, 26
    cx, cy = S // 2, S // 2
    rect = pygame.Rect(cx - BW // 2, cy - BH // 2, BW, BH)
    rad = 4

    # Baked outline frame (drawn first, slightly inflated) — the dark silhouette
    # that survives on the (170,220,245) day sky.
    pygame.draw.rect(surf, OUTLINE, rect.inflate(6, 6), border_radius=rad + 2)

    # Blush body: gentle vertical gradient masked to the rounded rect, giving the
    # flat card a touch of volume so it never reads as a paper cut-out.
    body = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    for y in range(rect.h):
        t = y / max(1, rect.h - 1)
        row = _lerp_color(PINK_HI, PINK_SHADE, t)
        body.fill(row + (255,), pygame.Rect(0, y, rect.w, 1))
    mask = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(),
                     border_radius=rad)
    body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(body, rect.topleft)

    # Closing flap — a downward V from the two top corners to the flap point at
    # centre. This is the envelope read. Dark under-edge first (its own outline
    # over the body), then the rose fill, then a shade triangle on the right half
    # so the V has a folded-paper lift. The flap is the UPPER triangle of the
    # body; below it the cream letter shows, so the closed envelope reads as
    # holding a real letter.
    top_l = (rect.x + 1, rect.y + 1)
    top_r = (rect.right - 1, rect.y + 1)
    flap_pt = (cx, rect.y + int(rect.h * 0.60))

    # Cream inner-letter wedge peeking under the flap: the lower-centre triangle
    # from the flap point down to the bottom edge, so a clear cream notch shows
    # below the rose V. Masked to the rounded body so it never bleeds past the
    # corners.
    cream = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    lx, ly = top_l[0] - rect.x, top_l[1] - rect.y
    rx, ry0 = top_r[0] - rect.x, top_r[1] - rect.y
    fx, fy = flap_pt[0] - rect.x, flap_pt[1] - rect.y
    pygame.draw.polygon(cream, CREAM + (255,),
                        [(lx + 2, fy - 1), (fx, fy + 2), (rx - 2, ry0 + fy - 1),
                         (rx - 2, rect.h - 2), (lx + 2, rect.h - 2)])
    cream.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(cream, rect.topleft)

    # Dark seam under the flap's lower diagonals so flap and letter separate.
    pygame.draw.line(surf, OUTLINE, (top_l[0] + 1, top_l[1]), flap_pt, 1)
    pygame.draw.line(surf, OUTLINE, (top_r[0] - 1, top_r[1]), flap_pt, 1)

    pygame.draw.polygon(surf, OUTLINE,
                        [(top_l[0] - 1, top_l[1] - 1),
                         (top_r[0] + 1, top_r[1] - 1),
                         (flap_pt[0], flap_pt[1] + 1)])
    pygame.draw.polygon(surf, ROSE_FLAP, [top_l, top_r, flap_pt])
    # Right-half shade triangle = the fold crease catching less light.
    pygame.draw.polygon(surf, ROSE_FLAP_SHADE,
                        [(cx, top_l[1]), top_r, flap_pt])

    # Warm keyline rim INSIDE the outline — a glowing blush edge on night sky,
    # subtle on day. Drawn after the flap so the whole closed shape is ringed.
    pygame.draw.rect(surf, KEYLINE, rect, width=1, border_radius=rad)

    # Ribbon tail — a tiny rose streamer dropping from below the seal, so the
    # billet-doux reads as tied/gifted. Kept small so it never competes with the
    # heart. Two short legs forming a narrow V tail.
    ry = flap_pt[1] + 2
    pygame.draw.line(surf, OUTLINE, (cx, ry), (cx - 4, ry + 7), 3)
    pygame.draw.line(surf, OUTLINE, (cx, ry), (cx + 4, ry + 7), 3)
    pygame.draw.line(surf, RIBBON, (cx, ry), (cx - 4, ry + 6), 2)
    pygame.draw.line(surf, RIBBON, (cx, ry), (cx + 4, ry + 6), 2)

    # HEART wax seal — the identity. Built BOLD from two lobe circles + a lower
    # point triangle so it reads as a HEART, not a dot, after the smoothscale to
    # 22px. Dark outline halo first for a firm anchor on both skies, then the red
    # fill, then a glossy highlight on the upper-left lobe = wax sheen.
    hcx, hcy = cx, flap_pt[1] - 1     # centred on the flap point — the romance
    lobe_r = 4
    lobe_dx = 3
    bottom = (hcx, hcy + 8)

    def _heart(color, cxx, cyy, lr, dx, bot):
        pygame.draw.circle(surf, color, (cxx - dx, cyy), lr)
        pygame.draw.circle(surf, color, (cxx + dx, cyy), lr)
        pygame.draw.polygon(surf, color,
                            [(cxx - dx - lr + 1, cyy + 1),
                             (cxx + dx + lr - 1, cyy + 1),
                             bot])

    # Outline halo (slightly larger) so the heart stays crisp on bright sky.
    _heart(OUTLINE, hcx, hcy, lobe_r + 1, lobe_dx, (bottom[0], bottom[1] + 1))
    _heart(HEART, hcx, hcy, lobe_r, lobe_dx, bottom)
    # Lower-right shade lobe for a waxy 3D bead read.
    pygame.draw.circle(surf, HEART_SHADE, (hcx + lobe_dx, hcy + 1), lobe_r - 1)
    pygame.draw.polygon(surf, HEART_SHADE,
                        [(hcx, hcy + 1), (hcx + lobe_dx + lobe_r - 1, hcy + 1),
                         bottom])
    # Re-lay the red core so the shade only darkens the rim, keeping it red.
    pygame.draw.circle(surf, HEART, (hcx - lobe_dx, hcy), lobe_r - 1)
    pygame.draw.circle(surf, HEART, (hcx + lobe_dx, hcy), lobe_r - 2)
    pygame.draw.polygon(surf, HEART,
                        [(hcx - lobe_dx - lobe_r + 2, hcy + 1),
                         (hcx + lobe_dx + lobe_r - 3, hcy + 1),
                         (bottom[0], bottom[1] - 1)])
    # Glossy sheen on the upper-left lobe = wax catching light.
    pygame.draw.circle(surf, HEART_HI, (hcx - lobe_dx - 1, hcy - 1), 1)

    return pygame.transform.smoothscale(surf, (22, 22))
