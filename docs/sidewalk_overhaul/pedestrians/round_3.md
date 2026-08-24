# Pedestrians — round 3 (VARIETY EXPANSION)

**Sheet:** `docs/sidewalk_overhaul/pedestrians/round_3.png` (1400×3134)
**Generator:** `tools/ped_explore_round3.py` (scratch copy of the pool + drawer; `game/` untouched)

Pool **50 → 57**: 3 new archetypes, 13 new rows, 6 rows nominated for retirement.

---

## 1. Three new archetypes

Chosen from the candidate list for one reason each: they add a *kind of outline event*
the pool does not own yet. Every existing accessory is horizontal (pole, yoke), overhead
and round (parasol, head tray), or hip-level (basket, cane, bundle).

| Key | Who | The outline event it adds |
|---|---|---|
| `A_ROD` | **Fisherman** — belted tunic, chest strap, creel on the back hip | A long springy **diagonal** running from the front hand up over the head to a tip ~8 px above the crown, with a hanging catch on a thread. The pool had no steep diagonal at all. |
| `A_BARROW` | **Handcart porter** — pitched-forward body, two shafts, load box, spoked wheel | A **vehicle on the deck**: the only cast member whose mass sits at ground level rather than on the shoulders. Doubles the footprint low down; the wheel *rolls* with `t`. |
| `A_PIPA` | **Strolling musician** — pear lute across the chest, neck past the far shoulder | A **bulge on the body edge plus a short spar clearing the head**, with two skin dots on opposite ends of it (fretting hand + plucking hand) — "playing", not "carrying". |

**Passed over, with reasons** (so the call can be overruled):

* **Alms-bowl monk** — a bare-headed narrow robe with a bowl at the waist *is* `A_ROBE` at
  14 px; the bowl is interior detail and dies first. It would be a palette variant wearing
  a story.
* **Water-carrier with front-slung jars** — two hung loads on a bar is exactly what
  `A_POLE` and `A_YOKE` already are. A third re-dress of one idea.

### Construction sketches (the code that would land as `_draw_one` branches)

```python
# A_ROD — torso is a belted short tunic; the ROD owns the silhouette.
rod_c = pf(P.get("rod", (132, 100, 62)))
hand = (cx + body_w * 0.9 + lean, arm_y + torso_h * 0.35)
mid  = (cx - body_w * 0.6, hy - head_r * 1.4)
tip  = (cx - body_w * 3.0, hy - total_h * 0.62 + gait * 1.5)   # tip flexes with the gait
pygame.draw.lines(surf, rod_c, False, [hand, mid, tip], max(1, body_w // 7))
# + creel ellipse on the back hip, + optional catch on a thread off the tip
```

```python
# A_BARROW — cart AHEAD of the body; body pitched via the existing stoop scalar.
wx = cx + body_w * 3.1 + lean;  wr = max(2, int(leg_h * 0.85));  wy = ground - wr
for off in (0, 1):                                    # two shafts back to the hands
    pygame.draw.line(surf, wood, (cx + body_w * 1.5 + lean, hand_y + off),
                     (wx - wr * 0.4, wy - wr * 0.2 + off), max(1, body_w // 8))
# load box on the frame, then hub + 3 spokes rotated by t*4.0 so the wheel turns
```

```python
# A_PIPA — pear body + neck that CLEARS the crown (a spar stopping at the
# shoulder just reads as a bulky sleeve).
body_r = pygame.Rect(bx - bwid // 2, by - bhei // 2, bwid, bhei)   # bwid = body_w*1.9
pygame.draw.ellipse(surf, wood, body_r)
neck_top = (bx - body_w * 1.15, hy - head_r * 2.1)
pygame.draw.line(surf, wood_dk, (bx, by - bhei * 0.35), neck_top, max(2, body_w // 5))
# raised elbow -> hand at the belly; second hand at the neck top
```

### Outline-distinctness check (IoU of the alpha mask at FAR 0.78×; lower = more distinct)

Shipped archetypes sit at **0.40–0.75** against each other (e.g. robe↔tunic 0.67,
tunic↔padded 0.75, pole↔tray 0.40). The new ones measure:

* `A_ROD` vs shipped: **0.22–0.50**
* `A_BARROW` vs shipped: **0.24–0.45**
* `A_PIPA` vs shipped: **0.26–0.62**

i.e. all three are at least as separable as the shipped archetypes are from one another.

---

## 2. The 13 new rows

8 in the new archetypes (3 fishermen, 3 barrows, 2 pipa players), 5 re-dressing existing
archetypes with genuinely new headwear / carry positions rather than new hues:

| Row | Archetype | What is new |
|---|---|---|
| N1 ochre fisher | `A_ROD` | conical hat, catch on the line |
| N2 teal young fisher | `A_ROD` | short/slim, bare-headed, no catch — a lighter frame under the same spar |
| N3 slate old fisher | `A_ROD` | stoop 0.16 + beard: the rod tips shallower over a bent back |
| N4 clay barrow | `A_BARROW` | stoop 0.20, hurried |
| N5 olive tall barrow | `A_BARROW` | taller + deeper pitch, cloth head-wrap |
| N6 stone barrow | `A_BARROW` | strolling, shallow pitch, pale sacked load, conical hat |
| N7 mauve pipa | `A_PIPA` | bun + hairpin, slim |
| N8 indigo pipa | `A_PIPA` | bald, bearded, stooped over the instrument |
| N9 flat-brim official | `A_ROBE` | **new hat `flatbrim`** (hard horizontal disc) + **new acc `scroll`** (tube out both sides at the waist) |
| N10 shawl matron | `A_SKIRT` | **new hat `shawl`** — head-cloth continues onto the shoulders, so head+shoulders read as one triangle |
| N11 back-basket gleaner | `A_STOOP` | **new acc `back_basket`** — tall pannier riding high on the BACK |
| N12 back-bundle traveller | `A_TUNIC` | **new acc `back_bundle`** — bedroll hump + chest strap |
| N13 ear-flap snow | `A_PADDED` | **new hat `earflap`** — flaps hang past the jaw, widening the head blob \[SNOW\] |

The three new carry positions (`back_basket`, `back_bundle`, plus the fisherman's creel)
put mass **behind** the figure — a part of the outline no shipped row uses.

---

## 3. CUT list — 6 nominated retires

Every one is a palette-only clone of a surviving row; no archetype loses its unique
construction, and each cut archetype keeps ≥4 rows.

| # | Row | Why it is weak |
|---|---|---|
| #5 | Robe · slate tall scholar | Palette-only clone of #1 — same bun+topknot, same stroll, same h1.10 narrow robe. At 14 px it is one person twice. |
| #10 | Skirt · stone basket | Third identical basket-arm matron after #6 and #8, in the same build band. |
| #13 | Tunic · ochre laborer | Sits between #11 and #15 on every axis (hurry+swing_arm, h1.0, b1.05) with no accessory — the most anonymous row in the pool. |
| #15 | Tunic · rust porter | Second clone of the #11 porter read; the tunic band still keeps 4 rows with a real height spread. |
| #30 | Pole · olive cloth | Duplicate of #27 (cloth-hat pole vendor, hurry, b1.05). The pole family loses only a hue. |
| #39 | Headload · ochre box | Fifth head tray with no unique note; #36–38/#40 already span the height range. |

Runners-up if the AD wants deeper cuts: **#34 Yoke · clay** (fifth identical yoke porter)
and **#28 Pole · sage conical** (third conical pole vendor).

---

## 4. Night-cap audit (measured, not asserted)

Rendered all **57** final rows × 3 gait phases onto the night deck and scanned the
**rendered** pixels:

```
hottest pedestrian px luma = 135   ·   px over 150 = 0   ·   gold-coin core = 230
PASS — every pedestrian px sits under the cap.
```

Note: the scratch drawer applies the **animals_cast-style second pull** on any night
colour still over 150 (`_cap_night`). `game/ped_cast.py` currently has only the generic
cool; the measurement passes either way today, but the new pale roles (ear-flap fur, pale
sacked load, scroll paper) are exactly the sort of thing that would drift over the cap
later, so folding the guard into `ped_cast._retint_person` at integration is recommended.

---

## 5. Open questions for the art director

1. Three archetypes vs. keeping the **monk** in place of the pipa player (the monk is more
   "town", the pipa more "promenade") — the sheet argues the monk cannot pay for a branch.
2. The barrow is the widest cast member (~26 px incl. cart). Is that acceptable spacing-wise
   in the near lane, or should the cart shrink ~15 %?
3. Cut depth: 6 as listed, or push to 8 with the two runners-up?
