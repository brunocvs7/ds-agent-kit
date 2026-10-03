# ds-agent-kit

CLI (`dskit`) que instala **skills e agentes do Claude Code** (`.claude/skills`, `.claude/agents`)
em qualquer repositório.

> CI e proteção de branch não ficam aqui — ficam em [`ds-workflows`](https://github.com/brunocvs7/ds-workflows).
> O esqueleto de projeto fica em [`ds-project-template`](https://github.com/brunocvs7/ds-project-template).

## Instalação

```bash
# direto do GitHub (recomendado)
uv tool install git+https://github.com/brunocvs7/ds-agent-kit

# atualizar depois
uv tool upgrade ds-agent-kit
```

Pré-requisito: [uv](https://docs.astral.sh/uv/).

## Uso

```bash
dskit list                       # mostra skills/agentes incluídos
dskit install [caminho]          # copia para <caminho>/.claude (não sobrescreve sem --force)
dskit install --force            # atualiza para a versão mais nova das skills
```

## O que vem incluído

| Tipo   | Nome            | Para quê                                                     |
|--------|-----------------|--------------------------------------------------------------|
| agente | `code-reviewer` | revisão de diffs de DS (bugs, data leakage, reprodutibilidade) |
| skill  | `pr-review`     | roda `make ci` e chama o `code-reviewer` no diff da branch |
| skill  | `ds-eda`        | EDA padronizada em `notebooks/` + `reports/figures/`          |

Para adicionar novos, crie arquivos em `src/ds_agent_kit/assets/claude/{skills,agents}/`.
Tudo nessa pasta é copiado por `dskit install`.

## Desenvolvimento

```bash
uv sync
uv run pre-commit install
uv run pytest
uv run dskit --help
```

Este repo usa o CI do `ds-workflows` (sem a etapa de conformidade): só merge na `main` via PR de `<tipo>/<descricao>` com CI verde.
