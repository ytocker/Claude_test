import math

import pygame


# AFTERBURNER — legendary rocket-thruster boot. The hero read is THRUST: a
# chrome/steel mecha boot shell with a rear exhaust nozzle at the heel and a
# layered flame plume (red outer → orange → white-hot core) streaming BEHIND
# the boot, blasting past the box on the low-t (heel) side. Chrome is sold by a
# bright top highlight + steel underside shadow on every plate so it reads
# metallic, not flat grey; riveted plating + glowing heat vents add the mecha
# detail. The flame is the signature — it is drawn on a soft SRCALPHA glow layer
# so even at 40px the eye sees a hot exhaust trail, not just a boot.
#
# Geometry is proportional in facing=1 (toe right, heel/exhaust left) space and
# mirrors for facing=-1 so one body of shapes serves both directions. The plume
# deliberately runs to t<0 (behind the heel) AND slightly above the box, so
# callers must leave rear + top headroom or it clips.

_CHROME   = (201, 210, 219)   # bright chrome plate
_CHROME_HI = (242, 247, 252)  # chrome specular highlight (the metal "shine")
_STEEL    = (110, 122, 136)   # steel mid
_STEEL_D  = ( 64,  72,  84)   # steel underside shadow
_PLATE_D  = ( 42,  46,  54)   # dark plating / seams / nozzle mouth
_RIVET    = (225, 232, 238)   # rivet dot

_FLAME_RED = (226,  40,  16)  # outer plume
_FLAME_ORG = (255, 122,  26)  # mid plume
_FLAME_YEL = (255, 226, 122)  # inner flame
_FLAME_WHT = (255, 252, 232)  # white-hot core
_VENT_GLOW = (255, 150,  40)  # heat-vent glow


def draw_shoe(surf, x, y, w, h, facing=1):
    """Draw a single side-profile AFTERBURNER rocket boot into box (x,y,w,h)."""
    def px(t):
        return x + (t * w if facing == 1 else (1.0 - t) * w)

    def py(t):
        return y + t * h

    def poly(color, pts):
        pygame.draw.polygon(surf, color, [(px(a), py(b)) for a, b in pts])

    def line(color, a, b, width):
        pygame.draw.line(surf, color, (px(a[0]), py(a[1])),
                         (px(b[0]), py(b[1])), max(1, int(round(width))))

    sole_top = 0.78

    # ── FLAME PLUME (drawn first, behind the boot, on a soft glow layer) ─────────
    # Layered concentric tongues streaming back from the heel nozzle (~t=0.06)
    # toward and past the box's rear edge (t<0). Painted onto an SRCALPHA temp at
    # an upscaled resolution so the hot edges bloom softly when blitted back —
    # the difference between "a boot" and "a ROCKET boot" at small scale.
    # The glow temp spans a fixed box-t window [T_MIN,T_MAX] (T_MIN<0 behind the
    # heel, T_MAX overlapping the nozzle) and is blitted back over exactly that
    # window — so the plume connects to the nozzle with no hard clip at t=0, and
    # the soft bloom survives downscale. Vertically it spans 2× box height,
    # centred on the heel mid-line, with the same overshoot above/below.
    T_MIN, T_MAX = -0.80, 0.18
    ss = 3  # supersample so concentric flame edges read smooth after bloom
    span = T_MAX - T_MIN
    gw = max(2, int(round(w * span * ss)))
    gh = max(2, int(round(h * 2 * ss)))
    glow = pygame.Surface((gw, gh), pygame.SRCALPHA)
    gy0 = h * ss * 1.0  # plume mid-line inside the 2×-tall temp

    def gpt(t, b):
        gx = (t - T_MIN) * w * ss
        return (gx, gy0 + b * h * ss)

    # Each flame layer is a tapering tongue: wide root at the nozzle, pinched
    # tail trailing back. Stacked red→orange→yellow→white so the core stays
    # hottest. The tail runs to t≈-0.78 (well past the box) for a long thrust.
    flame_layers = (
        (_FLAME_RED, (-0.78, 0.16), (-0.36, -0.22), (0.16, -0.06),
                     (0.16, 0.42), (-0.36, 0.54)),
        (_FLAME_ORG, (-0.58, 0.17), (-0.26, -0.09), (0.14, 0.02),
                     (0.14, 0.35), (-0.26, 0.45)),
        (_FLAME_YEL, (-0.38, 0.18), (-0.16, 0.03), (0.12, 0.09),
                     (0.12, 0.29), (-0.16, 0.36)),
        (_FLAME_WHT, (-0.22, 0.19), (-0.07, 0.11), (0.10, 0.14),
                     (0.10, 0.25), (-0.07, 0.31)),
    )
    for col, *pts in flame_layers:
        a = 250 if col is _FLAME_WHT else 220
        pygame.draw.polygon(glow, (*col, a), [gpt(t, b) for t, b in pts])

    # Ember sparks flung off the tail — tiny bright motes that say "exhaust".
    for et, eb, er in ((-0.64, 0.04, 0.06), (-0.50, 0.40, 0.05),
                       (-0.78, 0.24, 0.045), (-0.44, -0.10, 0.045)):
        cx, cy = gpt(et, eb)
        pygame.draw.circle(glow, (*_FLAME_YEL, 235), (int(cx), int(cy)),
                           max(1, int(er * h * ss)))

    soft = pygame.transform.smoothscale(glow, (max(1, int(w * span)), int(h * 2)))
    surf.blit(soft, (px(T_MIN if facing == 1 else T_MAX) -
                     (0 if facing == 1 else int(w * span)), py(0.0) - h))

    # ── dark exhaust nozzle bell at the heel ─────────────────────────────────────
    # A flared bell mouth the plume erupts from; the dark mouth + steel ring make
    # the thrust source read as machinery, not a fire decal.
    poly(_PLATE_D, [
        (0.04, 0.30), (0.10, 0.27), (0.13, 0.40),
        (0.13, 0.62), (0.10, 0.74), (0.04, 0.70),
    ])
    poly(_STEEL, [
        (0.10, 0.27), (0.16, 0.31), (0.16, 0.70),
        (0.10, 0.74), (0.13, 0.62), (0.13, 0.40),
    ])
    poly(_STEEL_D, [
        (0.10, 0.62), (0.16, 0.58), (0.16, 0.70), (0.10, 0.74),
    ])

    # ── chrome sole / thruster underframe ────────────────────────────────────────
    poly(_PLATE_D, [
        (0.13, 1.00), (0.92, 1.00), (0.97, 0.92),
        (0.90, 0.88), (0.16, 0.88), (0.13, 0.94),
    ])
    poly(_CHROME, [
        (0.13, 0.93), (0.16, sole_top), (0.90, sole_top),
        (0.96, 0.875), (0.96, 0.93), (0.92, 0.95), (0.16, 0.95),
    ])
    # Chrome specular streak along the sole top — the single brightest band.
    poly(_CHROME_HI, [
        (0.18, sole_top + 0.01), (0.88, sole_top + 0.01),
        (0.88, sole_top + 0.045), (0.18, sole_top + 0.05),
    ])
    poly(_STEEL_D, [
        (0.16, 0.95), (0.92, 0.95), (0.90, 0.88), (0.16, 0.91),
    ])

    # ── armoured chrome boot shell (the body) ────────────────────────────────────
    # A riveted plate body, taller at the heel where the nozzle climbs into the
    # cuff. Chrome base with a steel underside so the curve reads round/metallic.
    shell = [
        (0.16, sole_top), (0.16, 0.40), (0.22, 0.22),
        (0.40, 0.16), (0.62, 0.20), (0.78, 0.40),
        (0.90, 0.56), (0.92, sole_top),
    ]
    poly(_CHROME, shell)
    # Steel shadow along the lower/forward belly so chrome reads as a curved
    # volume catching light from above.
    poly(_STEEL, [
        (0.16, sole_top), (0.62, sole_top), (0.78, 0.46),
        (0.90, 0.58), (0.92, sole_top),
    ])
    poly(_STEEL_D, [
        (0.62, sole_top), (0.78, 0.46), (0.90, 0.58),
        (0.90, 0.66), (0.78, 0.56), (0.62, 0.70),
    ])
    # Top-edge chrome highlight along the instep ridge — the metal catch-light.
    pygame.draw.lines(
        surf, _CHROME_HI, False,
        [(px(t), py(b)) for t, b in
         ((0.22, 0.235), (0.40, 0.175), (0.62, 0.215), (0.78, 0.41))],
        max(1, int(round(h * 0.05))),
    )

    # ── armoured ankle cuff rising above the box (mecha greave) ──────────────────
    # A bevelled chrome cuff that breaks the box top; a dark ankle slot reads as
    # the opening you lock the foot into.
    poly(_CHROME, [
        (0.30, 0.24), (0.30, -0.10), (0.40, -0.20),
        (0.58, -0.18), (0.64, -0.02), (0.62, 0.22),
        (0.46, 0.16), (0.36, 0.20),
    ])
    poly(_STEEL, [
        (0.58, -0.18), (0.64, -0.02), (0.62, 0.22),
        (0.52, 0.18), (0.54, -0.04), (0.50, -0.17),
    ])
    poly(_CHROME_HI, [
        (0.30, -0.10), (0.40, -0.20), (0.47, -0.18),
        (0.38, -0.10), (0.33, 0.02),
    ])
    # Dark ankle slot sunk into the cuff top.
    hole_c = (px(0.47), py(-0.02))
    rx = max(1, int(round(w * 0.075)))
    ry = max(1, int(round(h * 0.11)))
    pygame.draw.ellipse(surf, _PLATE_D,
                        (hole_c[0] - rx, hole_c[1] - ry, rx * 2, ry * 2))

    # ── glowing heat-exhaust vents on the side plate ─────────────────────────────
    # Three angled slots venting heat — dark slot with a hot glow lip so they read
    # as live thruster vents, the second energy cue after the plume.
    vent_w = max(2, int(round(h * 0.10)))
    for vt0, vb0, vt1, vb1 in (
        (0.42, 0.40, 0.56, 0.36),
        (0.46, 0.52, 0.60, 0.48),
        (0.50, 0.64, 0.64, 0.60),
    ):
        line(_PLATE_D, (vt0, vb0 + 0.02), (vt1, vb1 + 0.02), vent_w)
        line(_VENT_GLOW, (vt0, vb0), (vt1, vb1), max(1, int(vent_w * 0.5)))

    # ── riveted plating seams + rivet dots ───────────────────────────────────────
    # A seam splitting the shell into two armour plates + rivets along it; the
    # rivets clamp to >=1px so the "bolted metal" cue survives the foot shrink.
    line(_STEEL_D, (0.30, 0.30), (0.34, sole_top), max(1, int(round(w * 0.014))))
    line(_STEEL_D, (0.66, 0.30), (0.74, 0.46), max(1, int(round(w * 0.012))))
    for rt, rb in ((0.24, 0.30), (0.40, 0.225), (0.58, 0.25),
                   (0.34, 0.62), (0.74, 0.58)):
        r = max(1, int(round(h * 0.045)))
        pygame.draw.circle(surf, _RIVET, (int(px(rt)), int(py(rb))), r)
        pygame.draw.circle(surf, _STEEL_D, (int(px(rt)), int(py(rb))),
                           r, max(1, r // 2))
