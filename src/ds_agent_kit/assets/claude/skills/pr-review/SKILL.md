---
name: pr-review
description: Revisa o PR/branch atual antes do merge — roda ruff e pytest localmente e delega a revisão do diff ao agente code-reviewer. Use quando o usuário pedir para revisar o PR, a branch ou "ver se está pronto para merge".
---

# Revisão de PR

1. Confirme que a branch atual segue `feature/<nome>` (`git branch --show-current`). Se não, avise.
2. Rode os mesmos checks do CI:
   - `uv run ruff check .`
   - `uv run ruff format --check .`
   - `uv run pytest -q`
3. Use o agente `code-reviewer` sobre `git diff origin/main...HEAD`.
4. Responda com: status dos checks (passou/falhou + saída relevante) e os achados do revisor,
   do mais grave para o menos grave.
