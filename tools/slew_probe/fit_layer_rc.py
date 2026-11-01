"""Fit per-layer wire R and C (per um) from a routed run's sign-off extraction.

For every routed signal net: per-layer routed length L_l (final DEF) and via counts, against the
extracted total wire capacitance and the sum of resistor values of that net (final SPEF). Least
squares C_net = sum_l c_l * L_l + c_via * n_via, and R_net = sum_l r_l * L_l + sum_v r_v * n_v.
The capacitance includes coupling to neighbours, as the sign-off STA sees it.

usage: fit_layer_rc.py RUN_DIR   (RUN_DIR = .../runs/wokwi)
"""
import glob
import os
import re
import sys

import numpy as np

LAYERS = ["met1", "met2", "met3", "met4"]


def def_routes(path):
    txt = open(path).read()
    units = int(re.search(r"UNITS DISTANCE MICRONS (\d+)", txt).group(1))
    nets_txt = txt.split("\nNETS ", 1)[1].split("\nEND NETS", 1)[0]
    out = {}
    for blk in nets_txt.split("\n    - ")[1:]:
        name = blk.split(None, 1)[0]
        if "+ USE CLOCK" in blk or "+ USE POWER" in blk or "+ USE GROUND" in blk:
            continue
        L = dict.fromkeys(LAYERS, 0.0)
        vias = {}
        for layer, rest in re.findall(r"(?:ROUTED|NEW) (\w+) (.*)", blk):
            pts = re.findall(r"\( (\S+) (\S+)(?: \S+)? \)", rest)
            if len(pts) >= 2:
                (x1, y1), (x2, y2) = pts[0], pts[1]
                x2 = x1 if x2 == "*" else x2
                y2 = y1 if y2 == "*" else y2
                if layer in L:
                    L[layer] += (abs(int(x2) - int(x1)) + abs(int(y2) - int(y1))) / units
            m = re.search(r"\)\s+(\w+)\s*;?\s*$", rest.strip())
            if m and not m.group(1).startswith("RECT"):
                v = m.group(1)
                vias[v] = vias.get(v, 0) + 1
        out[name.replace("\\", "")] = (L, vias)
    return out


def spef_nets(path):
    txt = open(path).read()
    names = dict(re.findall(r"^\*(\d+) (\S+)$", txt.split("*PORTS")[0].split("*NAME_MAP")[1], re.M))
    out = {}
    for blk in txt.split("*D_NET ")[1:]:
        head = blk.split("\n", 1)[0].split()
        name = names.get(head[0].lstrip("*"), head[0]).replace("\\", "")
        cap = float(head[1])
        res = blk.split("*RES", 1)[1].split("*END", 1)[0] if "*RES" in blk else ""
        rsum = sum(float(line.split()[3]) for line in res.strip().splitlines() if len(line.split()) == 4)
        out[name] = (cap, rsum)
    return out


def via_class(v):
    v = v.upper()
    for k in ("L1M1", "M1M2", "M2M3", "M3M4", "M4M5"):
        if k in v:
            return k
    return "OTHER"


def main(run):
    routes = def_routes(glob.glob(os.path.join(run, "final", "def", "*.def"))[0])
    vcls = ["L1M1", "M1M2", "M2M3", "M3M4"]
    print(f"routed signal nets in DEF: {len(routes)}")
    result = {}
    for corner in ("nom", "min", "max"):
        spef = spef_nets(glob.glob(os.path.join(run, "final", "spef", corner, "*.spef"))[0])
        rows, C, R = [], [], []
        for n, (L, vias) in routes.items():
            if n not in spef or sum(L.values()) < 5:
                continue
            vc = dict.fromkeys(vcls, 0)
            for v, k in vias.items():
                c = via_class(v)
                if c in vc:
                    vc[c] += k
            rows.append([L[l] for l in LAYERS] + [vc[c] for c in vcls])
            C.append(spef[n][0])
            R.append(spef[n][1])
        X, C, R = np.array(rows), np.array(C), np.array(R)
        nl = len(LAYERS)
        # C: per-layer per-um plus one shared per-via term
        Xc = np.hstack([X[:, :nl], X[:, nl:].sum(axis=1, keepdims=True)])
        c, *_ = np.linalg.lstsq(Xc, C, rcond=None)
        r, *_ = np.linalg.lstsq(X, R, rcond=None)
        cp, rp = Xc @ c, X @ r
        n_by_layer = {l: int((X[:, i] > 1.0).sum()) for i, l in enumerate(LAYERS)}
        um_by_layer = {l: float(X[:, i].sum()) for i, l in enumerate(LAYERS)}
        print(f"\n== {corner}: {len(C)} nets (length >= 5 um)")
        print("  layer  nets_using  total_um   C fF/um    R ohm/um")
        for i, l in enumerate(LAYERS):
            print(f"  {l:5s}  {n_by_layer[l]:10d}  {um_by_layer[l]:9.0f}  {1000 * c[i]:8.4f}  {r[i]:9.4f}")
        print(f"  per-via C {1000 * c[nl]:.4f} fF;  via R (ohm): " +
              ", ".join(f"{k} {r[nl + j]:.2f}" for j, k in enumerate(vcls)))
        for lab, y, p in (("C", C, cp), ("R", R, rp)):
            rel = (p - y) / np.maximum(y, 1e-12)
            print(f"  fit {lab}: R^2 {1 - ((y - p) ** 2).sum() / ((y - y.mean()) ** 2).sum():.4f}, "
                  f"median |err| {100 * np.median(np.abs(rel)):.1f} %, 90th pct {100 * np.percentile(np.abs(rel), 90):.1f} %")
        result[corner] = {l: (c[i], r[i]) for i, l in enumerate(LAYERS)}
    return result


if __name__ == "__main__":
    main(sys.argv[1])
