![](../../workflows/gds/badge.svg) ![](../../workflows/docs/badge.svg) ![](../../workflows/test/badge.svg)

# TMAC2B: the 8-row TMAC2, as a separate Tiny Tapeout design

TMAC2B is [TMAC2](https://github.com/Muhammad-Sohair/tt-ternary-mac-v2) with twice the rows: an **8 × 5**
array of multiplier-free ternary PEs on **3x2 tiles**, top module `tt_um_msohair_tmac2b`. It streams its
weights from the QSPI Pmod flash exactly as TMAC2 does, at half the host traffic per output.

**Status:** under investigation, not signed off, not submitted. TMAC2 (repo `tt-ternary-mac-v2`, tag
`signoff-a`) is the shuttle's submission and is not affected by anything here. TMAC2B could only be added
as a second design on TT SKY 26d if it reaches the full sign-off standard by 22 November 2026, and only if
the slew root cause is found by 12 November ([notes/v2b_00](notes/v2b_00_separation_and_gates.md)).
RTL: 16/16 cocotb tests. Hardening at 3x2 does not yet meet the slew standard ([notes/v2_05](notes/v2_05_b.md)).

## Notes

- [v2b_00 separation and gates](notes/v2b_00_separation_and_gates.md): why this is its own repo, the
  rules and dates for the slew investigation.
- [v2_05 B](notes/v2_05_b.md): the 8-row design, the four 3x2 runs, the repair-vs-extraction slew mismatch.

Inherited from TMAC2 (they describe the 4-row design and cite TMAC2's runs, which live in `tt-ternary-mac-v2`):

- [v2_00 plan and rules](notes/v2_00_plan_and_rules.md): the owner's go/no-go rules and the progress log.
- [v2_01 spec](notes/v2_01_spec.md): options A/B/C, two corrections to earlier estimates.
- [v2_02 flash timing](notes/v2_02_flash_timing.md): the W25Q128JV quad-read timing, verified against the
  datasheet before any RTL, and why the sample point is programmable.

The v1 sign-off numbers and notes below describe the v1 chip (tag `signoff-v7`), kept for the history.

## How the design works

```
SPI (mode 0) -> command decoder -> packed weight bytes -> trit decoder -> W[8][5] (2-bit codes)
                                -> int8 activations a[5] ------------------------------+
BIST (LFSR -> core -> MISR) -mux->  8 rows x 5 ternary PEs: dot = sum (a XOR neg)&nz + popcount(neg)
                                    pipelined 24-bit saturating accumulators
MISO <- status / sat16(acc >>> shift) / raw 24-bit / weights / BIST signature
```

## The engineering story (the useful part)

The `notes/` folder is a log of what happened, including the mistakes:

1. [Flow walkthrough](notes/01_flow_walkthrough.md): RTL → cocotb → GDS → reading timing/DRC/LVS reports,
   on a practice counter. The first gate-level run failed because the testbench sampled too early.
2. [Spec and options](notes/02_spec.md): three sized options. My area estimate turned out to be 1.55× too
   optimistic, and why.
3. [RTL and verification](notes/03_rtl_and_verification.md): the owner's design decisions, 8 bugs found
   and what each taught (one synthesis-only bug Vivado would have accepted), mutation testing.
4. [Hardening and sign-off](notes/04_signoff.md): 22 hardening runs. Pipelining and a reset synchroniser to
   close 50 MHz at ss/100 °C. Chasing max-slew from 1,325 violations down to one net, including a wrong
   theory I had to retract, and every warning explained.
5. [Silicon test plan](notes/05_silicon_test_plan.md): staged bring-up on the TT devkit, with what each
   failure would mean. The script is [devkit/tmac_bringup.py](devkit/tmac_bringup.py) (MicroPython, reuses
   the same Python model). For TMAC2 it also programs the QSPI Pmod flash and runs flash stages F1–F5
   ([notes/v2_04](notes/v2_04_devkit_bringup.md)); `test/test_devkit.py` runs the script against the RTL.

## Running it (Windows, no WSL or Docker needed)

```
python -m venv .venv && .venv\Scripts\pip install -r test/requirements.txt
cd test && mingw32-make                       # RTL simulation (iverilog 12 + cocotb 2.1)
mingw32-make GATES=yes                        # gate level: netlist from the gds action, PDK_ROOT set
python tmac_model.py --write-rtl              # regenerate the BIST signature after model/BIST changes
```

Hardening runs in GitHub Actions (`.github/workflows/gds.yaml`). The SKY130 cell models for gate-level
simulation come from `ciel` (`ciel enable --pdk-family sky130 -l sky130_fd_sc_hd <version>`).

`practice/counter/` holds the Step 1 design. The 4 × 10 versions (tag `acc24-shift-ref`, branch
`eval/4x10-acc24-3x2`) are in the v1 repo, `tt-ternary-mac`.

## License

Apache-2.0. Built on the Tiny Tapeout SKY template (Apache-2.0).
