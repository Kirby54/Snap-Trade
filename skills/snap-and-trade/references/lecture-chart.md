# Lire une capture de chart

Dans cet ordre. Noter ce qu'on voit, pas ce qu'on suppose.

## 1. Identifier

- **Actif** : nom/ticker en haut à gauche (TradingView), dans l'onglet
  (MT4/MT5), ou en titre (Binance). Inconnu → le dire, l'analyse reste
  possible.
- **Unité de temps** : 1m, 5m, 15m, 1h, 4h, D, W. Inconnue → demander la précision ; ne pas donner de signal
  exécutable avec une unité de temps devinée.
- **Dernier prix** : l'étiquette colorée sur l'axe de droite.
- **Axe des prix** : lire au moins deux graduations pour connaître
  l'échelle. Échelle log ou non : en tenir compte pour les distances.

## 2. Tendance et structure

- Haussière : sommets et creux de plus en plus hauts.
- Baissière : sommets et creux de plus en plus bas.
- Range : sommets et creux à peu près aux mêmes niveaux.
- Cassure de structure : le dernier creux d'une hausse (ou le dernier
  sommet d'une baisse) est cassé en clôture → la tendance est remise en
  cause.
- Position par rapport aux moyennes mobiles si elles sont affichées
  (prix au-dessus d'une MM montante = biais haussier).

## 3. Niveaux

- Supports/résistances : zones touchées au moins deux fois, sommets et
  creux marquants, chiffres ronds.
- Lignes, zones, Fibonacci ou annotations déjà tracés par l'utilisateur :
  les reprendre.
- Ancien support cassé = nouvelle résistance, et inversement.
- Gaps, mèches longues répétées au même prix.

## 4. Bougies

- Seulement les bougies **clôturées** (la dernière est souvent en cours).
- Englobante, pin bar / marteau / étoile filante, inside bar, doji sur un
  niveau, grande bougie de cassure.
- Taille moyenne d'une bougie récente : sert à dimensionner la marge du
  stop.

## 5. Indicateurs visibles

- RSI : au-dessus/sous 50, surachat > 70, survente < 30, divergences.
- MACD : croisement, histogramme, divergences.
- Moyennes mobiles : pente, croisements, prix qui rebondit dessus.
- Bandes de Bollinger, VWAP, Ichimoku... : seulement si visibles.
- Volume : hausse sur les cassures = confirmation ; cassure sans volume =
  méfiance.

## 6. Contexte

- Le prix est-il au milieu de nulle part (loin de tout niveau) ? Alors
  souvent PAS DE TRADE : le stop serait arbitraire.
- Le mouvement est-il déjà très étendu (plusieurs grandes bougies d'affilée
  sans pause) ? Entrer maintenant = mauvais R:R ; attendre un retour.
- Unité de temps très courte (1m–5m) : marges plus serrées, mais bruit
  plus fort. Le dire.
