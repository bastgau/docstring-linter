# 03 - Performance

## Conclusion

La performance **n'est pas un problème** aujourd'hui : l'outil est 2,4x plus rapide que pydoclint sur le même corpus. Les gains possibles existent (x2 sur l'extraction AST) mais passent après la justesse. Le principal levier coïncide avec le correctif de BUG-08 : une passe AST unique par fonction.

## Mesures [Vérifié]

Machine : conteneur Linux, 4 CPU, Python 3.14.7. Temps "real" de `time`, cache disque chaud, une exécution.

| Corpus | Outil | Temps |
|---|---|---|
| stdlib CPython 3.14 (1 059 fichiers, 18 Mo) | docstring-linter `--workers 1` | 4,58 s |
| idem | docstring-linter `--workers 0` (4 process) | 1,90 s |
| idem | ruff `--select D,DOC --preview --no-cache` | 0,46 s |
| `rich` 15.0.0 (100 fichiers, 38 515 lignes) | docstring-linter `--workers 1` | 0,41 s |
| idem | pydoclint 0.9.1 `--style=google` | 0,99 s |
| idem | docsig 0.96.0 | 2,23 s |
| idem | ruff `--select D,DOC --preview --no-cache` | 0,04 s |
| 1 fichier trivial | docstring-linter (démarrage) | 0,08 s |

Débit séquentiel : environ 4,3 ms par fichier sur la stdlib.

Attention : les outils ne vérifient pas la même chose (voir 07). La comparaison donne un ordre de grandeur, pas un classement.

## Profil [Vérifié]

`cProfile` sur la stdlib, séquentiel (16 s sous profilage, surcoût de l'instrumentation inclus) :

| Poste | Temps cumulé | Part |
|---|---|---|
| `parse_file` (lecture, `ast.parse`, extraction) | 14,1 s | 88 % |
| dont `compile` (`ast.parse`) | 1,5 s | 9 % |
| dont `_extract_raises` | 5,3 s | 33 % |
| dont détection `is_generator` (`ast.walk`) | 5,4 s | 34 % |
| `validate_entity` (toutes les règles) | 1,2 s | 7 % |

`ast.iter_child_nodes` est appelé 5,5 millions de fois. Chaque fonction est parcourue intégralement **deux fois** (`_extract_raises` puis `ast.walk` pour `yield`), plus une troisième fois pour `__init__` (`_self_attr_names`).

Les règles, bien qu'elles re-découpent chacune le docstring (ARCH-03), ne pèsent que 7 %.

## Constats

### PERF-01 - Double parcours AST par fonction [Vérifié] - Moyenne

`ast_parser.py:185` (`_extract_raises`) et `ast_parser.py:191` (`is_generator`) parcourent le même sous-arbre. Le second descend en plus dans les fonctions imbriquées (BUG-08).

Proposition : le `_BodyScanner` d'ARCH-01, qui collecte `raises` et `yields` en une passe et s'arrête aux portées imbriquées. Gain attendu : environ la moitié du temps d'extraction, soit 30 à 35 % du temps total [Déduit du profil, non mesuré].

Mise à jour après le lot 3 [Vérifié] : le parcours unique élagué (`_scan_body`) est en place. Gain mesuré sur la stdlib, 3 exécutions alternées : 4,76 s en moyenne avant, 4,46 s après, soit environ 6 %, dans le bruit de mesure. L'estimation ci-dessus était fausse : le surcoût d'instrumentation de cProfile gonflait la part des appels `ast.iter_child_nodes`. La performance reste sans enjeu.

### PERF-02 - `workers = 1` par défaut [Vérifié] - Basse

Le mode auto donne 2,4x sur 4 CPU pour la stdlib. Pour pre-commit (quelques fichiers), le séquentiel reste préférable à cause du coût de démarrage des process.

Proposition : défaut `0` (auto) avec un seuil, par exemple parallèle seulement au-delà de 50 fichiers.

```python
# cli.py - only pay the process pool start-up cost on large runs
_PARALLEL_THRESHOLD = 50

if workers <= 1 or len(files) < _PARALLEL_THRESHOLD:
    ...
```

### PERF-03 - Soumission fichier par fichier [Déduit] - Basse

`pool.submit` par fichier (`cli.py:187`) sérialise `LinterConfig` pour chaque tâche et crée un futur par fichier. `pool.map(..., chunksize=16)` réduirait les échanges inter-process. Gain probablement marginal au regard de PERF-01.

### PERF-04 - Parcours des répertoires exclus [Vérifié] - Basse

`collect_python_files` fait `rglob("*.py")` puis filtre (`cli.py:40`) : les répertoires exclus (`.venv`, `node_modules`, ...) sont quand même parcourus. Sur ce dépôt, `.venv` contient 933 fichiers `.py` et le surcoût mesuré est de 0,02 s (0,205 s pour `.` contre 0,180 s pour `src tests example`). Négligeable ici, sensible sur un monorepo.

Proposition : `os.walk` avec élagage de `dirnames` sur les motifs d'exclusion, et option de respect du `.gitignore` (comportement de ruff [Non vérifié]).

### PERF-05 - Pas de cache [Déduit] - Basse

ruff met en cache les résultats par fichier. Pour ce linter, le temps actuel ne le justifie pas. À réévaluer seulement si l'outil vise des monorepos de plusieurs dizaines de milliers de fichiers.

### PERF-06 - Python 3.14 free-threaded [Non vérifié] - Basse

Sur un build free-threaded, un `ThreadPoolExecutor` éviterait le coût de démarrage et la sérialisation. Piste exploratoire uniquement, pas prioritaire.

## Méthode de reproduction

```bash
# Timing
time docstring-linter "$(python -c 'import sysconfig;print(sysconfig.get_paths()["stdlib"])')" \
  --workers 1 --format json --config /nonexistent > /dev/null

# Profile
python - <<'EOF'
import cProfile, contextlib, io, pstats, sys, sysconfig
sys.argv = ["docstring-linter", sysconfig.get_paths()["stdlib"], "--format", "json", "--config", "/nonexistent"]
from linter.cli import main
profiler = cProfile.Profile()
with contextlib.redirect_stdout(io.StringIO()):
    profiler.enable()
    try:
        main()
    except SystemExit:
        pass
    profiler.disable()
pstats.Stats(profiler).sort_stats("tottime").print_stats(15)
EOF
```

Suggestion : ajouter un script `scripts/benchmark.sh` sur un corpus figé pour suivre l'évolution.
