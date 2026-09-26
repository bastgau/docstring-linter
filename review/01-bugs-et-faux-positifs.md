# 01 - Bugs et faux positifs

Tous les cas marqués **[Vérifié]** ont été reproduits avec `docstring-linter` installé depuis la révision `0957240`, sous Python 3.14.7, avec `--config /nonexistent` (configuration par défaut) sauf mention contraire. Les fichiers de test utilisés sont reproduits en annexe.

## Sommaire

| ID | Gravité | Sujet | Preuve |
|---|---|---|---|
| BUG-01 | Critique | Style non Google accepté, aucun fichier analysé, exit 0 | Vérifié |
| BUG-02 | Critique | Erreur de syntaxe / d'encodage : exit 0, message sur stdout, JSON pollué | Vérifié |
| BUG-03 | Critique | Chemin inexistant : "No Python files found." et exit 0 | Vérifié |
| BUG-04 | Haute | `--config` vers un fichier absent : défauts silencieux | Vérifié |
| BUG-05 | Haute | `select = ["ALL"]` dans un override désactive toutes les règles configurables | Vérifié |
| BUG-06 | Moyenne | Types des valeurs de config non validés (traceback ou comportement absurde) | Vérifié |
| BUG-07 | Haute | `exclude` : les globs `**` et `dir/*` ne fonctionnent pas | Vérifié |
| BUG-08 | Haute | Générateur imbriqué : la fonction parente est traitée comme générateur | Vérifié |
| BUG-09 | Haute | `raise err` : `err` exigé dans `Raises:` | Vérifié |
| BUG-10 | Haute | `raise mod.Error()` invisible, `mod.Error` non parsable dans `Raises:` | Vérifié |
| BUG-11 | Moyenne | Exceptions propagées impossibles à documenter (règle always-on) | Vérifié |
| BUG-12 | Critique | `(int, optional)` produit un type mismatch always-on | Vérifié |
| BUG-13 | Haute | Forward reference `"Node"` produit un type mismatch always-on | Vérifié |
| BUG-14 | Haute | `indentation` en erreur dès qu'une description tient sur deux lignes | Vérifié |
| BUG-15 | Haute | `def` sous `if`/`try`/`with` jamais analysés | Vérifié |
| BUG-16 | Moyenne | `self`/`cls` ignorés par nom et non par position | Vérifié |
| BUG-17 | Moyenne | Heuristique d'impératif : "Does" -> "Doe", "Settings" -> "Setting" | Vérifié |
| BUG-18 | Moyenne | Sections Napoleon à deux mots avalées silencieusement | Vérifié |
| BUG-19 | Haute | `Returns:` sans préfixe de type (forme du guide Google) rejeté, always-on | Vérifié |
| BUG-20 | Basse | `Returns:` : description avec `:` lue comme un type, continuation perdue | Vérifié |
| BUG-21 | Moyenne | `@overload` exige une docstring par signature | Vérifié |
| BUG-22 | Basse | Annotations GitHub non échappées | Déduit |
| BUG-23 | Basse | "1 files checked" | Vérifié |

---

## BUG-01 - Style non Google accepté, exit 0 [Vérifié] - Critique

`DocstringStyle` expose `numpy`, `sphinx`, `pep257` (`config.py:15-29`), la config les accepte (`_parse_style`, `config.py:491`), mais seul Google a un parser (`docstring_parser.py:345`). `get_parser` lève `ValueError`, capturée fichier par fichier dans `_lint_file_safe` (`cli.py:142`), imprimée, puis ignorée pour le code de sortie.

```console
$ echo 'style = "numpy"' > .docstring-linter.toml
$ docstring-linter tests/; echo "exit=$?"
Configuration error for tests/test_a.py: Unsupported docstring style: numpy
1 files checked, 0 errors.
exit=0
```

Correctif : réduire l'enum à `GOOGLE` (ou rejeter au chargement si `style not in PARSERS`), ce qui déclenche l'exit 2 déjà prévu par `main()`.

```python
# config.py - reject styles that have no parser at load time
def _parse_style(value: object) -> DocstringStyle:
    supported = ("google",)
    if value not in supported:
        msg = f"'style': invalid value {value!r}, expected one of {', '.join(supported)}."
        raise ValueError(msg)
    return DocstringStyle(value)
```

## BUG-02 - Erreurs d'analyse : exit 0, stdout, JSON invalide [Vérifié] - Critique

`cli.py:140-143` transforme `SyntaxError` et `ValueError` en message texte, imprimé sur **stdout** (`cli.py:184`, `cli.py:192`), sans effet sur le code de sortie. `UnicodeDecodeError` hérite de `ValueError` et s'affiche comme "Configuration error".

```console
$ printf 'def f(:\n' > src/broken.py
$ docstring-linter src/broken.py --format json; echo "exit=$?"
Syntax error in src/broken.py: invalid syntax (broken.py, line 1)
{
  "summary": { "files_checked": 1, "total_errors": 0, "files_with_errors": 0 },
  "errors": []
}
exit=0

$ printf '\xff\xfe bad' > src/latin.py
$ docstring-linter src/latin.py
Configuration error for src/latin.py: 'utf-8' codec can't decode byte 0xff in position 0: invalid start byte
1 files checked, 0 errors.
```

Conséquences : le JSON n'est plus parsable (`jq` échoue), une CI passe au vert sur un fichier cassé.

Correctif : messages sur `stderr`, compteur d'échecs, code de sortie 2 si au moins un fichier n'a pas pu être analysé ; distinguer `UnicodeDecodeError` et `OSError` ; en format `github-annotations`, émettre aussi un `::error`.

```python
# cli.py - keep failures out of stdout and out of the "config error" label
except SyntaxError as e:
    return filepath, [], f"{filepath}: syntax error: {e}"
except (UnicodeDecodeError, OSError) as e:
    return filepath, [], f"{filepath}: cannot read file: {e}"
```

```python
# cli.py, in run() - report on stderr and fail the run
failures = 0
...
if err_msg:
    print(err_msg, file=sys.stderr)
    failures += 1
...
if failures:
    return 2
return 1 if all_errors else 0
```

## BUG-03 - Chemin inexistant : exit 0 [Vérifié] - Critique

`collect_python_files` (`cli.py:21`) ignore silencieusement un chemin qui n'est ni un fichier `.py` ni un répertoire. Une faute de frappe dans un workflow désactive le linter sans bruit.

```console
$ docstring-linter srcc/; echo "exit=$?"
No Python files found.
exit=0
```

Correctif : erreur explicite et exit 2 pour un chemin inexistant. Garder "No Python files found." (exit 0) uniquement pour un répertoire existant mais vide.

## BUG-04 - `--config` introuvable : défauts silencieux [Vérifié] - Haute

`_find_config` renvoie `None` si le chemin explicite n'existe pas (`config.py:425-429`), ce qui charge les défauts.

```console
$ docstring-linter src/ --config /nonexistent
Config: defaults (no config file found)
```

Correctif : lever `ValueError(f"config file not found: {explicit_path}")`. Même traitement si `--config pyproject.toml` ne contient pas de section `[tool.docstring-linter]` (aujourd'hui : défauts silencieux, `config.py:405-407`).

## BUG-05 - `select = ["ALL"]` dans un override [Vérifié] - Haute

`_validate_rules` accepte `["ALL"]` dans un override, mais `for_path` filtre sur `RULES_REGISTRY` (`config.py:327`) : `"ALL"` disparaît, l'ensemble activé devient vide.

```toml
[[overrides]]
paths = ["src/**"]
select = ["ALL"]
```

Mesure sur `cases.py` : 17 erreurs sans override, 13 avec. Les 4 manquantes sont les règles configurables (`indentation`, `imperative_mood`, `docstring_exists`, `unknown_section`).

Correctif :

```python
# config.py, for_path - honour 'ALL' like the base level does
if override.select is None:
    enabled = set(self.enabled_rules)
elif override.select == ["ALL"]:
    enabled = set(RULES_REGISTRY)
else:
    enabled = {rule for rule in override.select if rule in RULES_REGISTRY}
```

## BUG-06 - Types de configuration non validés [Vérifié] - Moyenne

Les `cast(...)` de `_parse_toml_config` et `_parse_override` ne sont que des indications pour le type checker.

| Config | Résultat observé |
|---|---|
| `workers = "4"` | `TypeError: '>' not supported between instances of 'str' and 'int'` (traceback) |
| `exclude = "src"` | Accepté, itéré caractère par caractère, aucune erreur |
| `select = "ALL"` | `Configuration error: select: unknown rules 'A', 'L'.` |
| override `summary_max_length = "x"` | `TypeError` au moment du lint (traceback) |
| override `summary_max_length = -5` | Accepté sans le `max(1, ...)` appliqué au niveau racine (`config.py:619` vs `config.py:566-567`) [Déduit] |

Correctif : un petit validateur partagé, utilisé à la racine et dans les overrides (voir aussi ARCH-05).

```python
# config.py - one validator for scalar and list settings
def _expect(key: str, value: object, kind: type, minimum: int | None = None) -> object:
    if kind is int and (isinstance(value, bool) or not isinstance(value, int)):
        msg = f"'{key}': expected an integer, got {value!r}."
        raise ValueError(msg)
    if kind is bool and not isinstance(value, bool):
        msg = f"'{key}': expected true or false, got {value!r}."
        raise ValueError(msg)
    if kind is list and not (isinstance(value, list) and all(isinstance(v, str) for v in value)):
        msg = f"'{key}': expected a list of strings, got {value!r}."
        raise ValueError(msg)
    if minimum is not None and value < minimum:
        msg = f"'{key}': must be >= {minimum}, got {value!r}."
        raise ValueError(msg)
    return value
```

## BUG-07 - Globs d'exclusion inopérants [Vérifié] - Haute

`_is_excluded` utilise `Path.match` (`cli.py:57`), ancré à droite et sans sémantique récursive pour `**`, alors que les overrides utilisent `full_match` (`config.py:231`). Deux sémantiques de glob coexistent.

```text
path                 pattern     Path.match  full_match
a/tests/x/y.py       tests/**    False       False
tests/x/y.py         tests/*     False       False
tests/x/y.py         tests/**    False       True
src/pkg/tests/y.py   tests       False       False   (mais exclu par la branche "littéral")
```

Conséquences : `--exclude "tests/**"` n'exclut rien ; un motif littéral `tests` exclut tout répertoire `tests` à n'importe quelle profondeur (`cli.py:60`), ce qui n'est pas documenté.

Correctif : une seule fonction de correspondance (celle de `ConfigOverride.matches`), utilisée pour `exclude` et `overrides`, et documentée.

## BUG-08 - Générateur imbriqué [Vérifié] - Haute

`is_generator` parcourt tout le sous-arbre avec `ast.walk` (`ast_parser.py:191`), y compris les fonctions et lambdas imbriquées.

```python
def outer_with_nested_generator(values: list[int]) -> list[int]:
    """Return the values.

    Args:
        values (list[int]): Values.

    Returns:
        list[int]: The values.

    """

    def gen() -> Iterator[int]:
        yield from values

    return list(gen())
```

```text
[returns_section] Generator function must use 'Yields:' instead of 'Returns:'.
[yields_section] Missing 'Yields:' section. Function contains a yield statement.
```

Même défaut dans `_self_attr_names` (`ast_parser.py:142`) : un `self.x = ...` dans une fonction imbriquée de `__init__` est compté comme attribut [Déduit].

Correctif : réutiliser le parcours élagué de `_extract_raises` (qui s'arrête déjà sur `FunctionDef`, `AsyncFunctionDef`, `Lambda`) et y ajouter `ClassDef`. Voir PERF-01 : un seul parcours peut collecter `raises` et `yields`.

## BUG-09 - `raise err` [Vérifié] - Haute

`_extract_raises` prend tout `ast.Name` comme type d'exception (`ast_parser.py:311-319`).

```python
def reraise(value: int) -> int:
    """...
    Raises:
        ValueError: If the value is invalid.
    """
    try:
        return int(value)
    except ValueError as err:
        raise err
```

```text
[raises_section] 'err' raised in code but not documented in 'Raises:'.
[raises_match] 'ValueError' documented in 'Raises:' but not raised in code.
```

Deux erreurs, dont une always-on, sur un code correct. `pydoclint` ne signale rien sur ce cas [Vérifié].

Correctif : mémoriser les noms liés par `except X as name` et remplacer `raise name` par `X` (ou l'ignorer si `X` est un tuple ou absent).

## BUG-10 - Exceptions pointées [Vérifié] - Haute

Côté code, seul `ast.Name` est reconnu (`ast_parser.py:313-316`) : `raise errors.ValidationError(...)` est invisible. Côté docstring, `RAISE_PATTERN = r"^\s{4}(\w+)\s*:..."` (`docstring_parser.py:68`) n'accepte pas `errors.ValidationError:`.

```text
[raises_match] 'ValidationError' documented in 'Raises:' but not raised in code.
```

Correctif : extraire `ast.Attribute` (nom complet via `ast.unparse`, comparaison sur le dernier segment), accepter `[\w.]+` dans le parser.

## BUG-11 - Exceptions propagées [Vérifié] - Moyenne

`raises_match` est always-on et exige que toute exception documentée soit levée *directement* dans le corps.

```python
def propagated(value: str) -> int:
    """...
    Raises:
        ValueError: Propagated from int().
    """
    return int(value)
```

```text
[raises_match] 'ValueError' documented in 'Raises:' but not raised in code.
```

Documenter les exceptions propagées est une pratique courante et utile à l'appelant. Aujourd'hui, c'est impossible sans exclure le fichier.

Correctif proposé : sortir la vérification "documenté mais non levé" dans une politique (`raises_extraneous = "forbidden" | "optional"`), défaut `optional`.

## BUG-12 - `(int, optional)` [Vérifié] - Critique

La comparaison de types est textuelle (`rules/args.py:89-90`). La forme `name (type, optional): ...`, très répandue en Google style (Napoleon la documente [Non vérifié]), produit une erreur always-on.

```text
[args_match] Arg 'limit' type mismatch: signature='int | None', docstring='int, optional'.
```

Mesure sur `rich` 15.0.0 : 520 "type mismatch", dont **372 contiennent `, optional`** et **318 sont équivalents** une fois `, optional` retiré (ou `Optional[X]` ramené à `X`).

`pydoclint` a le même défaut par défaut (DOC105) [Vérifié]. C'est donc une opportunité de différenciation.

Correctif : normaliser les deux côtés avant comparaison.

```python
# rules/args.py - compare types modulo cosmetic differences
import ast


def _normalize_type(text: str) -> str:
    text = text.strip()
    text = text.removesuffix(", optional").strip()
    try:
        node = ast.parse(text, mode="eval").body
    except SyntaxError:
        return text
    # String forward reference: 'Node' -> Node
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return _normalize_type(node.value)
    return ast.unparse(node)
```

Étape suivante : ramener `Optional[X]`, `Union[X, None]` et `X | None` à une forme unique, puis `List`/`list`, `Dict`/`dict`. À exposer par une option `type_matching = "strict" | "normalized" | "off"`.

## BUG-13 - Forward references [Vérifié] - Haute

`ast.unparse` conserve les guillemets d'une annotation chaîne (`ast_parser.py:184`, `ast_parser.py:229`).

```text
[args_match] Arg 'other' type mismatch: signature=''Node'', docstring='Node'.
[returns_match] Return type mismatch: signature=''Node'', docstring='Node'.
```

84 occurrences sur `rich`. Correctif : dans `_extract_args` et pour `node.returns`, si l'annotation est un `ast.Constant` de type `str`, prendre `.value`. Couvert par `_normalize_type` ci-dessus.

## BUG-14 - Règle `indentation` [Vérifié] - Haute

`check_indentation` (`rules/structure.py:16-43`) compte les indentations distinctes hors première ligne et échoue au-delà de 2. Une section (`0`), une entrée (`4`) et une ligne de continuation (`8`) suffisent.

```python
def multiline_arg(value: int) -> int:
    """Return the value.

    Args:
        value (int): A long description that wraps
            onto a second line.

    Returns:
        int: The value.

    """
```

```text
[indentation] Inconsistent indentation in docstring.
```

62 occurrences sur `rich`. Le projet lui-même n'est pas touché car `line-length = 200` évite les continuations.

Correctif : vérifier que chaque indentation est multiple de 4 et cohérente avec la structure (en-têtes à 0, entrées à 4, continuations >= 8), ou retirer la règle, le docstring étant déjà nettoyé par `inspect.cleandoc`.

## BUG-15 - `def` sous `if` / `try` / `with` [Vérifié] - Haute

`_walk_body` ne descend que dans `ClassDef` (`ast_parser.py:64-70`).

```python
if sys.version_info >= (3, 12):

    def hidden_in_if(x):
        return x
```

Aucune erreur (ni docstring, ni annotation). Cas courants concernés : `if TYPE_CHECKING:`, `try: ... except ImportError:`, `if sys.version_info`, `if __name__ == "__main__":`.

Correctif :

```python
# ast_parser.py - also walk compound statements that are not new scopes
_BLOCKS = (ast.If, ast.Try, ast.TryStar, ast.With, ast.AsyncWith, ast.For, ast.AsyncFor, ast.While)

for node in body:
    if isinstance(node, ast.ClassDef):
        ...
    elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        ...
    elif isinstance(node, _BLOCKS):
        for block in (getattr(node, "body", []), getattr(node, "orelse", []), getattr(node, "finalbody", [])):
            _walk_body(block, filepath, entities, parent_class)
        for handler in getattr(node, "handlers", []):
            _walk_body(handler.body, filepath, entities, parent_class)
```

Les fonctions imbriquées dans des fonctions restent non analysées : c'est un choix défendable, mais à documenter (voir DOC-07) ou à rendre optionnel (`docsig --check-nested` le propose [Vérifié]).

## BUG-16 - `self` / `cls` par nom [Vérifié] - Moyenne

`skip = {"self", "cls"}` (`ast_parser.py:218`) s'applique à toutes les fonctions, par nom.

```python
class Meta(type):
    def __new__(mcs, name: str, bases: tuple[type, ...], ns: dict[str, object]) -> "Meta": ...
```

```text
[args_section] Arg 'mcs' in signature but not documented.
[args_order] Args order in docstring differs from signature. Expected: mcs, name, bases, ns. Got: name, bases, ns.
```

À l'inverse, une fonction de module avec un paramètre `cls`, ou un `@staticmethod` avec un paramètre `self`, perdent ce paramètre [Déduit].

Correctif : pour une méthode non `@staticmethod`, ignorer le premier paramètre positionnel quel que soit son nom ; ne rien ignorer pour une fonction de module. Nécessite de conserver les décorateurs (voir ARCH-07).

## BUG-17 - Heuristique d'impératif [Vérifié] - Moyenne

`_to_imperative` (`rules/docstring.py:151-180`) retire un `s` final :

```text
Does -> Doe      Goes -> Goe      Settings -> Setting      Bytes -> Byte
Uses -> Use      Parses -> Parse  Returns -> Return        Has -> (exception)
```

"Does"/"Goes" produisent une suggestion fausse ; les noms au pluriel en tête de résumé ("Settings for...") sont signalés. 68 erreurs `imperative_mood` sur `rich`.

Correctifs : table de verbes irréguliers (`does -> do`, `goes -> go`, `has -> have`, `is -> be`) ; ne signaler que si la forme proposée appartient à une liste de verbes connus (approche d'une liste blanche, utilisée par pydocstyle D401 [Non vérifié]).

## BUG-18 - Sections Napoleon à deux mots [Vérifié] - Moyenne

`CANDIDATE_SECTION_PATTERN = r"^([A-Z][A-Za-z]*):\s*$"` (`docstring_parser.py:63`) ne reconnaît qu'un mot. `Keyword Args:`, `See Also:`, `Other Parameters:` sont silencieusement fusionnés dans la description ou la section précédente.

```python
def kwargs_section(**kwargs: int) -> None:
    """Accept keyword arguments.

    Keyword Args:
        width (int): Width.

    Warning:
        Experimental.

    See Also:
        Something else.
    """
```

```text
[args_section] Arg '**kwargs' in signature but not documented.
[unknown_section] Unknown section 'Warning'.
```

`See Also:` et `Keyword Args:` ne sont ni reconnus ni signalés. `Warning:` est une section Napoleon standard [Non vérifié].

Correctif : reconnaître les en-têtes multi-mots ; décider pour chaque alias Napoleon (`Arguments`, `Parameters`, `Keyword Args`, `Warning(s)`, `See Also`, `References`, `Methods`) s'il est accepté, signalé comme alias (`Use 'Args:'`) ou inconnu. Accepter `Keyword Args:` comme documentation de `**kwargs`.

## BUG-19 - `Returns:` sans préfixe de type [Vérifié] - Haute

Le guide Google montre `Returns:` suivi d'une phrase, sans `type:` quand la signature est annotée [Non vérifié]. Ici, c'est une erreur always-on (`rules/args.py:229-230`).

```python
def google_guide_returns(value: int) -> int:
    """Return the value.

    Args:
        value (int): The value.

    Returns:
        The value unchanged.

    """
```

```text
[returns_match] Missing type in 'Returns:'. Expected 'int'.
```

Correctif : étendre `documented_types` (aujourd'hui limité à `Args:` et `Attributes:`) aux lignes `Returns:`/`Yields:`, ou ajouter `returns_types = "required" | "forbidden" | "optional"`.

## BUG-20 - Parsing de `Returns:` [Vérifié] - Basse

`RETURN_PATTERN = r"^\s{4}([^:]+?)\s*:\s*(.*)$"` (`docstring_parser.py:67`) prend tout ce qui précède le premier `:` comme type, et `_parse_returns` s'arrête à la première ligne.

```python
GoogleStyleParser().parse("Do it.\n\nReturns:\n    The mapping: key to value,\n        spanning two lines.\n").returns
# DocstringReturn(type_annotation='The mapping', description='key to value,')
```

Effet : type mismatch always-on sur une phrase contenant `:` ; description tronquée.

Correctif : n'accepter comme type qu'une expression parsable par `ast.parse(..., mode="eval")` ; concaténer les lignes de continuation comme pour `Args:`.

## BUG-21 - `@overload` [Vérifié] - Moyenne

```python
@overload
def conv(x: int) -> int: ...
@overload
def conv(x: str) -> str: ...
def conv(x: int | str) -> int | str:
    """Convert the value. ..."""
```

```text
L7  conv [docstring_exists] Missing docstring.
L9  conv [docstring_exists] Missing docstring.
```

Correctif : ignorer les fonctions décorées `@overload` / `@typing.overload`. Voir UX-04 pour `@property`, `@override`, dunders.

## BUG-22 - Annotations GitHub non échappées [Déduit] - Basse

`reporter.py:163` écrit `::error file=...,line=...,title=...::{message}` sans échappement. La documentation des workflow commands demande d'échapper `%`, `\r`, `\n` dans le message, et en plus `:` et `,` dans les propriétés [Non vérifié]. Les messages de `summary_final_period` incluent un extrait du résumé utilisateur (`Got: '...'`), donc un `%` ou un retour ligne peut y apparaître.

```python
# reporter.py - escape per GitHub workflow command rules
def _escape_data(text: str) -> str:
    return text.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")


def _escape_property(text: str) -> str:
    return _escape_data(text).replace(":", "%3A").replace(",", "%2C")
```

## BUG-23 - Pluriel [Vérifié] - Basse

`reporter.py:57`, `:76`, `:95`, `:115`, `:168-170` : "1 files checked".

---

## Annexe - fichiers de reproduction

Sorties obtenues avec `docstring-linter <fichier> --config /nonexistent --format text`. Les fichiers ne sont pas versionnés en `.py` pour ne pas être pris par les hooks pyright/ruff du dépôt.

Suggestion : les ajouter dans `tests/fixtures/` avec les erreurs attendues, comme tests de bout en bout (voir ARCH-10).

<details>
<summary>cases.py</summary>

```python
"""Edge cases for review."""

import sys
from collections.abc import Callable, Iterator

import requests_like as errors


def optional_arg(limit: int | None = None) -> int:
    """Return the limit.

    Args:
        limit (int, optional): Maximum value.

    Returns:
        int: The limit.

    """
    return limit or 0


def multiline_arg(value: int) -> int:
    """Return the value.

    Args:
        value (int): A long description that wraps
            onto a second line.

    Returns:
        int: The value.

    """
    return value


def google_guide_returns(value: int) -> int:
    """Return the value.

    Args:
        value (int): The value.

    Returns:
        The value unchanged.

    """
    return value


def outer_with_nested_generator(values: list[int]) -> list[int]:
    """Return the values.

    Args:
        values (list[int]): Values.

    Returns:
        list[int]: The values.

    """

    def gen() -> Iterator[int]:
        yield from values

    return list(gen())


def reraise(value: int) -> int:
    """Return the value.

    Args:
        value (int): The value.

    Returns:
        int: The value.

    Raises:
        ValueError: If the value is invalid.

    """
    try:
        return int(value)
    except ValueError as err:
        raise err


def dotted_raise(value: int) -> int:
    """Return the value.

    Args:
        value (int): The value.

    Returns:
        int: The value.

    Raises:
        ValidationError: If invalid.

    """
    if value < 0:
        raise errors.ValidationError("negative")
    return value


def propagated(value: str) -> int:
    """Convert the value.

    Args:
        value (str): The value.

    Returns:
        int: The value.

    Raises:
        ValueError: Propagated from int().

    """
    return int(value)


def forward_ref(other: "Node") -> "Node":
    """Return the node.

    Args:
        other (Node): The node.

    Returns:
        Node: The node.

    """
    return other


def does_things() -> None:
    """Does the thing.

    Returns:
        None

    """


if sys.version_info >= (3, 12):

    def hidden_in_if(x):
        return x


class Node:
    """Store a node.

    Attributes:
        value (int): The value.

    """

    def __init__(self, value: int) -> None:
        """Build the node.

        Args:
            value (int): The value.

        """
        self.value = value
        self._cache = None

    def __repr__(self) -> str:
        return "Node"

    @property
    def size(self) -> int:
        """The size of the node."""
        return 1


def kwargs_section(**kwargs: int) -> None:
    """Accept keyword arguments.

    Keyword Args:
        width (int): Width.

    Warning:
        Experimental.

    See Also:
        Something else.

    Returns:
        None

    """
```

</details>

<details>
<summary>more.py</summary>

```python
"""More cases."""

from typing import overload


@overload
def conv(x: int) -> int: ...
@overload
def conv(x: str) -> str: ...
def conv(x: int | str) -> int | str:
    """Convert the value.

    Args:
        x (int | str): Value.

    Returns:
        int | str: Converted value.

    """
    return x


class Base:
    """Define the base."""

    def run(self, value: int) -> int:
        """Run the job.

        Args:
            value (int): Value.

        Returns:
            int: Result.

        Raises:
            NotImplementedError: Always, subclasses implement it.

        """
        raise NotImplementedError


class Child(Base):
    """Define the child."""

    def run(self, value: int) -> int:  # inherits documentation
        return value


class Meta(type):
    """Define the metaclass."""

    def __new__(mcs, name: str, bases: tuple[type, ...], ns: dict[str, object]) -> "Meta":
        """Create the class.

        Args:
            name (str): Name.
            bases (tuple[type, ...]): Bases.
            ns (dict[str, object]): Namespace.

        Returns:
            Meta: New class.

        """
        return super().__new__(mcs, name, bases, ns)
```

</details>
