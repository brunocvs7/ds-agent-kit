---
name: add-dependency
description: Adiciona um pacote Python ao projeto com uv, no grupo certo (aplicação ou dev). Use quando o usuário pedir para instalar, adicionar ou usar uma biblioteca nova.
---

# Adicionar dependência

1. Decida o grupo:
   - usada em `src/` (roda em produção) → `uv add <pacote>`
   - usada só em notebooks, testes ou ferramentas → `uv add --dev <pacote>`
2. Nunca use `pip install`.
3. Confira que `pyproject.toml` e `uv.lock` mudaram juntos (`git status`).
4. Informe o pacote, a versão resolvida e o grupo escolhido.
