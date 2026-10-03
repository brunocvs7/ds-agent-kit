"""CLI `dskit`: instala skills/agentes do Claude Code e aplica regras de GitHub em repos."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from importlib.resources import as_file, files
from importlib.resources.abc import Traversable
from pathlib import Path

ASSETS = files("ds_agent_kit") / "assets"
RULESET_NAME = "protect-main"
DEFAULT_TEMPLATE = "ds-project-template"


def _walk(node: Traversable, prefix: Path = Path()) -> list[tuple[Path, Traversable]]:
    """Lista recursivamente (caminho relativo, recurso) de todos os arquivos de um diretório."""
    out: list[tuple[Path, Traversable]] = []
    for child in node.iterdir():
        rel = prefix / child.name
        if child.is_dir():
            out.extend(_walk(child, rel))
        else:
            out.append((rel, child))
    return sorted(out, key=lambda item: str(item[0]))


def bundled_claude_files() -> list[tuple[Path, Traversable]]:
    return _walk(ASSETS / "claude")


def install(target: Path, force: bool = False) -> tuple[list[Path], list[Path]]:
    """Copia assets/claude/** para <target>/.claude/. Retorna (copiados, pulados)."""
    dest_root = target / ".claude"
    copied: list[Path] = []
    skipped: list[Path] = []
    for rel, resource in bundled_claude_files():
        dest = dest_root / rel
        if dest.exists() and not force:
            skipped.append(dest)
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        with as_file(resource) as src:
            shutil.copyfile(src, dest)
        copied.append(dest)
    return copied, skipped


def _gh(*args: str, input_data: str | None = None) -> str:
    if shutil.which("gh") is None:
        sys.exit("Erro: GitHub CLI (gh) não encontrado. Instale em https://cli.github.com")
    result = subprocess.run(
        ["gh", *args], input=input_data, capture_output=True, text=True, check=False
    )
    if result.returncode != 0:
        sys.exit(f"Erro em `gh {' '.join(args)}`:\n{result.stderr.strip()}")
    return result.stdout.strip()


def current_repo() -> str:
    return _gh("repo", "view", "--json", "nameWithOwner", "-q", ".nameWithOwner")


def protect(repo: str) -> str:
    """Cria/atualiza o ruleset da branch padrão e ajusta as opções de merge do repo."""
    ruleset = (ASSETS / "github" / "protect-main.json").read_text()
    existing = json.loads(_gh("api", f"repos/{repo}/rulesets") or "[]")
    match = next((r for r in existing if r.get("name") == RULESET_NAME), None)
    if match:
        _gh(
            "api",
            "-X",
            "PUT",
            f"repos/{repo}/rulesets/{match['id']}",
            "--input",
            "-",
            input_data=ruleset,
        )
        action = "atualizado"
    else:
        _gh("api", "-X", "POST", f"repos/{repo}/rulesets", "--input", "-", input_data=ruleset)
        action = "criado"
    _gh(
        "api",
        "-X",
        "PATCH",
        f"repos/{repo}",
        "-F",
        "allow_squash_merge=true",
        "-F",
        "allow_merge_commit=false",
        "-F",
        "allow_rebase_merge=false",
        "-F",
        "delete_branch_on_merge=true",
    )
    return action


def _git(cwd: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=cwd, check=True)


def cmd_list(_: argparse.Namespace) -> None:
    for rel, _res in bundled_claude_files():
        print(f".claude/{rel.as_posix()}")


def cmd_install(args: argparse.Namespace) -> None:
    copied, skipped = install(Path(args.path), force=args.force)
    for p in copied:
        print(f"+ {p}")
    for p in skipped:
        print(f"= {p} (já existe; use --force para sobrescrever)")


def cmd_protect(args: argparse.Namespace) -> None:
    repo = args.repo or current_repo()
    print(f"Ruleset '{RULESET_NAME}' {protect(repo)} em {repo}")


def cmd_new(args: argparse.Namespace) -> None:
    template = args.template
    if "/" not in template:
        owner = _gh("api", "user", "-q", ".login")
        template = f"{owner}/{template}"
    visibility = "--private" if args.private else "--public"
    _gh("repo", "create", args.name, "--template", template, visibility, "--clone")
    path = Path(args.name).resolve()
    _git(path, "pull", "--ff-only")  # o repo gerado pode demorar a receber o conteúdo
    copied, _ = install(path)
    if copied:
        _git(path, "add", ".claude")
        _git(path, "commit", "-m", "chore: adiciona skills e agentes do ds-agent-kit")
        _git(path, "push")
    repo = _gh("repo", "view", args.name, "--json", "nameWithOwner", "-q", ".nameWithOwner")
    protect(repo)
    print(f"\nPronto: {repo} criado em {path}")
    print("Próximos passos: cd", args.name, "&& uv sync && git switch -c feature/inicio")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="dskit", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("list", help="lista skills/agentes incluídos")
    p.set_defaults(func=cmd_list)

    p = sub.add_parser("install", help="copia skills/agentes para <path>/.claude")
    p.add_argument("path", nargs="?", default=".")
    p.add_argument("--force", action="store_true", help="sobrescreve arquivos existentes")
    p.set_defaults(func=cmd_install)

    p = sub.add_parser("protect", help="aplica o ruleset de proteção da branch padrão")
    p.add_argument("--repo", help="owner/nome (padrão: repo do diretório atual)")
    p.set_defaults(func=cmd_protect)

    p = sub.add_parser("new", help="cria repo a partir do template + skills + proteção")
    p.add_argument("name")
    p.add_argument(
        "--template",
        default=DEFAULT_TEMPLATE,
        help=f"owner/repo do template (padrão: <você>/{DEFAULT_TEMPLATE})",
    )
    p.add_argument("--private", action="store_true")
    p.set_defaults(func=cmd_new)
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
