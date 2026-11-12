# Protocole de backtest (FX Replay ou tout outil de replay)

But : savoir si les signaux du mode capture gagnent plus qu'ils ne
perdent, sans se mentir.

## Règles anti-biais

1. **Ne jamais voir la suite.** Dans FX Replay, avancer jusqu'à un point,
   faire la capture, ne pas avancer avant d'avoir la fiche de trade.
2. **Choisir les points au hasard** (une date et une heure tirées avant de
   regarder le chart), pas « là où il se passe quelque chose ».
3. **Garder tous les signaux**, y compris les PAS DE TRADE et les pertes.
   Ne jamais refaire une analyse qui a perdu.
4. **Ne pas changer le plan après coup** : entrée, stop, TP tels que donnés
   par la fiche.
5. **Mélanger** marchés (forex, indices, crypto, actions) et unités de
   temps (5m, 15m, 1h, 4h), et noter `--source replay`.

## Déroulé d'un signal

1. Capture FX Replay → fiche de trade Snap & Trade.
2. Noter : `journal.py add ...` avec exactement les niveaux de la fiche.
3. Avancer le replay jusqu'à ce que l'un se produise :
   - l'entrée n'est jamais atteinte avant l'invalidation → `nofill`
   - le stop est touché avant TP1 → `sl`
   - TP1 touché, puis retour à l'entrée → `tp1`
   - TP2 touché → `tp2`
   - sortie manuelle (fin de séance, invalidation) → `exit --exit PRIX`
   Si stop et TP sont touchés dans la même bougie : compter `sl` (prudence).
4. Noter : `journal.py result ID --outcome ...`.

## Lire les stats

- **R moyen > 0** sur au moins 30 trades clôturés : avantage possible.
- **Taux de réussite** seul ne veut rien dire : 35 % à 2,5R gagne, 70 % à
  0,3R perd.
- `stats --by confidence` : les signaux 4–5/5 doivent faire mieux que les
  2/5. Sinon le barème ne sert à rien et il faut le revoir.
- `stats --by setup` : retirer ou corriger un setup qui perd sur un vrai
  échantillon.
- Les résultats passés en replay ne garantissent rien en réel (glissement,
  spread, émotions). Étape suivante : `--source paper` sur 1 à 2 mois.
