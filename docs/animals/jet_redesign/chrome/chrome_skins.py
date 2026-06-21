"""RETRO CHROME — secret JET FIGHTER redesign candidates (round 1).

Concept: a polished BARE-METAL Cold-War jet (F-86 Sabre / MiG-15 vibe).
The signature is SHINY aluminium read VALUE-first — a bright top highlight
band + a dark belly — plus ONE bold accent per take. Five genuinely
different sub-takes on the same chrome idea (accent scheme, wing sweep,
canopy size, chrome-render method). Drawn NOSE-RIGHT, UPRIGHT, LEVEL on a
64×84 SRCALPHA canvas with the fuselage mass centred at (32,44); the game
applies the inverted nose-up spin later, so these builds do NOT bake it.

Contract mirrors game/animal_jet_fighter.py so the winner lifts straight in:

  * `build_chrome_v*(wing_angle_deg) -> Surface`  one flat 64×84 frame.
  * a cached `(frame_idx, tilt_deg) -> Surface` getter from the local
    `_make_prebuilt_skin(build_fn)` (4 flat poses + per-(frame,3°) rotation
    cache, each run through the house outline).
  * `BUILDERS` maps the review label → getter (and the eventual production
    key `skin_chrome` → the chosen take).

Why the geometry sits where it does: collision is a fixed 14px circle at the
fuselage centre (32,44), so every take keeps its body mass anchored there for
fairness even when the wingspan runs wider.
"""
import math
import pygame

from game.parrot import SPRITE_W, _WING_ANGLES, _add_outline, _aaellipse


# ── canvas + body anchor (mirror animal_jet_fighter layout) ──────────────────
COMPOSITE_W = SPRITE_W          # 64
COMPOSITE_H = 84
DY          = 12
BCX, BCY = 32, 32 + DY          # fuselage centre → (32, 44)


def _make_prebuilt_skin(build_fn):
    """Cached `(frame_idx, tilt_deg) -> Surface` getter for a build_fn(angle):
    lazy 4-frame build + per-(frame, 3°) rotation cache, each frame run
    through the house silhouette outline."""
    state = {"frames": None, "rot": {}}

    def getter(frame_idx, tilt_deg):
        if state["frames"] is None:
            state["frames"] = [_add_outline(build_fn(a)) for a in _WING_ANGLES]
        frames = state["frames"]
        frame_idx %= len(frames)
        key = (frame_idx, int(round(tilt_deg / 3.0)) * 3)
        s = state["rot"].get(key)
        if s is None:
            s = pygame.transform.rotozoom(frames[frame_idx], key[1], 1.0)
            state["rot"][key] = s
        return s

    return getter


def _new():
    return pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)


def _blit_c(surf, src, center):
    surf.blit(src, src.get_rect(center=center).topleft)


# ── shared afterburner pulse (identical maths to production) ─────────────────
def _pulse(angle_deg):
    """0..1 throttle from the wing pose: brightest on the middle two frames,
    dimmest at the ends — a heartbeat the eye reads as thrust at 40px."""
    t = (50 - angle_deg) / 90.0
    return 1.0 - abs(t * 2.0 - 1.0)


def _pitch(angle_deg):
    """±1px nose pitch so the jet 'breathes' with the burner instead of sitting
    dead-still."""
    return int(round((_pulse(angle_deg) - 0.5) * 2.4))


def _baked_flame(length, width, core, mid, outer):
    """Bake ONE afterburner plume (outer haze → mid → white-hot core + shock
    beads) onto its own surface so both build targets stay identical and cheap.
    LEFT edge is the nozzle mouth; the plume streams RIGHT (aft)."""
    pad = 6
    w = length + pad * 2
    h = width + pad * 2
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    cy = h // 2

    def teardrop(col, ln, hw, alpha):
        pts = []
        n = 14
        for i in range(n + 1):
            t = i / n
            x = pad + t * ln
            r = hw * math.sin(math.pi * (0.15 + 0.85 * (1.0 - t))) * (1.0 - 0.15 * t)
            pts.append((x, cy - r))
        for i in range(n + 1):
            t = (n - i) / n
            x = pad + t * ln
            r = hw * math.sin(math.pi * (0.15 + 0.85 * (1.0 - t))) * (1.0 - 0.15 * t)
            pts.append((x, cy + r))
        layer = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.polygon(layer, (*col, alpha), pts)
        surf.blit(layer, (0, 0))

    teardrop(outer, length,             width / 2.0,  140)
    teardrop(mid,   int(length * 0.74), width / 3.0,  210)
    teardrop(core,  int(length * 0.46), width / 5.0,  255)
    pygame.draw.circle(surf, (255, 255, 255, 255), (pad + 2, cy), max(1, width // 8))
    for k in range(1, 3):
        dx = pad + int(length * 0.16 * k) + 2
        rad = max(1, width // 10 - (k - 1))
        pygame.draw.circle(surf, (255, 250, 232, 235), (dx, cy), rad)
    return surf


def _glow(radius, color, alpha=120):
    """Soft radial halo baked once — the warm aura behind the burner. Concentric
    fading rings so glow supports the silhouette, never swallows it."""
    d = radius * 2
    s = pygame.Surface((d, d), pygame.SRCALPHA)
    steps = 8
    for i in range(steps, 0, -1):
        a = int(alpha * (i / steps) ** 2)
        r = int(radius * i / steps)
        pygame.draw.circle(s, (*color, a), (radius, radius), r)
    return s


def _burner(surf, tail_x, nozzles, p, *, hot=(255, 255, 244),
            mid=(255, 168, 60), outer=(236, 72, 36), glow_col=(255, 150, 64)):
    """Common afterburner: per-nozzle tight halo + plume + glowing mouth, peak
    radius capped to the rear so the metal nose stays the dominant read."""
    flame_len = int(13 + p * 11)
    halo_r = int((10 + p * 5) * 0.84)
    glow = _glow(halo_r, glow_col, alpha=int(60 + p * 60))
    flame = _baked_flame(flame_len, 8, hot, mid, outer)
    for ny in nozzles:
        _blit_c(surf, glow, (tail_x + flame_len // 2 - 2, ny))
        surf.blit(flame, (tail_x - 2, ny - flame.get_height() // 2))


def _nozzle_mouths(surf, tail_x, nozzles):
    for ny in nozzles:
        pygame.draw.circle(surf, (255, 206, 130), (tail_x, ny), 2)
        pygame.draw.circle(surf, (255, 255, 245), (tail_x - 1, ny), 1)


# ── chrome value palette (shared metal read across all 5) ────────────────────
# The whole concept rides on VALUE: a bright top band, a mid body, a dark belly.
_AL_HI   = (236, 240, 248)       # hot top-highlight band (chrome glint)
_AL_BODY = (176, 184, 198)       # mid aluminium
_AL_LO   = (104, 112, 128)       # dark belly / underside
_AL_EDGE = (60, 66, 80)          # panel/outline shadow (value tell)
_CANOPY  = (58, 150, 200)        # cool canopy anchor (vs warm burner)
_CANOPY_H = (190, 232, 252)


# ═════════════════════════════════════════════════════════════════════════════
# V1 · SABRE RED-NOSE — swept wing, classic USAF Korean-War Sabre. Polished
#   aluminium with a RED radome nose and a RED-and-WHITE checkered tail band.
#   Chrome rendered as a hard top-highlight band over a dark belly. Medium
#   bubble canopy. Accent = red.
# ═════════════════════════════════════════════════════════════════════════════
_RED   = (214, 52, 48)
_RED_H = (250, 120, 110)


def build_chrome_v1(wing_angle_deg):
    surf = _new()
    p = _pulse(wing_angle_deg)
    pit = _pitch(wing_angle_deg)
    nose_x = 9 + pit
    tail_x = 50
    noz = (BCY - 7, BCY + 7)

    _burner(surf, tail_x, noz, p)

    # ── Swept tail fins (canted), drawn before body so root tucks under ──
    for sgn in (-1, 1):
        pygame.draw.polygon(surf, _AL_LO, [
            (tail_x - 5, BCY + sgn * 3), (tail_x + 7, BCY + sgn * 13),
            (tail_x + 9, BCY + sgn * 12), (tail_x + 1, BCY + sgn * 2)])
    # Checkered tail band: alternating red/white squares across the fin root.
    for sgn in (-1, 1):
        for k in range(3):
            col = _RED if k % 2 == 0 else (244, 244, 248)
            bx = tail_x - 4 + k * 3
            pygame.draw.polygon(surf, col, [
                (bx, BCY + sgn * 4), (bx + 3, BCY + sgn * 5),
                (bx + 4, BCY + sgn * 9), (bx + 1, BCY + sgn * 8)])

    # ── Swept wings (35° sweep), dark belly band then lit top facet ──
    for sgn in (-1, 1):
        pygame.draw.polygon(surf, _AL_LO, [
            (nose_x + 22, BCY + sgn * 2), (tail_x - 2, BCY + sgn * 22),
            (tail_x + 3, BCY + sgn * 22), (tail_x - 7, BCY + sgn * 6)])
        pygame.draw.polygon(surf, _AL_BODY, [
            (nose_x + 23, BCY + sgn * 2), (tail_x - 4, BCY + sgn * 20),
            (tail_x - 8, BCY + sgn * 6)])
        pygame.draw.polygon(surf, _AL_HI, [
            (nose_x + 24, BCY + sgn * 2), (nose_x + 33, BCY + sgn * 8),
            (tail_x - 9, BCY + sgn * 8), (tail_x - 8, BCY + sgn * 6)])
        pygame.draw.line(surf, _AL_EDGE, (nose_x + 23, BCY + sgn * 2),
                         (tail_x - 4, BCY + sgn * 20), 1)

    # ── Cigar fuselage: long bare-metal tube ──
    body = [(nose_x, BCY), (nose_x + 14, BCY - 6), (tail_x + 3, BCY - 5),
            (tail_x + 6, BCY), (tail_x + 3, BCY + 5), (nose_x + 14, BCY + 6)]
    pygame.draw.polygon(surf, _AL_BODY, body)
    pygame.draw.polygon(surf, _AL_LO,
                        [(nose_x + 14, BCY + 2), (tail_x + 3, BCY + 2),
                         (tail_x + 4, BCY + 5), (nose_x + 14, BCY + 6)])
    pygame.draw.polygon(surf, _AL_EDGE, body, 1)
    # Bright chrome spine highlight band along the top.
    pygame.draw.polygon(surf, _AL_HI,
                        [(nose_x + 6, BCY - 1), (nose_x + 14, BCY - 4),
                         (tail_x, BCY - 3), (tail_x, BCY - 1)])
    # Panel lines (subtle dark seams) reinforce the bare-metal read.
    for px in (nose_x + 20, nose_x + 30):
        pygame.draw.line(surf, _AL_EDGE, (px, BCY - 4), (px, BCY + 4), 1)

    # ── RED radome nose cone (the accent) ──
    pygame.draw.polygon(surf, _RED,
                        [(nose_x, BCY), (nose_x + 9, BCY - 4),
                         (nose_x + 9, BCY + 4)])
    pygame.draw.line(surf, _RED_H, (nose_x + 1, BCY - 1), (nose_x + 8, BCY - 3), 1)
    # Open nose intake lip (Sabre's chin intake) — dark mouth ring.
    pygame.draw.circle(surf, _AL_EDGE, (nose_x + 2, BCY), 2)

    # ── Bubble canopy (medium) ──
    _aaellipse(surf, _CANOPY, (nose_x + 18, BCY - 1), 5, 3)
    _aaellipse(surf, _CANOPY_H, (nose_x + 16, BCY - 2), 2, 1)

    _nozzle_mouths(surf, tail_x, noz)
    return surf


# ═════════════════════════════════════════════════════════════════════════════
# V2 · MIG RED-STAR — straight (un-swept) wing MiG-15, raw silver with a RED
#   air-intake nose ring and a bold RED STAR on the fuselage. Chrome rendered
#   as panel-line FACETS (banded top/belly with seams) rather than one smooth
#   band. Small canopy. Accent = red star.
# ═════════════════════════════════════════════════════════════════════════════
_STAR = (210, 44, 40)
_STAR_H = (248, 110, 100)


def build_chrome_v2(wing_angle_deg):
    surf = _new()
    p = _pulse(wing_angle_deg)
    pit = _pitch(wing_angle_deg)
    nose_x = 9 + pit
    tail_x = 50
    noz = (BCY,)                      # MiG single centre nozzle

    _burner(surf, tail_x, noz, p)

    # Single tall swept tail fin (MiG high tail), drawn as one dorsal blade.
    pygame.draw.polygon(surf, _AL_LO, [
        (tail_x - 6, BCY - 3), (tail_x + 8, BCY - 14),
        (tail_x + 10, BCY - 12), (tail_x - 1, BCY - 2)])
    pygame.draw.polygon(surf, _AL_BODY, [
        (tail_x - 5, BCY - 3), (tail_x + 6, BCY - 12), (tail_x - 1, BCY - 3)])
    # Red band near the fin tip.
    pygame.draw.line(surf, _STAR, (tail_x + 4, BCY - 11),
                     (tail_x + 8, BCY - 13), 2)

    # ── Straight (un-swept) wings: a near-rectangular planform ──
    for sgn in (-1, 1):
        pygame.draw.polygon(surf, _AL_LO, [
            (nose_x + 24, BCY + sgn * 2), (nose_x + 26, BCY + sgn * 22),
            (nose_x + 33, BCY + sgn * 22), (nose_x + 33, BCY + sgn * 3)])
        pygame.draw.polygon(surf, _AL_BODY, [
            (nose_x + 25, BCY + sgn * 2), (nose_x + 27, BCY + sgn * 20),
            (nose_x + 32, BCY + sgn * 20), (nose_x + 32, BCY + sgn * 3)])
        pygame.draw.polygon(surf, _AL_HI, [
            (nose_x + 25, BCY + sgn * 3), (nose_x + 27, BCY + sgn * 9),
            (nose_x + 32, BCY + sgn * 9), (nose_x + 32, BCY + sgn * 3)])
        pygame.draw.line(surf, _AL_EDGE, (nose_x + 25, BCY + sgn * 3),
                         (nose_x + 26, BCY + sgn * 21), 1)
        # Wingtip fuel tank (MiG tip-tank) — small bright pod.
        pygame.draw.circle(surf, _AL_HI, (nose_x + 29, BCY + sgn * 22), 2)
        pygame.draw.circle(surf, _AL_EDGE, (nose_x + 29, BCY + sgn * 22), 2, 1)

    # ── Stubby barrel fuselage ──
    body = [(nose_x, BCY), (nose_x + 12, BCY - 7), (tail_x + 2, BCY - 5),
            (tail_x + 6, BCY), (tail_x + 2, BCY + 5), (nose_x + 12, BCY + 7)]
    pygame.draw.polygon(surf, _AL_BODY, body)
    # FACET chrome: alternating top/belly bands separated by dark panel seams.
    pygame.draw.polygon(surf, _AL_HI,
                        [(nose_x + 8, BCY - 2), (nose_x + 12, BCY - 5),
                         (tail_x, BCY - 4), (tail_x, BCY - 2)])
    pygame.draw.polygon(surf, _AL_LO,
                        [(nose_x + 12, BCY + 2), (tail_x + 2, BCY + 2),
                         (tail_x + 3, BCY + 5), (nose_x + 12, BCY + 7)])
    pygame.draw.polygon(surf, _AL_EDGE, body, 1)
    # Multiple panel-line seams give the bare-metal facet read.
    for px in (nose_x + 16, nose_x + 24, nose_x + 32, nose_x + 40):
        pygame.draw.line(surf, _AL_EDGE, (px, BCY - 5), (px, BCY + 5), 1)
    pygame.draw.line(surf, _AL_EDGE, (nose_x + 12, BCY + 1),
                     (tail_x + 2, BCY + 1), 1)

    # ── RED air-intake nose ring (the MiG nose) ──
    pygame.draw.circle(surf, _STAR, (nose_x + 2, BCY), 4)
    pygame.draw.circle(surf, (30, 32, 40), (nose_x + 2, BCY), 2)
    pygame.draw.circle(surf, _STAR_H, (nose_x + 1, BCY - 1), 1)

    # ── HERO ACCENT: a bold red star on the mid-fuselage ──
    cx, cy, R = nose_x + 28, BCY - 1, 4
    pts = []
    for i in range(5):
        a = -math.pi / 2 + i * 2 * math.pi / 5
        pts.append((cx + R * math.cos(a), cy + R * math.sin(a)))
        a2 = a + math.pi / 5
        pts.append((cx + R * 0.42 * math.cos(a2), cy + R * 0.42 * math.sin(a2)))
    pygame.draw.polygon(surf, _STAR, pts)
    pygame.draw.polygon(surf, _STAR_H, pts, 1)

    # ── Small canopy ──
    _aaellipse(surf, _CANOPY, (nose_x + 16, BCY - 2), 4, 2)
    pygame.draw.circle(surf, _CANOPY_H, (nose_x + 14, BCY - 3), 1)

    _nozzle_mouths(surf, tail_x, noz)
    return surf


# ═════════════════════════════════════════════════════════════════════════════
# V3 · BLUE-ANGEL TRIM — swept wing, polished aluminium with a BLUE/YELLOW trim
#   scheme: a blue spine stripe down the chrome top band edged in yellow, and a
#   big BUBBLE canopy. Hard top-highlight chrome. Accent = blue + yellow.
# ═════════════════════════════════════════════════════════════════════════════
_BLUE   = (40, 86, 196)
_BLUE_H = (110, 156, 248)
_YEL    = (255, 206, 60)


def build_chrome_v3(wing_angle_deg):
    surf = _new()
    p = _pulse(wing_angle_deg)
    pit = _pitch(wing_angle_deg)
    nose_x = 9 + pit
    tail_x = 50
    noz = (BCY - 7, BCY + 7)

    _burner(surf, tail_x, noz, p, glow_col=(255, 150, 64))

    # Swept tail fins.
    for sgn in (-1, 1):
        pygame.draw.polygon(surf, _AL_LO, [
            (tail_x - 5, BCY + sgn * 3), (tail_x + 7, BCY + sgn * 13),
            (tail_x + 9, BCY + sgn * 12), (tail_x + 1, BCY + sgn * 2)])
        # Yellow tip flash on each fin.
        pygame.draw.line(surf, _YEL, (tail_x + 4, BCY + sgn * 8),
                         (tail_x + 8, BCY + sgn * 12), 2)

    # ── Swept wings ──
    for sgn in (-1, 1):
        pygame.draw.polygon(surf, _AL_LO, [
            (nose_x + 22, BCY + sgn * 2), (tail_x - 2, BCY + sgn * 22),
            (tail_x + 3, BCY + sgn * 22), (tail_x - 7, BCY + sgn * 6)])
        pygame.draw.polygon(surf, _AL_BODY, [
            (nose_x + 23, BCY + sgn * 2), (tail_x - 4, BCY + sgn * 20),
            (tail_x - 8, BCY + sgn * 6)])
        pygame.draw.polygon(surf, _AL_HI, [
            (nose_x + 24, BCY + sgn * 2), (nose_x + 33, BCY + sgn * 8),
            (tail_x - 9, BCY + sgn * 8), (tail_x - 8, BCY + sgn * 6)])
        pygame.draw.line(surf, _AL_EDGE, (nose_x + 23, BCY + sgn * 2),
                         (tail_x - 4, BCY + sgn * 20), 1)
        # Blue leading-edge flash (team-jet trim).
        pygame.draw.line(surf, _BLUE, (nose_x + 24, BCY + sgn * 2),
                         (tail_x - 6, BCY + sgn * 18), 1)

    # ── Slim fuselage ──
    body = [(nose_x, BCY), (nose_x + 14, BCY - 6), (tail_x + 3, BCY - 5),
            (tail_x + 6, BCY), (tail_x + 3, BCY + 5), (nose_x + 14, BCY + 6)]
    pygame.draw.polygon(surf, _AL_BODY, body)
    pygame.draw.polygon(surf, _AL_LO,
                        [(nose_x + 14, BCY + 2), (tail_x + 3, BCY + 2),
                         (tail_x + 4, BCY + 5), (nose_x + 14, BCY + 6)])
    pygame.draw.polygon(surf, _AL_EDGE, body, 1)
    # Chrome top band.
    pygame.draw.polygon(surf, _AL_HI,
                        [(nose_x + 6, BCY - 1), (nose_x + 14, BCY - 4),
                         (tail_x, BCY - 3), (tail_x, BCY - 1)])
    # ── BLUE spine stripe edged YELLOW (the accent) running nose→tail ──
    pygame.draw.line(surf, _BLUE, (nose_x + 6, BCY), (tail_x + 2, BCY + 1), 3)
    pygame.draw.line(surf, _BLUE_H, (nose_x + 8, BCY - 1), (tail_x, BCY - 1), 1)
    pygame.draw.line(surf, _YEL, (nose_x + 6, BCY + 2), (tail_x + 2, BCY + 3), 1)

    # Bare-metal nose cone (no red here — let the blue trim carry it).
    pygame.draw.polygon(surf, _AL_HI,
                        [(nose_x, BCY), (nose_x + 8, BCY - 3),
                         (nose_x + 8, BCY + 3)])
    pygame.draw.line(surf, _BLUE, (nose_x, BCY), (nose_x + 8, BCY), 1)

    # ── BIG bubble canopy (the take's signature shape change) ──
    _aaellipse(surf, _BLUE, (nose_x + 18, BCY - 1), 7, 4)
    _aaellipse(surf, _CANOPY, (nose_x + 18, BCY - 1), 6, 3)
    _aaellipse(surf, _CANOPY_H, (nose_x + 15, BCY - 3), 3, 1)
    pygame.draw.circle(surf, _CANOPY_H, (nose_x + 15, BCY - 3), 1)

    _nozzle_mouths(surf, tail_x, noz)
    return surf


# ═════════════════════════════════════════════════════════════════════════════
# V4 · RACING NUMBER — raw aluminium air-racer, NO national markings; just one
#   bold RACING NUMBER roundel on the wing + a black anti-glare panel ahead of
#   the canopy. Aggressive deep-swept wing. Hard-highlight chrome. Accent =
#   black "7" roundel.
# ═════════════════════════════════════════════════════════════════════════════
_RACE_BG  = (244, 246, 250)
_RACE_INK = (32, 34, 44)
_RACE_RIM = (220, 64, 56)


def build_chrome_v4(wing_angle_deg):
    surf = _new()
    p = _pulse(wing_angle_deg)
    pit = _pitch(wing_angle_deg)
    nose_x = 9 + pit
    tail_x = 50
    noz = (BCY - 6, BCY + 6)

    _burner(surf, tail_x, noz, p)

    # Swept tail fins.
    for sgn in (-1, 1):
        pygame.draw.polygon(surf, _AL_LO, [
            (tail_x - 5, BCY + sgn * 3), (tail_x + 8, BCY + sgn * 14),
            (tail_x + 10, BCY + sgn * 13), (tail_x + 1, BCY + sgn * 2)])

    # ── Deep-swept (45°) wings, aggressive arrowhead ──
    for sgn in (-1, 1):
        pygame.draw.polygon(surf, _AL_LO, [
            (nose_x + 20, BCY + sgn * 2), (tail_x - 1, BCY + sgn * 24),
            (tail_x + 4, BCY + sgn * 24), (tail_x - 6, BCY + sgn * 5)])
        pygame.draw.polygon(surf, _AL_BODY, [
            (nose_x + 21, BCY + sgn * 2), (tail_x - 3, BCY + sgn * 22),
            (tail_x - 7, BCY + sgn * 5)])
        pygame.draw.polygon(surf, _AL_HI, [
            (nose_x + 22, BCY + sgn * 2), (nose_x + 32, BCY + sgn * 8),
            (tail_x - 8, BCY + sgn * 8), (tail_x - 7, BCY + sgn * 5)])
        pygame.draw.line(surf, _AL_EDGE, (nose_x + 21, BCY + sgn * 2),
                         (tail_x - 3, BCY + sgn * 22), 1)

    # ── HERO ACCENT: white roundel + bold black "7" on each wing root ──
    for sgn in (-1, 1):
        rcx, rcy = nose_x + 27, BCY + sgn * 9
        pygame.draw.circle(surf, _RACE_RIM, (rcx, rcy), 4)
        pygame.draw.circle(surf, _RACE_BG, (rcx, rcy), 3)
        # Minimal "7": top bar + diagonal, the cheapest legible number at 40px.
        pygame.draw.line(surf, _RACE_INK, (rcx - 1, rcy - 2), (rcx + 2, rcy - 2), 1)
        pygame.draw.line(surf, _RACE_INK, (rcx + 2, rcy - 2), (rcx, rcy + 2), 1)

    # ── Slim racer fuselage ──
    body = [(nose_x, BCY), (nose_x + 13, BCY - 5), (tail_x + 3, BCY - 5),
            (tail_x + 7, BCY), (tail_x + 3, BCY + 5), (nose_x + 13, BCY + 5)]
    pygame.draw.polygon(surf, _AL_BODY, body)
    pygame.draw.polygon(surf, _AL_LO,
                        [(nose_x + 13, BCY + 2), (tail_x + 3, BCY + 2),
                         (tail_x + 4, BCY + 5), (nose_x + 13, BCY + 5)])
    pygame.draw.polygon(surf, _AL_EDGE, body, 1)
    # Mirror-bright chrome spine — the rawest metal of the five.
    pygame.draw.polygon(surf, _AL_HI,
                        [(nose_x + 5, BCY - 1), (nose_x + 13, BCY - 3),
                         (tail_x, BCY - 3), (tail_x, BCY - 1)])
    pygame.draw.line(surf, (255, 255, 255),
                     (nose_x + 6, BCY - 2), (tail_x - 4, BCY - 2), 1)

    # Spinner nose tip (polished cone).
    pygame.draw.polygon(surf, _AL_HI,
                        [(nose_x, BCY), (nose_x + 7, BCY - 3),
                         (nose_x + 7, BCY + 3)])
    pygame.draw.line(surf, _RACE_RIM, (nose_x, BCY), (nose_x + 4, BCY), 1)

    # ── Black anti-glare panel ahead of canopy + small canopy ──
    pygame.draw.polygon(surf, _RACE_INK,
                        [(nose_x + 9, BCY - 2), (nose_x + 16, BCY - 3),
                         (nose_x + 16, BCY - 1), (nose_x + 9, BCY)])
    _aaellipse(surf, _CANOPY, (nose_x + 18, BCY - 2), 4, 2)
    pygame.draw.circle(surf, _CANOPY_H, (nose_x + 16, BCY - 3), 1)

    _nozzle_mouths(surf, tail_x, noz)
    return surf


# ═════════════════════════════════════════════════════════════════════════════
# V5 · GOLD-BAR SABRE — swept wing Sabre rendered with PANEL-LINE FACETS (a grid
#   of riveted chrome panels) and a single bold YELLOW recognition band wrapped
#   round the rear fuselage, black-outlined (Korean War style). Medium canopy,
#   red wingtip caps. Accent = yellow band.
# ═════════════════════════════════════════════════════════════════════════════
_BAND   = (255, 200, 48)
_BAND_E = (40, 38, 36)
_TIP    = (212, 52, 48)


def build_chrome_v5(wing_angle_deg):
    surf = _new()
    p = _pulse(wing_angle_deg)
    pit = _pitch(wing_angle_deg)
    nose_x = 9 + pit
    tail_x = 50
    noz = (BCY - 7, BCY + 7)

    _burner(surf, tail_x, noz, p)

    # Swept tail fins.
    for sgn in (-1, 1):
        pygame.draw.polygon(surf, _AL_LO, [
            (tail_x - 5, BCY + sgn * 3), (tail_x + 7, BCY + sgn * 13),
            (tail_x + 9, BCY + sgn * 12), (tail_x + 1, BCY + sgn * 2)])

    # ── Swept wings with a faceted panel grid (rivet-line read) ──
    for sgn in (-1, 1):
        pygame.draw.polygon(surf, _AL_LO, [
            (nose_x + 22, BCY + sgn * 2), (tail_x - 2, BCY + sgn * 22),
            (tail_x + 3, BCY + sgn * 22), (tail_x - 7, BCY + sgn * 6)])
        pygame.draw.polygon(surf, _AL_BODY, [
            (nose_x + 23, BCY + sgn * 2), (tail_x - 4, BCY + sgn * 20),
            (tail_x - 8, BCY + sgn * 6)])
        pygame.draw.polygon(surf, _AL_HI, [
            (nose_x + 24, BCY + sgn * 2), (nose_x + 32, BCY + sgn * 7),
            (nose_x + 38, BCY + sgn * 7), (tail_x - 8, BCY + sgn * 6)])
        pygame.draw.line(surf, _AL_EDGE, (nose_x + 23, BCY + sgn * 2),
                         (tail_x - 4, BCY + sgn * 20), 1)
        # Spanwise + chordwise panel seams = the faceted chrome read.
        pygame.draw.line(surf, _AL_EDGE, (nose_x + 28, BCY + sgn * 5),
                         (tail_x - 6, BCY + sgn * 16), 1)
        pygame.draw.line(surf, _AL_EDGE, (nose_x + 30, BCY + sgn * 3),
                         (nose_x + 33, BCY + sgn * 12), 1)
        # Red wingtip cap.
        pygame.draw.circle(surf, _TIP, (tail_x - 3, BCY + sgn * 20), 1)

    # ── Fuselage with stacked panel facets ──
    body = [(nose_x, BCY), (nose_x + 14, BCY - 6), (tail_x + 3, BCY - 5),
            (tail_x + 6, BCY), (tail_x + 3, BCY + 5), (nose_x + 14, BCY + 6)]
    pygame.draw.polygon(surf, _AL_BODY, body)
    pygame.draw.polygon(surf, _AL_HI,
                        [(nose_x + 6, BCY - 1), (nose_x + 14, BCY - 4),
                         (tail_x, BCY - 3), (tail_x, BCY - 2)])
    pygame.draw.polygon(surf, _AL_LO,
                        [(nose_x + 14, BCY + 2), (tail_x + 3, BCY + 2),
                         (tail_x + 4, BCY + 5), (nose_x + 14, BCY + 6)])
    pygame.draw.polygon(surf, _AL_EDGE, body, 1)
    # Dense panel-line grid down the fuselage.
    for px in (nose_x + 14, nose_x + 22, nose_x + 30, nose_x + 38):
        pygame.draw.line(surf, _AL_EDGE, (px, BCY - 5), (px, BCY + 5), 1)
    pygame.draw.line(surf, _AL_EDGE, (nose_x + 6, BCY - 1), (tail_x, BCY - 1), 1)

    # ── HERO ACCENT: yellow recognition band, black-outlined, round the rear ──
    bx0, bx1 = nose_x + 33, nose_x + 39
    pygame.draw.polygon(surf, _BAND, [
        (bx0, BCY - 5), (bx1, BCY - 5), (bx1, BCY + 5), (bx0, BCY + 5)])
    pygame.draw.line(surf, _BAND_E, (bx0, BCY - 5), (bx0, BCY + 5), 1)
    pygame.draw.line(surf, _BAND_E, (bx1, BCY - 5), (bx1, BCY + 5), 1)

    # Bare-metal nose with a thin red trim ring.
    pygame.draw.polygon(surf, _AL_HI,
                        [(nose_x, BCY), (nose_x + 8, BCY - 3),
                         (nose_x + 8, BCY + 3)])
    pygame.draw.circle(surf, _TIP, (nose_x + 6, BCY), 1)
    pygame.draw.circle(surf, _AL_EDGE, (nose_x + 2, BCY), 1)

    # ── Medium canopy ──
    _aaellipse(surf, _CANOPY, (nose_x + 18, BCY - 1), 5, 3)
    _aaellipse(surf, _CANOPY_H, (nose_x + 16, BCY - 2), 2, 1)

    _nozzle_mouths(surf, tail_x, noz)
    return surf


# ─────────────────────────────────────────────────────────────────────────────
# Review registry: label → getter. The production key `skin_chrome` points at
# the front-runner take so the sheet can show it under its real name too.
# ─────────────────────────────────────────────────────────────────────────────
get_chrome_v1 = _make_prebuilt_skin(build_chrome_v1)
get_chrome_v2 = _make_prebuilt_skin(build_chrome_v2)
get_chrome_v3 = _make_prebuilt_skin(build_chrome_v3)
get_chrome_v4 = _make_prebuilt_skin(build_chrome_v4)
get_chrome_v5 = _make_prebuilt_skin(build_chrome_v5)

BUILDERS = {
    "chrome_v1": get_chrome_v1,
    "chrome_v2": get_chrome_v2,
    "chrome_v3": get_chrome_v3,
    "chrome_v4": get_chrome_v4,
    "chrome_v5": get_chrome_v5,
}
