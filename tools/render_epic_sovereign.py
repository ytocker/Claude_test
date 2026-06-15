"""Look-dev: the HORNED SOVEREIGN — late-game EPIC event boss (round 1).

Thesis: the classic horned devil reimagined as a regal infernal MONARCH —
broad-shouldered, sweeping ram-horns curling up into a CROWN-OF-HORNS, a
bat-wing mantle framing (never blobbing) a crisp V-taper torso, and a grand
barbed TRIDENT held vertical. Final-boss gravitas, clean-sheet — it borrows
NOTHING from the warren clown/jester (no cap/ruff/grin/harlequin, no plum-lime).

The whole design leans its gravitas into the UPPER-RADIATING silhouette: the
horn sweep + the trident tines. That is the part that survives at 1x and the
part that later tiles into the scrolling pillar — so it is drawn boldest and
darkest-cored, to hold value against a BRIGHT day sky.

Palette is fixed (not biome-driven) so the boss read stays loud across the
day/night cycle: oxblood crimson body, obsidian shadow-core, molten gold on the
horns + trident + trim. Gold doubles as the night-side rim light; oxblood +
obsidian stay deep and saturated so the figure never washes out on the day sky.

The signature prop is the TRIDENT: tall, vertical, and top/bottom-mirrorable.
In-game the held trident later becomes the scrolling pillar obstacle — mirrored
around the gap, the three barbed prongs tile top+bottom into a forked-spire
pillar and the haft reads as the gap. This sheet proves that fit with a small
mirrored pillar-pair thumbnail off to the side.

    PYTHONPATH=. python tools/render_epic_sovereign.py
"""
import math
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame


# ── fixed sovereign palette ──────────────────────────────────────────────────
# Deep + saturated so the figure survives a bright day sky; gold is the night
# rim light. No plum/lime anywhere — this lineage is oxblood/obsidian/gold.
OXBLOOD      = (150,  28,  40)   # the crimson body north-star
OXBLOOD_DK   = (104,  18,  28)   # shaded oxblood facet
OXBLOOD_LIT  = (190,  52,  60)   # lit oxblood edge
OBSIDIAN     = ( 30,  24,  28)   # near-black shadow-core / keyline
OBSIDIAN_LIT = ( 54,  44,  50)   # lifted obsidian facet
GOLD         = (240, 180,  60)   # molten gold horn + trim + trident
GOLD_LIT     = (255, 222, 138)   # lit gold facet / hot rim
GOLD_DK      = (158, 110,  30)   # gold shadow / keyline
EMBER        = (255, 120,  40)   # eye / maw molten glow (sparse accent)
EMBER_HOT    = (255, 226, 150)   # hottest core of the glow
BONE         = (232, 222, 198)   # fang ivory (used very sparingly)
INK          = ( 16,  12,  16)   # darkest keyline


def _shade(c, d):
    return (max(0, min(255, int(c[0] + d))),
            max(0, min(255, int(c[1] + d))),
            max(0, min(255, int(c[2] + d))))


# ── shared low-level paint helpers (not a figure builder) ────────────────────

def _grad_v(surf, rect, top, bot):
    """Vertical gradient fill into a rect."""
    x, y, w, h = rect
    for i in range(h):
        t = i / max(1, h - 1)
        c = (int(top[0] + (bot[0] - top[0]) * t),
             int(top[1] + (bot[1] - top[1]) * t),
             int(top[2] + (bot[2] - top[2]) * t))
        pygame.draw.line(surf, c, (x, y + i), (x + w, y + i))


def _glow(surf, x, y, r, col):
    """A soft additive ember bloom — the molten light cue (eyes, maw, trident
    tines), so the gold/ember accents read hot even at small size."""
    g = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
    for k in range(r, 0, -1):
        a = int(120 * (1 - k / r) ** 2)
        pygame.draw.circle(g, (*col, a), (r + 1, r + 1), k)
    surf.blit(g, (int(x - r - 1), int(y - r - 1)), special_flags=pygame.BLEND_RGBA_ADD)


def _rim(surf, pts, col, w):
    """A gold rim-light stroke down the lit edge of a mass — the night-side cue
    that keeps the silhouette legible after dark."""
    pygame.draw.lines(surf, col, False, [(int(p[0]), int(p[1])) for p in pts], w)


# ── the TRIDENT (signature prop, drawn standalone so the pillar can reuse it) ─
# Built top/bottom-MIRRORABLE around its own vertical axis: a forked crown of
# three barbed tines over a banded haft. `head_y` is where the tine fork sits;
# everything above it is the radiating crown that tiles into a pillar spire, and
# the haft below reads as the gap when mirrored. Geometry keys off `s` (the
# native K-scale) so it stays crisp at any size.

def _trident_head(surf, cx, head_y, s, *, hw):
    """The three barbed prongs + the cross-guard yoke they spring from. This is
    the part that radiates the boss's menace and the part that becomes the
    pillar's forked spire — so it is the boldest, darkest-cored mass here."""
    # Cross-guard yoke: a flared gold bar the three tines spring from.
    yoke = [(cx - hw * 1.7, head_y), (cx + hw * 1.7, head_y),
            (cx + hw * 1.2, head_y + 7 * s), (cx - hw * 1.2, head_y + 7 * s)]
    pygame.draw.polygon(surf, GOLD_DK, yoke)
    pygame.draw.polygon(surf, GOLD,
                        [(cx - hw * 1.5, head_y + s), (cx + hw * 1.5, head_y + s),
                         (cx + hw, head_y + 6 * s), (cx - hw, head_y + 6 * s)])
    pygame.draw.line(surf, GOLD_LIT, (cx - hw * 1.4, head_y + 2 * s),
                     (cx + hw * 1.4, head_y + 2 * s), max(1, s))

    # Three prongs: centre tall + straight, the two outer prongs sweep OUTWARD
    # then hook back to a barbed point — a forked crown, the radiating shape.
    tine_top = head_y - 46 * s
    for dx in (-1, 0, 1):
        bx = cx + dx * hw * 1.25
        if dx == 0:
            tip = (cx, tine_top)
            mid = (cx, head_y - 22 * s)
            base_l = cx - hw * 0.55
            base_r = cx + hw * 0.55
        else:
            tip = (cx + dx * hw * 2.4, tine_top + 8 * s)
            mid = (cx + dx * hw * 2.1, head_y - 20 * s)
            base_l = bx - hw * 0.5
            base_r = bx + hw * 0.5
        # A tapering spear-blade prong: wide root, needle tip, with a back-swept
        # barb halfway up so it reads as a wicked trident, not a plain fork.
        barb_y = (tip[1] + head_y) * 0.5
        barb_x = mid[0] - dx * hw * 0.9 if dx else cx - hw * 0.9
        blade = [(base_l, head_y), (base_r, head_y),
                 (mid[0] + hw * 0.28, mid[1]),
                 (tip[0], tip[1]),
                 (mid[0] - hw * 0.28, mid[1]),
                 (barb_x, barb_y)]
        pygame.draw.polygon(surf, GOLD_DK, blade)
        pygame.draw.polygon(surf, GOLD,
                            [(base_l + s, head_y), (base_r - s, head_y),
                             (mid[0] + hw * 0.18, mid[1]),
                             (tip[0], tip[1] + 2 * s)])
        # Hot lit edge down the tine + an ember spark at the needle tip.
        pygame.draw.line(surf, GOLD_LIT, (tip[0], tip[1] + 2 * s),
                         (base_l + s, head_y), max(1, s))
        _glow(surf, tip[0], tip[1], 5 * s, EMBER)
        pygame.draw.circle(surf, EMBER_HOT, (int(tip[0]), int(tip[1])), max(1, s))


def build_trident(surf, cx, head_y, foot_y, s, *, hw=6):
    """The full grand trident: a banded obsidian-and-gold haft with the barbed
    fork crown on top. Drawn so the upper crown carries the gravitas and the
    haft below it can read as the pillar gap when the prop is mirrored."""
    # Haft: a dark obsidian shaft with a slim gold lit rail (reads round, not
    # flat) and three gold binding-rings, ending in a spike-pommel.
    pygame.draw.line(surf, INK, (cx, head_y + 4 * s), (cx, foot_y), hw * 2 + 2 * s)
    pygame.draw.line(surf, OBSIDIAN, (cx, head_y + 4 * s), (cx, foot_y), hw * 2)
    pygame.draw.line(surf, OBSIDIAN_LIT, (cx - hw * 0.5, head_y + 4 * s),
                     (cx - hw * 0.5, foot_y), max(1, s))
    span = foot_y - head_y
    for t in (0.30, 0.55, 0.80):
        ry = head_y + span * t
        pygame.draw.rect(surf, GOLD_DK,
                         (int(cx - hw - 2 * s), int(ry - 3 * s),
                          int(2 * hw + 4 * s), int(6 * s)))
        pygame.draw.rect(surf, GOLD,
                         (int(cx - hw - 2 * s), int(ry - 2 * s),
                          int(2 * hw + 4 * s), int(3 * s)))
    # Spike pommel foot (so the haft also barbs at the bottom — symmetric menace
    # that helps the mirrored pillar tile read cleanly top + bottom).
    pommel = [(cx - hw, foot_y - 6 * s), (cx + hw, foot_y - 6 * s),
              (cx, foot_y + 10 * s)]
    pygame.draw.polygon(surf, GOLD_DK, pommel)
    pygame.draw.polygon(surf, GOLD, [(cx - hw + s, foot_y - 6 * s),
                                     (cx + hw - s, foot_y - 6 * s),
                                     (cx, foot_y + 8 * s)])
    _trident_head(surf, cx, head_y, s, hw=hw)


# ── the SOVEREIGN figure ─────────────────────────────────────────────────────

def build_sovereign(surf, cx, feet_y, s):
    """The horned infernal monarch standing on the ground line. Layered back to
    front: bat-wing mantle → legs → V-taper torso → pauldrons + arms → head +
    crown-of-horns → the held trident."""
    hip_y = feet_y - 118 * s
    chest_y = hip_y - 70 * s          # the broad shoulder line
    neck_y = chest_y - 8 * s

    # ── BAT-WING MANTLE (drawn FIRST, behind the body) ───────────────────────
    # A membranous wing-cape that FRAMES the figure rather than filling the gap
    # to the torso — the wings sweep UP-and-OUT to tall finger-spurs and the
    # membrane is scalloped, leaving daylight between wing and waist so the
    # torso's V never blobs into a plain triangle.
    for sgn in (-1, 1):
        shoulder = (cx + sgn * 30 * s, chest_y + 4 * s)
        # Wing finger-spurs fan up-and-out; the membrane is a scalloped trail.
        spur_top = (cx + sgn * 96 * s, chest_y - 64 * s)
        spur_mid = (cx + sgn * 104 * s, chest_y - 18 * s)
        spur_low = (cx + sgn * 78 * s, hip_y + 6 * s)
        # The leathery membrane — deep oxblood, kept NARROW near the waist so a
        # daylight notch stays between wing and torso (no triangle blob).
        membrane = [shoulder, spur_top, spur_mid,
                    (cx + sgn * 86 * s, chest_y + 18 * s),
                    spur_low,
                    (cx + sgn * 40 * s, hip_y - 8 * s),
                    (cx + sgn * 34 * s, chest_y + 26 * s)]
        pygame.draw.polygon(surf, OXBLOOD_DK, membrane)
        # Scalloped trailing edge (the bat-wing tell) cut as dark notches.
        for k, (a, b) in enumerate(((spur_top, spur_mid), (spur_mid, spur_low))):
            for j in range(3):
                t0 = j / 3
                t1 = (j + 0.5) / 3
                p0 = (a[0] + (b[0] - a[0]) * t0, a[1] + (b[1] - a[1]) * t0)
                p1 = (a[0] + (b[0] - a[0]) * t1, a[1] + (b[1] - a[1]) * t1)
                inner = (cx + sgn * 40 * s, (p0[1] + p1[1]) * 0.5)
                pygame.draw.polygon(surf, INK, [p0, p1, inner])
        # Wing struts (the finger bones) in gold — radiating, regal.
        for tip in (spur_top, spur_mid, spur_low):
            pygame.draw.line(surf, GOLD_DK, shoulder,
                             (int(tip[0]), int(tip[1])), max(1, int(2 * s)))
            pygame.draw.line(surf, GOLD, shoulder,
                             (int(tip[0]), int(tip[1])), max(1, s))
            pygame.draw.circle(surf, GOLD_LIT, (int(tip[0]), int(tip[1])), max(1, int(2 * s)))
        pygame.draw.polygon(surf, INK, membrane, max(1, int(2 * s)))

    # ── LEGS — stout digitigrade goat-legs with cloven hooves, planted wide ───
    for sgn in (-1, 1):
        hipp = (cx + sgn * 16 * s, hip_y)
        knee = (cx + sgn * 28 * s, hip_y + 56 * s)
        ankle = (cx + sgn * 18 * s, feet_y - 18 * s)
        for a, b, w in ((hipp, knee, 16 * s), (knee, ankle, 11 * s)):
            pygame.draw.line(surf, INK, a, b, int(w) + 2 * s)
            pygame.draw.line(surf, OXBLOOD_DK, a, b, int(w))
        pygame.draw.line(surf, OXBLOOD, (hipp[0] - sgn * 3 * s, hipp[1]),
                         (knee[0] - sgn * 3 * s, knee[1]), max(1, int(4 * s)))
        # Cloven hoof — a dark wedge split down the middle, gold-shod at the toe.
        hoof = [(ankle[0] - 10 * s, ankle[1]), (ankle[0] + 12 * s, ankle[1]),
                (ankle[0] + 14 * s, feet_y), (ankle[0] - 8 * s, feet_y)]
        pygame.draw.polygon(surf, OBSIDIAN, hoof)
        pygame.draw.polygon(surf, INK, hoof, max(1, s))
        pygame.draw.line(surf, INK, (ankle[0] + 3 * s, feet_y - 12 * s),
                         (ankle[0] + 3 * s, feet_y), max(1, int(2 * s)))
        pygame.draw.line(surf, GOLD, (ankle[0] - 8 * s, feet_y - 2 * s),
                         (ankle[0] + 14 * s, feet_y - 2 * s), max(1, int(2 * s)))

    # ── TORSO — a crisp inverted-V cuirass: broad shoulders tapering hard to a
    # narrow waist. Kept as its OWN sharp silhouette (NOT a soft triangle): the
    # waist pinches in well inside the wing notch, and a gold sternum spine +
    # ribbed plates sculpt the V so it never rhymes with a generic knight slab.
    waist = 18 * s
    torso = [(cx - 44 * s, chest_y), (cx + 44 * s, chest_y),
             (cx + 30 * s, chest_y + 34 * s),
             (cx + waist, hip_y), (cx - waist, hip_y),
             (cx - 30 * s, chest_y + 34 * s)]
    pygame.draw.polygon(surf, OXBLOOD, torso)
    # Lit left facet / dark right facet sculpt the volume.
    pygame.draw.polygon(surf, OXBLOOD_LIT,
                        [(cx - 44 * s, chest_y), (cx - 8 * s, chest_y),
                         (cx - waist, hip_y), (cx - 30 * s, chest_y + 34 * s)])
    pygame.draw.polygon(surf, OXBLOOD_DK,
                        [(cx + 12 * s, chest_y), (cx + 44 * s, chest_y),
                         (cx + 30 * s, chest_y + 34 * s), (cx + waist, hip_y)])
    pygame.draw.polygon(surf, INK, torso, max(1, int(2 * s)))
    # Ribbed cuirass plates (chevrons) + a molten sternum gem — armoured infernal
    # king, the gold catching as night rim.
    for i in range(3):
        ry = chest_y + 14 * s + i * 16 * s
        hwid = (34 - i * 8) * s
        pygame.draw.line(surf, GOLD_DK, (cx - hwid, ry + 4 * s), (cx, ry), max(1, int(2 * s)))
        pygame.draw.line(surf, GOLD_DK, (cx, ry), (cx + hwid, ry + 4 * s), max(1, int(2 * s)))
        pygame.draw.line(surf, GOLD, (cx - hwid + 2 * s, ry + 4 * s), (cx, ry + s), max(1, s))
        pygame.draw.line(surf, GOLD, (cx, ry + s), (cx + hwid - 2 * s, ry + 4 * s), max(1, s))
    # Sternum molten gem at the collar.
    _glow(surf, cx, chest_y + 6 * s, 8 * s, EMBER)
    pygame.draw.circle(surf, GOLD_DK, (cx, int(chest_y + 6 * s)), int(5 * s))
    pygame.draw.circle(surf, EMBER, (cx, int(chest_y + 6 * s)), int(3.5 * s))
    pygame.draw.circle(surf, EMBER_HOT, (cx, int(chest_y + 5 * s)), max(1, int(1.6 * s)))

    # ── PAULDRONS — broad spiked gold shoulder shelves that widen the top of
    # the silhouette (the regal breadth) without softening the waist taper.
    for sgn in (-1, 1):
        shx = cx + sgn * 40 * s
        pauld = [(cx + sgn * 16 * s, chest_y - 4 * s),
                 (shx + sgn * 22 * s, chest_y - 10 * s),
                 (shx + sgn * 18 * s, chest_y + 14 * s),
                 (cx + sgn * 18 * s, chest_y + 16 * s)]
        pygame.draw.polygon(surf, GOLD_DK, pauld)
        pygame.draw.polygon(surf, GOLD,
                            [(cx + sgn * 18 * s, chest_y - 2 * s),
                             (shx + sgn * 18 * s, chest_y - 7 * s),
                             (shx + sgn * 15 * s, chest_y + 10 * s),
                             (cx + sgn * 19 * s, chest_y + 12 * s)])
        pygame.draw.line(surf, GOLD_LIT, (cx + sgn * 18 * s, chest_y - 2 * s),
                         (shx + sgn * 18 * s, chest_y - 7 * s), max(1, s))
        # An upswept spike off the pauldron crest.
        spk = (shx + sgn * 30 * s, chest_y - 26 * s)
        pygame.draw.polygon(surf, GOLD_DK,
                            [(shx + sgn * 8 * s, chest_y - 8 * s),
                             (shx + sgn * 20 * s, chest_y - 6 * s), spk])
        pygame.draw.polygon(surf, GOLD,
                            [(shx + sgn * 10 * s, chest_y - 8 * s),
                             (shx + sgn * 18 * s, chest_y - 7 * s), spk], max(1, s))

    # ── ARMS — the LEFT (viewer) arm hangs gripping the trident; the RIGHT
    # rests as a fist on the hip. Stout, oxblood, gold-cuffed, dwarfed by the
    # pauldrons so breadth stays at the shoulders.
    # Right (viewer) arm — fist on hip.
    sh_r = (cx + 36 * s, chest_y + 6 * s)
    elb_r = (cx + 52 * s, chest_y + 38 * s)
    fist_r = (cx + 30 * s, hip_y - 6 * s)
    for a, b in ((sh_r, elb_r), (elb_r, fist_r)):
        pygame.draw.line(surf, INK, a, b, int(13 * s))
        pygame.draw.line(surf, OXBLOOD, a, b, int(10 * s))
    pygame.draw.circle(surf, GOLD_DK, (int(fist_r[0]), int(fist_r[1])), int(8 * s))
    pygame.draw.circle(surf, OXBLOOD_DK, (int(fist_r[0]), int(fist_r[1])), int(6 * s))
    # Left (viewer) arm — reaches down-out to grip the trident haft.
    sh_l = (cx - 36 * s, chest_y + 6 * s)
    elb_l = (cx - 54 * s, chest_y + 40 * s)
    grip_l = (cx - 70 * s, hip_y + 6 * s)
    for a, b in ((sh_l, elb_l), (elb_l, grip_l)):
        pygame.draw.line(surf, INK, a, b, int(13 * s))
        pygame.draw.line(surf, OXBLOOD, a, b, int(10 * s))
    pygame.draw.line(surf, OXBLOOD_LIT, (sh_l[0] - 2 * s, sh_l[1]),
                     (elb_l[0] - 2 * s, elb_l[1]), max(1, int(3 * s)))

    # ── HEAD — a lean angular infernal skull-face, brow-shadowed, ember eyes ──
    hr = 22 * s
    hy = neck_y - hr
    # Jaw is squared/tapered (not a soft ball) so the head reads regal + mean.
    head = [(cx - hr, hy - 6 * s), (cx + hr, hy - 6 * s),
            (cx + hr - 3 * s, hy + 10 * s), (cx + 10 * s, hy + hr),
            (cx - 10 * s, hy + hr), (cx - hr + 3 * s, hy + 10 * s)]
    pygame.draw.polygon(surf, OXBLOOD_DK, head)
    pygame.draw.polygon(surf, OXBLOOD,
                        [(cx - hr + 2 * s, hy - 4 * s), (cx + hr - 2 * s, hy - 4 * s),
                         (cx + hr - 5 * s, hy + 9 * s), (cx + 9 * s, hy + hr - 2 * s),
                         (cx - 9 * s, hy + hr - 2 * s), (cx - hr + 5 * s, hy + 9 * s)])
    pygame.draw.polygon(surf, INK, head, max(1, int(2 * s)))
    # Heavy brow shelf (the mean macro shape) + two molten ember eyes glaring.
    pygame.draw.polygon(surf, INK,
                        [(cx - 16 * s, hy - 2 * s), (cx + 16 * s, hy - 2 * s),
                         (cx + 12 * s, hy + 5 * s), (cx - 12 * s, hy + 5 * s)])
    for sgn in (-1, 1):
        ex = cx + sgn * 8 * s
        _glow(surf, ex, hy + 6 * s, 6 * s, EMBER)
        # An angry slit eye angled inward/down (the V-frown that reads as menace).
        eye = [(ex - sgn * 5 * s, hy + 3 * s), (ex + sgn * 5 * s, hy + 5 * s),
               (ex + sgn * 4 * s, hy + 9 * s), (ex - sgn * 4 * s, hy + 8 * s)]
        pygame.draw.polygon(surf, EMBER, eye)
        pygame.draw.circle(surf, EMBER_HOT, (int(ex), int(hy + 6 * s)), max(1, int(1.6 * s)))
    # A short snarling maw with two bone fangs (sparse — not a clown grin).
    my = hy + 15 * s
    pygame.draw.polygon(surf, INK,
                        [(cx - 9 * s, my), (cx + 9 * s, my),
                         (cx + 6 * s, my + 5 * s), (cx - 6 * s, my + 5 * s)])
    for fx in (-5, 5):
        pygame.draw.polygon(surf, BONE,
                            [(cx + fx * s - 2 * s, my + s), (cx + fx * s + 2 * s, my + s),
                             (cx + fx * s, my + 5 * s)])

    # ── CROWN-OF-HORNS — the gravitas. Great ram-horns spring from the temples,
    # sweep DOWN-and-OUT, curl forward in a full ram spiral, then a second pair
    # of straight regal spires rises between them: together a CROWN made of
    # horn. This is the upper-radiating silhouette that survives at 1x and tiles
    # into the pillar — so it is drawn boldest, gold, dark-cored.
    for sgn in (-1, 1):
        base = (cx + sgn * 16 * s, hy - 4 * s)
        # Ram-horn spiral: a thick curl swinging out, down, then forward-in.
        curl = []
        outer = []
        n = 16
        for i in range(n + 1):
            t = i / n
            ang = math.pi * (0.15 + 1.35 * t)        # sweep out → down → curl in
            rad = (26 - 14 * t) * s
            ox = base[0] + sgn * (10 * s + math.sin(ang) * rad)
            oy = base[1] - 14 * s + math.cos(ang) * rad + t * 8 * s
            curl.append((ox, oy))
            wseg = (10 - 7 * t) * s                   # horn tapers to its tip
            outer.append((ox + sgn * wseg, oy - wseg * 0.3))
        horn = curl + list(reversed(outer))
        pygame.draw.polygon(surf, GOLD_DK, [(int(p[0]), int(p[1])) for p in horn])
        pygame.draw.polygon(surf, GOLD,
                            [(int(p[0]), int(p[1])) for p in
                             (curl + list(reversed([(o[0] - sgn * 2 * s, o[1]) for o in outer])))])
        # Ribbed ram-growth ridges across the curl + a hot lit rail (night rim).
        for i in range(2, n, 2):
            a = curl[i]
            b = outer[i]
            pygame.draw.line(surf, GOLD_DK, (int(a[0]), int(a[1])),
                             (int(b[0]), int(b[1])), max(1, s))
        _rim(surf, curl, GOLD_LIT, max(1, s))
        # A straight regal crown-spire rising between the ram-curls.
        spire_base = (cx + sgn * 9 * s, hy - 8 * s)
        spire_tip = (cx + sgn * 16 * s, hy - 54 * s)
        spire = [(spire_base[0] - 5 * s, spire_base[1]),
                 (spire_base[0] + 5 * s, spire_base[1]),
                 (spire_tip[0] + 2 * s, spire_tip[1] + 6 * s),
                 (spire_tip[0], spire_tip[1])]
        pygame.draw.polygon(surf, GOLD_DK, [(int(p[0]), int(p[1])) for p in spire])
        pygame.draw.polygon(surf, GOLD,
                            [(int(spire_base[0] - 3 * s), int(spire_base[1])),
                             (int(spire_base[0] + 3 * s), int(spire_base[1])),
                             (int(spire_tip[0]), int(spire_tip[1] + 4 * s))])
        pygame.draw.line(surf, GOLD_LIT, (int(spire_tip[0]), int(spire_tip[1] + 4 * s)),
                         (int(spire_base[0] - 2 * s), int(spire_base[1])), max(1, s))
    # A small central crown-jewel finial seating the crown-of-horns.
    _glow(surf, cx, hy - 10 * s, 7 * s, EMBER)
    pygame.draw.polygon(surf, GOLD,
                        [(cx, int(hy - 22 * s)), (cx + 6 * s, int(hy - 12 * s)),
                         (cx, int(hy - 4 * s)), (cx - 6 * s, int(hy - 12 * s))])
    pygame.draw.polygon(surf, GOLD_DK,
                        [(cx, int(hy - 22 * s)), (cx + 6 * s, int(hy - 12 * s)),
                         (cx, int(hy - 4 * s)), (cx - 6 * s, int(hy - 12 * s))], max(1, s))
    pygame.draw.circle(surf, EMBER_HOT, (cx, int(hy - 12 * s)), max(1, int(1.8 * s)))

    # ── THE HELD TRIDENT — gripped in the left fist, planted on the ground. ──
    t_cx = cx - 70 * s
    build_trident(surf, t_cx, chest_y - 30 * s, feet_y + 2 * s, s, hw=6 * s // 1)
    # The gripping fist over the haft (drawn last so it reads in front).
    pygame.draw.circle(surf, GOLD_DK, (int(grip_l[0]), int(grip_l[1])), int(9 * s))
    pygame.draw.circle(surf, OXBLOOD, (int(grip_l[0]), int(grip_l[1])), int(7 * s))
    pygame.draw.line(surf, INK, (int(grip_l[0] - 7 * s), int(grip_l[1] - 2 * s)),
                     (int(grip_l[0] + 7 * s), int(grip_l[1] - 2 * s)), max(1, int(2 * s)))


# ── scene composition ────────────────────────────────────────────────────────

def _day_bg(surf, rect):
    """A BRIGHT day sky — the hard contrast test for the deep oxblood/obsidian."""
    x, y, w, h = rect
    sky = surf.subsurface(rect)
    _grad_v(sky, (0, 0, w, int(h * 0.72)), (96, 188, 240), (188, 226, 246))
    # Warm horizon haze.
    _grad_v(sky, (0, int(h * 0.62), w, int(h * 0.16)), (228, 232, 220), (236, 224, 188))
    # Sun-bleached ground band.
    _grad_v(sky, (0, int(h * 0.78), w, h - int(h * 0.78)), (196, 170, 110), (150, 124, 78))
    pygame.draw.line(sky, (120, 98, 60), (0, int(h * 0.78)), (w, int(h * 0.78)), 2)


def _night_bg(surf, rect):
    """A deep night sky — the test that the GOLD rim carries the read after
    dark while oxblood/obsidian stay legible."""
    x, y, w, h = rect
    sky = surf.subsurface(rect)
    _grad_v(sky, (0, 0, w, int(h * 0.78)), (14, 16, 40), (40, 30, 58))
    # A blood moon low on the horizon (sets the infernal mood).
    pygame.draw.circle(sky, (120, 40, 44), (int(w * 0.74), int(h * 0.40)), int(h * 0.10))
    pygame.draw.circle(sky, (164, 70, 66), (int(w * 0.74), int(h * 0.40)), int(h * 0.085))
    # Stars.
    import random
    rnd = random.Random(7)
    for _ in range(60):
        sx = rnd.randint(0, w)
        sy = rnd.randint(0, int(h * 0.7))
        pygame.draw.circle(sky, (200, 200, 220), (sx, sy), rnd.choice((1, 1, 2)))
    _grad_v(sky, (0, int(h * 0.78), w, h - int(h * 0.78)), (40, 30, 36), (20, 14, 20))
    pygame.draw.line(sky, (70, 50, 56), (0, int(h * 0.78)), (w, int(h * 0.78)), 2)


def _pillar_thumb(surf, ox, oy, tw, th):
    """Prove the trident PROP mirrors into a clean vertical pillar PAIR: the
    same head builder, top-half flipped to point DOWN into the gap, bottom-half
    upright pointing UP, with the haft reading as the gap between. Rendered tiny,
    the way the in-game scrolling tile will."""
    pygame.draw.rect(surf, (40, 44, 52), (ox, oy, tw, th))
    pygame.draw.rect(surf, (90, 96, 108), (ox, oy, tw, th), 1)
    # Sky strip behind so contrast reads.
    _grad_v(surf.subsurface((ox + 1, oy + 1, tw - 2, th - 2)),
            (0, 0, tw - 2, th - 2), (120, 196, 238), (180, 220, 244))
    gap_top = oy + int(th * 0.42)
    gap_bot = oy + int(th * 0.58)
    ps = 2  # tiny native scale, like the scrolling route
    # Each half-pillar is its OWN tile (a forked-spire crown + a stub of haft)
    # rendered tall so the prong fork sits AT the gap and the haft runs off the
    # tile edge — exactly how the scrolling obstacle is built and clipped.
    half_h = max(gap_top - oy, oy + th - gap_bot) + 40
    # BOTTOM pillar: trident upright, fork crown pointing UP at the gap.
    bot = pygame.Surface((tw, half_h), pygame.SRCALPHA)
    build_trident(bot, tw // 2, int(46 * ps), half_h + 6 * ps, ps, hw=4 * ps)
    surf.blit(bot, (ox, gap_bot - int(46 * ps)))
    # TOP pillar: the SAME prop flipped vertically — fork crown points DOWN.
    top = pygame.Surface((tw, half_h), pygame.SRCALPHA)
    build_trident(top, tw // 2, int(46 * ps), half_h + 6 * ps, ps, hw=4 * ps)
    top = pygame.transform.flip(top, False, True)
    surf.blit(top, (ox, gap_top + int(46 * ps) - half_h))
    # Gap guides.
    pygame.draw.line(surf, (255, 220, 90), (ox, gap_top), (ox + tw, gap_top), 1)
    pygame.draw.line(surf, (255, 220, 90), (ox, gap_bot), (ox + tw, gap_bot), 1)


def main():
    pygame.init()
    W, H = 1180, 760
    surf = pygame.Surface((W, H))
    surf.fill((26, 28, 34))

    font = pygame.font.SysFont("dejavusans", 26, bold=True)
    sub = pygame.font.SysFont("dejavusans", 16)
    tag = pygame.font.SysFont("dejavusans", 15, bold=True)

    # Two figure panels: DAY (left) and NIGHT (right), same figure, same scale.
    pan_w, pan_h = 430, 600
    pan_y = 96
    day_rect = pygame.Rect(40, pan_y, pan_w, pan_h)
    night_rect = pygame.Rect(40 + pan_w + 24, pan_y, pan_w, pan_h)
    _day_bg(surf, day_rect)
    _night_bg(surf, night_rect)

    # Supersample each figure panel for crisp anti-aliased curves, then blit.
    K = 2
    ground_frac = 0.86
    for rect, dark in ((day_rect, False), (night_rect, True)):
        fig = pygame.Surface((pan_w * K, pan_h * K), pygame.SRCALPHA)
        feet_y = int(pan_h * ground_frac) * K
        build_sovereign(fig, (pan_w // 2) * K, feet_y, K)
        small = pygame.transform.smoothscale(fig, (pan_w, pan_h))
        surf.blit(small, rect.topleft)
        # Ground shadow ellipse under the hooves.
        gy = rect.y + int(pan_h * ground_frac)
        sh = pygame.Surface((180, 26), pygame.SRCALPHA)
        pygame.draw.ellipse(sh, (0, 0, 0, 90), sh.get_rect())
        surf.blit(sh, (rect.centerx - 90, gy - 6))

    pygame.draw.rect(surf, (90, 96, 108), day_rect, 2)
    pygame.draw.rect(surf, (90, 96, 108), night_rect, 2)
    surf.blit(tag.render("DAY SKY", True, (40, 40, 50)), (day_rect.x + 10, day_rect.y + 8))
    surf.blit(tag.render("NIGHT SKY", True, (220, 220, 235)),
              (night_rect.x + 10, night_rect.y + 8))

    # Right column: the pillar-fit thumbnail + a 1x silhouette read.
    col_x = night_rect.right + 30
    surf.blit(sub.render("PILLAR-FIT", True, (235, 235, 240)), (col_x, pan_y + 4))
    surf.blit(sub.render("(prop mirrored)", True, (170, 174, 184)), (col_x, pan_y + 24))
    _pillar_thumb(surf, col_x, pan_y + 50, 96, 360)

    # A 1x blackout-ish silhouette read of the figure (does the upper-radiating
    # crown + tines hold at small size?).
    surf.blit(sub.render("1x READ", True, (235, 235, 240)), (col_x, pan_y + 430))
    sil_h = 150
    sil = pygame.Surface((110 * 3, sil_h * 3), pygame.SRCALPHA)
    build_sovereign(sil, 55 * 3, int(sil_h * 0.92) * 3, 3 * 110 // 200 + 1)
    sil_small = pygame.transform.smoothscale(sil, (110, sil_h))
    surf.blit(sil_small, (col_x, pan_y + 456))
    pygame.draw.rect(surf, (90, 96, 108), (col_x, pan_y + 456, 110, sil_h), 1)

    # Header.
    surf.blit(font.render("HORNED SOVEREIGN", True, GOLD_LIT), (40, 24))
    surf.blit(sub.render("infernal monarch event boss — crown-of-horns + grand trident — round 1",
                         True, (210, 196, 168)), (40, 60))
    # Palette swatches (kept clear of the right-hand pillar column).
    px = 470
    for name, col in (("oxblood", OXBLOOD), ("obsidian", OBSIDIAN), ("gold", GOLD)):
        pygame.draw.rect(surf, col, (px, 30, 28, 28))
        pygame.draw.rect(surf, (90, 96, 108), (px, 30, 28, 28), 1)
        surf.blit(sub.render(name, True, (210, 210, 220)), (px + 34, 36))
        px += 130

    out = "docs/epic_boss/horned-sovereign/round_1.png"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(surf, out)
    print("wrote", out)


if __name__ == "__main__":
    main()
