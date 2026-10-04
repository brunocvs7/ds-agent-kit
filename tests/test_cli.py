import pytest

from ds_agent_kit import cli


def run(*args, path):
    cli.main([*args, "--path", str(path)])


def installed(path):
    claude = path / ".claude"
    if not claude.exists():
        return set()
    skills = {f"skill:{d.name}" for d in (claude / "skills").glob("*")}
    agents = {f"agent:{f.stem}" for f in (claude / "agents").glob("*.md")}
    return skills | agents


def labels(kind=None):
    return {i.label for i in cli.bundled_items() if kind in (None, i.kind)}


def test_bundle_has_expected_items():
    assert {"skill:pr-review", "skill:ds-eda", "agent:code-reviewer"} <= labels()
    assert all(i.description() for i in cli.bundled_items())


def test_add_all(tmp_path):
    run("add", "--all", path=tmp_path)
    assert installed(tmp_path) == labels()
    assert (tmp_path / ".claude/skills/pr-review/SKILL.md").is_file()


def test_add_only_skills_or_agents(tmp_path):
    run("add", "--skills", path=tmp_path)
    assert installed(tmp_path) == labels("skill")
    run("add", "--agents", path=tmp_path)
    assert installed(tmp_path) == labels()


def test_add_by_name_with_and_without_kind(tmp_path):
    run("add", "pr-review", "agent:code-reviewer", path=tmp_path)
    assert installed(tmp_path) == {"skill:pr-review", "agent:code-reviewer"}


def test_unknown_name_fails(tmp_path):
    with pytest.raises(SystemExit, match="não existe"):
        run("add", "nao-existe", path=tmp_path)


def test_selection_required(tmp_path):
    with pytest.raises(SystemExit, match="--all"):
        run("add", path=tmp_path)


def test_modified_item_needs_force(tmp_path, capsys):
    run("add", "code-reviewer", path=tmp_path)
    agent = tmp_path / ".claude/agents/code-reviewer.md"
    agent.write_text("minha versão")

    run("add", "code-reviewer", path=tmp_path)
    assert agent.read_text() == "minha versão"
    assert "--force" in capsys.readouterr().out

    run("add", "code-reviewer", "--force", path=tmp_path)
    assert agent.read_text() != "minha versão"


def test_remove_one(tmp_path):
    run("add", "--all", path=tmp_path)
    run("remove", "ds-eda", path=tmp_path)
    assert installed(tmp_path) == labels() - {"skill:ds-eda"}


def test_remove_all_keeps_user_items(tmp_path):
    own_skill = tmp_path / ".claude/skills/minha-skill/SKILL.md"
    own_skill.parent.mkdir(parents=True)
    own_skill.write_text("---\nname: minha-skill\n---\n")
    settings = tmp_path / ".claude/settings.json"
    settings.write_text("{}")

    run("add", "--all", path=tmp_path)
    run("remove", "--all", path=tmp_path)

    assert installed(tmp_path) == {"skill:minha-skill"}
    assert settings.is_file()
    assert not (tmp_path / ".claude/agents").exists()


def test_list_shows_status(tmp_path, capsys):
    run("add", "pr-review", path=tmp_path)
    (tmp_path / ".claude/skills/pr-review/SKILL.md").write_text("editado")
    run("list", path=tmp_path)
    out = {line.split()[0]: line.split()[1] for line in capsys.readouterr().out.splitlines()}
    assert out["skill:pr-review"] == "modificado"
    assert out["skill:ds-eda"] == "não"
