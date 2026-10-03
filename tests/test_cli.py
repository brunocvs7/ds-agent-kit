import json

import pytest

from ds_agent_kit import cli


def test_bundled_assets_present():
    names = {rel.as_posix() for rel, _ in cli.bundled_claude_files()}
    assert "agents/code-reviewer.md" in names
    assert "skills/pr-review/SKILL.md" in names


def test_bundled_ruleset_is_valid_json():
    ruleset = json.loads((cli.ASSETS / "github" / "protect-main.json").read_text())
    checks = {
        c["context"]
        for rule in ruleset["rules"]
        if rule["type"] == "required_status_checks"
        for c in rule["parameters"]["required_status_checks"]
    }
    assert checks == {"lint", "test", "branch-name"}


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


@pytest.mark.parametrize(
    "existing, expected", [("[]", "criado"), ('[{"id": 7, "name": "protect-main"}]', "atualizado")]
)
def test_protect_creates_or_updates(monkeypatch, existing, expected):
    calls = []

    def fake_gh(*args, input_data=None):
        calls.append(args)
        return existing if args[-1].endswith("/rulesets") and len(args) == 2 else ""

    monkeypatch.setattr(cli, "_gh", fake_gh)
    assert cli.protect("me/repo") == expected
    method = "PUT" if expected == "atualizado" else "POST"
    assert any(method in c for c in calls)


def test_cli_list(capsys):
    cli.main(["list"])
    assert ".claude/skills/pr-review/SKILL.md" in capsys.readouterr().out
