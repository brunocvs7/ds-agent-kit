---
name: run-checks
description: Roda localmente os mesmos checks do CI (lint, testes e conformidade) e resume o resultado. Use antes de abrir um PR ou quando o usuário perguntar se o código vai passar no CI.
---

# Rodar checks

1. Rode `make ci`. Se não houver Makefile, rode `uv run pre-commit run --all-files` e `uv run pytest -q`.
2. Se o pre-commit corrigir arquivos sozinho, rode de novo para confirmar que passou.
3. Responda com uma linha por etapa (lint, test, check): ✅ ou ❌. Para cada ❌, mostre só o trecho
   relevante do erro e sugira a correção.
