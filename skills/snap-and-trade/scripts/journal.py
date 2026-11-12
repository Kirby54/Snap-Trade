#!/usr/bin/env python3
"""Journal de signaux Snap & Trade : note chaque signal, son résultat, et calcule les stats.

  python3 journal.py add --asset EURUSD --tf 15m --side short --entry 1.0850 --sl 1.0870 --tp1 1.0810 --tp2 1.0790 --confidence 3 --setup pullback
  python3 journal.py add --asset BTCUSD --tf 1h --side none --setup range       # PAS DE TRADE
  python3 journal.py result 1 --outcome tp1          # sl | tp1 | tp2 | be | exit (avec --exit PRIX) | nofill | open
  python3 journal.py list
  python3 journal.py stats [--by setup|confidence|asset|tf|side|source] [--json]

Résultats en R (1R = distance entrée -> stop), selon deux gestions :
  - « tout à TP1 »         : sl -1 · tp1/tp2 +R(TP1) · be 0 · exit au prix de sortie
  - « moitié TP1 / TP2 »   : sl -1 · tp1 = moitié à TP1, reste sorti à l'entrée · tp2 = moitié TP1 + moitié TP2
Les trades « nofill » (entrée jamais atteinte), « open » et les PAS DE TRADE ne comptent pas dans le taux de réussite.
"""
import argparse
import csv
import datetime as dt
import json
import math
import tempfile
from contextlib import contextmanager
import os
import sys

FIELDS = ["id", "date", "source", "asset", "tf", "side", "entry", "sl", "tp1", "tp2",
          "confidence", "setup", "outcome", "exit", "note", "cost_r"]
OUTCOMES = ["open", "sl", "tp1", "tp2", "be", "exit", "nofill"]
CLOSED = {"sl", "tp1", "tp2", "be", "exit"}
DEFAULT_FILE = os.path.join("trader", "journal.csv")


def num(x):
    if x in (None, ""):
        return None
    value = float(x)
    if not math.isfinite(value):
        raise ValueError("nombre fini requis")
    return value


def load(path):
    if not os.path.exists(path):
        return []
    with open(path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        required = set(FIELDS) - {"cost_r"}  # compatibilité avec les journaux v2.1
        headers = reader.fieldnames or []
        if (not required.issubset(headers) or set(headers) - set(FIELDS)
                or len(headers) != len(set(headers))):
            raise ValueError("en-tête du journal invalide")
        rows = list(reader)
    seen = set()
    for row in rows:
        if None in row or any(row.get(k) is None for k in required):
            raise ValueError("ligne du journal incomplète ou colonnes supplémentaires")
        ident = int(row["id"])
        if ident <= 0 or ident in seen:
            raise ValueError("identifiant dupliqué ou invalide")
        seen.add(ident)
        row.setdefault("cost_r", "0")
        a = argparse.Namespace(**row)
        for key in ("entry", "sl", "tp1", "tp2", "exit", "cost_r"):
            setattr(a, key, num(row.get(key)))
        err = validate(a)
        if row["side"] not in ("long", "short", "none") or err:
            raise ValueError(err or "sens du trade invalide")
    return rows


def save(path, rows):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".journal-", suffix=".tmp", dir=os.path.dirname(path) or ".")
    try:
        with os.fdopen(fd, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=FIELDS)
            w.writeheader()
            for r in rows:
                w.writerow({k: r.get(k, "") for k in FIELDS})
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


@contextmanager
def journal_lock(path):
    """Un seul lecteur/écrivain à la fois ; échouer sans écraser un journal."""
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    lock = path + ".lock"
    try:
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        raise ValueError("journal occupé (.lock) ; réessayer après la fin de l'autre commande")
    try:
        with os.fdopen(fd, "w") as fh:
            fh.write(str(os.getpid()))
        yield
    finally:
        os.unlink(lock)


def gross_r_multiples(row):
    """(R tout à TP1, R moitié TP1 / moitié TP2) pour un trade clôturé, sinon None."""
    if row["side"] not in ("long", "short") or row["outcome"] not in CLOSED:
        return None
    sign = 1 if row["side"] == "long" else -1
    entry, sl, tp1, tp2 = num(row["entry"]), num(row["sl"]), num(row["tp1"]), num(row["tp2"])
    risk = (entry - sl) * sign
    rr1 = (tp1 - entry) * sign / risk
    rr2 = (tp2 - entry) * sign / risk if tp2 is not None else rr1
    o = row["outcome"]
    if o == "sl":
        return -1.0, -1.0
    if o == "be":
        return 0.0, 0.0
    if o == "tp1":
        return rr1, rr1 / 2 if tp2 is not None else rr1
    if o == "tp2":
        return rr1, (rr1 + rr2) / 2
    r = (num(row["exit"]) - entry) * sign / risk  # exit
    return r, r


def r_multiples(row):
    gross = gross_r_multiples(row)
    if gross is None:
        return None
    cost = num(row.get("cost_r")) or 0.0
    values = tuple(v - cost for v in gross)
    if not all(math.isfinite(v) for v in values):
        raise ValueError("résultat R hors de la plage numérique")
    return values


def validate(a):
    for key in ("entry", "sl", "tp1", "tp2", "exit"):
        value = getattr(a, key, None)
        if value is not None and (not math.isfinite(value) or value <= 0):
            return f"{key} doit être fini et > 0"
    cost = getattr(a, "cost_r", None)
    if cost is not None and (not math.isfinite(cost) or cost < 0):
        return "cost-r doit être fini et >= 0"
    try:
        dt.date.fromisoformat(a.date) if a.date else None
    except ValueError:
        return "date invalide : utiliser YYYY-MM-DD"
    if getattr(a, "source", None) not in ("replay", "paper", "live"):
        return "source invalide"
    if not str(getattr(a, "asset", "")).strip():
        return "actif obligatoire"
    confidence = getattr(a, "confidence", None)
    if confidence not in (None, "") and str(confidence) not in tuple(map(str, range(6))):
        return "confiance invalide (0–5)"
    outcome = getattr(a, "outcome", None)
    if outcome not in (None, "", *OUTCOMES):
        return "résultat invalide"
    if a.side == "none":
        if outcome not in (None, "") or any(getattr(a, k, None) is not None for k in ("entry", "sl", "tp1", "tp2", "exit")) or cost:
            return "PAS DE TRADE ne doit contenir ni niveaux, ni résultat, ni coûts"
        return None
    if outcome == "exit" and a.exit is None:
        return "--outcome exit demande --exit PRIX"
    if outcome != "exit" and a.exit is not None:
        return "--exit ne s'utilise qu'avec --outcome exit"
    if outcome == "tp2" and a.tp2 is None:
        return "TP2 absent du plan"
    for k in ("entry", "sl", "tp1"):
        if getattr(a, k) is None:
            return f"--{k} est obligatoire pour un {a.side}"
    sign = 1 if a.side == "long" else -1
    if (a.entry - a.sl) * sign <= 0:
        return f"stop du mauvais côté pour un {a.side}"
    for k in ("tp1", "tp2"):
        v = getattr(a, k)
        if v is not None and (v - a.entry) * sign <= 0:
            return f"{k.upper()} du mauvais côté de l'entrée"
    if a.tp2 is not None and (a.tp2 - a.tp1) * sign <= 0:
        return "TP2 doit être au-delà de TP1"
    risk = (a.entry - a.sl) * sign
    if not math.isfinite(risk) or any(not math.isfinite((v - a.entry) / risk) for v in (a.tp1, a.tp2, a.exit) if v is not None):
        return "calcul R hors de la plage numérique"
    return None


def summarize(rows):
    signals = len(rows)
    no_trade = sum(1 for r in rows if r["side"] == "none")
    nofill = sum(1 for r in rows if r["outcome"] == "nofill")
    still_open = sum(1 for r in rows if r["side"] != "none" and r["outcome"] in ("open", ""))
    rs = [r_multiples(r) for r in rows]
    rs = [x for x in rs if x is not None]
    out = {"signals": signals, "no_trade": no_trade, "nofill": nofill, "open": still_open, "closed": len(rs)}
    for label, i in (("tp1", 0), ("split", 1)):
        vals = [x[i] for x in rs]
        if not vals:
            out[label] = None
            continue
        wins = [v for v in vals if v > 0]
        losses = [v for v in vals if v < 0]
        streak = worst = 0
        for v in vals:
            streak = streak + 1 if v < 0 else 0
            worst = max(worst, streak)
        out[label] = {
            "win_rate": len(wins) / len(vals) * 100,
            "avg_r": sum(vals) / len(vals),
            "total_r": sum(vals),
            "profit_factor": (sum(wins) / -sum(losses)) if losses else None,
            "max_losing_streak": worst,
        }
    return out


def print_summary(title, s):
    print(f"{title} · R après coûts renseignés (0 = brut)")
    print(f"  signaux {s['signals']} · PAS DE TRADE {s['no_trade']} · non exécutés {s['nofill']} · "
          f"ouverts {s['open']} · clôturés {s['closed']}")
    for label, name in (("tp1", "tout à TP1      "), ("split", "moitié TP1 / TP2")):
        m = s[label]
        if not m:
            continue
        pf = f"{m['profit_factor']:.2f}" if m["profit_factor"] is not None else ("∞" if m["total_r"] > 0 else "—")
        print(f"  {name}  réussite {m['win_rate']:.0f} % · R moyen {m['avg_r']:+.2f} · total {m['total_r']:+.1f}R · "
              f"profit factor {pf} · pire série {m['max_losing_streak']} pertes")
    if s["closed"] < 30:
        print(f"  note : {s['closed']} trades clôturés, moins de 30 : échantillon trop petit pour conclure")


def main():
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except Exception:
            pass
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--file", default=DEFAULT_FILE, help=f"fichier journal (défaut {DEFAULT_FILE})")
    sub = p.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("add", help="noter un signal")
    a.add_argument("--asset", required=True)
    a.add_argument("--tf", default="")
    a.add_argument("--side", required=True, choices=["long", "short", "buy", "sell", "none"])
    a.add_argument("--entry", type=float)
    a.add_argument("--sl", type=float)
    a.add_argument("--tp1", type=float)
    a.add_argument("--tp2", type=float)
    a.add_argument("--confidence", type=int, choices=range(0, 6), default=None)
    a.add_argument("--setup", default="")
    a.add_argument("--source", default="replay", choices=["replay", "paper", "live"])
    a.add_argument("--date", default=None, help="date du signal (défaut : aujourd'hui)")
    a.add_argument("--outcome", choices=OUTCOMES, default=None)
    a.add_argument("--exit", type=float)
    a.add_argument("--note", default="")
    a.add_argument("--cost-r", type=float, default=0.0, help="coûts totaux réalisés / risque initial (défaut 0, stats brutes)")

    r = sub.add_parser("result", help="noter le résultat d'un signal")
    r.add_argument("id", type=int)
    r.add_argument("--outcome", required=True, choices=OUTCOMES)
    r.add_argument("--exit", type=float)
    r.add_argument("--note", default=None)
    r.add_argument("--cost-r", type=float, default=None)

    sub.add_parser("list", help="afficher le journal")
    s = sub.add_parser("stats", help="statistiques")
    s.add_argument("--by", choices=["setup", "confidence", "asset", "tf", "side", "source"])
    s.add_argument("--json", action="store_true")

    args = p.parse_args()
    try:
        with journal_lock(args.file):
            return execute(args)
    except (OSError, ValueError, OverflowError, ZeroDivisionError) as exc:
        print(f"refus : {exc}", file=sys.stderr)
        return 1


def execute(args):
    rows = load(args.file)

    if args.cmd == "add":
        args.side = {"buy": "long", "sell": "short"}.get(args.side, args.side)
        err = validate(args)
        if err:
            print(f"refus : {err}", file=sys.stderr)
            return 1
        if args.outcome == "exit" and args.exit is None:
            print("refus : --outcome exit demande --exit PRIX", file=sys.stderr)
            return 1
        new_id = max((int(x["id"]) for x in rows), default=0) + 1
        fmt = lambda v: "" if v is None else repr(v)
        row = {
            "id": new_id, "date": args.date or dt.date.today().isoformat(), "source": args.source,
            "asset": args.asset.upper(), "tf": args.tf, "side": args.side,
            "entry": fmt(args.entry), "sl": fmt(args.sl), "tp1": fmt(args.tp1), "tp2": fmt(args.tp2),
            "confidence": "" if args.confidence is None else args.confidence, "setup": args.setup,
            "outcome": args.outcome or ("" if args.side == "none" else "open"),
            "exit": fmt(args.exit), "note": args.note, "cost_r": repr(args.cost_r),
        }
        r_multiples(row)  # vérifier les calculs avant toute écriture
        rows.append(row)
        save(args.file, rows)
        print(f"#{new_id} noté : {row['asset']} {row['tf']} {args.side.upper()}"
              + (f" entrée {args.entry} stop {args.sl} TP1 {args.tp1}" if args.side != "none" else " (PAS DE TRADE)"))
        return 0

    if args.cmd == "result":
        match = [x for x in rows if int(x["id"]) == args.id]
        if not match:
            print(f"refus : signal #{args.id} introuvable", file=sys.stderr)
            return 1
        row = match[0]
        if row["side"] == "none":
            print(f"refus : #{args.id} est un PAS DE TRADE, pas de résultat à noter", file=sys.stderr)
            return 1
        if args.outcome == "exit" and args.exit is None:
            print("refus : --outcome exit demande --exit PRIX", file=sys.stderr)
            return 1
        if args.outcome == "tp2" and not row["tp2"]:
            print(f"refus : #{args.id} n'a pas de TP2", file=sys.stderr)
            return 1
        candidate = dict(row)
        candidate["outcome"] = args.outcome
        candidate["exit"] = "" if args.exit is None else repr(args.exit)
        if args.cost_r is not None:
            candidate["cost_r"] = repr(args.cost_r)
        a = argparse.Namespace(**candidate)
        for key in ("entry", "sl", "tp1", "tp2", "exit", "cost_r"):
            setattr(a, key, num(candidate.get(key)))
        err = validate(a)
        if err:
            raise ValueError(err)
        r_multiples(candidate)
        row.update(candidate)
        row["outcome"] = args.outcome
        row["exit"] = "" if args.exit is None else repr(args.exit)
        if args.note is not None:
            row["note"] = args.note
        save(args.file, rows)
        rr = r_multiples(row)
        extra = f" → {rr[0]:+.2f}R (tout à TP1) · {rr[1]:+.2f}R (moitié TP1 / TP2)" if rr else ""
        print(f"#{args.id} {row['asset']} : {args.outcome}{extra}")
        return 0

    if args.cmd == "list":
        if not rows:
            print(f"journal vide ({args.file})")
            return 0
        for x in rows:
            rr = r_multiples(x)
            res = f"{rr[0]:+.2f}R" if rr else (x["outcome"] or "—")
            lvl = f"{x['entry']} / {x['sl']} / {x['tp1']}" + (f" / {x['tp2']}" if x["tp2"] else "") if x["side"] != "none" else "PAS DE TRADE"
            print(f"#{x['id']:>3} {x['date']} {x['asset']:<8} {x['tf']:<4} {x['side']:<5} "
                  f"{lvl:<34} conf {x['confidence'] or '-'} {x['setup']:<10} {res}")
        return 0

    # stats
    if not rows:
        print("{}" if args.json else f"journal vide ({args.file})")
        return 0
    groups = {"global": rows}
    if args.by:
        groups = {}
        for x in rows:
            groups.setdefault(x.get(args.by) or "—", []).append(x)
    result = {k: summarize(v) for k, v in sorted(groups.items())}
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
    else:
        for k, v in result.items():
            print_summary(k if args.by is None else f"{args.by} = {k}", v)
    return 0


if __name__ == "__main__":
    sys.exit(main())
