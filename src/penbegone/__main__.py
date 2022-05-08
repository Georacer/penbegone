"""Command-line interface."""
import click


@click.command()
@click.version_option()
def main() -> None:
    """Pen Begone."""


if __name__ == "__main__":
    main(prog_name="penbegone")  # pragma: no cover
