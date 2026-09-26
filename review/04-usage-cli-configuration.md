# 04 - Usage, CLI et configuration

## Expérience de première utilisation [Vérifié]

Scénario : un projet existant, documenté en Google style "classique", lance l'outil sans configuration. Mesure sur `rich` 15.0.0 :

```text
{'files_checked': 100, 'total_errors': 2410, 'files_with_errors': 100}
```

| Règle | Erreurs | Nature dominante |
|---|---|---|
| `args_match` | 502 | 382 type mismatch (dont 318 équivalents modulo `, optional`, 84 forward refs) |
| `docstring_exists` | 449 | Docstrings réellement absentes (dunders, privées incluses) |
| `blank_lines` | 383 | 333 "blank line before closing quotes" |
| `args_section` | 225 | Paramètres non documentés |
| `returns_section` | 162 | Dont `@property` et générateurs |
| `returns_none` | 130 | `Returns: None` exigé sur `-> None` |
| `attributes_section` | 126 | Section `Attributes:` exigée |
| `returns_match` | 81 | Dont `Returns:` sans type |
| `imperative_mood` | 68 | Dont "Does" -> "Doe" |
| `indentation` | 62 | Descriptions sur plusieurs lignes (BUG-14) |
| autres | 222 | |

100 % des fichiers en erreur. Un tiers au moins des erreurs relève soit d'un faux positif (types, indentation), soit d'une convention maison que peu de projets suivent (ligne vide avant `"""`, `Returns: None`). L'utilisateur conclut vite que l'outil "ne marche pas" sur son code.

## Constats

| ID | Gravité | Sujet | Statut |
|---|---|---|---|
| UX-01 | Critique | Aucune suppression inline | Reporté |
| UX-02 | Haute | Défauts très opinionnés, pas de preset | Corrigé |
| UX-03 | Haute | Pas de baseline ni de mode "diff" | Reporté |
| UX-04 | Haute | Portée non réglable (privé, dunder, overload, property, override) | Partiel |
| UX-05 | Moyenne | Toutes les erreurs pointent la ligne `def` | Reporté |
| UX-06 | Critique | Codes de sortie (voir BUG-01 à BUG-04) | Corrigé |
| UX-07 | Moyenne | Sorties : couleurs forcées, pas de `--quiet`, `--statistics`, `--select` | Partiel |
| UX-08 | Moyenne | Pas d'autofix | Reporté |
| UX-09 | Moyenne | Chemins relatifs au répertoire courant, pas au fichier de config | Corrigé |
| UX-10 | Haute | Hook pre-commit inutilisable sans Python 3.14 par défaut | Partiel |
| UX-11 | Moyenne | GitHub Action : injection, build à chaque run, Python à fournir | Partiel |
| UX-12 | Basse | Identifiants de politiques affichés comme des règles | Écarté |
| UX-13 | Basse | Pas de `--version`, pas de `--explain` | Partiel |

### UX-01 - Suppression inline [Vérifié] - Critique

**Statut : Reporté.** Après vérification de l'affichage dans VS Code.

Aucun mécanisme `# noqa` ou équivalent (`grep` sur `src/` : aucune lecture de commentaire). Combiné aux 11 règles always-on (ARCH-06), tout faux positif est bloquant.

Proposition minimale, lisible depuis le `CodeEntity` si la ligne source est conservée :

```python
def legacy_api(x):  # docstring-linter: ignore[args_match, returns_match]
    ...
```

Implémentation : `tokenize` ou lecture de la ligne `node.lineno` (et des lignes de décorateurs), regex `# (?:noqa|docstring-linter: ignore)(?:\[([\w, ]+)\])?`, filtrage des `LintError` de l'entité. pydoclint propose un mode noqa natif (`--native-mode-noqa-location`) [Vérifié via `--help`].

Bonus utile : signaler les suppressions inutiles (équivalent de `RUF100` de ruff [Non vérifié]).

### UX-02 - Défauts opinionnés [Vérifié] - Haute

**Statut : Corrigé.** `b676b02`, complété par `735d616`, `ce82164`, `66b3bed`, `f7df8f3`. `convention = "google"` fixe des défauts proches du guide Google ; `strict` reste le défaut. Sur `rich`, 758 erreurs avec `google` contre 2 410 à la revue [Vérifié].

Valeurs par défaut qui s'écartent des usages courants du Google style :

| Réglage | Défaut | Usage courant Google [Non vérifié] |
|---|---|---|
| `blank_lines_before_closing_quotes` | 1 | 0 dans les exemples du guide Google et de Napoleon |
| `returns_none` | `required` | Section omise quand la fonction ne retourne rien |
| `documented_types` | `required` | Types optionnels si la signature est annotée |
| `raises_section` | `required` | Recommandé, rarement exigé exhaustivement |
| `attributes_section` | `required`, privés inclus | Attributs publics seulement |
| `imperative_mood` | appliqué aux classes | Usuellement fonctions et méthodes (D401) |
| `return_type_annotation` | activée | Relève d'un linter de typage (ruff `ANN`), pas des docstrings |

Ces choix sont légitimes pour un style maison, mais ils devraient être un **preset** explicite, pas le comportement implicite.

Proposition :

```toml
[tool.docstring-linter]
convention = "google"   # permissive defaults matching the Google guide
# convention = "strict" # current behaviour
```

`convention` fixe les valeurs par défaut des politiques ; chaque clé explicite reste prioritaire.

### UX-03 - Baseline / mode diff [Déduit] - Haute

**Statut : Reporté.** Conception proposée (options `--baseline` et `--generate-baseline`, empreinte sans numéro de ligne, fichier JSON, pas de réécriture automatique), à reprendre plus tard.

Pour adopter l'outil sur une base existante, il faut soit tout corriger, soit exclure massivement. pydoclint propose `--baseline` et `--generate-baseline` [Vérifié via `--help`].

Proposition : `--generate-baseline .docstring-linter-baseline.json` (empreinte par `filepath`, `entity_name`, `rule`, `message`, sans numéro de ligne pour résister aux décalages) puis `--baseline` pour ne remonter que les nouvelles erreurs.

### UX-04 - Portée non réglable [Vérifié] - Haute

**Statut : Partiel.** `ce82164`, `65839f4`. Options `exclude_dunder_methods`, `exclude_private`, `exclude_overridden`, `properties_as_attributes` ; `@overload` toujours ignoré. `exclude_overridden` ne couvre que `@override` : `Child.run` sans décorateur reste signalé [Vérifié]. Pas d'option pour les attributs privés (`attributes_section` est optionnel avec `google`).

Observé :

| Cas | Comportement actuel |
|---|---|
| `__repr__` sans docstring | `docstring_exists` |
| `@overload` | `docstring_exists` par signature (BUG-21) |
| `@property def size(self) -> int` | `returns_section` exigé |
| Méthode surchargée sans docstring (`Child.run`) | `docstring_exists` |
| Attribut `self._cache` | `attributes_section` exigé |
| Fonction `_private` | Traitée comme publique [Déduit] |

`scope` ne distingue que modules, classes, fonctions et méthodes. Les concurrents offrent ces réglages : docsig `--check-dunders`, `--check-protected`, `--check-overridden`, `--check-property-returns`, `--check-nested` ; pydoclint `--skip-checking-private-functions`, `--should-document-private-class-attributes`, `--treat-property-methods-as-class-attributes` [Vérifié via `--help`].

Proposition :

```toml
[tool.docstring-linter.scope]
private = false        # _name
dunder = false         # __name__, except __init__
overloads = false      # @overload stubs
overridden = false     # @override / @typing.override
properties = "attribute"  # document @property like an attribute, no Returns
private_attributes = false
```

### UX-05 - Ligne de l'erreur [Vérifié] - Moyenne

**Statut : Reporté.** Approche proposée : niveau intermédiaire (ligne précise pour les règles de mise en page et les entrées, en-tête de section ou guillemets ouvrants sinon, `docstring_exists` et `return_type_annotation` sur le `def`), un en-tête `traceback` par ligne distincte, `# noqa` lu sur la ligne `def`/`class`.

`make_error` utilise `entity.line` (`rules/_base.py:36-55`) : toutes les erreurs d'une entité pointent la ligne `def`/`class`. Pour une annotation GitHub ou un saut d'éditeur, la ligne fautive dans le docstring serait plus utile (entrée `Args:` erronée, section mal ordonnée). Dépend d'ARCH-03 (modèle ligne à ligne) et d'ARCH-07 (`docstring_line`).

### UX-06 - Codes de sortie [Vérifié] - Critique

**Statut : Corrigé.** `b2fd640` : codes 0, 1 et 2. `8a9e4b4` : code 3 pour une erreur interne (voir ARCH-08), priorité 3 > 2 > 1 > 0 ; tableau du README complété.

Détail dans BUG-01 à BUG-04. Contrat proposé et à documenter :

| Code | Signification |
|---|---|
| 0 | Aucune erreur |
| 1 | Erreurs de lint |
| 2 | Configuration invalide, chemin inexistant, fichier illisible ou non parsable |
| 3 | Erreur interne |

### UX-07 - Sorties [Vérifié] - Moyenne

**Statut : Partiel.** Couleurs désactivées hors terminal et avec `NO_COLOR` (`0355225`), `--statistics` (`9c90fd5`). `--select`/`--ignore` en CLI écartés. Restent : ligne `Config:` sur stdout, pas de SARIF ni de niveau `warning`.

- Codes ANSI toujours émis, même vers un pipe ou un fichier (`reporter.py:18-30`) ; pas de `NO_COLOR` ni `--no-color`. Vérifié : la sortie redirigée contient `\x1b[1m`, `\x1b[96m`, etc.

  ```python
  # reporter.py - disable colors when not writing to a terminal
  import os
  import sys

  _USE_COLOR = sys.stdout.isatty() and "NO_COLOR" not in os.environ
  ```

- La ligne `Config: ...` s'imprime sur stdout en `traceback` et `text` (`cli.py:255-259`) : utile, mais à envoyer sur stderr ou derrière `--verbose`.
- Pas de `--select` / `--ignore` en CLI : impossible de tester une règle isolément sans éditer la config.
- Pas de `--statistics` (compte par règle) : c'est pourtant le premier besoin d'une équipe qui évalue l'outil (le tableau ci-dessus a dû être produit par script).
- Pas de SARIF (déjà au `TODO.md`) : utile pour GitHub Code Scanning.
- `github-annotations` émet toujours `::error` ; un niveau `warning` configurable permettrait une adoption progressive.

### UX-08 - Pas d'autofix [Vérifié] - Moyenne

**Statut : Reporté.** Approche proposée : `--fix` et `--diff`, d'abord les règles de mise en page (texte du docstring seul), correction du texte source du littéral (positions AST et `ast.get_source_segment`, vérifiées), fichier inchangé si l'AST hors docstrings diffère après correction.

Beaucoup de règles sont mécaniques : `blank_lines`, `summary_final_period`, `section_capitalization`, `entry_spacing`, `returns_none`, `section_order`, et la synchronisation des types depuis la signature. ruff propose des corrections pour une partie de ses règles `D` [Vérifié : `ruff rule --all` indique "Fix is always/sometimes available" pour certaines]. pydoclint ne corrige pas [Non vérifié].

Un `--fix` limité aux règles de mise en page serait un différenciateur fort (voir 07). Prérequis : modèle ligne à ligne (ARCH-03) et réécriture du littéral dans la source (positions via `ast.get_source_segment` ou `tokenize`).

### UX-09 - Chemins relatifs au CWD [Déduit] - Moyenne

**Statut : Corrigé.** `23fc020`. `exclude`, `--exclude` et les `paths` des overrides sont résolus depuis le dossier du fichier de config (y compris avec `--config`), depuis le répertoire courant sans config. Lancé depuis `src/`, le cas de reproduction donne le même résultat que depuis la racine [Vérifié]. Décision : la config reste cherchée depuis le répertoire courant (documenté), pas de config par fichier comme ruff.

`ConfigOverride.matches` (`config.py:213-231`) et `exclude` comparent au répertoire courant, pas au répertoire du fichier de config. Lancer `docstring-linter .` depuis `src/` avec un override `paths = ["src/**"]` ne l'applique pas. ruff résout les chemins relativement au fichier de configuration [Non vérifié].

Proposition : conserver `config_dir` dans `LinterConfig` et calculer les chemins relatifs à lui.

### UX-10 - Hook pre-commit [Déduit] - Haute

**Statut : Partiel.** `a1fb08e`. Le contournement `language_version: python3.14` est documenté dans le README. La vraie solution (OPS-03) est reportée au lot 0.

`.pre-commit-hooks.yaml` déclare `language: python`. pre-commit crée un venv avec l'interpréteur par défaut ; avec `requires-python = ">=3.14,<3.15"`, l'installation échoue partout où le Python par défaut n'est pas 3.14 (la majorité des postes et runners en septembre 2026 [Non vérifié]). Contournement utilisateur : `language_version: python3.14`, à documenter a minima. Vraie solution : OPS-03.

### UX-11 - GitHub Action [Vérifié] - Moyenne

**Statut : Partiel.** `319326e`. Inputs passés par variables d'environnement, une tentative `src/; echo INJECTED` n'exécute plus rien [Vérifié en simulant l'étape] ; description de `format` complétée. Décisions : `pip install` des sources conservé jusqu'à PyPI, pas de `setup-python` intégré (effet de bord sur le job appelant).

`action.yml` :

```yaml
run: docstring-linter ${{ inputs.paths }} --format ${{ inputs.format }} ${{ inputs.extra-args }}
```

- Les inputs sont interpolés directement dans le script shell. Si un workflow consommateur y passe une valeur contrôlée par un tiers (titre de PR, nom de branche), c'est une injection de commande. Le guide de durcissement GitHub recommande de passer par des variables d'environnement [Non vérifié].

  ```yaml
  - name: Run docstring-linter
    shell: bash
    env:
      PATHS: ${{ inputs.paths }}
      FORMAT: ${{ inputs.format }}
      EXTRA_ARGS: ${{ inputs.extra-args }}
    run: |
      # Word splitting on PATHS and EXTRA_ARGS is intended
      # shellcheck disable=SC2086
      docstring-linter $PATHS --format "$FORMAT" $EXTRA_ARGS
  ```

- `pip install ${{ github.action_path }}` reconstruit le paquet à chaque exécution, via le backend setuptools legacy (OPS-02).
- L'utilisateur doit lui-même installer Python 3.14 (`actions/setup-python`) ; un input `python-version` avec installation intégrée simplifierait.
- La description de l'input `format` omet `traceback`.

### UX-12 - Identifiants de politiques [Déduit] - Basse

**Statut : Écarté.** Décision : pas de message spécifique.

Une erreur `[returns_section]` ressemble à une règle ; `ignore = ["returns_section"]` échoue avec "unknown rule" (`config.py:528`). Le message devrait l'orienter : "'returns_section' is a policy, set returns_section = \"optional\"".

### UX-13 - `--version`, `--explain` [Vérifié] - Basse

**Statut : Partiel.** `--version` reporté : la version sera gérée plus tard par la CI/CD (voir OPS-04). `--explain` écarté ; à la place, `--list-rules` affiche les règles always-on dans une section dédiée (`3bc192e`).

Pas de `--version` (utile pour les rapports de bug et le débogage pre-commit). Pas d'équivalent à `ruff rule <code>` pour afficher la doc d'une règle depuis le terminal ; `--list-rules` masque les règles always-on, alors qu'elles apparaissent dans les sorties.

## Points positifs à conserver

- Validation stricte de la configuration, messages clairs, exit 2. [Vérifié]
- `--list-rules` affiche la valeur effective de chaque politique et option, et les overrides avec la valeur de base. [Vérifié]
- Format `traceback` cliquable dans les éditeurs.
- Overrides par chemin avec règle "le dernier gagne" explicite et documentée.
- Double support `pyproject.toml` / `.docstring-linter.toml`.
