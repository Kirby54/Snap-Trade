# 📸 Snap & Trade

[![tests](https://github.com/Kirby54/Snap-Trade/actions/workflows/tests.yml/badge.svg)](https://github.com/Kirby54/Snap-Trade/actions/workflows/tests.yml)
![version](https://img.shields.io/badge/version-2.1.0-blue)
![licence](https://img.shields.io/badge/licence-MIT-green)
![python](https://img.shields.io/badge/python-3.10%2B-blue)

La skill Claude de trading **tout-en-un**. Envoie une **capture de n'importe
quel chart** (actions, crypto, forex, indices, futures ; toute unité de temps ;
TradingView, MT4/MT5, FX Replay, Binance...) et reçois l'analyse étape par
étape, puis une fiche de trade claire :

### 🔴 SHORT · NDX · 5 min

**Confiance** 🟢🟢⚪⚪⚪ faible (2/5) · **R:R** 1,8 / 2,4

| | niveau | détail |
| --- | --- | --- |
| 🟢 **Entrée** | **28 295** | limite, après une bougie de rejet clôturée |
| 🔴 **Stop loss** | **28 375** | au-dessus du dernier sommet + marge |
| 🎯 **TP1** | **28 150** | 1,8R |
| 🎯 **TP2** | **28 100** | 2,4R |
| ⛔ **Invalidation** | **28 375** | clôture 5 min au-dessus |

## ⚡ Installation

**Claude Code (plugin, une commande)** :

```
/plugin marketplace add Kirby54/Snap-Trade
/plugin install snap-and-trade@snap-and-trade
```

**Claude Code / Desktop (à la main)** : copie `skills/snap-and-trade` dans
`~/.claude/skills/` (Windows : `%USERPROFILE%\.claude\skills\`).

**Claude.ai** : zippe le dossier `skills/snap-and-trade` et importe-le dans
*Paramètres > Capacités > Skills*.

Python 3.10+ suffit : bibliothèque standard, aucune clé API pour l'analyse.

## 🧭 Ce qu'elle fait

**Mode capture** : lecture du chart → structure → niveaux → setup → score de
confluence sur 5 → vérification des chiffres par script (R:R minimum 1,5, stop
du bon côté) → fiche de trade → taille de position si tu donnes ton capital.

**Mode modules** : les 11 outils du pack
[day-trader-skill](https://github.com/Jakeschincariol/day-trader-skill) dans
une seule skill :

| module | rôle |
| --- | --- |
| 🔎 scanner | scanne les actions US : cassures, drapeaux, survente, range d'ouverture |
| 📰 news | news Yahoo + dépôts 8-K de la SEC, seulement les nouvelles |
| 📊 analyst | résultats trimestriels SEC EDGAR : CA, marges, BPA |
| ⏱️ entry | signale la bougie qui clôture au-dessus du range d'ouverture |
| 🚪 exit | stop et objectif avant d'entrer |
| 🎲 timemachine | 10 000 séances simulées + historique du setup |
| 💰 budget | taille de position dans tes limites |
| 🛡️ risk | PASS / BLOCK sur toutes tes règles de risque |
| 🏦 broker | ticket d'ordre Alpaca, paper par défaut, jamais sans ton oui |
| 🔔 alerts | alertes de prix, stop, objectif, cloche d'ouverture |
| 🏛️ pelosi | trades déclarés des membres du Congrès |

**Mode journal** : chaque signal et son résultat dans un journal, puis les
stats (taux de réussite, R moyen, profit factor, pire série), au global ou par
confiance, setup, actif. Fait pour les backtests FX Replay sans biais
([protocole](skills/snap-and-trade/references/backtest.md)).

### Ce que chaque mode couvre

| | actions / ETF US | crypto, forex, indices, futures | long | short |
| --- | --- | --- | --- | --- |
| capture + journal | ✅ | ✅ | ✅ | ✅ |
| news, analyst, scanner, pelosi | ✅ | ❌ | — | — |
| entry, exit, timemachine, budget | ✅ | ❌ | ✅ | ❌ |
| risk, broker (Alpaca), alerts | ✅ | ❌ | ✅ | sortie seulement |

## 💬 Utilisation

- Colle une capture : « long ou short ? », « donne-moi SL et TP »,
  « analyse, j'ai 2 000 $ et je risque 1 % ».
- Appelle un module : « scanne le marché », « des news sur TSLA ? »,
  « résultats d'Apple », « qu'achète Pelosi ? ».
- Journal : « note ce trade », « TP1 touché sur le #4 », « mes stats par
  confiance ».

## 📈 Résultats

Backtest en cours sur FX Replay, protocole
[ici](skills/snap-and-trade/references/backtest.md). Les chiffres seront
publiés ici tels quels, pertes comprises, une fois 30 trades clôturés.

## 🧪 Tests

```bash
python -m unittest discover -s tests
```

324 tests, lancés à chaque push sur Linux, Windows et macOS.

## ⚠️ Avertissement

Outil d'analyse technique et d'apprentissage, **pas un conseil en
investissement**. Une capture montre le passé ; le plan est une lecture, pas
une prédiction. La plupart des traders particuliers perdent de l'argent,
surtout avec levier. Teste en démo / paper trading d'abord.

## Licence

MIT. Les modules day-trader sont © 2026 Jake Schincariol (MIT), voir
[LICENSE](LICENSE). Historique des versions : [CHANGELOG](CHANGELOG.md).
