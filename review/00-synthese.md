# Revue tierce de docstring-linter - Synthèse

Date : 2026-09-26. Révision analysée : `0957240` (branche `develop`).

## Objet et méthode

Revue exhaustive du projet : architecture, code, justesse fonctionnelle des règles, performances, usage (CLI, configuration, intégrations), documentation, packaging/CI, positionnement face à la concurrence.

Ce qui a été fait concrètement :

- Lecture intégrale de `src/linter/` (2 470 lignes), des docs, de la CI, des scripts et de la configuration outillage.
- Exécution de la suite de tests sous Python 3.14.7 : **372 tests passent en 1,45 s, couverture branches 94,39 %**.
- Exécution de ruff, pylint et pyright sur le projet : 0 erreur (pylint 10/10).
- Fichiers de cas limites écrits pour la revue (reproduits dans les rapports) et exécutés.
- Benchmarks sur la stdlib CPython 3.14 (1 059 fichiers) et sur le paquet `rich` 15.0.0 (100 fichiers, 38 515 lignes).
- Profilage cProfile d'une exécution complète.
- Comparaison exécutée avec `pydoclint` 0.9.1, `docsig` 0.96.0 et `ruff` 0.16.8 (règles `D` et `DOC`).

## Convention de preuve

Chaque constat porte l'un des marqueurs suivants :

| Marqueur | Signification |
|---|---|
| **[Vérifié]** | Reproduit par exécution ou lu dans le code, preuve citée (commande, sortie, `fichier:ligne`). |
| **[Déduit]** | Conclusion tirée de la lecture du code ou d'une documentation connue, non exécutée ici. |
| **[Non vérifié]** | Connaissance externe (écosystème, conventions) non revérifiée pendant la revue. |

Gravité : **Critique** (résultat faux ou CI verte à tort), **Haute** (bloque l'adoption), **Moyenne**, **Basse**.

## Rapports

| Fichier | Contenu |
|---|---|
| [01-bugs-et-faux-positifs.md](01-bugs-et-faux-positifs.md) | Défauts fonctionnels reproduits, faux positifs mesurés, correctifs proposés |
| [02-architecture-et-code.md](02-architecture-et-code.md) | Structure, modèle de règles, parsing, configuration, tests |
| [03-performance.md](03-performance.md) | Mesures, profil, goulots, pistes chiffrées |
| [04-usage-cli-configuration.md](04-usage-cli-configuration.md) | Expérience utilisateur, défauts, CLI, sorties, pre-commit, GitHub Action |
| [05-documentation.md](05-documentation.md) | README, docs, fichiers annexes, incohérences |
| [06-packaging-ci-outillage.md](06-packaging-ci-outillage.md) | Distribution, versions Python, workflows, chaîne d'approvisionnement |
| [07-positionnement-et-concurrence.md](07-positionnement-et-concurrence.md) | Intérêt du projet, comparatif mesuré, stratégie |

## Suivi des corrections

État à la révision `0f8fdae` de la branche `claude/project-comprehensive-review-qvro8c`. Le verdict, le tableau de bord et les priorités ci-dessous décrivent la révision `0957240` analysée ; chaque point des rapports 01 à 06 porte maintenant une ligne **Statut**.

| Statut | Signification |
|---|---|
| Corrigé | Proposition appliquée, revérifiée sur le code actuel. |
| Partiel | Une partie appliquée ; le reste est détaillé sous le point. |
| Reporté | Reporté explicitement (lot 0, `# noqa`, gestion de version, baseline, PyPI, ligne des erreurs, autofix, CHANGELOG et CONTRIBUTING). |
| Écarté | Décision de ne pas appliquer. |
| Non traité | Pas encore discuté. |

| Rapport | Corrigé | Partiel | Reporté | Écarté | Non traité | Total |
|---|---|---|---|---|---|---|
| 01 - Bugs (BUG) | 23 | 0 | 0 | 0 | 0 | 23 |
| 02 - Architecture (ARCH) | 2 | 7 | 1 | 0 | 0 | 10 |
| 03 - Performance (PERF) | 3 | 1 | 0 | 2 | 0 | 6 |
| 04 - Usage (UX) | 2 | 6 | 4 | 1 | 0 | 13 |
| 05 - Documentation (DOC) | 5 | 2 | 1 | 1 | 1 | 10 |
| 06 - Packaging et CI (OPS) | 2 | 2 | 6 | 3 | 0 | 13 |
| **Total** | **37** | **18** | **12** | **7** | **1** | **75** |

Mesures sur la révision `0f8fdae` [Vérifié] :

- Tests : 590 (372 à la revue), couverture branches 96 % (94,39 %).
- `rich` 15.0.0 : 1 990 erreurs avec les défauts (`strict`), 758 avec `convention = "google"`, contre 2 410 à la revue. Les 2 erreurs de plus depuis `89c4a28` sont deux `raise` nus réels, dans `console.py` et `live.py`. Les 100 fichiers restent signalés, notamment parce que 95 modules n'ont pas de docstring.
- Les fichiers de reproduction de l'annexe du rapport 01 ne produisent plus que les erreurs attendues : avec `convention = "google"` et une ligne vide avant `"""`, il reste `hidden_in_if` (sans docstring) et `Child.run` (surcharge sans `@override`).

Principaux points ouverts : `# noqa` (UX-01, ARCH-06), lot 0 (OPS-01 à OPS-03, matrice de versions), baseline (UX-03), publication PyPI (OPS-05).

## Verdict global

Le code est propre, strictement typé, bien testé au niveau unitaire et sans dépendance. Le concept de **politiques tri-états** (`required` / `forbidden` / `optional`) appliqué uniformément et la **validation stricte de la configuration** sont de vrais points forts.

En revanche, l'outil n'est pas encore prêt pour un usage hors du dépôt lui-même :

1. **Échecs silencieux avec code de sortie 0** : style non supporté, fichier illisible, erreur de syntaxe, chemin inexistant, `--config` introuvable. En CI, ces cas passent au vert. [Vérifié]
2. **Faux positifs massifs sur du Google style réel** : sur `rich`, 2 410 erreurs dans 100 % des fichiers ; 318 des 520 "type mismatch" ne diffèrent que par `, optional`, 84 par des guillemets de forward reference. [Vérifié]
3. **Aucune échappatoire** : pas de suppression inline (`# noqa`), pas de baseline, et 11 règles "always-on" non désactivables. Un seul faux positif est bloquant. [Vérifié]
4. **Extraction AST incomplète** : fonctions sous `if`/`try` ignorées, générateur imbriqué qui contamine la fonction parente, `raise err` interprété comme un type d'exception, exceptions pointées (`mod.Error`) invisibles. [Vérifié]
5. **Distribution** : paquet importable nommé `linter` (collision probable), Python `>=3.14,<3.15` uniquement, pas de `[build-system]`, absent de PyPI. [Vérifié]

## Tableau de bord

| Axe | Note /5 | Commentaire court |
|---|---|---|
| Qualité du code | 4 | Typage strict, lisible, docstrings cohérentes ; dispatcher de règles monolithique. |
| Justesse des règles | 2 | Bonne logique de fond, mais extraction AST et comparaison de types trop naïves. |
| Tests | 3,5 | 94 % de couverture, mais entités construites à la main : la couche AST est peu couverte par des cas réels. |
| Performance | 4 | 0,41 s sur `rich` (2,4x plus rapide que pydoclint, 10x plus lent que ruff). Non bloquant. |
| Usage / DX | 2 | Config stricte appréciable ; pas de noqa, pas de baseline, défauts très opinionnés, couleurs forcées. |
| Documentation | 3 | Référence des règles détaillée ; README sans installation, exemple de sortie obsolète, fichiers annexes périmés. |
| Packaging / CI | 2,5 | CI riche ; nom de paquet, bornes Python, build legacy, flux beta cassé. |
| Positionnement | 2,5 | Niche réelle (style maison strict Google + mise en page), marché occupé par ruff et pydoclint. |

## Priorités recommandées

| Prio | ID | Action | Effort | Statut |
|---|---|---|---|---|
| P0 | BUG-01 à BUG-04 | Codes de sortie non nuls et messages sur stderr pour tout échec d'analyse ou de configuration | S | Corrigé |
| P0 | UX-01 | Suppression inline `# noqa: rule` (ligne `def`/`class`) | M | Reporté |
| P0 | BUG-12, BUG-13 | Normaliser les types avant comparaison (`, optional`, guillemets, `Optional[X]`) | M | Corrigé |
| P0 | BUG-08 à BUG-10, BUG-15, BUG-16 | Corriger l'extraction AST (portées imbriquées, `raise` de variable, noms pointés, blocs `if`/`try`, premier paramètre) | M | Corrigé |
| P0 | BUG-14 | Corriger ou supprimer la règle `indentation` | S | Corrigé |
| P0 | OPS-01 à OPS-03 | Renommer le paquet importable, déclarer le build backend, élargir `requires-python` | S | Reporté |
| P1 | BUG-05 à BUG-07 | `select = ["ALL"]` en override, typage des valeurs de config, glob d'exclusion | S | Corrigé |
| P1 | UX-02, UX-04 | Preset "google" moins strict, options de portée (privé, dunder, overload, property) | M | Corrigé, Partiel |
| P1 | BUG-18, BUG-19 | Sections Napoleon à deux mots, `Returns:` sans type | M | Corrigé |
| P1 | DOC-01 à DOC-03 | README (installation, positionnement), docs obsolètes | S | Corrigé, Corrigé, Partiel |
| P1 | OPS-05, OPS-06 | Publication PyPI, flux de release beta | S | Reporté, Écarté |
| P2 | UX-03, UX-08 | Baseline, autofix des règles de mise en page | L | Reporté |
| P2 | ARCH-02, ARCH-03, PERF-01 | Registre de règles déclaratif, modèle ligne à ligne du docstring, passe AST unique | L | Corrigé, Partiel, Corrigé |

Effort : S = moins d'une journée, M = 1 à 3 jours, L = plus.

## Points à discuter en priorité

1. **Philosophie des règles always-on** : faut-il garder 11 règles non désactivables sans suppression inline ? (voir ARCH-06, UX-01)
2. **Cible** : style maison strict (état actuel) ou Google "officiel" par défaut ? Cela conditionne les valeurs par défaut (UX-02) et le positionnement (07).
3. **Versions Python** : 3.14 seul est-il un choix assumé ? (OPS-03)
4. **Contribuer à pydoclint plutôt que concurrencer ?** Option à évaluer honnêtement (07, section Stratégie).
