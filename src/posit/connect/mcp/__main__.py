import click

from .server import run_stdio_server, run_streamable_http_server


@click.group()
def cli():
    pass


@cli.command()
def stdio():
    run_stdio_server()


@cli.command()
@click.option("--host", default="127.0.0.1")
@click.option("--port", default=8001)
def http(host: str, port: int):
    run_streamable_http_server(host, port)


if __name__ == "__main__":
    cli()
