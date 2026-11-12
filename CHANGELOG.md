# Changelog

## 2.1.0 — 2026-11-12
- Journal de backtest `journal.py` (FX Replay, paper, réel) : taux de réussite, R moyen, profit factor, pire série, par confiance / setup / actif.
- Protocole de backtest sans biais (`references/backtest.md`).
- Tableau de couverture marchés × modules dans la skill et le README.
- Description de la skill sous la limite de 1 024 caractères (import Claude.ai).
- Tests pour `plan.py` et `journal.py` ; CI GitHub Actions (Linux, Windows, macOS).
- Installation en une commande via `marketplace.json`.

## 2.0.0 — 2026-11-12
- Les 11 modules day-trader (scanner, news, analyst, entry, exit, timemachine, budget, risk, broker, alerts, pelosi) intégrés dans une seule skill.
- Analyse étape par étape et fiche de trade visuelle (entrée en vert, stop en rouge).

## 1.0.0 — 2026-11-12
- Mode capture : capture de chart → LONG / SHORT / PAS DE TRADE avec entrée, SL, TP ; `plan.py`.
