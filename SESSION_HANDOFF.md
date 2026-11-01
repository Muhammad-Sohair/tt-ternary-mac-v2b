# Session handoff — 2026-11-01 (v2b, TMAC2B)

**B is stopped for TT SKY 26d (owner's decision rule, 1 Nov).** A (repo `tt-ternary-mac-v2`, tag
`signoff-a`, `main` green at 2c24307) is the only submission and was not touched by any of this work. Nothing
was submitted or paid; B's tiles are not to be bought.

## Gates

| gate | date | outcome |
|---|---|---|
| repo split, CI here | 1 Nov | done (d5b47f4; baseline run 41295299103 = old `b-dev` run exactly) |
| root cause identified | 12 Nov 2026 | **met 1 Nov** (notes/v2b_01) |
| B fully signed off | 22 Nov 2026 | **not reached**: final run failed the slew condition; B stopped |
| shuttle closes | 30 Nov 2026 | owner submits A |

## What was found (notes/v2b_01–03)

1. **Root cause.** Repair's parasitic estimate uses the sky130 tech-LEF isolated-wire capacitance
   (~0.08 fF/µm) where sign-off extraction gives 0.16–0.21 fF/µm; route length is not a factor. Post-GRT
   repair also downsized drivers on the optimistic view (3 of 29 final violators).
2. **Fix.** `LAYERS_RC` fitted from extraction (5,749 nets, R² 0.996; resistance already matched the LEF).
   Verified: estimate / extraction ≈ 1.0 on long nets (was ~0.4). The old 55 % post-GRT slew margin then hangs
   repair; 20 % works.
3. **Runs** (all DRC/LVS/antenna 0, precheck and GL test pass):

   | run | slew pins max_ss / nom_ss | worst | clock root | setup WS | util |
   |---|---|---|---|---|---|
   | baseline 41295299103 | 122 / 96 | +462 ps | fanout 16, cap viol. | +2.48 | 69.7 % |
   | lrc2 41309116865 (`eval/lrc2`) | 4 / 0 (1 net) | +65 ps | fanout 16, cap viol. | +2.31 | 71.2 % |
   | final 41316591374 (`eval/final`) | 60 / 33 (13 nets) | +2,105 ps | fanout 2, fixed | +1.18 | 73.4 % |

## v3 input

- Start from lrc2 (calibrated `LAYERS_RC`, margin 20 %) and fix only the clock root
  (`CTS_DISTANCE_BETWEEN_BUFFERS`), without also tightening the PnR slew limit: the final run changed both and
  the new long single-load nets (hold/fan-out buffers into 0.10–0.15 pF) are unexplained ([UNVERIFIED]).
- Add `li1` and `VIAS_R` to the calibration (both read 0 in the resizer with design-level `LAYERS_RC`).
- Upstream: known since 2022, open-pdks #251 (open) and #250 (removed sky130 `LAYERS_RC`). A comment with this
  evidence is drafted in `notes/drafts/open-pdks-251-comment.md`, **not posted**: the owner decides.
- C (PSRAM activations) and the APS6404L CS-low datasheet check remain v3 items (A's handoff).

## Tooling (works on this PC)

- LibreLane 3.0.14 in **WSL2 Ubuntu's own Docker engine** (Docker Desktop untouched, still broken).
  `ghcr.io/librelane/librelane:3.0.14` is the CI's exact build; PDK `8afc8346` in `~/pdk` via the image's
  `ciel`. Full local flow in `~/v2b_local`; about 1 h+ per run with 4 CPUs / 3.9 GB, slower than CI in repair
  and routing.
- `tools/slew_probe/`: `probe.tcl` (repair view vs sign-off view on a CI run), `fit_layer_rc.py`,
  `replay_postgrt_repair.tcl` (replay one step with knobs), `estimate_caps.*` (estimate vs extraction, all
  nets).
- Gotchas: Git Bash rewrites `/mnt/c/...` (use `MSYS_NO_PATHCONV=1`); LibreLane's private env (`_LIB_CORNER_*`,
  `_LAYER_RC_*`, `_SDC_IN`, `_PNR_EXCLUDED_CELLS`) is not in `_env.tcl` and must be set when replaying a step;
  SPEF caps can be in exponent form; `repair_design -verbose`'s "Remaining" counts nets to visit, not
  violations.

## Branches here

`main` (notes, tools), `eval/lrc1` (hung, cancelled 41303043155), `eval/lrc2`, `eval/final`. Keep them: the
notes cite their runs.
