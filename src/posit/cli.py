import io
import tarfile

import click

from . import connect


@click.group()
def main():
    """The Posit command line interface."""
    pass


@main.group(name="connect")
def _connect():
    """Work with Posit Connect."""
    pass


@_connect.command()
@click.argument("content")
@click.option("--output", "-o", default=".", help="Output directory for the downloaded content.")
def download(content, output):
    """Download content from Connect."""
    client = connect.Client()
    bundle = client.content.get(content).bundles.find_one()

    if bundle is None:
        return

    buffer = io.BytesIO()
    bundle.download(buffer)
    buffer.seek(0)
    with tarfile.open(fileobj=buffer, mode="r:gz") as tar:
        tar.extractall(path=output, filter="data")


if __name__ == "__main__":
    main()
