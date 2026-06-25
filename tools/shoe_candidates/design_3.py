import pygame


# NEON CIRCUIT — LED light-up cyber high-top (epic). The whole read is EMISSION:
# a near-black tech upper that recedes so the lit cues are the silhouette — an
# electric-blue→magenta sole light-strip with a soft halo, circuit-trace lines
# climbing the side panel, glowing eyelets, and a light-up heel chevron. The
# glow is faked the cheap procedural way: a few expanding low-alpha strokes laid
# under each bright core line on an SRCALPHA temp, so the neon reads as light
# spilling outward rather than a flat coloured line — and survives the 40px foot.
# Geometry is proportional so the same call serves product-shot and bird-foot.
# Like RETRO 1 the collar rises above the box top (t < 0); callers reserve it.

_BLACK    = ( 14,  16,  24)   # near-black tech upper
_BLACK_D  = (  8,   9,  15)   # darker seams / sole body
_BLACK_HI = ( 30,  34,  48)   # cool panel sheen so it reads tech, not matte
_CYAN     = ( 25, 224, 255)   # electric-blue glow (strip front)
_MAGENTA  = (255,  60, 199)   # magenta glow (strip rear)
_VIOLET   = (122,  72, 255)   # violet mid-blend
_HOT      = (221, 246, 255)   # hot light core


def _lerp(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def draw_shoe(surf, x, y, w, h, facing=1):
    """Draw a single side-profile NEON CIRCUIT high-top into box (x,y,w,h)."""
    def px(t):
        return x + (t * w if facing == 1 else (1.0 - t) * w)

    def py(t):
        return y + t * h

    def P(t):
        return (px(t[0]), py(t[1]))

    def poly(color, pts):
        pygame.draw.polygon(surf, color, [P(p) for p in pts])

    def line(color, a, b, width):
        pygame.draw.line(surf, color, P(a), P(b), max(1, int(round(width))))

    # A dedicated SRCALPHA layer for every emissive cue: glow halos are additive
    # low-alpha strokes that must spill past the dark upper without darkening it.
    glow = pygame.Surface(surf.get_size(), pygame.SRCALPHA)

    def gline(a, b, color, core_w, halo_w, layers=4):
        """Emissive line — widening low-alpha halo passes under a hot core."""
        pa, pb = P(a), P(b)
        for i in range(layers, 0, -1):
            f = i / layers
            wpx = max(1, int(round(core_w + (halo_w - core_w) * f)))
            alpha = int(46 * (1.0 - f) + 18)
            pygame.draw.line(glow, (*color, alpha), pa, pb, wpx)
        pygame.draw.line(glow, (*_lerp(color, _HOT, 0.5), 235), pa, pb,
                         max(1, int(round(core_w))))

    def gdot(t, color, core_r, halo_r):
        cx, cy = P(t)
        for i in range(4, 0, -1):
            f = i / 4
            r = max(1, int(round(core_r + (halo_r - core_r) * f)))
            alpha = int(50 * (1.0 - f) + 22)
            pygame.draw.circle(glow, (*color, alpha), (cx, cy), r)
        pygame.draw.circle(glow, (*_lerp(color, _HOT, 0.6), 240),
                           (cx, cy), max(1, int(round(core_r))))

    sole_top = 0.82

    # ── dark outsole body ──────────────────────────────────────────────────────
    # Black tread block; the light-strip sits as a channel just above it.
    poly(_BLACK_D, [
        (0.03, 1.00), (0.95, 1.00), (0.98, 0.93),
        (0.91, 0.905), (0.06, 0.905), (0.03, 0.95),
    ])
    poly(_BLACK, [
        (0.05, 0.94), (0.07, sole_top), (0.92, sole_top),
        (0.96, 0.905), (0.95, 0.95), (0.92, 0.965), (0.07, 0.965),
    ])

    # ── near-black tech upper ───────────────────────────────────────────────────
    # One continuous dark mass: toe → instep → tall heel counter, with a cool
    # sheen facet up the side so it reads as moulded tech panel, not flat ink.
    upper = [
        (0.07, sole_top), (0.07, 0.40), (0.13, 0.30), (0.24, 0.30),
        (0.34, 0.26), (0.62, 0.30), (0.80, 0.40), (0.90, 0.56),
        (0.93, 0.70), (0.93, sole_top),
    ]
    poly(_BLACK, upper)
    # Cool panel sheen — a slim lighter facet down the instep.
    poly(_BLACK_HI, [
        (0.34, 0.30), (0.50, 0.31), (0.56, 0.46), (0.40, 0.44),
    ])
    # Heel counter darker block so the chevron pops on it.
    poly(_BLACK_D, [
        (0.07, sole_top), (0.07, 0.40), (0.20, 0.34), (0.20, sole_top),
    ])

    # ── tall lit collar (HERO rises above box top, t < 0) ───────────────────────
    # A padded black cyber cuff; a thin neon rim line traces its open top so the
    # high-top silhouette itself reads as a lit ring.
    collar = [
        (0.13, 0.42), (0.125, 0.06), (0.17, -0.12), (0.27, -0.16),
        (0.40, -0.10), (0.45, 0.10), (0.42, 0.34), (0.30, 0.40),
        (0.20, 0.40),
    ]
    poly(_BLACK, collar)
    poly(_BLACK_HI, [
        (0.125, 0.06), (0.17, -0.12), (0.27, -0.16), (0.24, -0.10),
        (0.18, -0.06), (0.155, 0.06),
    ])

    # ── circuit-trace lines climbing the side panel ─────────────────────────────
    # Right-angled "PCB" traces with node dots — the tech-panel signature. Drawn
    # as cyan emissive so they glow faintly without competing with the strip.
    trace_w = max(1, w * 0.013)
    halo = w * 0.045
    gline((0.40, 0.66), (0.40, 0.50), _CYAN, trace_w, halo, layers=3)
    gline((0.40, 0.50), (0.54, 0.50), _CYAN, trace_w, halo, layers=3)
    gline((0.54, 0.50), (0.54, 0.40), _CYAN, trace_w, halo, layers=3)
    gline((0.60, 0.64), (0.72, 0.64), _VIOLET, trace_w, halo, layers=3)
    gline((0.72, 0.64), (0.72, 0.54), _VIOLET, trace_w, halo, layers=3)
    gdot((0.54, 0.40), _CYAN, max(1, w * 0.012), w * 0.030)
    gdot((0.40, 0.66), _CYAN, max(1, w * 0.011), w * 0.026)
    gdot((0.72, 0.54), _VIOLET, max(1, w * 0.012), w * 0.030)

    # ── glowing lace eyelets ────────────────────────────────────────────────────
    # A short diagonal row of lit eyelets up the throat — the brightest small
    # cues, so the lacing reads even before the strip at tiny scale.
    eyelets = [(0.32, 0.46), (0.38, 0.40), (0.45, 0.35), (0.52, 0.31)]
    for i, e in enumerate(eyelets):
        c = _lerp(_CYAN, _MAGENTA, i / (len(eyelets) - 1))
        gdot(e, c, max(1, w * 0.013), w * 0.034)
    # Faint lace strokes zig-zagging between eyelets so it reads laced.
    lace_w = max(1, h * 0.030)
    for i in range(len(eyelets) - 1):
        a, b = eyelets[i], eyelets[i + 1]
        line((150, 170, 200), (a[0], a[1] + 0.04), (b[0], b[1] + 0.04), lace_w)

    # ── light-up heel chevron ───────────────────────────────────────────────────
    # A bold "<" mark stacked on the heel counter — a strong rear cue that holds
    # at 40px even when the fine traces blur out.
    cw = max(1, w * 0.018)
    chal = w * 0.055
    gline((0.155, 0.42), (0.105, 0.55), _MAGENTA, cw, chal, layers=4)
    gline((0.105, 0.55), (0.155, 0.68), _MAGENTA, cw, chal, layers=4)

    # ── electric-blue→magenta LED sole strip with halo (the silhouette read) ────
    # A continuous lit channel along the whole midsole, colour-shifting blue→
    # magenta front-to-back. Built as many short segments so the gradient is
    # smooth and the halo blooms evenly under it — this is the dominant glow.
    sy0, sy1 = 0.80, 0.815
    x0, x1 = 0.085, 0.915
    segs = 16
    sole_w = max(1, h * 0.075)
    sole_halo = h * 0.34
    for s in range(segs):
        t0 = s / segs
        t1 = (s + 1) / segs
        ax = x0 + (x1 - x0) * t0
        bx = x0 + (x1 - x0) * t1
        ay = sy0 + (sy1 - sy0) * t0
        by = sy0 + (sy1 - sy0) * t1
        # blue at the toe (right) shifting to magenta at the heel (left)
        col = _lerp(_MAGENTA, _CYAN, t0)
        gline((ax, ay), (bx, by), col, sole_w, sole_halo, layers=5)

    # Composite all emission over the dark shoe — additive-ish blend so halos
    # brighten the sky behind without muddying the black upper.
    surf.blit(glow, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
