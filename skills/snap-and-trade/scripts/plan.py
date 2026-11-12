#!/usr/bin/env python3
"""Vérifie un plan et dimensionne une position (Python standard, sans réseau).

Prix et objectifs dans la devise de cotation ; capital, budget, coûts et
notionnel dans la devise du compte. --fx-rate convertit cotation -> compte.
Code de sortie : 0 valide, 1 refus de risque, 2 arguments invalides.
Les pertes calculées sont des estimations, pas une garantie d'exécution.
"""
import argparse
from decimal import Decimal, InvalidOperation, ROUND_FLOOR, localcontext
import json
import math
import sys

MIN_RR = 1.5
MAX_RISK_PCT = 2.0


def number(text):
    try:
        value = Decimal(text)
        if not value.is_finite() or not math.isfinite(float(value)):
            raise ValueError
        return value
    except (InvalidOperation, ValueError, OverflowError):
        raise argparse.ArgumentTypeError("nombre fini requis")


def fmt(x):
    mag = abs(x)
    decimals = 2 if mag >= 100 else 4 if mag >= 1 else 6
    return f"{x:,.{decimals}f}".replace(",", " ")


def plain(value):
    if isinstance(value, Decimal):
        out = float(value)
        if not math.isfinite(out) or (value != 0 and out == 0):
            raise ValueError("calcul hors de la plage numérique prise en charge")
        return out
    if isinstance(value, dict):
        return {k: plain(v) for k, v in value.items()}
    if isinstance(value, list):
        return [plain(v) for v in value]
    return value


def calculate(a):
    side = "long" if a.side in ("long", "buy") else "short"
    sign = 1 if side == "long" else -1
    errors, warnings = [], []
    risk = (a.entry - a.sl) * sign
    if risk <= 0:
        errors.append(f"stop du mauvais côté pour un {side}")
    elif risk / a.entry * 100 < a.min_stop_pct:
        errors.append(f"stop trop serré (< {a.min_stop_pct} % du prix)")
    minimum_stop = a.avg_candle * a.min_candle_multiple if a.avg_candle is not None else None
    if minimum_stop is not None and risk > 0 and risk < minimum_stop:
        errors.append(f"stop inférieur au minimum bougies : {risk} < {minimum_stop}")
    if a.open_price is not None:
        if (a.open_price - a.sl) * sign <= 0:
            errors.append("gap au-delà du stop : plan caduc")
        elif (a.tp[0] - a.open_price) * sign <= 0:
            errors.append("gap au-delà de TP1 : mouvement déjà réalisé, plan caduc")
        else:
            warnings.append("ouverture dans les bornes : attendre la confirmation et recalculer au prix d'entrée ; aucune exécution automatique")
    for first, second in zip(a.tp, a.tp[1:]):
        if (second - first) * sign <= 0:
            errors.append("les TP doivent être strictement ordonnés du plus proche au plus éloigné")
            break
    # Coût aller-retour estimé par unité, dans la devise du compte.
    loss_per_unit = risk * a.point_value * a.fx_rate + a.cost_per_unit
    targets = []
    for tp in a.tp:
        reward = (tp - a.entry) * sign
        if reward <= 0:
            errors.append(f"TP {fmt(tp)} du mauvais côté de l'entrée")
        net_reward = reward * a.point_value * a.fx_rate - a.cost_per_unit
        targets.append({"tp": tp, "reward": reward,
                        "rr": reward / risk if risk > 0 else None,
                        "net_rr": net_reward / loss_per_unit if risk > 0 else None})
    if risk > 0 and targets[0]["net_rr"] < a.min_rr:
        errors.append(f"R:R net vers TP1 = {targets[0]['net_rr']:.2f}, sous le minimum {a.min_rr}")
        cost_price = a.cost_per_unit / (a.point_value * a.fx_rate)
        better = (a.tp[0] + a.min_rr * a.sl - sign * (1 + a.min_rr) * cost_price) / (1 + a.min_rr)
        if better > 0 and (better - a.sl) * sign > 0 and (minimum_stop is None or (better - a.sl) * sign >= minimum_stop):
            warnings.append(f"entrée limite à {fmt(better)} pour atteindre {a.min_rr}R net ; confirmer le setup à ce prix")
    size = None
    if a.account is not None or a.risk_amount is not None:
        budget = a.risk_amount if a.risk_amount is not None else a.account * a.risk_pct / 100
        effective_pct = budget / a.account * 100 if a.account is not None else None
        if effective_pct is not None and effective_pct > MAX_RISK_PCT:
            message = f"risque de {effective_pct.normalize():f} % au-dessus des {MAX_RISK_PCT} % recommandés"
            warnings.append(message)
            if not a.allow_high_risk:
                errors.append(message + " ; --allow-high-risk requis pour une demande explicite")
        if risk > 0:
            qty = budget / loss_per_unit
            notional_per_unit = a.entry * a.point_value * a.fx_rate
            if a.max_notional is not None:
                qty = min(qty, a.max_notional / notional_per_unit)
            if a.qty_step is not None:
                qty = (qty / a.qty_step).to_integral_value(rounding=ROUND_FLOOR) * a.qty_step
            if qty <= 0 or (a.min_qty is not None and qty < a.min_qty):
                errors.append("budget insuffisant pour la quantité minimale / le pas de quantité")
            size = {"risk_budget": budget, "qty": qty,
                    "max_loss": qty * loss_per_unit,
                    "notional": qty * notional_per_unit}
            if a.account is not None and size["notional"] > a.account:
                warnings.append(f"exposition {fmt(size['notional'])} > capital {fmt(a.account)} : levier x{size['notional'] / a.account:.1f} nécessaire")
    if a.qty_step is None and size is not None:
        warnings.append("quantité théorique : préciser --qty-step et --min-qty selon le courtier")
    warnings.append("perte estimée au stop ; gaps, frais ou glissement non renseignés peuvent l'augmenter")
    return {"side": side, "entry": a.entry, "sl": a.sl, "risk_per_unit": risk,
            "risk_pct_of_price": risk / a.entry * 100 if risk > 0 else None,
            "fx_rate": a.fx_rate, "cost_per_unit": a.cost_per_unit,
            "avg_candle": a.avg_candle, "minimum_stop_distance": minimum_stop,
            "targets": targets, "size": size, "valid": not errors,
            "errors": errors, "warnings": warnings}


def main():
    # Pipes use the Windows locale by default; keep CLI/JSON UTF-8 everywhere.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--side", required=True, choices=["long", "short", "buy", "sell"])
    for flag in ("entry", "sl"):
        p.add_argument("--" + flag, type=number, required=True)
    p.add_argument("--tp", type=number, nargs="+", required=True)
    for flag in ("account", "risk-amount", "qty-step", "min-qty", "max-notional", "avg-candle", "open-price"):
        p.add_argument("--" + flag, type=number)
    for flag, default in (("risk-pct", "1"), ("point-value", "1"), ("min-rr", "1.5"),
                          ("min-candle-multiple", "1.5"), ("fx-rate", "1"), ("cost-per-unit", "0"), ("min-stop-pct", "0.05")):
        p.add_argument("--" + flag, type=number, default=Decimal(default))
    p.add_argument("--allow-high-risk", action="store_true")
    p.add_argument("--json", action="store_true")
    a = p.parse_args()
    for key, value in vars(a).items():
        if isinstance(value, Decimal):
            nonnegative = key in ("cost_per_unit", "min_stop_pct")
            if value < 0 or (not nonnegative and value == 0):
                p.error(f"--{key.replace('_', '-')} doit être {'>= 0' if nonnegative else '> 0'}")
    if any(tp <= 0 for tp in a.tp):
        p.error("tous les TP doivent être > 0")
    if a.min_candle_multiple < 1:
        p.error("--min-candle-multiple doit être >= 1")
    if a.risk_pct > 100:
        p.error("--risk-pct doit être <= 100")
    if a.account is not None and a.risk_amount is not None and a.risk_amount > a.account:
        p.error("le risque en montant dépasse le capital")
    if a.account is None and a.risk_amount is None and any(v is not None for v in (a.qty_step, a.min_qty, a.max_notional)):
        p.error("les contraintes de taille demandent --account ou --risk-amount")
    try:
        with localcontext() as ctx:
            ctx.prec = 40
            result = plain(calculate(a))
    except (ArithmeticError, ValueError) as exc:
        p.error(f"calcul impossible : {exc}")
    if a.json:
        print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
    else:
        print(f"{'VALIDE' if result['valid'] else 'REFUSÉ'} {result['side'].upper()} entrée {fmt(result['entry'])} stop {fmt(result['sl'])}")
        for i, target in enumerate(result["targets"], 1):
            rr = f"{target['net_rr']:.2f}R net" if target["net_rr"] is not None else "R:R indisponible"
            print(f"  TP{i} {fmt(target['tp'])} ({rr})")
        if result["size"]:
            s = result["size"]
            print(f"  Quantité {s['qty']:.10g} ; perte estimée {fmt(s['max_loss'])} ; exposition {fmt(s['notional'])}")
        for label in ("errors", "warnings"):
            for message in result[label]:
                print(f"  {label}: {message}")
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
