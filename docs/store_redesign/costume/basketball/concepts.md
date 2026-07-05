# Basketball v2 — 5 Concepts

**Core rule for ALL designs:** the basketball (orange sphere with black seam curves) is the
PRIMARY identity prop and must be drawn LAST. Previous designs had no ball — that's fixed here.

**Basketball ball recipe (composite space):**
```python
import math
bx, by = BCX - 8, BCY + 24   # at feet; shift Y up for dribble/dunk variants
pygame.draw.circle(surf, (230, 115, 30), (bx, by), 7)       # orange body
pygame.draw.circle(surf, (20, 20, 20),   (bx, by), 7, 1)    # outline
pygame.draw.line(surf, (20, 20, 20), (bx, by-7), (bx, by+7), 1)   # vertical seam
pygame.draw.arc(surf, (20,20,20), (bx-9, by-7, 12, 14), 0.3, math.pi-0.3, 1)
pygame.draw.arc(surf, (20,20,20), (bx-3, by-7, 12, 14), math.pi+0.3, 2*math.pi-0.3, 1)
```

**Kit stack (basketball-specific — DIFFERENT from soccer):**
- Jersey: sleeveless TANK (no sleeves) — shoulder straps or bare shoulders are the hoops tell
- Shorts: LONG/baggy (knee-length, longer than soccer's short shorts)
- Footwear: high-top sneakers with thick sole + ankle collar (not soccer cleats)
- Optional: thin headband, wristband on near wing

---

## Design 1 — THE NBA HOME

**Archetype:** Classic NBA home uniform (white home kit)
**Jersey:** White body via palette (`body_main=(245,245,248)`). Orange `(210,85,20)` shoulder
straps + side panels. Bold orange "23" on chest cleared of any pattern.
**Shorts:** Bright white, with orange side stripe. Hem at BCY+8.
**Sneakers:** White high-tops with orange accent strip, thick grey rubber sole.
**Ball position:** At feet `(BCX-8, BCY+24)`. Drawn LAST.
**Palette:** White + NBA orange `(210,85,20)` + near-black `(20,20,28)` + grey sole.
**Distinctness:** Only white-body design with orange accent system.

---

## Design 2 — THE ROAD WARRIOR

**Archetype:** Away/road dark uniform (Brooklyn Nets black away style)
**Jersey:** Deep black body via palette (`body_main=(22,22,30)`). White "7" on chest.
White shoulder piping outlines the tank armholes.
**Shorts:** Black with white side stripe. Hem at BCY+8.
**Sneakers:** Black high-tops with white sole stripe, chrome accent.
**Ball position:** Dribble height `(BCX-16, BCY+12)` — ball at thigh, "about to dribble."
**Palette:** Black + white + silver/chrome accent `(180,185,200)`.
**Distinctness:** Only dark-body design; dribble-height ball implies motion.

---

## Design 3 — THE RETRO '80s LEGEND

**Archetype:** 1980s short-shorts style (Celtics green, canvas Converse)
**Jersey:** Celtics green body via palette (`body_main=(0,130,60)`). White horizontal
chest stripe with "33" in white on the green panel.
**Shorts:** Retro SHORT white shorts (barely clearing BCY+6, not baggy — the retro tell),
with thin green side stripe.
**Sneakers:** Classic white canvas high-top (Converse CONS silhouette), green toe cap.
**Ball position:** Held near the near-wing at `(BCX+12, BCY-2)` — "passing" pose.
**Palette:** Celtic green `(0,130,60)` + white + gold `(200,160,10)` accent.
**Distinctness:** Short shorts (not baggy), green, ball in "pass" position at wing level.

---

## Design 4 — THE LAKER DUNKER

**Archetype:** Purple + gold franchise (Lakers away), ball raised in dunk pose
**Jersey:** Deep purple body via palette (`body_main=(90,20,140)`). Gold `(240,180,0)`
arm piping + bold gold "24" on chest with dark outline.
**Shorts:** Purple with gold side stripe. Hem at BCY+8.
**Sneakers:** White/gold high-tops with purple tongue.
**Ball position:** RAISED near wing — `(BCX+12, BCY-6)` — Pip holding it overhead in dunk arc.
**Palette:** Lakers purple `(90,20,140)` + gold `(240,180,0)` + white accents.
**Distinctness:** Only design with ball raised overhead; purple body unique in the set.

---

## Design 5 — THE STREETBALLER

**Archetype:** Blacktop outdoor hoops — mesh jersey, Jordan 1 sneakers, no team markings
**Jersey:** Concrete grey body via palette (`body_main=(135,135,145)`). Mesh-dot pattern
overlay over the chest. Big "BALL" or just "1" in dark on chest.
**Shorts:** Baggy dark charcoal shorts (longer hem at BCY+10).
**Sneakers:** Jordan 1-silhouette: black main + white midsole + red accent tab.
**Ball position:** Dribble height `(BCX-16, BCY+12)` — spinning orange ball.
**Palette:** Concrete grey + charcoal + blacktop black + hot orange `(230,115,30)`.
**Distinctness:** No team colour, urban feel, longest shorts, Jordan silhouette sneaker.
