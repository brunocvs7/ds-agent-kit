from ds_agent_kit import cli


def test_bundled_assets_present():
    names = {rel.as_posix() for rel, _ in cli.bundled_claude_files()}
    assert "agents/code-reviewer.md" in names
    assert "skills/pr-review/SKILL.md" in names


def test_install_copies_files(tmp_path):
    copied, skipped = cli.install(tmp_path)
    assert (tmp_path / ".claude/agents/code-reviewer.md").is_file()
    assert len(copied) == len(cli.bundled_claude_files())
    assert skipped == []


def test_install_skips_existing_unless_forced(tmp_path):
    cli.install(tmp_path)
    target = tmp_path / ".claude/agents/code-reviewer.md"
    target.write_text("custom")

    _, skipped = cli.install(tmp_path)
    assert target in skipped
    assert target.read_text() == "custom"

    cli.install(tmp_path, force=True)
    assert target.read_text() != "custom"


def test_cli_list(capsys):
    cli.main(["list"])
    assert ".claude/skills/pr-review/SKILL.md" in capsys.readouterr().out
