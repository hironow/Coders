"""
colorbar - PyGMT-compatible plotting method.

Modern mode implementation using nanobind.
"""


def colorbar(
    self,
    position: str | None = None,
    frame: bool | str | list[str] | None = None,
    cmap: str | None = None,
    **kwargs,
):
    """
    Add a color scale bar to the figure.

    Modern mode version.

    Parameters:
        position: Position specification
                 Format: [g|j|J|n|x]refpoint+w<width>[+h<height>][+j<justify>][+o<dx>[/<dy>]]
        frame: Frame/annotations for colorbar
        cmap: Color palette (if not using current)
    """
    args = []

    # Color map
    if cmap:
        args.append(f"-C{cmap}")

    # Position
    if position:
        args.append(f"-D{position}")
    else:
        # Default horizontal colorbar
        args.append("-D5c/1c+w8c+h+jBC")

    # Frame
    if frame is not None:
        if frame is True:
            args.append("-Ba")
        elif isinstance(frame, str):
            args.append(f"-B{frame}")
        elif isinstance(frame, list):
            for f in frame:
                if isinstance(f, str):
                    args.append(f"-B{f}")

    self._session.call_module("colorbar", " ".join(args))
