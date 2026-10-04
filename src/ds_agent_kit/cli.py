"""CLI `dskit`: adiciona e remove skills e agentes do Claude Code em repositórios."""

from __future__ import annotations

import argparse
import shutil
import sys
from dataclasses import dataclass
from importlib.resources import as_file, files
from importlib.resources.abc import Traversable
from pathlib import Path

ASSETS = files("ds_agent_kit") / "assets" / "claude"
KINDS = {"skill": "skills", "agent": "agents"}


@dataclass(frozen=True)
class Item:
    """Uma skill (pasta skills/<nome>/) ou um agente (arquivo agents/<nome>.md) do kit."""

    kind: str
    name: str
    source: Traversable

    @property
    def rel(self) -> Path:
        """Caminho relativo a .claude/ onde o item fica instalado."""
        if self.kind == "skill":
            return Path("skills") / self.name
        return Path("agents") / f"{self.name}.md"

    @property
    def label(self) -> str:
        return f"{self.kind}:{self.name}"

    def description(self) -> str:
        main = self.source / "SKILL.md" if self.kind == "skill" else self.source
        for line in main.read_text().splitlines():
            if line.startswith("description:"):
                return line.removeprefix("description:").strip()
        return ""


def _files(node: Traversable, prefix: Path = Path()) -> list[tuple[Path, Traversable]]:
    """Lista recursivamente (caminho relativo, recurso) dos arquivos de um diretório."""
    out: list[tuple[Path, Traversable]] = []
    for child in node.iterdir():
        rel = prefix / child.name
        out.extend(_files(child, rel) if child.is_dir() else [(rel, child)])
    return sorted(out, key=lambda item: str(item[0]))


def bundled_items() -> list[Item]:
    items = [Item("skill", d.name, d) for d in (ASSETS / "skills").iterdir() if d.is_dir()] + [
        Item("agent", f.name.removesuffix(".md"), f)
        for f in (ASSETS / "agents").iterdir()
        if f.name.endswith(".md")
    ]
    return sorted(items, key=lambda i: (i.kind, i.name))


def status(item: Item, target: Path) -> str:
    """'instalado', 'modificado' (difere da versão do kit) ou 'não instalado'."""
    dest = target / ".claude" / item.rel
    if not dest.exists():
        return "não instalado"
    pairs = _files(item.source) if item.kind == "skill" else [(Path(), item.source)]
    for rel, resource in pairs:
        installed = dest / rel if item.kind == "skill" else dest
        if not installed.is_file() or installed.read_bytes() != resource.read_bytes():
            return "modificado"
    return "instalado"


def select(names: list[str], all_: bool, skills: bool, agents: bool) -> list[Item]:
    """Resolve a seleção do usuário (nomes, `skill:nome`, --all, --skills, --agents)."""
    items = bundled_items()
    chosen = [i for i in items if all_ or (skills and i.kind == "skill")]
    chosen += [i for i in items if agents and i.kind == "agent" and i not in chosen]
    for name in names:
        kind, _, bare = name.rpartition(":")
        matches = [i for i in items if i.name == bare and kind in ("", i.kind)]
        if not matches:
            sys.exit(f"Erro: '{name}' não existe no kit. Veja `dskit list`.")
        if len(matches) > 1:
            options = ", ".join(m.label for m in matches)
            sys.exit(f"Erro: '{name}' é ambíguo; use {options}.")
        if matches[0] not in chosen:
            chosen.append(matches[0])
    if not chosen:
        sys.exit("Erro: informe nomes ou use --all, --skills ou --agents.")
    return chosen


def add(item: Item, target: Path) -> None:
    dest = target / ".claude" / item.rel
    if item.kind == "skill":
        shutil.rmtree(dest, ignore_errors=True)
        for rel, resource in _files(item.source):
            (dest / rel).parent.mkdir(parents=True, exist_ok=True)
            with as_file(resource) as src:
                shutil.copyfile(src, dest / rel)
    else:
        dest.parent.mkdir(parents=True, exist_ok=True)
        with as_file(item.source) as src:
            shutil.copyfile(src, dest)


def remove(item: Item, target: Path) -> bool:
    """Remove o item; apaga também as pastas que ficarem vazias. Retorna se havia algo."""
    claude = target / ".claude"
    dest = claude / item.rel
    if not dest.exists():
        return False
    shutil.rmtree(dest) if dest.is_dir() else dest.unlink()
    for parent in (claude / KINDS[item.kind], claude):
        if parent.is_dir() and not any(parent.iterdir()):
            parent.rmdir()
    return True


def cmd_list(args: argparse.Namespace) -> None:
    target = Path(args.path)
    for item in bundled_items():
        print(f"{item.label:<24} {status(item, target):<14} {item.description()[:70]}")


def cmd_add(args: argparse.Namespace) -> None:
    target = Path(args.path)
    for item in select(args.names, args.all, args.skills, args.agents):
        current = status(item, target)
        if current == "instalado":
            print(f"= {item.label} (já instalado)")
        elif current == "modificado" and not args.force:
            print(f"! {item.label} difere da versão do kit — use --force para sobrescrever")
        else:
            add(item, target)
            print(f"{'~' if current == 'modificado' else '+'} {item.label}")


def cmd_remove(args: argparse.Namespace) -> None:
    target = Path(args.path)
    for item in select(args.names, args.all, args.skills, args.agents):
        print(f"- {item.label}" if remove(item, target) else f"= {item.label} (não instalado)")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="dskit", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("list", help="lista skills/agentes do kit e o status no projeto")
    p.add_argument("--path", default=".", help="raiz do projeto (padrão: diretório atual)")
    p.set_defaults(func=cmd_list)

    for name, func, verb in (("add", cmd_add, "adiciona"), ("remove", cmd_remove, "remove")):
        p = sub.add_parser(name, help=f"{verb} skills/agentes em <path>/.claude")
        p.add_argument("names", nargs="*", help="nomes (ex.: pr-review ou skill:pr-review)")
        p.add_argument("--all", action="store_true", help="todas as skills e agentes")
        p.add_argument("--skills", action="store_true", help="todas as skills")
        p.add_argument("--agents", action="store_true", help="todos os agentes")
        p.add_argument("--path", default=".", help="raiz do projeto (padrão: diretório atual)")
        if name == "add":
            p.add_argument("--force", action="store_true", help="sobrescreve itens modificados")
        p.set_defaults(func=func)
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
