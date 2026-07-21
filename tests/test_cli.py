from typer.testing import CliRunner

from banana_netcraze import __main__ as cli


class FakeClient:
    def __init__(self, url: str, username: str, password: str):
        self.url = url
        self.username = username
        self.password = password

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return None

    def download_startup_config(self):
        return "startup-config.txt", "interface Home\n"

    def download_firmware(self):
        return "firmware.bin", b"firmware"


def test_startup_config_stdout(monkeypatch):
    monkeypatch.setattr(cli, "NetcrazeClient", FakeClient)
    runner = CliRunner()

    result = runner.invoke(
        cli.app, ["startup-config", "--password", "secret", "--stdout"]
    )

    assert result.exit_code == 0
    assert result.stdout == "interface Home\n"


def test_startup_config_uses_router_filename(monkeypatch, tmp_path):
    monkeypatch.setattr(cli, "NetcrazeClient", FakeClient)
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()

    result = runner.invoke(cli.app, ["startup-config", "--password", "secret"])

    assert result.exit_code == 0
    assert result.stdout == ""
    assert result.stderr == "Saved startup-config.txt\n"
    assert (tmp_path / "startup-config.txt").read_text() == "interface Home\n"


def test_firmware_uses_router_filename(monkeypatch, tmp_path):
    monkeypatch.setattr(cli, "NetcrazeClient", FakeClient)
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()

    result = runner.invoke(cli.app, ["firmware", "--password", "secret"])

    assert result.exit_code == 0
    assert result.stdout == ""
    assert result.stderr == "Saved firmware.bin\n"
    assert (tmp_path / "firmware.bin").read_bytes() == b"firmware"
