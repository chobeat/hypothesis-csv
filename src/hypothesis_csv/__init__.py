"""Package version metadata for hypothesis-csv."""

from importlib.metadata import PackageNotFoundError, version


try:
    dist_name = "hypothesis-csv"
    __version__ = version(dist_name)
except PackageNotFoundError:
    __version__ = "unknown"
