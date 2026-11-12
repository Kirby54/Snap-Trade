---
name: snap-and-trade
description: >-
  Snap & Trade, la skill de trading tout-en-un. (1) L'utilisateur envoie une
  capture d'écran de n'importe quel graphique (actions, crypto, forex,
  indices, matières premières, futures; toute unité de temps, toute
  plateforme : TradingView, MT4/MT5, Binance...) et reçoit l'analyse
  complète étape par étape puis une fiche de trade visuelle : LONG / SHORT /
  PAS DE TRADE, entrée, stop loss, TP1, TP2, R:R, invalidation, taille de
  position. (2) Elle contient aussi les 11 modules du pack day-trader :
  scanner (cassures, drapeaux, survente sur tout le marché US), news (Yahoo +
  8-K SEC), analyst (résultats trimestriels SEC EDGAR), entry (timing de
  cassure du range d'ouverture), exit (stop et objectif), timemachine
  (10 000 simulations + historique), budget (taille de position), risk
  (contrôle des limites PASS/BLOCK), broker (tickets d'ordre Alpaca, paper
  par défaut, jamais sans un oui), alerts (alertes de prix, cloche
  d'ouverture) et pelosi (trades déclarés du Congrès). À utiliser dès qu'une
  capture de chart est envoyée, ou quand l'utilisateur dit « analyse ce
  chart », « buy ou sell ? », « long ou short ? », « donne-moi SL et TP »,
  « je rentre où ? », « scanne le marché », « des news sur TSLA ? »,
  « résultats d'Apple », « combien d'actions ? », « check mon risque »,
  « passe l'ordre », « alerte-moi si », « qu'achète Pelosi », « what's the
  trade », « long or short », « scan the market », « any news on ».
argument-hint: "[capture du chart] | [module] [TICKER] [capital, risque %]"
---

# Snap & Trade

Une seule skill, deux façons de l'utiliser :

1. **Mode capture** (le principal) : une capture d'écran entre, l'analyse
   détaillée puis une fiche de trade sortent.
2. **Mode modules** : les 11 outils du pack day-trader (scanner, news,
   résultats, entrée, sortie, simulation, taille, risque, ordre, alertes,
   Congrès), chacun appelable seul ou enchaîné.

`${CLAUDE_SKILL_DIR}` est le dossier de cette skill. Tous les scripts et
fichiers d'exemple sont dans `${CLAUDE_SKILL_DIR}/scripts/`. Sous Windows,
`python` au lieu de `python3`. Les scripts n'utilisent que Python standard.

---

## Mode capture

### Avant d'analyser, lire

- `references/lecture-chart.md` : la checklist de lecture d'une capture.
- `references/setups.md` : les setups, et où vont entrée, stop et objectifs.
- `references/format-reponse.md` : **le format exact de la réponse** (à
  suivre à la lettre : analyse étape par étape, puis la fiche visuelle).

### Étapes

1. **Lire la capture** (`lecture-chart.md`) : actif, unité de temps, dernier
   prix, échelle, structure, niveaux, bougies clôturées, indicateurs et
   volume visibles. Ne jamais inventer un prix illisible. Estimé = « ≈ ».
   Noter aussi l'heure affichée : séance ouverte ou fermée ?
2. **Choisir le setup** (`setups.md`) et **compter les confluences** :

   | élément | 1 point si |
   | --- | --- |
   | tendance | le trade va dans le sens de la structure de l'UT affichée |
   | niveau | entrée sur support/résistance, cassure clôturée ou retest |
   | signal bougie | bougie de confirmation clôturée |
   | momentum | indicateur visible dans le même sens (ou divergence pour un retournement) |
   | volume | volume visible en hausse dans le sens du trade |

   0–1 : PAS DE TRADE · 2 : faible · 3 : moyenne · 4–5 : élevée.
   Contre la tendance de fond : plafonné à « faible ».
3. **Placer entrée, SL, TP** : stop derrière le niveau qui invalide l'idée +
   marge (10–25 % d'une bougie moyenne) ; TP1 au prochain niveau, TP2 au
   suivant ou à 3R. Pas de niveau logique pour le stop = pas de trade.
4. **Vérifier avec le script** (obligatoire, montrer le résultat) :

   ```bash
   python3 "${CLAUDE_SKILL_DIR}/scripts/plan.py" --side short --entry 28295 --sl 28375 --tp 28150 28100
   python3 "${CLAUDE_SKILL_DIR}/scripts/plan.py" --side long --entry 1.0850 --sl 1.0822 --tp 1.0910 --account 2000 --risk-pct 1 --point-value 100000
   ```

   `--point-value` : 1 actions/crypto, 100000 lot forex, 50 ES, 20 NQ, 2 MNQ,
   5 MES. Si le script REFUSE, le trade est refusé (proposer l'entrée limite
   qu'il suggère, ou PAS DE TRADE).
5. **Enrichir si possible** (action ou ETF US uniquement, données gratuites
   Yahoo/SEC, peuvent avoir du retard) :
   - `news.py check TICKER` : une news ou un 8-K récent qui explique le
     mouvement ? Le signaler.
   - `facts.py` (module analyst) : résultats publiés cette semaine ? Le
     signaler comme risque de gap.
   - Plan **long** sur action US : proposer le module `timemachine` pour
     rejouer le plan sur 60 jours de bougies 5 min.
   Pour crypto, forex, indices, futures : sauter cette étape et le dire.
6. **Risque** : R:R vers TP1 ≥ **1,5**. Capital donné : risque 1 % par
   défaut, avertir au-delà de 2 %. Jamais assouplir.
7. **Répondre** avec `references/format-reponse.md`, dans la langue de
   l'utilisateur.
8. **Proposer la suite** en une ligne : taille (module `budget`), contrôle
   (module `risk`), alertes sur SL/TP (module `alerts`), ordre en paper
   trading (module `broker`).

---

## Mode modules

Chaque module a sa doc complète dans `references/modules/<module>.md`.
**Lire cette doc avant de lancer le script du module.**

| module | script | à quoi il sert | déclencheurs |
| --- | --- | --- | --- |
| scanner | `scan.py` | scanne les actions US : cassure 20 jours, drapeau, reprise MM20, survente, cassure du range d'ouverture → `trader/watchlist.json` | « scanne le marché », « qu'est-ce qui casse », « watchlist » |
| news | `news.py` | news Yahoo + 8-K SEC par ticker, nouvelles seulement, taguées | « des news sur », « pourquoi ça bouge », « briefing » |
| analyst | `facts.py` | résultats SEC EDGAR : CA, marges, BPA, trimestre vs an dernier, TTM | « résultats de », « le 10-Q », « marges » |
| entry | `entry.py` | attend la bougie qui CLÔTURE au-dessus du range d'ouverture ou d'un niveau → `trader/entry.json` | « dis-moi quand entrer », « surveille TSLA » |
| exit | `exit.py` | stop (milieu du range, bas, %, ATR) et objectif (1R/2R) → `trader/plan.json` | « mon stop », « plan de sortie » |
| timemachine | `timemachine.py` | 10 000 séances simulées + chaque fois passée où le setup s'est déclenché | « simule ce trade », « backtest », « quelles chances » |
| budget | `size.py` | taille en actions entières dans 4 limites → `trader/orders.json` (bracket Alpaca) | « combien d'actions », « j'ai 5 000 $ » |
| risk | `check.py` | PASS / BLOCK sur toutes les limites (perte max, R:R, perte du jour, fenêtre horaire...) | « check mon ordre », « est-ce que ça passe » |
| broker | `ticket.py` | ticket d'ordre lisible + JSON Alpaca, paper par défaut, clôture avant la fin de séance | « passe l'ordre », « coupe ma position », « connecte Alpaca » |
| alerts | `alerts.py` | alertes stop/objectif/heure de sortie, %, cloche d'ouverture NYSE, prix → `trader/prices.json` | « alerte-moi si », « le marché est ouvert ? » |
| pelosi | `ptr.py` | trades déclarés des membres du Congrès (PTR de la Chambre) | « qu'achète Pelosi », « trades du Congrès » |

Fichiers d'exemple dans `scripts/` : `config.example.json` (règles de
budget et de risque, à copier en `trader/config.json`), `targets.example.json`,
`alerts.example.json`, `metrics.example.json`,
`claude_desktop_config.example.json` (serveur MCP Alpaca).

### La chaîne complète (journée de day trading, actions US, long)

`scanner` → `news` → `entry` → `exit` → `timemachine` → `budget` → `risk` →
`broker` → `alerts`. Les modules se passent le relais par les fichiers du
dossier `trader/` (dans le dossier de travail).

---

## Règles (tous modes)

- Toujours une réponse directe : LONG, SHORT ou PAS DE TRADE.
- Stop et objectifs fixés avant l'entrée ; un stop ne s'éloigne jamais.
- Une bougie non clôturée ne confirme rien.
- Aucun prix inventé ; aucun pourcentage de réussite tiré d'une capture
  (seul le module `timemachine` donne des fréquences, calculées sur données).
- Une capture montre le passé : le plan est une lecture, pas une prédiction.

## Ce que la skill ne fait jamais

- Passer un ordre sans les trois conditions du module `broker` : `risk` a
  donné PASS sur cet ordre exact aujourd'hui, l'utilisateur a écrit un oui
  explicite pour cet ordre, et il a cliqué « Autoriser une fois » sur la
  carte de Claude. Paper trading par défaut. Jamais d'outil d'ordre en
  « Toujours autoriser ».
- Demander ou afficher des clés API dans le chat (variables
  d'environnement ou config Claude Desktop uniquement).
- Promettre un gain, élargir un stop, pousser au levier.

## Avertissement

Outil d'analyse technique et d'apprentissage, pas un conseil en
investissement personnalisé. La plupart des traders particuliers perdent de
l'argent, surtout avec levier. Le stop est un plan, pas une garantie. À
tester d'abord en démo / paper trading.
