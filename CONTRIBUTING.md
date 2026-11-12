# Contribuer

Python 3.10+ ; bibliothèque standard uniquement pour les scripts et tests.
Depuis la racine du dépôt :

```bash
python tools/validate_repo.py
python -m unittest discover -s tests
```

Les tests utilisent des fixtures ; aucun compte courtier ni clé API n'est
nécessaire. Les tests ne prouvent pas la performance des signaux de trading.

Pour une correction : ajouter une reproduction qui échoue avant la correction,
puis vérifier la suite complète. Garder les codes de sortie et les clés JSON
existantes ; documenter tout changement de comportement dans CHANGELOG.md.
Vérifier les trois systèmes et deux versions Python de la CI avant fusion.

Pour une nouvelle règle de signal : documenter les conditions observables,
l'abstention et le déclencheur clôturé ; évaluer hors échantillon suivant le
[protocole](skills/snap-and-trade/references/backtest.md). Ne pas ajouter de
taux de réussite sans données reproductibles. Ne jamais committer de clés,
de portefeuille personnel ou de journaux de trading réels.

Les modules dérivés de day-trader-skill conservent leur attribution MIT dans
LICENSE. Les changements au mode broker doivent préserver le PASS sur l'ordre
exact, le consentement explicite et la confirmation de l'outil de courtage.
