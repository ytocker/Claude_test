# PROFILE frame + tag — 4 placement options (brainstorm, no renders)

## Bug that triggered this
Current frame: cot.union(bird_r).inflate(18,18), height-capped to
(cloud.top-6)-fr.top. Measured: Pip's real drawn bbox bottom = 292 (verified,
mask threshold 8), current frame bottom = 290. **Pip's feet stick out 2px below
his own frame.**

## Verified geometry (orchestrator-checked)
- Pip real silhouette bbox: (59,242,64,50), bottom=292.
- cloud_rect(): (28,296,160,26).
- Rope columns (draw_signchain formula, STORE row cx=102 cy=386 ang=-3):
  left sgn=-1 at y306=42.4 y316=42.0 y334=41.3 y348=40.7 (near-vertical)
  right sgn=+1 at y306=176.0 y316=174.0 y334=170.4 y348=167.7 (rakes inward)
- STORE plank rotated bbox top: y359.
- Subtitle bbox bottom: y178.
- Frame right-edge cap: fr.right <= 168 (room for deck run to continue to START).

## A — sill-plate: frame rests on cloud's shoulder, tag hangs BELOW on straps
Frame Rect(23,208,118,98) -> bottom 306. Pip clearance 306-292=14px.
Bottom rail crosses the cloud (deliberate - cloud puffs out below/right).
Ropes never touch it (anchors at y316, 10px below rail).
Tag: plate 110x28 at x49-159,y324-352. Two 3px gold straps + nail() rings from
rail y306 to plate top y324, same iron vocabulary as the chain.
Clearances: ropeL 5.2px, ropeR 6.8px, STORE 7px, cloud tip 3px (straps run
through that gap). Hit rect 116x48.
Tappable because: tethered hardware (straps+rings), sits alone in thumb band.
Feasibility: trivial - 2 lines + 4 nails on existing plate code.

## B — portrait-straddle: frame encloses house+Pip+cloud; tag STRADDLES bottom rail
Frame Rect(23,208,145,126) -> bottom 334 (right edge 168 = exactly at cap).
Pip clearance 334-292=42px, most generous of the four. Contains cloud
vertically (13px above rail) and on the left.
**Real defect, stated plainly:** left rope crosses the bottom rail at y334,
x41.5, inside frame's x23-168. Right rope (171.7 at that y) stays outside.
Proposed fix: an _iron_ring on the rail where the rope passes, turning the
crossing into a visible fixing point - on-thesis since the chain already
claims to hang from the framed cloud.
Tag: plate 108x28 centred (102,334) -> x48-156,y320-348, rail passes behind it.
Clearances: Pip 28px, ropeL 4.1px, ropeR 10.6px, STORE 11px (best of the four).
Known asymmetry: plate centres at x102 (ropes' midpoint), not frame centre x95.5,
so it reads correct against ropes but slightly right against the rail.
Tappable because: a plate breaking a continuous rail is a strong "separate
object" cue - the interruption itself is the affordance.
Feasibility: trivial - current plate code, different rect, one ring.

## C — header-cartouche: open-bottom frame (no bottom rail); tag ABOVE as crown
Frame: top rail y204, x23-141. Two 2px verticals x23/x141, y204-312, gold
finial beads at the bottom. NO bottom rail - clipping Pip is structurally
impossible. Legs stand in the cloud, finials read as sinking into it.
ropeL (x42) vs left leg (x23) = 19px apart, co-exist only 13 rows; finials end
y312, anchors start y316.
Tag: plate 120x30 centred (82,202) -> x22-142,y187-217, sits ON the top rail.
Clearances: subtitle 9px, Pip-top 25px, ropes 79px away - least constrained
geometry of the four.
Honest cost: stacks a THIRD text element under SKYBIT/POCKET SKY FLYER in the
top third, puts the control in the least thumb-reachable part of the screen.
Geometrically safest, ergonomically weakest.

## D — medallion-collar: circular avatar ring around Pip; tag IS the rim (arc text)
Frame: collar centre (91,266), outer r=58, inner r=46, 12px gutter, gold
annulus + cached radial tint inside.
Pip containment vs inner r=46: worst bbox corner (123,292) at distance 41.2 ->
4.8px clear; (59,242) at 40.0 -> 6.0px. Below feet: 46-26=20px. Real silhouette
is empty at those corners so true clearance is larger.
Best rope separation of any option: at y316 collar spans only x62-120 -> 20px
from ropeL, 44px from ropeR - never near either column at any y.
Tag: "PROFILE" @11px, per-glyph rotozoom to tangent, on r=52 gutter centreline,
bottom-dead-centre +-33deg -> x63-119. Chevron at trailing end. WHOLE DISC
(116x116) is the hit target - largest, most obviously-tappable control on the
menu after START.
Honest cost: 11px is the smallest type in the menu (sign planks run 17px), arc
text needs real tuning. Straight-plate alternatives verified NOT to work: need
>=105px width, either hits the left rope column or shifts ~11px off-axis
(glaring on a circle). The arc is not a flourish here, it's the only fit.
Feasibility: pure pygame - draw.circle, one cached SRCALPHA radial, rotozoom
per glyph.

## Designer's pick: A (sill-plate)
Only option that fixes the bug without renegotiating anything else in the
frozen composition. Keeps the tag where the user just shipped it (below),
buys 14px of genuine padding vs today's -2px, rail stays 10px clear of rope
anchors (no rope-crossing concession needed). Spends only 31px of the unused
right-edge budget.

Runner-up: B. Better picture (42px padding, whole floating home as one
portrait), straddle is what the user explicitly asked to revisit. Costs: left
rope threading the bottom rail (mitigated by an iron ring) and plate 6.5px
right of frame centre.

C is the safe geometric answer but the wrong ergonomic one. D is the most
distinctive with the best clearances of all four, but rests entirely on 11px
arc-set type carrying the menu's second-most-important label.

A's frame + B's straddling tag is NOT viable: a plate centred on A's rail
(y306) would span y292-320 and land 0px off Pip's feet - the frame must reach
~y334 before straddle is legal, which is why B is a separate option.
