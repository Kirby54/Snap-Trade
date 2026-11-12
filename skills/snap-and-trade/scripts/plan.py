#!/usr/bin/env python3
"""Vérifie un plan de trade et calcule R:R et taille de position.

Exemples :
  python3 plan.py --side long  --entry 364.18 --sl 358.32 --tp 370.04 375.90
  python3 plan.py --side short --entry 67450 --sl 68120 --tp 66110 65300 --account 2000 --risk-pct 1
  python3 plan.py --side long  --entry 1.0850 --sl 1.0822 --tp 1.0910 --account 2000 --risk-pct 1 --point-value 100000

Code de sortie : 0 = plan valide, 1 = plan refusé, 2 = arguments invalides.
"""
import argparse
import json
import sys

MIN_RR = 1.5
MAX_RISK_PCT = 2.0


def fmt(x: float) -> str:
    if x == 0:
        return "0"
    mag = abs(x)
    decimals = 2 if mag >= 100 else 4 if mag >= 1 else 6
    return f"{x:,.{decimals}f}".replace(",", " ")


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except Exception:
            pass
    p =argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--side", required=True, choices=["long", "short", "buy", "sell"])
    p.add_argument("--entry", type=float, required=True)
    p.add_argument("--sl", type=float, required=True, help="stop loss")
    p.add_argument("--tp", type=float, nargs="+", required=True, help="un ou plusieurs take profit")
    p.add_argument("--account", type=float, help="capital du compte")
    p.add_argument("--risk-pct", type=float, default=1.0, help="risque par trade en %% du capital (défaut 1)")
    p.add_argument("--risk-amount", type=float, help="risque par trade en montant (remplace --risk-pct)")
    p.add_argument("--point-value", type=float, default=1.0,
                   help="valeur d'un point de prix pour 1 unité/contrat/lot (1 actions/crypto, 100000 lot forex, 50 ES...)")
    p.add_argument("--min-rr", type=float, default=MIN_RR)
    p.add_argument("--json", action="store_true")
    a = p.parse_args()

    side = "long" if a.side in ("long", "buy") else "short"
    sign = 1 if side == "long" else -1
    errors, warnings = [], []

    if min(a.entry, a.sl, *a.tp) <= 0:
        print("Prix invalides : tous les prix doivent être > 0.", file=sys.stderr)
        return 2

    risk = (a.entry - a.sl) * sign
    if risk <= 0:
        errors.append(f"stop du mauvais côté : pour un {side}, le stop doit être "
                      f"{'sous' if side == 'long' else 'au-dessus de'} l'entrée")
    elif risk / a.entry < 0.0005:
        errors.append("stop trop serré (< 0,05 % du prix) : le spread et le bruit le toucheraient")

    targets = []
    for tp in a.tp:
        reward = (tp - a.entry) * sign
        if reward <= 0:
            errors.append(f"TP {fmt(tp)} du mauvais côté de l'entrée")
            continue
        targets.append({"tp": tp, "reward": reward, "rr": reward / risk if risk > 0 else None})

    if risk > 0 and targets and targets[0]["rr"] < a.min_rr:
        errors.append(f"R:R vers TP1 = {targets[0]['rr']:.2f}, sous le minimum {a.min_rr}")
        # prix d'entrée limite qui ramènerait TP1 au R:R minimum
        tp1 = targets[0]["tp"]
        better = (tp1 + a.min_rr * a.sl) / (1 + a.min_rr)
        warnings.append(f"entrée limite à {fmt(better)} pour atteindre {a.min_rr}R vers TP1 avec le même stop")

    size = None
    if a.account is not None or a.risk_amount is not None:
        if a.risk_amount is not None:
            budget = a.risk_amount
        else:
            if a.risk_pct > MAX_RISK_PCT:
                warnings.append(f"risque de {a.risk_pct} % par trade, au-dessus des {MAX_RISK_PCT} % recommandés")
            budget = a.account * a.risk_pct / 100
        if risk > 0:
            qty = budget / (risk * a.point_value)
            size = {
                "risk_budget": budget,
                "qty": qty,
                "max_loss": qty * risk * a.point_value,
                "notional": qty * a.entry * a.point_value,
            }
            if a.account and size["notional"] > a.account:
                warnings.append(f"exposition {fmt(size['notional'])} > capital {fmt(a.account)} : levier "
                                f"x{size['notional'] / a.account:.1f} nécessaire")

    result = {
        "side": side, "entry": a.entry, "sl": a.sl, "risk_per_unit": risk,
        "risk_pct_of_price": risk / a.entry * 100 if risk > 0 else None,
        "targets": targets, "size": size, "valid": not errors,
        "errors": errors, "warnings": warnings,
    }

    if a.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"{'VALIDE' if not errors else 'REFUSÉ'}  {side.upper()}  entrée {fmt(a.entry)}  stop {fmt(a.sl)}")
        if risk > 0:
            print(f"  Risque / unité  {fmt(risk)} ({risk / a.entry * 100:.2f} % du prix)")
        for i, t in enumerate(targets, 1):
            rr = f"{t['rr']:.2f}R" if t["rr"] is not None else "?"
            print(f"  TP{i}            {fmt(t['tp'])}  ({rr})")
        if size:
            unit = "unités" if a.point_value == 1 else "lots/contrats"
            print(f"  Taille          {size['qty']:.6g} {unit}  (risque {fmt(size['risk_budget'])}, "
                  f"perte max au stop {fmt(size['max_loss'])}, exposition {fmt(size['notional'])})")
        for e in errors:
            print(f"  - refus : {e}")
        for w in warnings:
            print(f"  - note : {w}")
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
