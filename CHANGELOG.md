# Changelog

## 2.2.0 — 2026-11-13
- Validation stricte des nombres, budgets, coûts, ordre des TP et résultats du journal.
- Dimensionnement décimal : conversion de devise, coûts, pas/minimum de quantité,
  plafond de notionnel et demande explicite pour dépasser 2 % de risque.
- R:R net ; perte au stop présentée comme estimation, pas garantie.
- Journal : verrou exclusif, fichiers temporaires uniques, rejet des CSV mal formés,
  statistiques nettes avec `cost_r`, compatibilité des anciens CSV, TP1 sans TP2 corrigé.
- Risk/broker : rejet des valeurs non finies ; contrôle des champs financiers à l'entrée du risk.
- Règles contre-tendance harmonisées et scénarios non confirmés explicitement conditionnels.
- Tests de non-régression, contrôles du dépôt, CI limitée en permissions et durée.
- Protocole hors échantillon et limites de validation documentés, sans résultats fabriqués.

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
