"""CLI `dskit`: instala skills e agentes do Claude Code em repositórios."""

from __future__ import annotations

import argparse
import shutil
from importlib.resources import as_file, files
from importlib.resources.abc import Traversable
from pathlib import Path

ASSETS = files("ds_agent_kit") / "assets"


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


def cmd_list(_: argparse.Namespace) -> None:
    for rel, _res in bundled_claude_files():
        print(f".claude/{rel.as_posix()}")


def cmd_install(args: argparse.Namespace) -> None:
    copied, skipped = install(Path(args.path), force=args.force)
    for p in copied:
        print(f"+ {p}")
    for p in skipped:
        print(f"= {p} (já existe; use --force para sobrescrever)")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="dskit", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("list", help="lista skills/agentes incluídos")
    p.set_defaults(func=cmd_list)

    p = sub.add_parser("install", help="copia skills/agentes para <path>/.claude")
    p.add_argument("path", nargs="?", default=".")
    p.add_argument("--force", action="store_true", help="sobrescreve arquivos existentes")
    p.set_defaults(func=cmd_install)

    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
