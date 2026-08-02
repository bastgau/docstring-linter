# TODO

Les priorités sont notées de 1 (faible) à 10 (haute).

## Nouvelles règles

- [x] `args_order` -- vérifier que l'ordre des args dans `Args:` correspond à l'ordre de la signature -- **7**
- [x] `unknown_section` -- signaler une section non reconnue (ex: `Argument:` au lieu de `Args:`) -- **7**
- [x] `duplicate_arg` -- détecter un argument documenté deux fois dans `Args:` -- **6**
- [x] `multiline_summary` -- interdire une summary qui s'étale sur plusieurs lignes -- **5**
  Couvert par le parser, qui coupe le résumé à la première ligne, et par `blank_lines` qui exige la ligne vide avant la description.
- [x] `raises_description` -- exiger une description dans chaque entrée `Raises:` -- **4**
  Couvert par `raises_match`.
- [x] `entry_spacing` -- imposer la forme `name (type): description` dans `Args:`, `Attributes:` et `Raises:` -- **6**

- [x] `return_description` -- exiger une description dans `Returns:` (pas seulement un type) -- **4**
  Couvert par `returns_descriptions`, qui gouverne `Returns:` et `Yields:`. La description des entrées `Args:`, `Attributes:` et `Raises:` reste toujours obligatoire. `Returns: None` est exempté.
- [ ] `description_too_long` -- limiter la longueur des lignes de description (configurable, comme `summary_too_long`) -- **5**
- [ ] `no_trailing_whitespace` -- interdire les espaces en fin de ligne dans la docstring -- **4**

## CLI / config

- [x] Format de sortie `traceback` -- en-tête cliquable `File "path", line N, in entity` -- **7**
- [x] Rejeter les clés de configuration inconnues -- **9**
  Clé inconnue au niveau racine, dans `[scope]` ou dans un override, nom de règle inconnu dans `select` / `ignore`, règle always-on dans `ignore`, valeur de `style` ou de policy invalide : erreur sur stderr et code de sortie 2 avant toute lecture de fichier.
- [x] Configuration par répertoire -- `[[tool.docstring-linter.overrides]]` avec `paths` -- **7**
  Globs `full_match`, dernier bloc correspondant gagnant, `ignore` retire et `select` remplace, `scope.*` et les réglages d'exécution refusés dans un override.
- [ ] `--quiet` -- n'afficher que les erreurs, supprimer le résumé et la config -- **5**
- [ ] `--watch` -- relancer automatiquement sur les fichiers modifiés -- **3**

## Parser

- [ ] Entrée `Raises:` réduite à un identifiant nu, sans deux-points -- **3**
  `RuntimeError` seul n'est pas reconnu comme une entrée et remonte en « non documenté ». L'accepter ferait passer toute ligne de continuation d'un seul mot pour une exception.
- [ ] `no_blank_line_in_section` travaille ligne à ligne -- **3**
  La règle ne distingue pas le début d'une entrée d'une ligne de continuation, ce qui interdit d'en faire un compteur configurable comme `blank_lines`.

## Documentation

- [ ] Décider du sort de `RULES.md` -- **6**
  Seule documentation des 11 règles always-on, absentes de `--list-rules`. Piste : générer l'ossature depuis `RULES_REGISTRY`, `POLICIES_REGISTRY` et `OPTIONS_REGISTRY`, ne garder à la main que les exemples.
- [ ] Décider du sort de `TESTS.md` -- **6**
  301 lignes sur 313 sont la copie exacte du docstring du test. Piste : générer, et vérifier dans `lint-tests.sh` que le fichier commité correspond.
- [ ] Aligner la version -- **5**
  `pyproject.toml` déclare `0.1.0`, les tags vont jusqu'à `v0.5.0`, `README.md` référence `v0.1.0` dans les exemples pre-commit et GitHub Action.

## Intégration

- [ ] Sortie SARIF -- format standard pour les annotations de PR GitHub -- **6**
- [x] Hook pre-commit prêt à l'emploi -- `.pre-commit-hooks.yaml` + testé via `.pre-commit-config-hook.yaml` dans CI -- **8**
- [ ] Plugin VS Code -- afficher les erreurs inline dans l'éditeur -- **7**
- [x] GitHub Action -- action prête à l'emploi pour les workflows CI -- `action.yml` + `.github/workflows/` -- **8**
- [ ] Badge de couverture docstring -- pourcentage de fonctions correctement documentées -- **5**
