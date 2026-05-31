"""
Small per-biome signature motif painters (the one hero structure each biome
places on the near-ridge baseline). Kept tiny — identity comes from silhouette
+ value against the sky_field gradient, not fine detail. Each reads the stage
palette's struct_* colors so it retints across all day-stages automatically.

ctx is a scene_engine.SceneCtx: (surf, w, h, ground_y, phase, scroll, pal, dpal).
"""
import math
import pygame


def _struct(ctx):
    p = ctx.pal
    return (p.get('struct_light', (200, 185, 160)),
            p.get('struct_mid', (165, 140, 110)),
            p.get('struct_dark', (110, 88, 66)),
            p.get('struct_accent', (140, 110, 80)))


# ── Group A signatures ────────────────────────────────────────────────────────

def draw_mesa_arch(ctx):
    """A flat-topped sandstone butte with an eroded arch window beside a smaller
    stack — the desert-mesa hero silhouette."""
    surf, w, gy = ctx.surf, ctx.w, ctx.ground_y
    light, mid, dark, accent = _struct(ctx)
    bx = int(w * 0.60)
    top = gy - int(gy * 0.30)
    bw = int(w * 0.30)
    # Main butte body (flat top, slightly battered sides).
    body = [(bx, gy), (bx + 6, top), (bx + bw - 6, top), (bx + bw, gy)]
    pygame.draw.polygon(surf, mid, body)
    # Shadowed right face.
    pygame.draw.polygon(surf, dark,
                        [(bx + bw // 2, top), (bx + bw - 6, top),
                         (bx + bw, gy), (bx + bw // 2, gy)])
    # Sunlit cap rim.
    pygame.draw.line(surf, light, (bx + 6, top), (bx + bw - 6, top), 3)
    # Arch window carved through the lower body.
    ax = bx + int(bw * 0.5)
    ay = gy - int(gy * 0.10)
    arch = pygame.Surface((w, gy), pygame.SRCALPHA)
    pygame.draw.ellipse(arch, (0, 0, 0, 0), (0, 0, 1, 1))  # keep SRCALPHA
    # punch the arch by drawing sky-colored hole? Instead draw arch as two legs.
    leg_w = max(4, int(bw * 0.12))
    pygame.draw.arc(surf, dark, (ax - 18, ay - 30, 36, 60), math.radians(20),
                    math.radians(160), leg_w)
    # Smaller companion stack to the left.
    sx = bx - int(bw * 0.55)
    st = gy - int(gy * 0.18)
    sw = int(bw * 0.42)
    pygame.draw.polygon(surf, mid, [(sx, gy), (sx + 4, st), (sx + sw - 4, st), (sx + sw, gy)])
    pygame.draw.line(surf, light, (sx + 4, st), (sx + sw - 4, st), 2)


def draw_basalt_columns(ctx):
    """A bundle of vertical basalt columns with a lava-ember glow that rides the
    night-ness of the stage — the volcanic-caldera hero."""
    surf, w, gy = ctx.surf, ctx.w, ctx.ground_y
    light, mid, dark, accent = _struct(ctx)
    base = int(w * 0.52)
    n = 7
    cw = int(w * 0.045)
    glow = ctx.pal.get('glow_color', (255, 110, 40))
    # Ember glow pooled at the column bases, stronger on darker stages.
    from scene_engine import soft_disc
    night = max(0.0, min(1.0, (95 - (0.2126 * ctx.pal.get('sky_top', (0,0,0))[0]
                                     + 0.7152 * ctx.pal.get('sky_top', (0,0,0))[1]
                                     + 0.0722 * ctx.pal.get('sky_top', (0,0,0))[2])) / 75.0))
    if night > 0.05:
        s = pygame.Surface((w, gy), pygame.SRCALPHA)
        pygame.draw.ellipse(s, (*glow, int(120 * night)),
                            (base - cw, gy - 26, n * cw + 2 * cw, 40))
        surf.blit(s, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
    for i in range(n):
        x = base + i * cw
        ch = gy - int(gy * (0.16 + 0.10 * abs(math.sin(i * 1.3))))
        col = mid if i % 2 else dark
        pygame.draw.rect(surf, col, (x, ch, cw - 1, gy - ch))
        pygame.draw.line(surf, light, (x, ch), (x + cw - 2, ch), 2)
    # Lava seam glowing at the base.
    pygame.draw.line(surf, glow, (base - cw, gy - 2), (base + n * cw, gy - 2), 3)


def draw_stilt_houses(ctx):
    """A small cluster of stilt houses over water with a reflection — the misty
    karst water-town hero."""
    surf, w, gy = ctx.surf, ctx.w, ctx.ground_y
    light, mid, dark, accent = _struct(ctx)
    water = ctx.pal.get('water_tint', (90, 120, 130))
    # Reflection band just below the houses.
    cx = int(w * 0.55)
    for i, dx in enumerate((-40, 0, 38)):
        x = cx + dx
        hw = 22 - i % 2 * 4
        hh = 18
        roof_y = gy - 30 - (i % 2) * 6
        # stilts
        for sxp in (x - hw // 2 + 3, x + hw // 2 - 3):
            pygame.draw.line(surf, dark, (sxp, gy), (sxp, roof_y + hh), 2)
        # body
        pygame.draw.rect(surf, mid, (x - hw // 2, roof_y, hw, hh))
        # roof
        pygame.draw.polygon(surf, dark, [(x - hw // 2 - 3, roof_y),
                                         (x + hw // 2 + 3, roof_y),
                                         (x, roof_y - 10)])
        pygame.draw.line(surf, light, (x - hw // 2 - 3, roof_y), (x, roof_y - 10), 1)
    # Soft water reflection streak.
    s = pygame.Surface((w, gy), pygame.SRCALPHA)
    pygame.draw.ellipse(s, (*water, 60), (cx - 60, gy - 8, 120, 12))
    surf.blit(s, (0, 0))


def draw_summit_shrine(ctx):
    """A tiny ridge-top shrine + prayer flags for the alpine biome (mostly the
    ridge snow-caps carry it, this just adds a human mark)."""
    surf, w, gy = ctx.surf, ctx.w, ctx.ground_y
    light, mid, dark, accent = _struct(ctx)
    x = int(w * 0.5)
    y = gy - int(gy * 0.30)
    pygame.draw.rect(surf, mid, (x - 8, y, 16, 18))
    pygame.draw.polygon(surf, dark, [(x - 11, y), (x + 11, y), (x, y - 10)])
    pygame.draw.line(surf, light, (x - 11, y), (x, y - 10), 1)
    # a couple of flag lines
    pygame.draw.line(surf, accent, (x + 8, y + 2), (x + 30, y + 10), 1)
