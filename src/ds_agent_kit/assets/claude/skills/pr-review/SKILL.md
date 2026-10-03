---
name: pr-review
description: Revisa o PR/branch atual antes do merge — roda os mesmos checks do CI localmente e delega a revisão do diff ao agente code-reviewer. Use quando o usuário pedir para revisar o PR, a branch ou "ver se está pronto para merge".
---

# Revisão de PR

1. Confirme que a branch atual segue `<tipo>/<descricao>` com tipo em
   feature, fix, hotfix, refactor, experiment, docs, chore, test, ci (`git branch --show-current`).
   Se não seguir, avise — o check `ci / branch-name` vai falhar.
2. Rode os mesmos checks do CI:
   - se existir `Makefile` com alvo `ci`: `make ci` (pre-commit + pytest + conformidade);
   - senão: `uv run pre-commit run --all-files` e `uv run pytest -q`.
3. Use o agente `code-reviewer` sobre `git diff origin/main...HEAD`.
4. Responda com: status de cada check (passou/falhou + saída relevante) e os achados do revisor,
   do mais grave para o menos grave.
