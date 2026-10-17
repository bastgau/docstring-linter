# 02 - Architecture et code

## Vue d'ensemble

```text
cli.main
  load_config -------------> LinterConfig (+ overrides)
  run
    collect_python_files      (rglob + exclude)
    lint_file (par fichier, séquentiel ou ProcessPool)
      config.for_path          (override résolu)
      ast_parser.parse_file --> [CodeEntity]          (module, classes, fonctions, méthodes)
      GoogleStyleParser.parse -> ParsedDocstring      (summary, args, returns, raises, ...)
      rules.validate_entity --> [LintError]           (~30 fonctions check_*)
    reporter.report_*         (traceback, text, json, github-annotations)
```

| Module | Lignes | Rôle |
|---|---|---|
| `cli.py` | 265 | Arguments, collecte des fichiers, parallélisme, dispatch des sorties |
| `config.py` | 641 | Registres de règles/politiques/options, dataclasses de config, chargement TOML, overrides |
| `ast_parser.py` | 350 | Extraction des entités et signatures |
| `docstring_parser.py` | 367 | Parsing Google |
| `rules/*.py` | 1 144 | Règles, regroupées par thème |
| `reporter.py` | 270 | Formats de sortie et `--list-rules` |
| `models.py` | 212 | Dataclasses |

[Vérifié] par `wc -l`.

## Points forts

- **Zéro dépendance runtime** (`dependencies = []`) : installation triviale, pas de conflit. [Vérifié]
- **Typage strict** : pyright `strict`, ruff `select = ["ALL"]`, pylint 10/10, 0 erreur. [Vérifié]
- **Séparation claire** des étapes (extraction AST, parsing docstring, règles, rendu), fonctions pures faciles à tester.
- **Configuration stricte** : clés, règles et valeurs de politique inconnues rejetées avant tout lint, exit 2. [Vérifié]
- **Modèle "politique vs règle de contenu"** bien pensé : la politique décide *si* la section doit exister, la règle de contenu vérifie *ce qui* est écrit, sans double signalement en mode `forbidden` (`rules/__init__.py:107-138`).
- **Dogfooding** : le linter s'applique à `src/` et `tests/` via pre-commit. [Vérifié]

## Constats

| ID | Gravité | Sujet | Statut |
|---|---|---|---|
| ARCH-01 | Moyenne | Couche d'extraction AST trop superficielle | Corrigé |
| ARCH-02 | Moyenne | Règles non déclaratives, dispatcher monolithique, registres dupliqués | Corrigé |
| ARCH-03 | Moyenne | Docstring re-parsé par chaque règle de structure, 3 définitions d'un en-tête | Partiel |
| ARCH-04 | Moyenne | Abstraction multi-style creuse | Corrigé |
| ARCH-05 | Moyenne | Options énumérées à la main à 5 endroits | Corrigé |
| ARCH-06 | Haute | Always-on sans échappatoire | Corrigé |
| ARCH-07 | Moyenne | Modèle `CodeEntity` trop pauvre | Partiel |
| ARCH-08 | Haute | `ValueError` comme fourre-tout au niveau fichier | Corrigé |
| ARCH-09 | Basse | Code mort ou trompeur | Corrigé |
| ARCH-10 | Moyenne | Tests unitaires qui contournent l'AST | Corrigé |

### ARCH-01 - Extraction AST superficielle [Vérifié] - Moyenne

**Statut : Corrigé.** `65839f4`. `_scan_body` collecte raises et yields en une passe élaguée aux portées imbriquées, avec les alias `except` et les noms pointés. Implémenté par un parcours itératif plutôt qu'un `NodeVisitor`.

`ast_parser.py` est la source des bugs les plus coûteux (BUG-08, 09, 10, 15, 16, 21). Causes communes :

- parcours ad hoc (`ast.walk`, file manuelle, `node.body` direct) au lieu d'un visiteur unique qui connaît les portées ;
- informations jetées tôt : décorateurs, première ligne de docstring, `except ... as name`, noms pointés.

Proposition : un `ast.NodeVisitor` qui maintient une pile de portées et remplit `CodeEntity` en une passe (voir PERF-01 pour le gain). Exemple de squelette :

```python
# ast_parser.py - single pass, scope-aware body scan for one function
class _BodyScanner(ast.NodeVisitor):
    """Collect raises and yields of one function, without entering nested scopes."""

    def __init__(self) -> None:
        self.raises: list[RaiseInfo] = []
        self.is_generator = False
        self._aliases: dict[str, str] = {}  # except X as name -> X

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:  # nested scope: skip
        return

    visit_AsyncFunctionDef = visit_FunctionDef
    visit_Lambda = visit_FunctionDef
    visit_ClassDef = visit_FunctionDef

    def visit_Yield(self, node: ast.Yield) -> None:
        self.is_generator = True
        self.generic_visit(node)

    visit_YieldFrom = visit_Yield

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:
        if node.name and node.type is not None:
            self._aliases[node.name] = ast.unparse(node.type)
        self.generic_visit(node)

    def visit_Raise(self, node: ast.Raise) -> None:
        exc = node.exc.func if isinstance(node.exc, ast.Call) else node.exc
        if isinstance(exc, (ast.Name, ast.Attribute)):
            name = ast.unparse(exc)
            self.raises.append(RaiseInfo(exception_type=self._aliases.get(name, name), line=node.lineno))
        self.generic_visit(node)
```

### ARCH-02 - Règles non déclaratives [Vérifié] - Moyenne

**Statut : Corrigé.** `6bfff7a` : tests de cohérence (`tests/linter/test_registries.py`) entre registres, catégories, `ALWAYS_ON`, champs de `LinterConfig`, titres de `docs/` et règles émises, qui échouent sur une règle ou une politique ajoutée à moitié [Vérifié]. `10cd726` : `validate_entity` découpé en `_check_summary`, `_check_function`, `_check_class` et `_check_layout`, sans `noqa` ; sorties identiques sur `rich` et la stdlib [Vérifié]. Décision : table déclarative écartée tant qu'il n'y a qu'un style. Sous-points antérieurs : `section_order` (`acdcf43`), `--select` (`89c4a28`), UX-12 écarté.

Ajouter une règle impose de toucher au moins 4 endroits : `RULES_REGISTRY`, `RULES_CATEGORIES`, `ALWAYS_ON` (`config.py:83-156`), `validate_entity` (`rules/__init__.py:59-165`, marqué `noqa: C901, PLR0912, PLR0915`), plus la doc. Les politiques ajoutent `POLICIES_REGISTRY`, un champ `LinterConfig` et un appel dans le dispatcher.

La dérive est déjà visible :

- `section_order` est décrit comme "Args, Returns, Yields, Raises, Example(s), Note(s)" (`config.py:129`) alors que l'ordre réel commence par `Attributes` et inclut `Todo` (`rules/_base.py:20-31`). [Vérifié]
- Le commentaire de `OFF_BY_DEFAULT` mentionne un flag `--select` qui n'existe pas (`config.py:138`, `cli.py:207-225`). [Vérifié]
- Les erreurs de politique portent des identifiants (`returns_section`, `args_section`, ...) absents de `RULES_REGISTRY` : un utilisateur qui écrit `ignore = ["returns_section"]` reçoit "unknown rule". [Déduit de `config.py:528`]

Proposition, sans framework de plugins :

```python
# rules/registry.py - one declarative table drives dispatch, --list-rules and docs
@dataclass(frozen=True)
class Rule:
    id: str
    category: str
    description: str
    kind: Literal["configurable", "always_on", "policy"]
    applies_to: frozenset[NodeType]
    check: Callable[[CodeEntity, ParsedDocstring | None, LinterConfig], list[LintError]]


RULES: tuple[Rule, ...] = (...)
```

`validate_entity` devient une boucle de 5 lignes ; `--list-rules`, la doc et les tests de complétude se génèrent depuis `RULES`.

### ARCH-03 - Docstring re-parsé par chaque règle [Vérifié] - Moyenne

**Statut : Partiel.** `acdcf43`. Les en-têtes connus sont définis une seule fois (`sections.py`) et partagés par le parser et les règles. Restent : `CANDIDATE_SECTION_PATTERN` pour les sections inconnues, deux jeux de regex d'entrée, pas de modèle ligne à ligne.

`GoogleStyleParser` produit un `ParsedDocstring` sémantique, mais 9 règles de structure (`check_indentation`, `check_section_capitalization`, `check_section_order`, `check_empty_section`, `check_blank_lines`, `check_named_section`, `check_entry_spacing`, `check_no_blank_line_in_section`, `extract_section_headers`) refont chacune leur `split("\n")` et leurs regex.

Trois définitions d'un en-tête de section coexistent :

| Regex | Fichier | Particularité |
|---|---|---|
| `SECTION_PATTERN` | `docstring_parser.py:59` | Liste fermée, sensible à la casse |
| `CANDIDATE_SECTION_PATTERN` | `docstring_parser.py:63` | Un seul mot, majuscule initiale, ligne non strippée |
| `SECTION_HEADER_RE` | `rules/_base.py:33` | N'importe quel mot, casse libre |

Et deux définitions d'une entrée : `ARG_PATTERN`/`ARG_NO_TYPE_PATTERN` (parser) et `_ENTRY_LAX`/`_ENTRY_STRICT` (`rules/structure.py:11-13`).

Conséquences : incohérences possibles entre ce que le parser comprend et ce que les règles vérifient (BUG-18 en est un exemple) ; impossible de rapporter une ligne précise (UX-05) ; `ParsedDocstring.examples` est rempli mais aucune règle ne le lit (`check_named_section` relit le texte brut). [Vérifié par grep]

Proposition : le parser produit un modèle ligne à ligne, consommé par toutes les règles.

```python
# models.py - line-aware docstring model shared by all rules
@dataclass
class Section:
    name: str             # as written, e.g. "Args", "args", "Keyword Args"
    header_line: int      # 0-based line index inside the docstring
    blank_lines_before: int
    entries: list[Entry]


@dataclass
class Entry:
    line: int
    raw: str
    name: str | None
    type_annotation: str | None
    description: str
```

### ARCH-04 - Abstraction multi-style creuse [Vérifié] - Moyenne

**Statut : Corrigé.** `b2fd640` : `DocstringStyle` réduit à `GOOGLE`, docstrings de paquet alignées. `e077ef9` : `BaseDocstringParser`, `PARSERS`, `get_parser`, `DocstringStyle`, la clé `style` et l'option `--style` supprimés ; `lint_file` utilise `GoogleStyleParser` directement. `style = "google"` donne désormais "unknown configuration key" et le code 2 (à signaler dans le CHANGELOG, DOC-05). Sorties identiques sur `rich` [Vérifié].

`BaseDocstringParser`, `PARSERS`, `DocstringStyle` (4 valeurs), `--style` masqué et les docstrings de paquet (`__init__.py:3-4`, `docstring_parser.py:3-5`) annoncent NumPy, Sphinx et PEP 257. Or toutes les règles de structure sont codées pour Google (`GOOGLE_SECTIONS`, `GOOGLE_SECTION_ORDER`, indentation à 4). Résultat : BUG-01 et une promesse non tenue.

Recommandation (cohérente avec la règle "pas de fonctionnalité spéculative" du `CLAUDE.md`) : supprimer les styles non implémentés et `BaseDocstringParser` tant qu'un second style n'est pas réellement développé. Si NumPy devient un objectif, le modèle ligne à ligne d'ARCH-03 est le bon point d'extension.

### ARCH-05 - Options énumérées à la main [Vérifié] - Moyenne

**Statut : Corrigé.** `b6ad01e` : validation typée par tables (`INT_OPTIONS`, `BOOL_OPTIONS`, `CHOICE_OPTIONS`) partagée par la racine et les overrides. `8bb902d` : `SETTING_KEYS` et `OVERRIDABLE_OPTIONS` déduits des tables de types (`TYPED_OPTIONS`), `option_values()` générique ; ajouter une option ne touche plus que 5 endroits au lieu de 8. Tests de cohérence : option listée = champ typé, tableau des clés et liste des options d'override de `docs/configuration.md` exacts. Ensembles de clés, valeurs et sortie de `--list-rules` identiques avant et après [Vérifié]. Décision : table `Option` unique écartée.

La liste des options apparaît dans `SETTING_KEYS`, `OVERRIDABLE_OPTIONS`, `OPTIONS_REGISTRY`, `LinterConfig`, `option_values()` et `_parse_toml_config` (`config.py:67-80`, `159-193`, `276-306`, `345-364`, `577-641`). Chaque ajout doit être répliqué ; la validation de type manque (BUG-06) et les bornes (`max(1, ...)`) ne s'appliquent qu'au niveau racine.

Proposition : une table unique.

```python
# config.py - single source of truth for options
@dataclass(frozen=True)
class Option:
    type: type
    default: object
    description: str
    overridable: bool = False
    minimum: int | None = None


OPTIONS: dict[str, Option] = {
    "summary_max_length": Option(int, 80, "Maximum summary line length", overridable=True, minimum=1),
    "workers": Option(int, 1, "Parallel workers, 0 = auto", minimum=0),
    ...
}
```

### ARCH-06 - Always-on sans échappatoire [Vérifié] - Haute

**Statut : Corrigé.** Option 1 retenue (`672ee78`, voir UX-01) : les règles always-on restent non désactivables dans la configuration, mais `# docstring-linter: ignore[rule]` les fait taire sur une entité. Atténué aussi : `raises_extraneous` sorti des règles always-on (`6f95960`), niveaux de `type_matching` (`735d616`).

11 règles sont non désactivables (`config.py:142-156`) et `ignore` les refuse explicitement (`config.py:530-533`). Justification donnée : "requiring a section and then tolerating wrong content in it makes no sense" (`docs/always-on-rules.md`).

L'argument tient pour un code parfaitement analysé. Il ne tient plus dès qu'un faux positif existe : BUG-09, 10, 11, 12, 13, 19, 20 touchent tous des règles always-on. Sans `# noqa` ni baseline (UX-01, UX-03), la seule issue est d'exclure le fichier entier.

Options à discuter :

1. Conserver always-on au niveau configuration, mais autoriser `# noqa: <rule>` sur la ligne de l'entité (recommandé, coût faible).
2. Rendre ces règles désactivables avec un avertissement.
3. Réduire le périmètre always-on aux défauts non ambigus (`duplicate_arg`, `empty_section`, arg fantôme) et passer les comparaisons de types en politique.

### ARCH-07 - Modèle `CodeEntity` trop pauvre [Vérifié] - Moyenne

**Statut : Partiel.** `ce82164`, `66b3bed`. Ajout de `decorators`, `init_args` et `class_docstring`. Pas de `docstring_line` ni de `parent` (voir UX-05).

`CodeEntity` (`models.py:61-93`) ne porte ni décorateurs, ni ligne de début de docstring, ni parent structuré. Conséquences : `_is_init` teste un suffixe de chaîne (`rules/args.py:98-108`), impossible de traiter `@overload`, `@property`, `@staticmethod`, `@override` (BUG-16, BUG-21, UX-04), toutes les erreurs pointent la ligne `def` (UX-05).

Champs à ajouter : `decorators: list[str]`, `docstring_line: int | None`, `parent: str | None`, `is_private: bool`, `is_dunder: bool`.

### ARCH-08 - `ValueError` fourre-tout [Vérifié] - Haute

**Statut : Corrigé.** `b2fd640` : configuration validée une fois dans `main()`, `SyntaxError`, `UnicodeDecodeError` et `OSError` en code 2. `8a9e4b4` : toute autre exception est attrapée fichier par fichier, nommée sur stderr avec sa trace, les autres fichiers sont analysés, code 3. Reproduit avant/après avec un fichier qui fait lever `RecursionError` à `ast.parse` parmi 61 : avant, run arrêté sans sortie, code 1, fichier non nommé ; après, 62 fichiers analysés, fichier nommé, code 3 [Vérifié].

`_lint_file_safe` (`cli.py:127-143`) attrape `ValueError` en supposant une erreur de configuration. En pratique, elle couvre `UnicodeDecodeError`, le style non supporté et toute `ValueError` d'un bug interne, et les convertit en succès (BUG-01, BUG-02). Une exception d'un autre type (ex. `RecursionError` sur un fichier très imbriqué [Déduit]) arrête tout le run avec une traceback, y compris en mode parallèle via `future.result()`.

Proposition : erreurs de configuration validées une fois dans `main()` ; au niveau fichier, attraper `SyntaxError`, `UnicodeDecodeError`, `OSError` explicitement ; laisser remonter le reste comme bug interne avec exit 3 et le nom du fichier en cause.

### ARCH-09 - Code mort ou trompeur [Vérifié] - Basse

**Statut : Corrigé.** Constantes `quantity` disparues (`6f95960`). `183aa75` : `OFF_BY_DEFAULT` supprimé, `--list-rules` compte et étiquette les règles coupées par la convention active (3 en `google`, 0 en `strict`) [Vérifié] ; `ParsedDocstring.examples` supprimé ; `.vulture` supprimé avec ses 3 références, vulture ne signale rien sans lui [Vérifié].

- `OFF_BY_DEFAULT` est vide ; la mécanique (affichage "disabled by default", filtrages) existe sans cas d'usage.
- `ParsedDocstring.examples` jamais lu par une règle.
- `.vulture` liste `YELLOW` et `GREEN` comme inutilisés alors qu'ils le sont dans `report_policies` ; références de lignes périmées.
- `quantity = 2`, `quantity = 3`, `quantity = 4` (`rules/structure.py:40`, `rules/docstring.py:166-173`) : contournement de `PLR2004` qui réduit la lisibilité ; une constante nommée (`_MAX_DISTINCT_INDENTS = 2`) serait plus claire.

### ARCH-10 - Tests [Vérifié] - Moyenne

**Statut : Corrigé.** `tests/linter/test_end_to_end.py` (34 tests passant par le vrai parsing AST), tests de cohérence des registres et de `TESTS.md` (`6bfff7a`, `2ecc362`) ; 589 tests, couverture branches 96,24 %. `5779bbd` : seuil `fail_under` relevé de 85 à 90 [Vérifié]. Décision : pas de test de corpus (stdlib instable d'une version corrective à l'autre, code tiers à éviter, cas de l'annexe déjà couverts par `test_end_to_end.py`).

État : 372 tests, 1,45 s, 94,39 % de couverture branches, seuil CI 85 %.

Limites :

- Les tests de règles construisent `CodeEntity` à la main (`tests/linter/rules/conftest.py`, `_func`), donc contournent `ast_parser`. Aucun des bugs BUG-08 à BUG-16 n'est détectable par ces tests.
- `cli.py` à 79 % : chemin parallèle (`cli.py:186-193`) et `main()` (`--list-rules`, affichage "Config:") non couverts.
- Pas de test de bout en bout sur un corpus réel.
- `TESTS.md` annonce 369 tests pour 372 réels (voir DOC-03).

Propositions :

1. **Fixtures annotées** : `tests/fixtures/*.py` avec l'erreur attendue en commentaire, et un test paramétré qui compare.

   ```python
   def optional_arg(limit: int | None = None) -> int:  # expect: (none)
       """Return the limit.

       Args:
           limit (int, optional): Maximum value.
       ...
   ```

2. **Test de corpus** : lint d'une version figée d'un projet Google style (ex. un sous-ensemble de `rich`), snapshot des compteurs par règle ; toute variation doit être justifiée dans la PR.
3. Test de complétude des registres : chaque règle de `RULES_REGISTRY` est documentée dans `docs/` et a au moins un test.
4. Relever le seuil de couverture à 90 %.
