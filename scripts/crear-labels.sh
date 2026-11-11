#!/usr/bin/env bash
# Crea las etiquetas del proyecto. Requiere GitHub CLI autenticado (gh auth login).
# Uso: ./scripts/crear-labels.sh OWNER/REPO
set -e
REPO="${1:?Uso: $0 OWNER/REPO}"
mk() { gh label create "$1" --color "$2" --description "$3" --repo "$REPO" --force; }
mk epic                 6f42c1 "Épica"
mk user-story           0e8a16 "Historia de usuario"
mk tech-story           1d76db "Historia técnica"
mk RF                   fbca04 "Requerimiento funcional"
mk RNF                  d93f0b "Requerimiento no funcional"
mk bug                  b60205 "Defecto"
mk acta                 c5def5 "Acta de ceremonia"
mk cambio-de-diseño     e99695 "Altera el diseño original"
mk requirement-request  f9d0c4 "Solicitud de requerimiento entre grupos"
mk prioridad-alta       b60205 "Prioridad alta"
mk prioridad-media      fbca04 "Prioridad media"
mk prioridad-baja       0e8a16 "Prioridad baja"
echo "Etiquetas creadas en $REPO"
