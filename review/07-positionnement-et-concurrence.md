# 07 - Positionnement, intérêt et concurrence

## Le problème adressé

Les docstrings dérivent du code : paramètre renommé mais pas sa documentation, exception ajoutée non documentée, type changé. Deux familles d'outils existent :

1. **Forme** : le docstring respecte-t-il une convention (PEP 257, Google, NumPy) ? Exemple : ruff `D`.
2. **Cohérence** : le docstring décrit-il la signature et le corps réels ? Exemples : pydoclint, docsig, ruff `DOC`.

docstring-linter couvre les deux, avec un parti pris : un **style maison strict et entièrement paramétrable** via des politiques tri-états.

## Paysage (versions PyPI vérifiées le 2026-09-26 via `pip index versions`)

| Outil | Version | Famille | Styles | Statut |
|---|---|---|---|---|
| ruff, règles `D` | 0.16.8 | Forme | PEP 257, Google, NumPy | 48 règles, corrections automatiques sur une partie [Vérifié] |
| ruff, règles `DOC` | 0.16.8 | Cohérence | Google, NumPy [Non vérifié] | 7 règles, **toutes en preview** (DOC102, 201, 202, 402, 403, 501, 502) [Vérifié] |
| pydoclint | 0.9.1 | Cohérence | Google, NumPy, Sphinx (défaut `numpy`) | Actif ; baseline, noqa, nombreuses options [Vérifié via `--help`] |
| docsig | 0.96.0 | Cohérence (paramètres) | Google, NumPy, Sphinx [Non vérifié] | Options dunders, protected, overridden, nested, property [Vérifié via `--help`] |
| pylint `docparams` | 4.0.8 | Cohérence | Google, NumPy, Sphinx [Non vérifié] | Extension livrée avec pylint [Vérifié : `pylint/extensions/docparams.py`] |
| pydocstyle | 6.3.0 | Forme | PEP 257, Google, NumPy | Déprécié au profit de ruff, dépôt archivé [Source web, date non revérifiée] |
| darglint | 1.8.1 | Cohérence | Google, NumPy, Sphinx | Archivé en décembre 2022, fork `darglint2` [Source web] |
| interrogate | 1.7.0 | Couverture | - | Mesure le taux de docstrings, ne valide pas le contenu |
| numpydoc (validation) | 1.11.0 | Forme + cohérence | NumPy | Spécifique NumPy |
| docstring-linter | non publié | Forme + cohérence | Google | Ce projet |

## Comparaison mesurée sur les mêmes entrées [Vérifié]

### Sur les cas limites de 01

| Cas | docstring-linter | pydoclint 0.9.1 (`--style=google`) |
|---|---|---|
| `limit (int, optional)` pour `int \| None` | Erreur (always-on) | Erreur DOC105 |
| Description d'argument sur 2 lignes | Erreur `indentation` | Rien |
| `Returns:` sans type | Erreur always-on | Erreur DOC203 |
| Générateur imbriqué | 2 erreurs | Rien |
| `raise err` | 2 erreurs | Rien |
| `raise errors.ValidationError` documenté `ValidationError` | Erreur | Erreur DOC503 (compare le nom pointé) |
| Exception propagée documentée | Erreur always-on | Erreur DOC502 (désactivable : `--skip-checking-raises`) |
| Forward ref `"Node"` | 2 erreurs | Rien |
| `Does the thing.` | `Doe` suggéré | Hors périmètre |
| `**kwargs` sous `Keyword Args:` | Erreur | Erreur DOC101/DOC103 |
| Attribut privé `_cache` | Erreur | Hors défaut (option dédiée) |
| Docstring sur `__init__` | Accepté (convention du projet) | DOC301 (préfère la docstring de classe) |

Lecture : pydoclint a moins de faux positifs sur l'extraction AST (portées imbriquées, re-raise, forward refs), mais partage certains défauts de comparaison textuelle. Aucun outil n'est "correct par défaut" sur le Google style réel.

### Sur `rich` 15.0.0 (100 fichiers)

| Outil | Temps | Signalements |
|---|---|---|
| docstring-linter (défauts) | 0,41 s | 2 410 |
| pydoclint `--style=google` | 0,99 s | 387 |
| docsig (défauts) | 2,23 s | 434 lignes de sortie |
| ruff `D,DOC --preview` | 0,04 s | non comparé (périmètre différent) |

Les volumes ne sont pas comparables un à un : docstring-linter vérifie aussi la présence (`docstring_exists`), la mise en page et le style maison.

Suivi, révision `0f8fdae` [Vérifié] : 1 990 signalements avec les défauts, 758 avec `convention = "google"`. Les faux positifs AST et de types listés dans 01 sont corrigés ; le README contient désormais un tableau comparatif (DOC-04).

## Forces distinctives de docstring-linter

1. **Politiques tri-états homogènes** : 15 politiques `required` / `forbidden` / `optional` couvrant sections, types, descriptions, `Returns: None`, position et ponctuation du résumé. On peut *interdire* une construction (types dans les docstrings, `Returns: None`), pas seulement l'exiger. pydoclint a des booléens sur certains axes, avec une sémantique moins uniforme [Vérifié via `--help`, appréciation].
2. **Mise en page paramétrable** : nombre de lignes vides avant les sections et avant `"""`, forme exacte `name (type): description`, ordre des sections. ruff `D` couvre une partie, sans ce niveau de réglage [Déduit].
3. **Overrides par chemin** avec résolution explicite "le dernier gagne".
4. **Configuration stricte** : toute clé ou valeur inconnue est une erreur.
5. **Zéro dépendance**, code petit et lisible, facile à auditer et à forker.
6. **Sortie `traceback`** cliquable.

## Faiblesses face au marché

| Faiblesse | Impact | Référence |
|---|---|---|
| Non publié sur PyPI | Bloquant | OPS-05 |
| Python 3.14 uniquement | Bloquant pour la majorité des projets | OPS-03 |
| Pas de noqa, pas de baseline | Bloquant sur une base existante | UX-01, UX-03 |
| Faux positifs AST et types | Perte de confiance immédiate | 01 |
| Google uniquement | Exclut les projets NumPy / Sphinx | ARCH-04 |
| 10x plus lent que ruff | Faible en pratique | 03 |
| Pas d'intégration éditeur (LSP) | Moyen | TODO.md |

## Intérêt du projet

**Pour son auteur et son équipe** : réel. Il encode un style maison précis, vérifié en CI, que ni ruff ni pydoclint ne peuvent exprimer entièrement.

**Pour un public plus large** : conditionnel. Le marché converge vers ruff pour la forme ; pydoclint est la référence pour la cohérence, et ruff `DOC` pourrait l'absorber quand il sortira de preview (7 règles en preview à ce jour [Vérifié]). Un nouvel outil doit apporter une raison claire de l'ajouter à côté de ruff.

Niche crédible : **"le linter de docstrings Google strict, configurable et auto-correcteur"**, utilisé *en complément* de ruff (`D` désactivé ou limité) et à la place de pydoclint pour les équipes qui veulent imposer une forme exacte.

## Stratégie : trois options

### Option A - Outil de niche assumé (recommandée)

- Google uniquement, dit clairement.
- Priorité à la justesse (01), puis noqa + baseline, puis **`--fix`** sur la mise en page et la synchronisation des types depuis la signature. L'autofix est le différenciateur le plus fort : ni pydoclint ni ruff `DOC` ne réécrivent le contenu Args/Returns [Non vérifié pour pydoclint].
- Preset `convention = "google"` permissif et `convention = "strict"` (état actuel).
- Documenter la cohabitation avec ruff : quelles règles `D` désactiver pour éviter les doublons.

Exemple de guide de cohabitation à publier :

```toml
[tool.ruff.lint]
select = ["D"]
ignore = [
    "D417",  # undocumented params: covered by args_section
    "D401",  # imperative mood: covered by imperative_mood
    "D413",  # blank line after last section: covered by blank_lines
]

[tool.ruff.lint.pydocstyle]
convention = "google"
```

Les correspondances exactes entre règles `D` et règles de ce projet sont à établir règle par règle [Non vérifié].

### Option B - Généraliste multi-style

Ajouter NumPy et Sphinx pour concurrencer pydoclint frontalement. Effort élevé (modèle ligne à ligne indispensable, ARCH-03), bénéfice incertain face à un acteur établi et à ruff `DOC`.

### Option C - Contribuer en amont

Porter les idées différenciantes (politiques `forbidden`, normalisation des types, mise en page) dans pydoclint ou ruff. Impact plus large, maintenance partagée, mais perte de maîtrise du style maison. À envisager si l'objectif est l'impact plutôt que l'outil.

## Analyse SWOT

| | Positif | Négatif |
|---|---|---|
| **Interne** | Code propre et typé, zéro dépendance, politiques tri-états, config stricte, overrides, tests nombreux | Faux positifs, pas de noqa/baseline, Python 3.14 seul, paquet `linter`, non publié, Google seul |
| **Externe** | ruff `DOC` encore en preview, pydocstyle et darglint abandonnés, demande d'autofix non couverte | ruff domine et peut étendre `DOC`, pydoclint mature et actif, faible visibilité d'un nouvel outil |

## Sources web

- [PyCQA/pydocstyle - README (dépréciation)](https://github.com/PyCQA/pydocstyle/blob/master/README.rst)
- [PyCQA/pydocstyle](https://github.com/PyCQA/pydocstyle)
- [terrencepreilly/darglint](https://github.com/terrencepreilly/darglint/tree/master/darglint)
- [akaihola/darglint2](https://github.com/akaihola/darglint2)
