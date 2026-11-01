# v2b Step 0 — B as its own design, and the rules for the slew investigation

Decided by the owner on 1 Nov 2026, after B had been stopped on 29 Oct (notes/v2_05_b.md).

## Separation from A

- **A is untouched.** A (TMAC2, `tt_um_msohair_tmac2`, 2x2) lives in `Muhammad-Sohair/tt-ternary-mac-v2`,
  tag `signoff-a`, `main` green at 2c24307 (GDS run 40810128379 reproduces sign-off run 40677816085). No
  commits, CI runs or branch changes there. A is the TT SKY 26d submission whatever happens here.
- **B is a separate Tiny Tapeout design**: repo `Muhammad-Sohair/tt-ternary-mac-v2b`, top module
  `tt_um_msohair_tmac2b`, 3x2 tiles. Every TT chip carries every design on the shuttle, so B would be an
  additional design next to A and cost only its own tiles.
- This repo was seeded on 1 Nov from A's repo branch `b-dev` (a933c0d), with its full history.
  **`b-dev` in `tt-ternary-mac-v2` is superseded by this repo**; it is left as it was and not updated (that
  note is recorded here only, by the owner's rule). Its run IDs (40698174384, 40756594220, 40756606063,
  40756615511) and those of A cited in the inherited notes belong to `tt-ternary-mac-v2`.
- Changes at the split: top module renamed `tt_um_msohair_tmac2` → `tt_um_msohair_tmac2b` (source file,
  `info.yaml`, `test/tb.v`, `test/Makefile`, `test/tmac_model.py`, devkit `PROJECT`); `info.yaml` title and
  description, `docs/info.md` and README updated for 8 rows (8-byte loads, 8 outputs, 10-byte READ_W,
  512-clock BIST, 8-byte hand example). No RTL behaviour changed. A's tags were not copied.

## Investigation rules (owner's, verbatim in substance)

1. Goal: find **why** post-GRT repair reports 0 slew violations while extraction shows up to 1.2 ns.
   Diagnosis first, fixes second.
2. Tooling: get LibreLane running locally — fix Docker **without a factory reset**, or another supported
   route such as WSL2, whichever is faster. If neither works within a day, investigate in GitHub Actions
   with extra debug outputs (the repair step's estimated parasitics vs post-route extraction for the worst
   nets).
3. **Hard gate 12 Nov 2026:** root cause not identified → B stops for good; findings become v3 input.
4. **22 Nov 2026:** if fixed, B must meet the full v1/A standard (timing at all corners, DRC/LVS,
   gate-level sim incl. slow test, mutation tests with control, slew residuals no worse than A's). Otherwise
   it is not submitted.
5. C is not attempted this shuttle (bigger tiles, and blocked by the same slew problem).
6. Never submit, pay or create accounts. Report progress against 12 Nov and 22 Nov at every handoff.

## Gates

| gate | date | status |
|---|---|---|
| repo split, CI running here | 1 Nov | see progress log |
| root cause identified | **12 Nov 2026** | — |
| B fully signed off | **22 Nov 2026** | — |
| shuttle closes | 30 Nov 2026 | owner submits/pays |

## Progress log

| date | status |
|---|---|
| 1 Nov | repo split from `b-dev`, module renamed; first CI run on the new repo (below) |
