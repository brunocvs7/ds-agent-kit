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

Rode dentro da raiz do projeto (ou passe `--path`):

```bash
dskit list                          # o que o kit oferece e o status no projeto

dskit add --all                     # todas as skills e todos os agentes
dskit add --skills                  # só as skills
dskit add --agents                  # só os agentes
dskit add pr-review code-reviewer   # itens específicos
dskit add skill:pr-review           # prefixo skill:/agent: se houver nome repetido

dskit remove ds-eda                 # remove um item
dskit remove --agents               # remove todos os agentes do kit
dskit remove --all                  # remove tudo que veio do kit
```

Status no `dskit list`:

| Status | Significado |
|---|---|
| `instalado` | igual à versão do kit |
| `modificado` | existe no projeto, mas difere do kit (você editou, ou o kit foi atualizado) |
| `não instalado` | não está no projeto |

- `add` não sobrescreve itens `modificado` — use `--force` para trocar pela versão do kit.
  Para atualizar tudo depois de um `uv tool upgrade ds-agent-kit`: `dskit add --all --force`.
- `remove` só apaga itens que existem no kit. Skills/agentes criados por você e outros arquivos
  de `.claude/` (ex.: `settings.json`) nunca são tocados.

## O que vem incluído

| Tipo   | Nome            | Para quê                                                     |
|--------|-----------------|--------------------------------------------------------------|
| agente | `code-reviewer` | revisão de diffs de DS (bugs, data leakage, reprodutibilidade) |
| skill  | `pr-review`     | roda `make ci` e chama o `code-reviewer` no diff da branch |
| skill  | `ds-eda`        | EDA padronizada em `notebooks/` + `reports/figures/`          |

Para adicionar novos, crie arquivos em `src/ds_agent_kit/assets/claude/{skills,agents}/`.
Skill = uma pasta com `SKILL.md`; agente = um arquivo `<nome>.md`. Eles aparecem no `dskit list` automaticamente.

## Desenvolvimento

```bash
uv sync
uv run pre-commit install
uv run pytest
uv run dskit list
```

Este repo usa o CI do `ds-workflows` (sem a etapa de conformidade): só merge na `main` via PR de `<tipo>/<descricao>` com CI verde.
