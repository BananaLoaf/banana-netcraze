import sys
from pathlib import Path

import typer

from banana_netcraze.client import NetcrazeClient

app = typer.Typer(help="CLI for Keenetic/Netcraze routers.")

PASSWORD_OPTION = typer.Option(
    ...,
    "--password",
    "-p",
    envvar="NETCRAZE_PASSWORD",
    prompt=True,
    hide_input=True,
    help="Router account password.",
)
URL_OPTION = typer.Option(
    "http://192.168.1.1",
    "--url",
    envvar="NETCRAZE_URL",
    help="Router base URL.",
)
USERNAME_OPTION = typer.Option(
    "admin",
    "--username",
    "-u",
    envvar="NETCRAZE_USERNAME",
    help="Router account username.",
)
OUTPUT_OPTION = typer.Option(
    None,
    "--output",
    "-o",
    help="Output file path. Defaults to the filename returned by the router.",
)
STDOUT_OPTION = typer.Option(
    False,
    "--stdout",
    help="Write content to stdout instead of saving a file.",
)


def _validate_output_options(output: Path | None, stdout: bool) -> None:
    if output is not None and stdout:
        raise typer.BadParameter("--output cannot be used together with --stdout.")


@app.command("startup-config")
def download_startup_config(
    url: str = URL_OPTION,
    username: str = USERNAME_OPTION,
    password: str = PASSWORD_OPTION,
    output: Path | None = OUTPUT_OPTION,
    stdout: bool = STDOUT_OPTION,
) -> None:
    """Download startup-config.txt from the router."""
    _validate_output_options(output, stdout)

    with NetcrazeClient(url=url, username=username, password=password) as client:
        filename, content = client.download_startup_config()

    if stdout:
        sys.stdout.write(content)
        return

    target = output or Path(filename)
    target.write_text(content)
    typer.echo(f"Saved {target}", err=True)


@app.command("firmware")
def download_firmware(
    url: str = URL_OPTION,
    username: str = USERNAME_OPTION,
    password: str = PASSWORD_OPTION,
    output: Path | None = OUTPUT_OPTION,
    stdout: bool = STDOUT_OPTION,
) -> None:
    """Download firmware from the router."""
    _validate_output_options(output, stdout)

    with NetcrazeClient(url=url, username=username, password=password) as client:
        filename, content = client.download_firmware()

    if stdout:
        sys.stdout.buffer.write(content)
        return

    target = output or Path(filename)
    target.write_bytes(content)
    typer.echo(f"Saved {target}", err=True)


if __name__ == "__main__":
    app()
