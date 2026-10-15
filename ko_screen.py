"""Kind-Overshoot screen. Official score stays 0 unless a deleted axis closes and flips.

Not a model of the ocean. Not a carbon flux. The measurements belong to their authors.
"""
import json
from pathlib import Path

def side(vals, residual):
    if any(v == residual for v in vals):
        return 0
    if all(v < residual for v in vals):
        return -1
    if all(v > residual for v in vals):
        return 1
    return 0

def kind_overshoot(*, intact, stripped, products, residual, axis_published, one_source,
                   same_units, support_kind, identity_abs_tol):
    out = {"score": 0.0, "verdict": None, "intact_side": None, "stripped_side": None, "identity_gaps": None}
    if support_kind != "closed_pairs":
        out["verdict"] = "SUPPORT_NOT_CLOSED_PAIRS"
        return out
    if not (axis_published and one_source and same_units):
        out["verdict"] = "GATE"
        return out
    if min(len(intact), len(stripped), len(products)) < 2 or not (len(intact) == len(stripped) == len(products)):
        out["verdict"] = "NOT_A_RECTANGLE"
        return out
    gaps = [round(p - i, 6) for p, i in zip(products, intact)]
    out["identity_gaps"] = gaps
    if any(abs(g) > identity_abs_tol for g in gaps):
        out["verdict"] = "AXIS_DOES_NOT_CLOSE"
        return out
    si, ss = side(intact, residual), side(stripped, residual)
    out["intact_side"], out["stripped_side"] = si, ss
    if si == 0 or ss == 0:
        out["verdict"] = "STRADDLE"
        return out
    if si == ss:
        out["verdict"] = "SAME_SIDE"
        return out
    out["verdict"] = "FLIP"
    return out

def main():
    pairs = [
        {"study": "Henson et al. 2012", "f100": 4.0, "f1000": 0.66, "te": 0.19},
        {"study": "DeVries and Weber 2017", "f100": 7.3, "f1000": 1.1, "te": 0.13},
        {"study": "Nowicki et al. 2022", "f100": 6.4, "f1000": 1.1, "te": 0.15},
    ]
    for p in pairs:
        p["product"] = round(p["f100"] * p["te"], 6)
        p["gap"] = round(p["product"] - p["f1000"], 6)
    residual = 1.7
    primary = kind_overshoot(
        intact=[p["f1000"] for p in pairs],
        stripped=[p["f100"] for p in pairs],
        products=[p["product"] for p in pairs],
        residual=residual, axis_published=True, one_source=True, same_units=True,
        support_kind="closed_pairs", identity_abs_tol=0.02,
    )
    assert primary["verdict"] == "AXIS_DOES_NOT_CLOSE" and primary["score"] == 0.0
    result = json.loads(Path(__file__).with_name("ko_result.json").read_text())
    assert result["primary"]["verdict"] == primary["verdict"]
    assert result["pairs"] == pairs
    print("ok", primary["verdict"], "score", primary["score"])

if __name__ == "__main__":
    main()
