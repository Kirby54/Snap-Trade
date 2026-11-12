---
name: snap-and-trade
description: >-
  Snap & Trade, tout-en-un. L'utilisateur envoie une capture d'écran de
  n'importe quel graphique (actions, crypto, forex, indices, matières
  premières, futures; n'importe quelle unité de temps, n'importe quelle
  plateforme : TradingView, MT4/MT5, Binance, broker...) et reçoit
  directement un plan de trade : LONG (achat) / SHORT (vente) / PAS DE TRADE,
  l'entrée, le stop loss, un ou deux take profit, le ratio risque/rendement,
  le niveau d'invalidation et, s'il donne son capital, la taille de position.
  Regroupe en une seule skill la lecture du graphique (scanner), le timing
  d'entrée, le plan de sortie (SL/TP), le contrôle du risque, le calcul de
  taille et les alertes. À utiliser dès qu'une capture de chart est envoyée,
  ou quand l'utilisateur dit « analyse ce chart », « buy ou sell ? »,
  « long ou short ? », « donne-moi SL et TP », « je rentre où ? », « c'est
  quoi le setup », « what's the trade », « long or short », « where's my
  stop », « entry stop target ».
argument-hint: "[capture du chart] [capital et risque % optionnels]"
---

# Snap & Trade

Une capture d'écran entre, un plan de trade sort. Pas de questions inutiles :
si le chart est lisible, on répond directement avec un sens, une entrée, un
stop et des objectifs. Si le chart ne montre pas d'avantage clair, la bonne
réponse est **PAS DE TRADE**, et on dit quoi attendre.

`${CLAUDE_SKILL_DIR}` est le dossier de cette skill.

## Ce qu'il faut lire avant d'analyser

- `references/lecture-chart.md` : la checklist pour lire une capture
  (actif, unité de temps, axe des prix, tendance, structure, niveaux,
  bougies, indicateurs visibles, volume).
- `references/setups.md` : les setups reconnus, et pour chacun où va
  l'entrée, le stop et les objectifs, en long comme en short.

## Étapes

1. **Lire la capture** avec `references/lecture-chart.md`. Noter l'actif,
   l'unité de temps, le dernier prix et les niveaux, uniquement à partir de
   ce qui est visible. Ne jamais inventer un prix qu'on ne peut pas lire sur
   l'axe. Si l'axe des prix est illisible, le dire et exprimer le plan en
   repères visibles (« sous le dernier creux à gauche ») ou demander une
   capture plus nette.
2. **Choisir le setup** dans `references/setups.md`, et compter les
   confluences (barème ci-dessous). Moins de 2 points : PAS DE TRADE.
3. **Placer entrée, SL et TP** selon le setup :
   - Le stop va là où l'idée est fausse : au-delà du dernier creux (long)
     ou du dernier sommet (short) qui protège le setup, plus une marge
     (environ 10 à 25 % de la taille moyenne d'une bougie visible).
     Jamais au milieu du bruit.
   - TP1 au prochain niveau de support/résistance visible, TP2 au niveau
     suivant ou à 3R.
   - Un stop qui ne tient pas sur un niveau logique = pas de trade.
4. **Vérifier les chiffres** avec le script, qui refuse un stop du mauvais
   côté et calcule R:R et taille :

   ```bash
   python3 "${CLAUDE_SKILL_DIR}/scripts/plan.py" --side short --entry 67450 --sl 68120 --tp 66110 65300
   python3 "${CLAUDE_SKILL_DIR}/scripts/plan.py" --side long --entry 1.0850 --sl 1.0822 --tp 1.0910 --account 2000 --risk-pct 1 --point-value 100000
   ```

   `--point-value` = valeur d'un point pour 1 unité (1 pour actions/crypto,
   100000 pour un lot forex standard, 50 pour l'ES, 20 pour le NQ...).
   Sous Windows, `python` au lieu de `python3`.
5. **Contrôle du risque** (règles fixes, jamais assouplies) :
   - R:R vers TP1 d'au moins **1.5**. En dessous : PAS DE TRADE, ou
     proposer d'attendre un meilleur prix d'entrée (ordre limite) qui
     ramène le R:R à 1.5.
   - Si l'utilisateur a donné son capital : risque par trade 1 % par défaut,
     jamais plus de 2 % sauf demande explicite.
   - Contre la tendance de fond : confiance plafonnée à « faible ».
6. **Répondre** avec le format ci-dessous, dans la langue de l'utilisateur.

## Barème de confluence

Un point par élément présent et visible sur la capture :

| élément | compte si |
| --- | --- |
| tendance | le trade va dans le sens de la structure (sommets/creux) de l'unité de temps affichée |
| niveau | l'entrée se fait sur un support/résistance, une cassure clôturée ou un retest |
| signal bougie | une bougie de confirmation clôturée (englobante, pin bar, cassure franche) |
| momentum | un indicateur visible (RSI, MACD, moyennes mobiles...) va dans le même sens, ou une divergence pour un retournement |
| volume | volume visible en hausse sur le mouvement dans le sens du trade |

0 à 1 : PAS DE TRADE. 2 : confiance faible. 3 : moyenne. 4 à 5 : élevée.

## Format de réponse

```
SIGNAL : SHORT (vente)  ·  confiance : moyenne (3/5)
Actif / UT : BTCUSD · 1h  ·  dernier prix lu : 67 480

Entrée      67 450  (limite sur le retest de l'ancien support)
Stop loss   68 120  (au-dessus du dernier sommet 68 010 + marge)
TP1         66 110  (2.0R, support du 8)
TP2         65 300  (3.2R, creux de la semaine)
Invalidation : clôture 1h au-dessus de 68 120

Pourquoi : structure baissière (sommets décroissants), cassure clôturée du
support 67 600, retest en cours, RSI sous 50.
Gestion : à TP1, prendre la moitié et remonter le stop au prix d'entrée.
Taille (2 000 $, risque 1 %) : 0.0298 BTC → perte max 20 $ au stop.
```

Pour PAS DE TRADE : dire pourquoi en une ligne, et ce qui ferait naître un
trade (« long si clôture 4h au-dessus de 1.0900, stop sous 1.0860 »).

## Règles

- Toujours une réponse directe : LONG, SHORT ou PAS DE TRADE. Pas de « ça
  dépend » sans plan.
- Le stop et les objectifs sont fixés avant l'entrée. Un stop ne s'éloigne
  jamais une fois le trade en cours.
- Une bougie qui n'est pas clôturée ne confirme rien.
- Chaque prix vient de la capture (ou d'un prix donné par l'utilisateur).
  Rien d'inventé. Si un chiffre est estimé, l'écrire « ≈ ».
- La confiance ne s'exprime jamais en pourcentage de réussite : une capture
  ne permet pas de calculer une probabilité.
- Une capture montre le passé. Le plan est une lecture technique, pas une
  prédiction.

## Ce que la skill ne fait jamais

Elle ne passe aucun ordre, ne promet aucun gain, n'élargit jamais un stop
pour faire passer un trade, et ne pousse jamais à augmenter le levier.

## Avertissement

Outil d'analyse technique et d'apprentissage, pas un conseil en
investissement personnalisé. La plupart des traders particuliers perdent
de l'argent, surtout avec levier. Le stop est un plan, pas une garantie :
un gap ou un marché rapide peut l'exécuter plus loin. À tester d'abord en
compte démo / paper trading.
