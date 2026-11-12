# Dimensionnement et limites

`plan.py` ne passe aucun ordre. Prix strictement positifs uniquement : pas de
contrats inverses, d'options, ni de produits à payoff non linéaire. Un calcul
valide ne démontre ni la qualité du setup ni la faisabilité chez le courtier.

## Unités

| Paramètre | Unité / règle |
| --- | --- |
| `--entry`, `--sl`, `--tp` | Prix du même instrument, dans sa devise de cotation |
| `--point-value` | Valeur d'un point par unité/lot/contrat dans la devise de cotation |
| `--fx-rate` | Unité de devise du compte pour une unité de devise de cotation, défaut 1 |
| `--account`, `--risk-amount`, `--max-notional` | Devise du compte |
| `--cost-per-unit` | Coût aller-retour estimé par unité/lot/contrat dans la devise du compte, défaut 0 |
| `--qty-step`, `--min-qty` | Pas et minimum du courtier ; sans pas, quantité théorique |
| `--min-stop-pct` | Filtre technique en % du prix, défaut 0,05 ; ne modélise pas le spread réel |

Confirmer les spécifications du symbole exact et le taux de conversion.
Les exemples forex à 100000 supposent une cotation dont une unité de prix
vaut 100000 unités de la devise de cotation par lot. Ne pas confondre point,
pip, tick, valeur du tick et devise du compte.

## Calcul

Perte par unité = distance entrée-stop × valeur du point × conversion + coûts.
Gain net par unité = distance entrée-TP × valeur du point × conversion − coûts.
Le ratio contrôlé est gain net / perte par unité ; le ratio brut reste dans
`targets[].rr`, le net dans `targets[].net_rr`.

La quantité est le minimum des limites de budget de risque et de notionnel,
puis arrondie **vers le bas** au pas demandé. Si elle ne permet pas une unité
minimale, le plan est refusé. `size.max_loss` conserve son nom pour compatibilité,
mais représente une **perte estimée** avec ces hypothèses, jamais une garantie.
Le notionnel d'un future n'est pas sa marge exigée par le courtier.

```bash
# Contrats entiers, budget de risque de 100 dans la devise du compte
python3 skills/snap-and-trade/scripts/plan.py --side long --entry 5000 --sl 4990 --tp 5025 --risk-amount 100 --point-value 5 --qty-step 1 --min-qty 1 --cost-per-unit 2

# Action cotée USD, compte EUR, conversion illustrative et non cours actuel
python3 skills/snap-and-trade/scripts/plan.py --side long --entry 100 --sl 98 --tp 105 --account 2000 --fx-rate 0.9 --qty-step 1 --cost-per-unit 0.1
```

Les frais fixes par ordre, le spread variable, les gaps et le glissement ne
sont pas prévus automatiquement. Estimer prudemment les coûts par unité ou
recalculer après dimensionnement. Aucun appel à un courtier ou fournisseur
FX n'est effectué. Au-delà de 2 % du capital, `--allow-high-risk` est exigé ;
ce drapeau doit correspondre à une demande explicite, jamais à une initiative
de l'assistant. Le risque en montant ne peut pas dépasser le capital fourni.
