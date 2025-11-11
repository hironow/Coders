"""
psconvert - Convert PostScript to other formats.

Figure method (imported into Figure class).
"""



def psconvert(
    self,
    prefix: str | None = None,
    fmt: str = "g",
    crop: bool = True,
    portrait: bool = False,
    adjust: bool = True,
    dpi: int = 300,
    gray: bool = False,
    anti_aliasing: str | None = None,
    **kwargs,
):
    """
    Convert PostScript figure to other formats (PNG, PDF, JPEG, etc.).

    This method wraps GMT's psconvert module to convert the current figure
    from PostScript to various raster or vector formats.

    Based on PyGMT's psconvert implementation for API compatibility.

    Parameters
    ----------
    prefix : str, optional
        Output file name prefix. If not specified, uses the figure name.
    fmt : str, optional
        Output format. Options:
        - "b" : BMP
        - "e" : EPS (Encapsulated PostScript)
        - "f" : PDF
        - "g" : PNG (default)
        - "j" : JPEG
        - "t" : TIFF
        - "s" : SVG (Scalable Vector Graphics)
        Default is "g" (PNG).
    crop : bool, optional
        Crop the output to minimum bounding box (default: True).
        Uses ghostscript's bbox device.
    portrait : bool, optional
        Force portrait mode (default: False, uses GMT defaults).
    adjust : bool, optional
        Adjust image size to fit DPI (default: True).
    dpi : int, optional
        Resolution in dots per inch for raster formats (default: 300).
    gray : bool, optional
        Convert to grayscale image (default: False).
    anti_aliasing : str, optional
        Anti-aliasing settings. Options:
        - "t" : text
        - "g" : graphics
        - "tg" : both text and graphics

    Examples
    --------
    >>> import pygmt
    >>> fig = pygmt.Figure()
    >>> fig.coast(
    ...     region=[-10, 10, 35, 45],
    ...     projection="M15c",
    ...     land="tan",
    ...     water="lightblue",
    ...     frame=True
    ... )
    >>> # Convert to PNG (default)
    >>> fig.psconvert(prefix="map", fmt="g", dpi=150)
    >>>
    >>> # Convert to PDF
    >>> fig.psconvert(prefix="map", fmt="f")
    >>>
    >>> # Convert to high-res JPEG
    >>> fig.psconvert(prefix="map_hires", fmt="j", dpi=600, crop=True)

    Notes
    -----
    This function requires Ghostscript to be installed for most conversions.
    The PostScript file is automatically generated from the current figure
    state before conversion.

    Format codes:
    - Raster formats (b, g, j, t) support DPI settings
    - Vector formats (e, f, s) are resolution-independent
    - PNG (g) is recommended for web use
    - PDF (f) is recommended for publications
    """
    # Build GMT command arguments
    args = []

    # Output format (-T option)
    args.append(f"-T{fmt}")

    # Crop (-A option)
    if crop:
        args.append("-A")

    # Portrait mode (-P option)
    if portrait:
        args.append("-P")

    # Adjust to DPI (-E option)
    if adjust:
        args.append(f"-E{dpi}")

    # DPI for raster (-E option if adjust=False)
    if not adjust and fmt in ["b", "g", "j", "t"]:
        args.append(f"-E{dpi}")

    # Grayscale (-C option)
    if gray:
        args.append("-C")

    # Anti-aliasing (-Q option)
    if anti_aliasing is not None:
        args.append(f"-Q{anti_aliasing}")

    # Prefix (-F option)
    if prefix is not None:
        args.append(f"-F{prefix}")
    else:
        # Use figure name as prefix
        args.append(f"-F{self._figure_name}")

    # Execute via nanobind session
    # In modern mode, we need to call psconvert with the current figure
    try:
        self._session.call_module("psconvert", " ".join(args))
    except RuntimeError as e:
        # Provide helpful error message if Ghostscript is missing
        if "gs" in str(e).lower() or "ghostscript" in str(e).lower():
            raise RuntimeError(
                "psconvert requires Ghostscript to be installed. "
                "Please install Ghostscript and ensure 'gs' is in your PATH."
            ) from e
        else:
            raise
