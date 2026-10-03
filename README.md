# ds-agent-kit

CLI (`dskit`) que leva para qualquer repositório:

- **skills e agentes do Claude Code** (`.claude/skills`, `.claude/agents`);
- **regras de GitHub**: ruleset que protege a `main` (PR obrigatório + checks `lint`, `test`, `branch-name`);
- **bootstrap de projetos** a partir do `ds-project-template`.

## Instalação

```bash
# direto do GitHub (recomendado)
uv tool install git+https://github.com/<seu-usuario>/ds-agent-kit

# atualizar depois
uv tool upgrade ds-agent-kit
```

Pré-requisitos: [uv](https://docs.astral.sh/uv/) e [GitHub CLI](https://cli.github.com) autenticado (`gh auth login`).

## Uso

```bash
dskit list                       # mostra skills/agentes incluídos
dskit install [caminho]          # copia para <caminho>/.claude (não sobrescreve sem --force)
dskit protect [--repo dono/repo] # aplica o ruleset protect-main + só squash merge
dskit new meu-projeto [--private] [--template dono/ds-project-template]
                                 # cria repo do template, instala skills, protege a main
```

## O que vem incluído

| Tipo   | Nome            | Para quê                                                     |
|--------|-----------------|--------------------------------------------------------------|
| agente | `code-reviewer` | revisão de diffs de DS (bugs, data leakage, reprodutibilidade) |
| skill  | `pr-review`     | roda ruff + pytest e chama o `code-reviewer` no diff da branch |
| skill  | `ds-eda`        | EDA padronizada em `notebooks/` + `reports/figures/`          |

Para adicionar novos, crie arquivos em `src/ds_agent_kit/assets/claude/{skills,agents}/`.
Tudo nessa pasta é copiado por `dskit install`.

## Desenvolvimento

```bash
uv sync
uv run ruff check . && uv run ruff format --check .
uv run pytest
uv run dskit --help
```

Este repo segue as mesmas regras do template: só merge na `main` via PR de `feature/*` com CI verde.
