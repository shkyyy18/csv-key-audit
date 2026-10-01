from . import core
from .common import main


def cli():
    return main(core, "csv-key-audit")


if __name__ == "__main__":
    raise SystemExit(cli())
