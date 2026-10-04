---
name: new-branch
description: Cria uma branch de trabalho no padrão <tipo>/<descricao> a partir da main atualizada. Use quando o usuário pedir para começar uma tarefa, feature, correção ou experimento.
---

# Nova branch

1. Escolha o tipo pela intenção: feature, fix, hotfix, refactor, experiment, docs, chore, test ou ci.
   Se não estiver claro, pergunte.
2. Monte a descrição em kebab-case, minúsculas, sem acentos (ex.: `feature/modelo-churn`).
3. Rode:
   ```bash
   git switch main && git pull --ff-only
   git switch -c <tipo>/<descricao>
   ```
4. Confirme o nome da branch criada.
