# TODO

Les priorités sont notées de 1 (faible) à 10 (haute).

## Nouvelles règles

- [x] `param_order` -- vérifier que l'ordre des args dans `Args:` correspond à l'ordre de la signature -- **7**
- [x] `unknown_section` -- signaler une section non reconnue (ex: `Argument:` au lieu de `Args:`) -- **7**
- [x] `duplicate_arg` -- détecter un argument documenté deux fois dans `Args:` -- **6**

- [ ] `description_too_long` -- limiter la longueur des lignes de description (configurable, comme `summary_too_long`) -- **5**
- [ ] `no_trailing_whitespace` -- interdire les espaces en fin de ligne dans la docstring -- **4**
- [ ] `multiline_summary` -- interdire une summary qui s'étale sur plusieurs lignes -- **5**
- [ ] `return_description` -- exiger une description dans `Returns:` (pas seulement un type) -- **4**
- [ ] `raises_description` -- exiger une description dans chaque entrée `Raises:` -- **4**

## CLI / config

- [ ] `--quiet` -- n'afficher que les erreurs, supprimer le résumé et la config -- **5**
- [ ] `--watch` -- relancer automatiquement sur les fichiers modifiés -- **3**

## Intégration

- [ ] Sortie SARIF -- format standard pour les annotations de PR GitHub -- **6**
- [x] Hook pre-commit prêt à l'emploi -- `.pre-commit-hooks.yaml` + testé via `.pre-commit-config-hook.yaml` dans CI -- **8**
- [ ] Plugin VS Code -- afficher les erreurs inline dans l'éditeur -- **7**
- [x] GitHub Action -- action prête à l'emploi pour les workflows CI -- `action.yml` + `.github/workflows/` -- **8**
- [ ] Badge de couverture docstring -- pourcentage de fonctions correctement documentées -- **5**
