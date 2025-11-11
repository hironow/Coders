"""
grdcontour - PyGMT-compatible plotting method.

Modern mode implementation using nanobind.
"""

from pathlib import Path


def grdcontour(
    self,
    grid: str | Path,
    region: str | list[float] | None = None,
    projection: str | None = None,
    interval: int | float | str | None = None,
    annotation: int | float | str | None = None,
    pen: str | None = None,
    limit: list[float] | None = None,
    frame: bool | str | list[str] | None = None,
    **kwargs,
):
    """
    Draw contour lines from a grid file.

    Modern mode version.

    Parameters:
        grid: Grid file path
        region: Map region
        projection: Map projection
        interval: Contour interval
        annotation: Annotation interval
        pen: Contour pen specification
        limit: Contour limits [low, high]
        frame: Frame settings
    """
    args = [str(grid)]

    # Contour interval
    if interval is not None:
        args.append(f"-C{interval}")

    # Annotation
    if annotation is not None:
        args.append(f"-A{annotation}")

    # Projection
    if projection:
        args.append(f"-J{projection}")

    # Region
    if region:
        if isinstance(region, str):
            args.append(f"-R{region}")
        elif isinstance(region, list):
            args.append(f"-R{'/'.join(map(str, region))}")

    # Pen
    if pen:
        args.append(f"-W{pen}")

    # Limits
    if limit:
        args.append(f"-L{limit[0]}/{limit[1]}")

    # Frame
    if frame is not None:
        if frame is True:
            args.append("-Ba")
        elif isinstance(frame, str):
            args.append(f"-B{frame}")

    self._session.call_module("grdcontour", " ".join(args))
