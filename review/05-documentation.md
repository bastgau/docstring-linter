# 05 - Documentation

## Inventaire [Vérifié]

| Fichier | Lignes | Public | Langue | État |
|---|---|---|---|---|
| `README.md` | 186 | Utilisateur | EN | Incomplet, exemple de sortie obsolète |
| `docs/configuration.md` | 137 | Utilisateur | EN | Complet, précis |
| `docs/configurable-rules.md` | 267 | Utilisateur | EN | Bon, exemples Bad/Good |
| `docs/always-on-rules.md` | 503 | Utilisateur | EN | Bon |
| `docs/style-policies.md` | 588 | Utilisateur | EN | Bon, contient une section hors sujet |
| `RELEASE.md` | 44 | Mainteneur | EN | Décrit un flux beta qui ne fonctionne pas (OPS-06) |
| `TESTS.md` | 680 | Mainteneur | EN/FR | Périmé (369 tests annoncés, 372 réels) |
| `TODO.md` | 53 | Mainteneur | FR | Partiellement périmé |
| `scripts/README.md` | 68 | Mainteneur | EN | Correct |
| `CLAUDE.md` | 38 | Agent | EN | Correct |

Points forts : la référence des règles est riche, avec des exemples "Bad / Good" systématiques et l'explication des interactions politique / règle de contenu. `docs/configuration.md` est précis sur l'ordre de découverte, les overrides et la configuration stricte.

## Constats

| ID | Gravité | Sujet | Statut |
|---|---|---|---|
| DOC-01 | Haute | README : pas d'installation, exemple de sortie faux | Corrigé |
| DOC-02 | Moyenne | Support NumPy / Sphinx / PEP 257 annoncé dans le code | Corrigé |
| DOC-03 | Moyenne | Fichiers annexes périmés, langues mélangées | Partiel |
| DOC-04 | Haute | Aucun positionnement ni comparaison | Corrigé |
| DOC-05 | Moyenne | Pas de CHANGELOG, CONTRIBUTING, guide "ajouter une règle" | Non traité |
| DOC-06 | Basse | Liens absolus `/docs/...` | Non traité |
| DOC-07 | Moyenne | Limitations connues non documentées | Corrigé |
| DOC-08 | Moyenne | Sémantique de `exclude` fausse dans la doc | Partiel |
| DOC-09 | Basse | Descriptions internes incohérentes | Corrigé |
| DOC-10 | Basse | Documentation non générée depuis les registres | Écarté |

### DOC-01 - README [Vérifié] - Haute

**Statut : Corrigé.** `a1fb08e`. README réécrit : installation, prérequis, sortie réelle, codes de sortie, conventions.

- **Pas de section Installation.** Le paquet n'est pas sur PyPI (`pip index versions docstring-linter` : aucun résultat), et rien n'indique comment l'installer (`pip install git+https://...`, `uvx --from git+...`).
- **Pas de prérequis Python.** Python 3.14 exclusivement : c'est la première chose qu'un utilisateur doit savoir.
- **Exemple de sortie obsolète.** Le README montre 2 erreurs sur `example/docstring_format_reference.py` ligne 84 (`divide`). En réalité :

  ```console
  $ docstring-linter example/ --format text
  Config: /home/user/docstring-linter/pyproject.toml
  2 files checked, 0 errors.
  ```

  Recommandation : un exemple de sortie généré par un script (ou vérifié par un test) à partir d'un fichier d'exemple dédié et volontairement fautif.
- La section "What is checked?" liste des catégories sans montrer l'apport principal : la cohérence docstring / signature et les politiques tri-états.
- Pas de badge de version, de CI ni de couverture (Codecov est configuré).

Structure suggérée :

```markdown
# docstring-linter
One-line pitch + badges

## Why            (3 bullets: what it checks that others don't)
## Install        (pip / uvx / pre-commit / GitHub Action, Python requirement)
## Quick start    (one command, one real output)
## Configuration  (minimal example + link)
## Suppressing    (noqa, baseline, once implemented)
## Rules          (links)
## Comparison     (short table, link to details)
## Exit codes
```

### DOC-02 - Styles annoncés [Vérifié] - Moyenne

**Statut : Corrigé.** `b2fd640`. Les docstrings de `__init__.py` et `docstring_parser.py` ne mentionnent plus que Google.

`src/linter/__init__.py:3-4` : "with support for Google, NumPy, Sphinx, and PEP 257 styles". `docstring_parser.py:3-5` : "Extensible via abstract base class for multiple styles (Google, NumPy, Sphinx, PEP 257)". Seul Google existe (BUG-01, ARCH-04). À aligner sur le README, qui dit correctement "Google-style".

### DOC-03 - Fichiers annexes périmés [Vérifié] - Moyenne

**Statut : Partiel.** `TESTS.md` tenu à jour à chaque commit (582 tests), toujours maintenu à la main. Restent : `TODO.md` (items `RULES.md` et version périmés, rédigé en français), commentaires de section en français dans `.pre-commit-config.yaml`, `.vulture` périmé.

- `TESTS.md` : "369 tests" contre 372 exécutés. 680 lignes maintenues à la main, redondantes avec les docstrings des tests (constat déjà noté dans `TODO.md`). Recommandation : le générer (`pytest --collect-only` + docstrings) ou le supprimer.
- `TODO.md` :
  - item "Décider du sort de `RULES.md`" alors que `RULES.md` n'existe plus (remplacé par `docs/`) ;
  - item "Aligner la version" qui cite des tags jusqu'à `v0.5.0` et un README en `v0.1.0`, alors que `v0.9.0` existe et que le README l'utilise (tags vérifiés via l'API GitHub) ;
  - rédigé en français, comme les commentaires de `pyproject.toml` et `.pre-commit-config.yaml`, alors que le reste est en anglais.
- `.vulture` : références de lignes périmées (ARCH-09).

### DOC-04 - Positionnement absent [Vérifié] - Haute

**Statut : Corrigé.** `a1fb08e`. Section "How it compares" du README.

Aucune mention de ruff, pydoclint, pydocstyle, darglint ou docsig. Un visiteur ne sait pas pourquoi choisir cet outil. Voir 07 pour le contenu d'un tableau comparatif honnête (y compris ce que l'outil ne fait pas).

### DOC-05 - Contribution et historique [Vérifié] - Moyenne

**Statut : Non traité.**

- Pas de `CHANGELOG.md` : les notes de release sont la liste brute des sujets de commits (`publish-release.yml`). Les changements de comportement (nouvelles politiques, règles devenues always-on) ne sont pas signalés comme tels.
- Pas de `CONTRIBUTING.md` : ajouter une règle implique 4 à 6 fichiers (ARCH-02) et des conventions strictes (commitlint : sujet en minuscules, 15 caractères minimum, corps interdit).
- Pas de `SECURITY.md`.

### DOC-06 - Liens absolus [Déduit] - Basse

**Statut : Non traité.** Le README utilise toujours `/docs/...`.

Le README utilise `/docs/configuration.md`. Ces liens fonctionnent sur GitHub mais seront cassés dans la description PyPI, qui reprend le README. Utiliser des URL complètes `https://github.com/bastgau/docstring-linter/blob/main/docs/...` ou des liens relatifs réécrits au build.

### DOC-07 - Limitations non documentées [Vérifié] - Moyenne

**Statut : Corrigé.** `8e448bb`. Section "Known limitations" du README : 9 points, revérifiés sur le code (fonctions imbriquées, `raise` indirects, attributs hors `__init__`, alias de types, `@override`, ligne `def`, Google seul, pas de `# noqa` ni de baseline). Le `raise` nu dans un `except` typé et l'affectation multiple `self.a, self.b = ...` ont ensuite été corrigés (`1ce67fb`) et retirés de la liste.

Non mentionnées nulle part :

- fonctions et classes imbriquées dans des fonctions jamais analysées ;
- `def` sous `if` / `try` / `with` jamais analysés (BUG-15) ;
- seules les exceptions levées directement et nommées simplement sont vues (BUG-09, BUG-10, BUG-11) ;
- comparaison de types purement textuelle (BUG-12, BUG-13) ;
- erreurs toujours rapportées sur la ligne `def` (UX-05).

Tant que ces points ne sont pas corrigés, une section "Known limitations" évite des rapports de bug et fixe les attentes.

### DOC-08 - `exclude` [Vérifié] - Moyenne

**Statut : Partiel.** `b6ad01e`. Sémantique unifiée (BUG-07) et documentée dans `docs/style-policies.md` ("Exclusion Patterns"). La section n'a pas été déplacée dans `docs/configuration.md`.

`docs/configuration.md` et `--help` parlent de "Glob patterns". Les globs récursifs ne fonctionnent pas (BUG-07), et un motif littéral exclut un nom de répertoire à toute profondeur. La section "Default Exclusion Patterns" est placée dans `docs/style-policies.md:565-567`, alors qu'il ne s'agit pas d'une politique de style ; sa place est `docs/configuration.md`.

### DOC-09 - Descriptions internes [Vérifié] - Basse

**Statut : Corrigé.** Description de `section_order` (`acdcf43`), commentaire sur `--select` (`89c4a28`), input `format` d'`action.yml` (`319326e`).

- `RULES_REGISTRY["section_order"]` : "Args, Returns, Yields, Raises, Example(s), Note(s)" ; ordre réel : Attributes, Args, Returns, Yields, Raises, Example(s), Note(s), Todo. Cette chaîne est affichée par `--list-rules`.
- Commentaire `config.py:138` : mentionne `--select`, flag inexistant.
- `action.yml` : input `format` décrit "(text, json, github-annotations)", sans `traceback`.

### DOC-10 - Documentation non générée [Vérifié] - Basse

**Statut : Écarté.** Remplacé par le test de cohérence qui exige un titre dans `docs/` pour chaque règle et politique (`6bfff7a`, voir ARCH-02).

Registres (`RULES_REGISTRY`, `POLICIES_REGISTRY`, `OPTIONS_REGISTRY`) et pages `docs/` sont maintenus séparément. Proposition déjà esquissée dans `TODO.md` : générer le squelette (tableaux, valeurs par défaut) depuis le registre unique d'ARCH-02 / ARCH-05, garder les exemples à la main, et vérifier en CI que le fichier committé est à jour.

```bash
# scripts/check-docs.sh - fail when generated docs drift from the registry
uv run python -m linter.docs > /tmp/rules.md
diff -u docs/generated-rules.md /tmp/rules.md
```
