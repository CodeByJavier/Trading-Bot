#!/usr/bin/env bash
# Guarda en el repositorio los archivos indicados, sin chocar con otras ejecuciones.
#
# Uso: bash .github/guardar.sh "mensaje del commit" ruta1 ruta2 ...
#
# Si otra ejecución guardó justo antes, se trae sus cambios y vuelve a intentarlo. Si los cambios
# chocan (las dos tocaron el mismo estado), se descarta esta ejecución sin marcarla como fallo:
# la siguiente parte del estado más reciente y repite el trabajo.
set -u
mensaje="$1"
shift
git config user.name "bot-trading"
git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
for ruta in "$@"; do
  if [ -e "$ruta" ]; then git add -A "$ruta"; fi
done
if git diff --cached --quiet; then
  echo "Nada nuevo que guardar."
  echo "cambios=false" >> "$GITHUB_OUTPUT"
  exit 0
fi
git commit -q -m "$mensaje"
for intento in 1 2 3; do
  if git push -q; then
    echo "Guardado (intento $intento)."
    echo "cambios=true" >> "$GITHUB_OUTPUT"
    exit 0
  fi
  if ! git pull -q --rebase; then
    git rebase --abort
    echo "Otra ejecución guardó antes el mismo estado: esta se descarta; la siguiente lo repetirá."
    echo "cambios=false" >> "$GITHUB_OUTPUT"
    exit 0
  fi
done
echo "No se pudo guardar tras 3 intentos; la siguiente ejecución lo repetirá."
echo "cambios=false" >> "$GITHUB_OUTPUT"
