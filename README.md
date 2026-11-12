# Snap & Trade

Une skill Claude tout-en-un : envoie une **capture d'écran de n'importe quel
graphique** (actions, crypto, forex, indices, futures ; n'importe quelle unité
de temps ; TradingView, MT4/MT5, Binance...) et reçois directement :

- **LONG (achat) / SHORT (vente) / PAS DE TRADE**
- l'entrée, le **stop loss**, **TP1** et **TP2**
- le ratio risque/rendement et le niveau d'invalidation
- la taille de position si tu donnes ton capital et ton risque

```
SIGNAL : SHORT (vente)  ·  confiance : moyenne (3/5)
Actif / UT : BTCUSD · 1h  ·  dernier prix lu : 67 480

Entrée      67 450  (limite sur le retest de l'ancien support)
Stop loss   68 120  (au-dessus du dernier sommet 68 010 + marge)
TP1         66 110  (2.0R)
TP2         65 300  (3.2R)
Invalidation : clôture 1h au-dessus de 68 120
```

Elle regroupe en une seule skill la lecture du chart, le timing d'entrée, le
plan de sortie, le contrôle du risque (R:R minimum 1.5, risque 1 % par défaut)
et le calcul de taille. Inspirée du pack
[day-trader-skill](https://github.com/Jakeschincariol/day-trader-skill).

## Installation

**Claude Code** : copie le dossier `skills/snap-and-trade` dans
`~/.claude/skills/` (Windows : `%USERPROFILE%\.claude\skills\`).

**Plugin** : ce repo est aussi un plugin Claude Code (`.claude-plugin/plugin.json`).

**Claude.ai / Desktop** : zippe le dossier `skills/snap-and-trade` et importe-le
dans *Paramètres > Capacités > Skills*.

## Utilisation

Colle une capture et écris par exemple « long ou short ? », « donne-moi SL et
TP », ou « analyse, j'ai 2 000 $ et je risque 1 % ».

Le script de calcul peut aussi s'utiliser seul :

```bash
python3 skills/snap-and-trade/scripts/plan.py --side short --entry 67450 --sl 68120 --tp 66110 65300 --account 2000 --risk-pct 1
```

## Avertissement

Outil d'analyse technique et d'apprentissage, **pas un conseil en
investissement**. Une capture montre le passé ; le plan est une lecture
technique, pas une prédiction. La plupart des traders particuliers perdent de
l'argent, surtout avec levier. Teste en compte démo d'abord.

## Licence

MIT
