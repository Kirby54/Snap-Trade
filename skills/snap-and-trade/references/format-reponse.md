# Format de réponse (mode capture)

Deux parties, dans cet ordre : **① l'analyse, étape par étape**, puis
**② la fiche de trade**. Les couleurs passent par les pastilles emoji, qui
s'affichent partout (Claude Desktop, claude.ai, mobile, GitHub) :

| pastille | sens |
| --- | --- |
| 🟢 | entrée, LONG, élément présent / favorable |
| 🔴 | SHORT, stop loss, élément défavorable |
| 🎯 | objectifs (TP) |
| ⛔ | invalidation |
| ⚪ | PAS DE TRADE, élément absent / non visible |
| 🟡 | point d'attention |

Règles de mise en page :
- Les prix toujours en **gras**, espace pour les milliers (28 295), virgule
  décimale en français.
- Le titre de la fiche commence par la pastille du sens : 🟢 LONG, 🔴 SHORT,
  ⚪ PAS DE TRADE.
- Jauge de confiance sur 5 : `🟢🟢🟢⚪⚪` (autant de 🟢 que de points).
- Les tableaux, pas de bloc de code pour la fiche (sinon les emoji et le gras
  ne s'affichent pas).
- Analyse courte : une à trois lignes par étape.

---

## Modèle

### 🔍 Analyse

**1 · Lecture** — NDX (Nasdaq-100) · 5 min · dernier prix **28 286,72** ·
séance probablement fermée (22:14 UTC).

**2 · Structure** — 🔴 baissière depuis 16 h : sommets décroissants
≈ 28 545 → 28 470 → 28 420 → 28 360.

**3 · Niveaux**

| niveau | rôle |
| --- | --- |
| **28 360** | dernier sommet descendant |
| **28 290 – 28 310** | résistance de la dernière heure |
| **28 215** | bas du range actuel |
| **28 150** | congestion du début de séance |
| **28 100** | bas du rebond de 15 h 30 |

**4 · Setup** — pullback dans la tendance baissière (vente sur rejet de la
résistance).

**5 · Confluence** — 2/5

| | élément | lu sur la capture |
| --- | --- | --- |
| 🟢 | tendance | sommets décroissants |
| 🟢 | niveau | entrée sur la résistance 28 290–28 310 |
| ⚪ | bougie | pas encore de rejet clôturé |
| ⚪ | momentum | aucun indicateur affiché |
| ⚪ | volume | volume non affiché |

**6 · Vérification** — `plan.py` : ✅ VALIDE · risque 80 pts (0,28 %) ·
TP1 1,81R · TP2 2,44R. ❌ Variante refusée : vente sous 28 205 → 0,91R.

**7 · Contexte** — 🟡 indice, pas d'action US : news et résultats non
vérifiés.

---

### 🔴 SHORT · NDX · 5 min

**Confiance** 🟢🟢⚪⚪⚪ faible (2/5) · **R:R** 1,8 / 2,4

| | niveau | détail |
| --- | --- | --- |
| 🟢 **Entrée** | **28 295** | limite, après une bougie de rejet clôturée sur 28 290–28 310 |
| 🔴 **Stop loss** | **28 375** | au-dessus du sommet ≈ 28 360 + marge · risque 80 pts |
| 🎯 **TP1** | **28 150** | 1,8R · congestion de début de séance |
| 🎯 **TP2** | **28 100** | 2,4R · bas du rebond |
| ⛔ **Invalidation** | **28 375** | clôture 5 min au-dessus |

**⚙️ Gestion** — à TP1, sortir la moitié et remonter le stop à l'entrée.

**📏 Taille** — 1 MNQ = 160 $ de risque au stop · 1 NQ = 1 600 $. Donne ton
capital pour un calcul exact.

**🟡 À vérifier** — gap à l'ouverture : au-delà de 28 375 ou sous 28 150, le
plan est caduc, renvoyer une capture.

**➡️ Suite** — noter ce signal dans le journal · `alerts` sur 28 295 /
28 375 · `budget` pour la taille.

<sub>Lecture technique, pas un conseil financier. Teste en démo d'abord.</sub>

---

## Variante PAS DE TRADE

### ⚪ PAS DE TRADE · ETHUSD · 15 min

**Pourquoi** — prix au milieu du range 3 120–3 210, aucun stop logique.

| | déclencheur | entrée | stop | objectif |
| --- | --- | --- | --- | --- |
| 🟢 | clôture 15 min > **3 210** | **3 215** | **3 185** | **3 270** |
| 🔴 | clôture 15 min < **3 120** | **3 115** | **3 148** | **3 060** |
