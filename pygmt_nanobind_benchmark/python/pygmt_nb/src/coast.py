"""
coast - PyGMT-compatible plotting method.

Modern mode implementation using nanobind.
"""




def coast(
    self,
    region: str | list[float] | None = None,
    projection: str | None = None,
    land: str | None = None,
    water: str | None = None,
    shorelines: bool | str | int | None = None,
    resolution: str | None = None,
    borders: str | list[str] | None = None,
    frame: bool | str | list[str] | None = None,
    dcw: str | list[str] | None = None,
    **kwargs,
):
    """
    Draw coastlines, borders, and water bodies.

    Modern mode version.

    Parameters:
        region: Map region
        projection: Map projection
        land: Fill color for land areas (e.g., "tan", "lightgray")
        water: Fill color for water areas (e.g., "lightblue")
        shorelines: Shoreline pen specification
                   - True: default shoreline pen
                   - str: Custom pen (e.g., "1p,black", "thin,blue")
                   - int: Resolution level (1-4)
        resolution: Shoreline resolution (c, l, i, h, f)
        borders: Border specification
                - str: Single border spec (e.g., "1/1p,red")
                - list: Multiple border specs
        frame: Frame settings (same as basemap)
        dcw: Country/region codes to plot
            - str: Single code (e.g., "JP")
            - list: Multiple codes
    """
    # Validate that if region or projection is provided, both must be provided
    if (region is None and projection is not None) or (region is not None and projection is None):
        raise ValueError("Must provide both region and projection (not just one)")

    args = []

    # Region
    if region:
        if isinstance(region, str):
            args.append(f"-R{region}")
        elif isinstance(region, list):
            args.append(f"-R{'/'.join(map(str, region))}")

    # Projection
    if projection:
        args.append(f"-J{projection}")

    # Land fill
    if land:
        args.append(f"-G{land}")

    # Water fill
    if water:
        args.append(f"-S{water}")

    # Shorelines
    if shorelines is not None:
        if isinstance(shorelines, bool) and shorelines:
            args.append("-W")
        elif isinstance(shorelines, (str, int)):
            args.append(f"-W{shorelines}")

    # Resolution
    if resolution:
        args.append(f"-D{resolution}")

    # Borders
    if borders:
        if isinstance(borders, str):
            args.append(f"-N{borders}")
        elif isinstance(borders, list):
            for border in borders:
                args.append(f"-N{border}")

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

    # DCW (country codes)
    if dcw:
        if isinstance(dcw, str):
            args.append(f"-E{dcw}")
        elif isinstance(dcw, list):
            for code in dcw:
                args.append(f"-E{code}")

    # Default to shorelines if no visual options specified
    has_visual_options = land or water or (shorelines is not None) or borders or dcw
    if not has_visual_options:
        args.append("-W")

    self._session.call_module("coast", " ".join(args))
