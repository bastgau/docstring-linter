# 06 - Packaging, CI et outillage

## Constats

| ID | Gravité | Sujet | Statut |
|---|---|---|---|
| OPS-01 | Critique | Paquet importable nommé `linter` | Reporté |
| OPS-02 | Haute | Pas de `[build-system]`, backend setuptools legacy, licence dépréciée | Reporté |
| OPS-03 | Haute | `requires-python = ">=3.14,<3.15"` | Reporté |
| OPS-04 | Basse | Version statique `0.1.0`, pas de `--version` | Reporté |
| OPS-05 | Haute | Absent de PyPI malgré le job de publication | Reporté |
| OPS-06 | Haute | Flux de release beta cassé, changelog beta incorrect | Écarté |
| OPS-07 | Moyenne | Chaîne d'approvisionnement de la CI | Corrigé |
| OPS-08 | Basse | Erreurs dans `.pre-commit-config.yaml` | Partiel |
| OPS-09 | Basse | `pyrightconfig.json` lié au devcontainer | Écarté |
| OPS-10 | Basse | Résidus de template dans `pyproject.toml` | Partiel |
| OPS-11 | Moyenne | CI mono-version, mono-OS | Reporté |
| OPS-12 | Basse | Le workflow `action.yml` teste `@main`, pas le commit courant | Corrigé |
| OPS-13 | Basse | commitlint interdit corps et trailers | Écarté |

### OPS-01 - Nom du paquet importable [Vérifié] - Critique

**Statut : Reporté.** Lot 0.

Le wheel installe un paquet top-level `linter` :

```text
linter/__init__.py
linter/ast_parser.py
linter/cli.py
...
docstring_linter-0.1.0.dist-info/top_level.txt
```

`linter` est un nom générique : toute autre distribution qui installe un module `linter` écrase ou est écrasée par celui-ci dans le même environnement, sans avertissement. C'est à corriger **avant** la première publication PyPI, car le renommage casse ensuite les imports des utilisateurs.

Correctif : `src/docstring_linter/`, `[project.scripts] docstring-linter = "docstring_linter.cli:main"`, et mise à jour de `pythonpath`, `pyrightconfig.json`, `ruff.src`, tests.

### OPS-02 - Build backend [Vérifié] - Haute

**Statut : Reporté.** Lot 0.

`pyproject.toml` n'a pas de `[build-system]`. `uv build` retombe sur setuptools et émet :

```text
SetuptoolsDeprecationWarning: `project.license` as a TOML table is deprecated
```

Correctif :

```toml
[build-system]
requires = ["uv_build>=0.11,<0.13"]
build-backend = "uv_build"

[project]
license = "MIT"
license-files = ["LICENSE"]
```

Les bornes de `uv_build` sont à ajuster à la version réellement utilisée [Non vérifié]. `hatchling` est une alternative équivalente.

### OPS-03 - Versions Python [Vérifié] - Haute

**Statut : Reporté.** Lot 0, avec la matrice de versions (OPS-11).

`requires-python = ">=3.14,<3.15"`.

- **Borne haute** : bloque l'installation sur 3.15 dès sa sortie, prévue en octobre 2026 selon le calendrier PEP 790 [Non vérifié]. Plafonner `requires-python` est déconseillé car pip et uv choisissent alors d'anciennes versions ou échouent [Non vérifié].
- **Borne basse** : exclut 3.10 à 3.13, encore majoritaires. Pour un linter, c'est l'environnement de l'utilisateur qui compte (pre-commit, CI, IDE).

Pourquoi 3.14 est nécessaire aujourd'hui [Vérifié par lecture] :

1. Annotations évaluées paresseusement (PEP 649) : `LinterConfig.for_path(...) -> LinterConfig` (`config.py:308`) référence la classe dans son propre corps, et les modules de règles importent `CodeEntity`, `LintError`, `ParsedDocstring` uniquement sous `TYPE_CHECKING` (`rules/args.py:9-10`, `rules/docstring.py:9-10`, `rules/attributes.py:9-10`, `reporter.py:13-15`).
2. `PurePath.full_match` (Python 3.13+) dans `config.py:231`.

Coût de l'élargissement à 3.10+ [Déduit] : `from __future__ import annotations` en tête de chaque module, et une fonction de glob maison (`fnmatch` segment par segment, ou `glob.translate` disponible depuis 3.13). Limite inhérente et acceptable : l'outil ne peut pas parser une syntaxe plus récente que son interpréteur.

Recommandation : `requires-python = ">=3.10"` (ou `>=3.12` pour limiter l'effort), sans borne haute, avec une matrice CI (OPS-11).

### OPS-04 - Version [Vérifié] - Basse

**Statut : Reporté.** Version et `--version` seront gérées plus tard par la CI/CD. `pyproject.toml` déclare toujours `0.1.0`, y compris au tag `v0.9.0` [Vérifié par `git show v0.9.0:pyproject.toml`].

`version = "0.1.0"` est figée ; la CI la remplace au build depuis le tag (`uv version ${{ github.ref_name }}`, `publish-release.yml`). En local et depuis Git, l'outil se déclare `0.1.0` alors que le dernier tag est `v0.9.0`. Aucun `--version`.

Correctif : `--version` via `importlib.metadata.version("docstring-linter")` ; optionnellement une version dynamique depuis Git (`hatch-vcs`, `uv-dynamic-versioning` [Non vérifié]).

### OPS-05 - PyPI [Vérifié] - Haute

**Statut : Reporté.** Cause vérifiée dans le log du job "Publish to PyPI" de `v0.9.0` : `invalid-publisher`, aucun trusted publisher déclaré sur PyPI (le projet n'existe pas, 404 sur `pypi.org/pypi/docstring-linter/json`). À faire après le lot 0 : déclarer un pending publisher (`bastgau` / `docstring-linter` / `publish-release.yml` / environnement `pypi`), passer les liens du README en URL complètes (DOC-06), ne pas relancer le job de `v0.9.0`.

Le job `pypi-publish` existe (trusted publishing, environnement `pypi`), 4 releases stables sont publiées sur GitHub (`v0.3.0`, `v0.4.0`, `v0.5.0`, `v0.9.0`, vérifié via l'API), mais `pip index versions docstring-linter` ne renvoie rien. Soit l'environnement `pypi` / le trusted publisher n'est pas configuré, soit le job échoue [Déduit, logs non consultés]. Le nom semble libre [Déduit].

C'est le principal frein de distribution : sans PyPI, pas de `pip install`, pas de `uvx docstring-linter`, pas de résolution de version par pre-commit hors Git.

À faire dans l'ordre : OPS-01, OPS-02, OPS-03, puis publication.

### OPS-06 - Flux de release beta [Déduit] - Haute

**Statut : Écarté.** Correctifs proposés (condition sur le job `build`, `git describe` pour le changelog beta) et refusés.

`publish-release.yml` :

```yaml
guard:
  needs: tests
  if: ${{ !contains(github.ref_name, '-') }}   # skipped for beta tags
build:
  needs: [tests, guard]                        # no if: condition
```

Selon la sémantique GitHub Actions, un job dont une dépendance est `skipped` est lui-même ignoré, sauf condition explicite (`if: ${{ !cancelled() && ... }}`) [Non vérifié ici, comportement documenté]. Pour un tag `v1.0.0-beta.1`, `guard` est ignoré, donc `build` et `github-publish` aussi : aucune pré-release n'est créée, contrairement à `RELEASE.md`. Aucune pré-release n'existe sur le dépôt [Vérifié], ce qui est cohérent mais ne prouve pas le défaut (aucun tag beta n'a été poussé [Vérifié]).

Second défaut : pour un tag beta, l'étape `last_stable` est ignorée, `PREVIOUS` est vide, et le changelog contient **tout l'historique** (`git log HEAD`) au lieu des commits depuis le tag précédent annoncés par `RELEASE.md`.

Correctif :

```yaml
build:
  needs: [tests, guard]
  if: ${{ !cancelled() && needs.tests.result == 'success' && contains(fromJSON('["success", "skipped"]'), needs.guard.result) }}
```

Et pour le changelog beta, prendre le tag précédent quel qu'il soit : `git describe --tags --abbrev=0 HEAD^`.

### OPS-07 - Chaîne d'approvisionnement [Vérifié] - Moyenne

**Statut : Corrigé.** `629fe46` (secrets et `permissions`), `2049cda` (archive dotenv-linter vérifiée par sha256 en CI, installateur épinglé dans `scripts/install.sh`), `4580d83` (30 actions épinglées par SHA). Vérifié localement ; pas encore exécuté sur un runner GitHub.

- `lint.yml` et `scripts/install.sh` exécutent `curl -sSfL https://raw.githubusercontent.com/dotenv-linter/dotenv-linter/master/install.sh | sudo sh` : script récupéré depuis une branche mobile et exécuté en root. Le binaire est épinglé (`v4.0.0`), pas l'installeur. Épingler l'URL sur un tag ou un SHA, ou utiliser une action dédiée.
- Actions épinglées par tag majeur (`actions/checkout@v7`, ...) et non par SHA. Dependabot est configuré pour `github-actions`, ce qui rend l'épinglage par SHA peu coûteux à maintenir.
- `tests: secrets: inherit` (`ci.yml`, `publish-release.yml`) transmet tous les secrets alors que seul `CODECOV_TOKEN` est utilisé. Déclarer `secrets: CODECOV_TOKEN: ${{ secrets.CODECOV_TOKEN }}`.
- Pas de `permissions:` au niveau de `ci.yml` (défaut du dépôt appliqué) [Déduit].

### OPS-08 - `.pre-commit-config.yaml` [Vérifié] - Basse

**Statut : Partiel.** `651718b`. `groups: [local]` et `files: ^src/` corrigés. Les commentaires de section restent en français.

- Hook `mixed-line-ending` : `groups: [locals]` au lieu de `[local]`, il ne s'exécute donc jamais dans le groupe `local`.
- Hook `pyright-src` : pas de filtre `files: ^src/`, contrairement aux autres hooks "src" ; il reçoit aussi les fichiers de `tests/` quand ils sont modifiés.
- Commentaires de sections en français (le reste du dépôt est en anglais).

### OPS-09 - `pyrightconfig.json` [Vérifié] - Basse

**Statut : Écarté.** `09d7134`. Chemin du devcontainer conservé (choix du projet).

`"venv": "/workspaces/docstring-linter/.venv"` est un chemin du devcontainer. Ailleurs, pyright affiche `venv /workspaces/docstring-linter/.venv subdirectory not found`. Remplacer par `"venvPath": "."`, `"venv": ".venv"`.

### OPS-10 - Résidus dans `pyproject.toml` [Vérifié] - Basse

**Statut : Partiel.** `651718b`. Sections sqlfluff supprimées. `line-length = 200` et les groupes `github-src`/`github-tests` sont conservés.

- `[tool.sqlfluff.core]` et `[tool.sqlfluff.indentation]` (dialecte `mariadb`) : sans rapport avec le projet.
- `[tool.pylint.format] max-module-lines = 1100` et `line-length = 200` : choix assumé, mais 200 colonnes réduit la lisibilité en revue et masque BUG-14 dans les docstrings du projet.
- Groupes `github-src` et `github-tests` qui dupliquent les versions de `dev` : trois endroits à mettre à jour par bump (visible dans l'historique des commits Dependabot).

### OPS-11 - Matrice CI [Vérifié] - Moyenne

**Statut : Reporté.** Job Windows écarté ; matrice de versions reportée au lot 0 (avec OPS-03).

Une seule version Python (`vars.PYTHON_VERSION`), un seul OS (`ubuntu-latest`). Après OPS-03, ajouter une matrice de versions et au moins un job Windows : le code manipule des chemins (`Path.match`, `full_match`, `Path.resolve()` dans le format `traceback`) dont le comportement diffère selon les séparateurs [Déduit].

### OPS-12 - Test de l'action [Vérifié] - Basse

**Statut : Corrigé.** `319326e`. Le workflow utilise `uses: ./` et teste donc le commit courant.

`.github/workflows/action.yml` utilise `bastgau/docstring-linter@main`, donc la version déjà poussée sur `main`, pas le commit testé. `uses: ./` testerait le code de la PR ou du push courant.

### OPS-13 - commitlint [Vérifié] - Basse

**Statut : Écarté.** Règle conservée ; les commits de la branche ont été réécrits sans corps ni trailers.

`.commitlintrc.mjs` impose `body-empty: always` et `footer-empty: always`. Cela interdit d'expliquer le "pourquoi" d'un changement dans le commit et bloque les trailers standards (`Co-authored-by`, `Signed-off-by` hors Dependabot, `Fixes #N`). Choix de projet, mais coûteux pour la traçabilité : à rediscuter.

## Points positifs

- Pipeline structuré en workflows réutilisables (`lint`, `tests`, `build`, `action`).
- Verrouillage des dépendances (`uv.lock`) et hook `uv lock --check`.
- Dependabot pour `uv` et `github-actions`.
- Publication PyPI prévue en trusted publishing (pas de token stocké).
- Garde "release stable uniquement depuis `main`".
- Hooks de sécurité locaux (`detect-private-key`, fichiers interdits).
