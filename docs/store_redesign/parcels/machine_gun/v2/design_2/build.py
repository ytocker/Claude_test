"""NERF BLASTER — bright foam-dart toy parcel cosmetic.

A chunky kid-safe dart blaster carried below Pip, rotating with his bank. The
identity is the BRIGHT-ORANGE shell plus a rotating dart drum showing yellow
foam-dart TIP circles at the front and a wide muzzle — orange + foam tips read
unmistakably as a toy, never a real gun. A blue grip + a small blue trigger
nub asymmetrize the held end so the front/back is never ambiguous.

22px read tradeoffs: at the 44->22 downscale fine detail dissolves, so the read
is carried by bold masses with clear VALUE + hue separation. Pip is red-orange,
so an orange shell alone fuses into him — the blue grip/trigger is grown into a
chunky cool L-mass so a bright-cool block always borders Pip's body and breaks
the fuse. The orange stays (NERF identity) but the contrast lever is the blue.

The toy read is pinned by three fat round YELLOW foam-dart tips (dropped from
four — four merge to one warm speck at true size) sitting on a DARK drum hub, so
the tips pop as a distinct bright value instead of melting into warm-grey mush.
The muzzle and drum are split by a cool grey rim + a sky gap so the two orange
circles don't read as one blob at tilt.

Drawn on a 44px work surface then smoothscaled to 22 so the rims and tip dots
antialias cleanly. A cool-dark outline is laid first (inflated, +1px on the top
edge that meets Pip) so the shell separates from him and reads on DAY sky; a warm
keyline rides the orange top edge so the shell still separates on NIGHT sky.
"""
import pygame

# Tight toy palette. Orange is the shell (NERF identity); the COOL BLUE grip is
# grown chunky as the separation lever against Pip's red-orange body; yellow is
# the foam-dart tips, kept high-value so they pop off the dark drum hub.
ORANGE = (240, 122, 30)      # main shell — the identity mass
ORANGE_HI = (255, 168, 92)   # warm top lift on the shell
ORANGE_LO = (190,  84, 16)   # underside shade so the shell reads as a volume
BLUE = (46, 123, 224)        # grip + trigger — brighter/cooler, the contrast lever
BLUE_HI = (130, 186, 248)    # blue highlight
BLUE_LO = (28,  78, 168)     # blue shade so the chunky grip reads as a volume
YELLOW = (255, 224, 70)      # foam-dart tips — bright, high-value pop
YELLOW_HI = (255, 246, 180)  # dart-tip highlight
GREY = (150, 158, 172)       # muzzle ring + drum rim
GREY_HI = (206, 214, 226)    # muzzle rim light (brightest value, NIGHT lifeline)
HUB = (58, 60, 74)           # dark drum hub — distinct value so yellow tips pop
OUTLINE = (28, 26, 36)       # cool-dark: separates from Pip + reads on day sky
KEYLINE = (255, 206, 150)    # warm rim — the NIGHT lifeline on the shell


def build(mode="normal") -> pygame.Surface:
    # Mode-agnostic: one static blaster sprite for every Pip skin.
    S = 44
    surf = pygame.Surface((S, S), pygame.SRCALPHA)
    cx, cy = S // 2, S // 2

    # --- silhouette geometry -------------------------------------------------
    # A compact toy run: a stubby orange shell body with a fat round dart DRUM
    # slung under the front, a wide grey muzzle projecting forward, and a CHUNKY
    # blue grip + foregrip dropping from the back. Front is LEFT. Everything kept
    # ~4px off every edge so the rotozoom never clips the muzzle or grip at bank.
    body = pygame.Rect(14, cy - 6, 16, 10)         # orange shell, centre-right
    muzzle_c = (9, cy - 1)                          # wide muzzle, projects left
    muzzle_r = 6
    drum_c = (18, cy + 6)                           # round dart drum, slung down
    drum_r = 7
    # Chunky blue L-mass: a tall back grip plus a forward toe so a cool block
    # spans the held end — the strongest separation lever against Pip's body.
    grip = [(26, cy + 2), (34, cy + 2), (34, cy + 13),
            (29, cy + 13), (29, cy + 8), (26, cy + 8)]

    # --- baked outline pass (drawn first, inflated) --------------------------
    # One cool-dark silhouette under every mass so the blaster separates from Pip
    # and reads on day sky. The top edge that meets Pip is inflated +1px extra.
    pygame.draw.circle(surf, OUTLINE, drum_c, drum_r + 3)
    pygame.draw.circle(surf, OUTLINE, muzzle_c, muzzle_r + 3)
    pygame.draw.polygon(surf, OUTLINE,
                        [(24, cy + 1), (36, cy + 1), (36, cy + 14),
                         (28, cy + 14), (28, cy + 9), (24, cy + 9)])
    pygame.draw.rect(surf, OUTLINE, body.inflate(5, 6).move(0, -1),
                     border_radius=4)              # +1px top edge meeting Pip

    # --- chunky blue grip (held end, back) — the separation mass -------------
    # Drawn before the shell so the shell border sits clean over it. Bright/cool
    # so a value-light cool block always borders Pip regardless of bank angle.
    pygame.draw.polygon(surf, BLUE, grip)
    pygame.draw.polygon(surf, BLUE_LO,
                        [(29, cy + 8), (34, cy + 8), (34, cy + 13), (29, cy + 13)])
    pygame.draw.line(surf, BLUE_HI, (27, cy + 3), (33, cy + 3), 2)   # top lift

    # --- wide muzzle ring (front) --------------------------------------------
    # A fat orange ring with a BRIGHT grey rim and a yellow foam-tip core — the
    # grey rim is the brightest value, pinning "this end fires" and splitting the
    # muzzle from the drum behind it so the two orange circles never fuse.
    pygame.draw.circle(surf, GREY, muzzle_c, muzzle_r)
    pygame.draw.circle(surf, ORANGE, muzzle_c, muzzle_r - 1)
    pygame.draw.circle(surf, GREY_HI, muzzle_c, muzzle_r - 1, 1)     # bright rim
    pygame.draw.circle(surf, YELLOW, muzzle_c, muzzle_r - 3)         # loaded dart
    pygame.draw.circle(surf, YELLOW_HI, (muzzle_c[0] - 1, muzzle_c[1] - 1), 1)

    # --- the DART DRUM (slung under the front) -------------------------------
    # Orange ring -> bright grey rim -> DARK hub holding three fat YELLOW tips.
    # The dark hub is a distinct value from the bright yellow tips so they pop as
    # round darts instead of merging into warm-grey mush. Three, not four — four
    # blur to one speck; three fat dots stay unmistakably round at true size.
    pygame.draw.circle(surf, ORANGE, drum_c, drum_r)
    pygame.draw.circle(surf, GREY_HI, drum_c, drum_r, 1)            # bright rim ring
    pygame.draw.circle(surf, HUB, drum_c, drum_r - 2)              # dark hub
    for dx, dy in ((0, -3), (3, 2), (-3, 2)):                      # 3 fat tips
        tx, ty = drum_c[0] + dx, drum_c[1] + dy
        pygame.draw.circle(surf, YELLOW, (tx, ty), 3)
        pygame.draw.circle(surf, YELLOW_HI, (tx - 1, ty - 1), 1)

    # --- orange shell body ---------------------------------------------------
    pygame.draw.rect(surf, ORANGE, body, border_radius=4)
    pygame.draw.rect(surf, ORANGE_LO, (body.x + 2, body.bottom - 3, body.w - 4, 3),
                     border_radius=2)                # underside shade
    pygame.draw.line(surf, ORANGE_HI, (body.x + 3, body.y + 2),
                     (body.right - 3, body.y + 2), 2)  # top lift

    # --- blue trigger guard nub (under the shell, ahead of the grip) ---------
    # A blue trigger loop pinned at the shell underside so more cool borders the
    # warm shell along its lower run — extends the contrast block forward.
    pygame.draw.rect(surf, BLUE, (23, cy + 4, 4, 5), border_radius=1)
    pygame.draw.rect(surf, BLUE_HI, (23, cy + 4, 4, 1))

    # --- warm night keyline along the shell top run --------------------------
    # Rides just inside the outline on the orange upper edge so the shell still
    # separates from a dark sky from the same single sprite.
    pygame.draw.line(surf, KEYLINE, (body.x + 1, body.y),
                     (body.right - 2, body.y), 1)

    return pygame.transform.smoothscale(surf, (22, 22))
