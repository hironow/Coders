"""
grdimage - PyGMT-compatible plotting method.

Modern mode implementation using nanobind.
"""

from pathlib import Path

from pygmt_nb.clib import Grid


def grdimage(
    self,
    grid: str | Path | Grid,
    projection: str | None = None,
    region: str | list[float] | None = None,
    cmap: str | None = None,
    frame: bool | str | list[str] | None = None,
    **kwargs,
):
    """
    Plot a grid as an image.

    Modern mode version.

    Parameters:
        grid: Grid file path (str/Path) or Grid object
        projection: Map projection
        region: Map region
        cmap: Color palette (e.g., "viridis", "rainbow")
        frame: Frame settings
    """
    args = []

    # Grid file
    if isinstance(grid, str | Path):
        args.append(str(grid))
    elif isinstance(grid, Grid):
        # For Grid objects, we'd need to write to temp file
        # For now, assume grid path
        raise NotImplementedError("Grid object support not yet implemented in modern mode")

    # Projection
    if projection:
        args.append(f"-J{projection}")

    # Region
    if region:
        if isinstance(region, str):
            args.append(f"-R{region}")
        elif isinstance(region, list):
            args.append(f"-R{'/'.join(map(str, region))}")

    # Color map
    if cmap:
        args.append(f"-C{cmap}")

    # Frame
    if frame is not None:
        if frame is True:
            args.append("-Ba")
        elif isinstance(frame, str):
            args.append(f"-B{frame}")

    self._session.call_module("grdimage", " ".join(args))
