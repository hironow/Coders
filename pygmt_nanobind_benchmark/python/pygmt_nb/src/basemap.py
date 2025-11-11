"""
basemap - Plot base maps and frames for pygmt_nb.

Modern mode implementation using nanobind for direct GMT C API access.
"""


def basemap(
    self,
    region: str | list[float] | None = None,
    projection: str | None = None,
    frame: bool | str | list[str] | None = None,
    **kwargs,
):
    """
    Draw a basemap (map frame, axes, and optional grid).

    Modern mode version - no -K/-O flags needed.

    Parameters
    ----------
    region : str or list
        Map region. Can be:
        - List: [west, east, south, north]
        - String: Region code (e.g., "JP" for Japan)
    projection : str
        Map projection (e.g., "X10c", "M15c")
    frame : bool, str, or list, optional
        Frame and axis settings:
        - True: automatic frame with annotations
        - False or None: no frame
        - str: GMT frame specification (e.g., "a", "afg", "WSen")
        - list: List of frame specifications
    **kwargs : dict
        Additional GMT options (not yet implemented)

    Examples
    --------
    >>> fig = Figure()
    >>> fig.basemap(region=[0, 10, 0, 10], projection="X10c", frame=True)
    """
    if region is None:
        raise ValueError("region parameter is required for basemap()")
    if projection is None:
        raise ValueError("projection parameter is required for basemap()")

    # Store region and projection for subsequent commands
    self._region = region
    self._projection = projection

    # Build GMT command arguments
    args = []

    # Region
    if isinstance(region, str):
        args.append(f"-R{region}")
    elif isinstance(region, list):
        if len(region) != 4:
            raise ValueError("Region must be [west, east, south, north]")
        args.append(f"-R{'/'.join(map(str, region))}")

    # Projection
    args.append(f"-J{projection}")

    # Frame - handle spaces in labels
    def _escape_frame_spaces(value: str) -> str:
        """Escape spaces in GMT frame specifications."""
        if " " not in value:
            return value
        import re

        pattern = r"(\+[lLS])([^+]+)"

        def quote_label(match):
            prefix = match.group(1)
            content = match.group(2)
            if " " in content:
                return f'{prefix}"{content}"'
            return match.group(0)

        return re.sub(pattern, quote_label, value)

    if frame is True:
        args.append("-Ba")
    elif frame is False or frame is None:
        args.append("-B0")
    elif isinstance(frame, str):
        args.append(f"-B{_escape_frame_spaces(frame)}")
    elif isinstance(frame, list):
        for f in frame:
            if f is True:
                args.append("-Ba")
            elif f is False:
                args.append("-B0")
            elif isinstance(f, str):
                args.append(f"-B{_escape_frame_spaces(f)}")

    # Execute via nanobind (103x faster than subprocess!)
    self._session.call_module("basemap", " ".join(args))
