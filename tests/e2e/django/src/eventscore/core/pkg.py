from collections.abc import Iterator
from pathlib import Path


def walk_files(
    top: str | Path,
    max_depth: int = -1,
    exclude_dirs: set[str] | None = None,
    include_ext: set[str] | None = None,
) -> Iterator[Path]:
    """
    Walk through the files recursively.

    :param top: Path to start from
    :type top: str | Path
    :param max_depth: Max recursion depth.
        If -1, there is no limit for recursion
    :type max_depth: int
    :param exclude_dirs: Dirs to exclude.
        No dirs are excluded by default, but it is recommended
        to exlude dirs such as __pycache__, .tox etc
    :type exclude_dirs: set[str] | None
    :param include_ext: Extensions to include.
        If None or empty, all extensions are included
    :type include_ext: set[str] | None
    :return: Generator that produces files
        satisfying all given values
    :rtype: Iterator[Path]
    """
    assert max_depth > 0 or max_depth == -1, "max_depth must be positive or -1"
    exclude_dirs = exclude_dirs or set()
    top = Path(top)
    if max_depth == 0:
        return
    for child in top.iterdir():
        if child.is_file() and (
            not include_ext or child.name.split(".")[-1] in include_ext
        ):
            yield child
        elif (
            child.is_dir()
            and child.name not in exclude_dirs
            and is_python_package(child)
        ):
            yield from walk_files(child, max_depth - 1 if max_depth > 0 else -1)


def is_python_package(path: Path) -> bool:
    """
    Determine whether a given directory is a package or not.

    :param path: Path to the inspected dir
    :type path: Path
    :return: True if dir is a Python package, False otherwise
    :rtype: bool
    """
    for child in path.iterdir():
        if not child.is_file():
            continue
        if child.name == "__init__.py":
            return True
    return False


def module_name_from_path(file_path: Path, pkg_root: Path, pkg: str) -> str:
    """
    Compute importable module path.

    :param file_path: Path to the .py file
    :type file_path: Path
    :param pkg_root: Root of the package
    :type pkg_root: Path
    :param pkg: Package to import
    :type pkg: str
    :return: Importable path to module
    :rtype: str
    """
    rel = file_path.relative_to(pkg_root).with_suffix("")  # strip .py
    parts = rel.parts
    return ".".join([pkg] + list(parts))
