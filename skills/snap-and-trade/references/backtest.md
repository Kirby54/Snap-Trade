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

- **R moyen > 0** : statistique descriptive ; 30 trades sont un premier
  contrôle, jamais une preuve suffisante de rentabilité.
- **Taux de réussite** seul ne veut rien dire : 35 % à 2,5R gagne, 70 % à
  0,3R perd.
- `stats --by confidence` : les signaux 4–5/5 doivent faire mieux que les
  2/5. Sinon le barème ne sert à rien et il faut le revoir.
- `stats --by setup` : retirer ou corriger un setup qui perd sur un vrai
  échantillon.
- Les résultats passés en replay ne garantissent rien en réel (glissement,
  spread, émotions). Étape suivante : `--source paper` sur 1 à 2 mois.

## Reproductibilité et validation hors échantillon

- Figer avant la série : version du dépôt, modèle et version, prompt,
  paramètres, marchés/UT, dates tirées au sort, coûts, règle de sortie.
- Conserver la capture originale (sans futur), la réponse brute, les prix
  saisis et la commande `plan.py`. Vérifier manuellement les niveaux lus.
- Séparer une période de développement et une période finale jamais utilisée
  pour ajuster les règles. Ne pas mélanger replay, paper et réel dans un verdict.
- Publier le journal complet anonymisé et le nombre de signaux PAS DE TRADE,
  non exécutés, ouverts et clôturés ; ne pas supprimer les pertes.
- Indiquer frais, spread et glissement dans `--cost-r` lors du résultat :
  coûts monétaires totaux / risque monétaire initial. Sans cela, stats brutes.
- Rapporter taille d'échantillon, R moyen net, profit factor et pire série,
  par marché/UT/confiance, ainsi que les limites et régimes couverts. Un
  échantillon court ou dépendant ne justifie pas une probabilité de réussite.
- Un stop touché peut être exécuté au-delà du niveau : saisir `outcome exit`
  et le prix effectif. Une sortie manuelle après TP1 ne peut pas être décrite
  par un seul prix de position restante : utiliser le prix de sortie moyen
  pondéré de toute la position (frais saisis séparément).

## Journal fiable

Une commande à la fois. Écriture atomique avec fichier temporaire unique et
verrou `.lock` ; si une autre commande est active, l'accès est refusé. Après
un arrêt brutal, supprimer le verrou uniquement après avoir vérifié qu'aucun
processus n'utilise le journal, puis faire une copie de sauvegarde. Préférer
un disque local (les garanties d'un partage réseau dépendent du système).
Les anciens CSV sans `cost_r` sont lus comme bruts et migrés à la prochaine
écriture. Une ligne mal formée est refusée sans écraser le fichier.
Les séries de pertes sont comptées dans l'ordre d'enregistrement des signaux,
pas dans l'ordre de clôture ; elles ne représentent pas un drawdown monétaire.
Sans TP2, la gestion split sort toute la position à TP1. Les deux colonnes
comparent des gestions alternatives théoriques, pas deux résultats exécutés.
