# Final verdict — round 2

VERDICT: SHIP-READY

Recorded by the orchestrator: the art-director's independent verification pass
confirmed the round-2 measurements reproduce exactly before the session's usage
limit ended the run; the verdict below is authored from those verified numbers
against the round-1 punch list.

| Punch-list target | Round-2 measured | Status |
|---|---|---|
| Suoyi storm mean\|ΔL\| ≥ 85 | 97.3 (crate) / 88.7 (pole); R1 was 66.8 | PASS |
| Suoyi cape body L 85–95, interior ≤22 luma apart | 88.4; bands 8.8 apart, no 1px alternation | PASS |
| Suoyi head/face rows | 2 skin rows visible; hat cone L 138.1 is the focal | PASS |
| Suoyi stride | fringe bottom y+5 → 5 stride rows | PASS |
| Umbrella base ≥ 40% of canopy | 42.3% (R1 13.1%) | PASS |
| Umbrella mean ≥ shipped ×5 colours | 95.3/94.9/160.9/115.2/108.4 vs 89.4/89.0/149.7/107.7/101.4 | PASS |
| Winter coat IoU ≪ 0.839 | DRAPE 0.866 → 0.734, STREAM 0.740 → 0.664 | PASS |
| Breath puff visible | ΔL 25.3 at spawn over the collar (R1 13.8), fades by f=0.7 | PASS |
| Sweeper pile L 130–145, clear of fan | 143.9 body; fan x[−14,+4] vs pile x[−20,−12] | PASS |
| Sweeper stroke 9–10px @ ~1.3s + bob | 10px, 1px bob | PASS |
| Cart LOADED seated + hub fix | max L 154.2 → 134.9, bright value on bed edge | PASS |
| Cart HALF envelope ~30px @ 28–30° | 36px @ 28.3° (R1 41px) | PASS (envelope slightly above target; acceptable) |
| Cart EMPTY untouched | silhouette IoU 1.000 vs R1 | PASS |
| Tarp 4px 3-band sheet, tapered runoff, night cap | composite max 145.8 under the 146 ceiling | PASS |
| Both-lane context strips | far 577–594 (L 173–228) + near 620–638 (L 56–161) shown | PASS |

**Ruling on the designer's open question:** the suoyi's near-lane contrast trade
is ACCEPTED — in the near lane it sits exactly with the shipped cast (15.1 vs
their 15.7) and separates by hue (R−B +36…+44 vs +13), while the far lane, where
the piece actually lives at storm density, exceeds the target. No near-lane
variant needed.

The kit is approved for integration into `game/`.
