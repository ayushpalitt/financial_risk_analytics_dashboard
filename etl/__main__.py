"""Command-line entry point for `python -m etl`."""

from etl.pipeline import main


if __name__ == "__main__":
    raise SystemExit(main())
