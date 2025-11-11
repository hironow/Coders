"""
grdview - Create 3-D perspective plots.

Figure method (imported into Figure class).
"""

from pathlib import Path


def grdview(
    self,
    grid: str | Path,
    region: str | list[float] | None = None,
    projection: str | None = None,
    perspective: str | list[float] | None = None,
    frame: bool | str | list | None = None,
    cmap: str | None = None,
    drapegrid: str | Path | None = None,
    surftype: str | None = None,
    plane: str | float | None = None,
    shading: str | float | None = None,
    zscale: str | float | None = None,
    zsize: str | float | None = None,
    contourpen: str | None = None,
    meshpen: str | None = None,
    facadepen: str | None = None,
    transparency: float | None = None,
    **kwargs,
):
    """
    Create 3-D perspective image or surface mesh from a grid.

    Reads a 2-D grid and produces a 3-D perspective plot by drawing a
    mesh, painting a colored/gray-shaded surface, or by scanline conversion
    of these views.

    Based on PyGMT's grdview implementation for API compatibility.

    Parameters
    ----------
    grid : str or Path
        Name of the input grid file.
    region : str or list, optional
        Map region. Format: [xmin, xmax, ymin, ymax, zmin, zmax]
        If not specified, uses grid bounds.
    projection : str, optional
        Map projection. Example: "M10c" for Mercator.
    perspective : str or list, optional
        3-D view perspective. Format: [azimuth, elevation] or "azimuth/elevation"
        Example: [135, 30] for azimuth=135°, elevation=30°
    frame : bool, str, or list, optional
        Frame and axes settings.
    cmap : str, optional
        Color palette name or .cpt file for coloring the surface.
    drapegrid : str or Path, optional
        Grid to drape on top of relief (for coloring).
    surftype : str, optional
        Surface type to plot:
        - "s" : surface (default)
        - "m" : mesh (wireframe)
        - "i" : image
        - "c" : colored mesh
        - "w" : waterfall (x direction)
        - "W" : waterfall (y direction)
    plane : str or float, optional
        Draw a plane at this z-level. Format: "z_level[+gfill]"
    shading : str or float, optional
        Illumination intensity. Can be grid file or constant.
    zscale : str or float, optional
        Vertical exaggeration. Example: "10c" or 2 (multiply z by this).
    zsize : str or float, optional
        Set z-axis size. Example: "5c"
    contourpen : str, optional
        Pen for contour lines. Example: "0.5p,black"
    meshpen : str, optional
        Pen for mesh lines. Example: "0.25p,gray"
    facadepen : str, optional
        Pen for facade lines. Example: "1p,black"
    transparency : float, optional
        Transparency level (0-100).

    Examples
    --------
    >>> import pygmt
    >>> fig = pygmt.Figure()
    >>> # Create 3D surface view of a grid
    >>> fig.grdview(
    ...     grid="@earth_relief_10m",
    ...     region=[-120, -110, 30, 40, -4000, 4000],
    ...     projection="M10c",
    ...     perspective=[135, 30],
    ...     surftype="s",
    ...     cmap="geo",
    ...     frame=["af", "zaf"]
    ... )
    >>> fig.savefig("3d_surface.ps")
    >>>
    >>> # Wireframe mesh view
    >>> fig.grdview(
    ...     grid="@earth_relief_10m",
    ...     region=[-120, -110, 30, 40],
    ...     projection="M10c",
    ...     perspective=[135, 30],
    ...     surftype="m",
    ...     meshpen="0.5p,black"
    ... )

    Notes
    -----
    This function wraps the GMT grdview module for 3-D visualization
    of gridded data. Useful for creating perspective views of DEMs,
    topography, or any gridded surface.
    """
    # Build GMT command arguments
    args = []

    # Input grid
    args.append(str(grid))

    # Region (-R option)
    if region is not None:
        if isinstance(region, list):
            args.append(f"-R{'/'.join(str(x) for x in region)}")
        else:
            args.append(f"-R{region}")

    # Projection (-J option)
    if projection is not None:
        args.append(f"-J{projection}")

    # Perspective (-p option)
    if perspective is not None:
        if isinstance(perspective, list):
            args.append(f"-p{'/'.join(str(x) for x in perspective)}")
        else:
            args.append(f"-p{perspective}")

    # Frame (-B option)
    if frame is not None:
        if isinstance(frame, bool):
            if frame:
                args.append("-B")
        elif isinstance(frame, list):
            for f in frame:
                args.append(f"-B{f}")
        else:
            args.append(f"-B{frame}")

    # Color palette (-C option)
    if cmap is not None:
        args.append(f"-C{cmap}")

    # Drape grid (-G option)
    if drapegrid is not None:
        args.append(f"-G{drapegrid}")

    # Surface type (-Q option)
    if surftype is not None:
        args.append(f"-Q{surftype}")
    else:
        # Default to surface
        args.append("-Qs")

    # Plane (-N option)
    if plane is not None:
        args.append(f"-N{plane}")

    # Shading (-I option)
    if shading is not None:
        if isinstance(shading, (int, float)):
            args.append(f"-I+d{shading}")
        else:
            args.append(f"-I{shading}")

    # Z-scale (-JZ option)
    if zscale is not None:
        args.append(f"-JZ{zscale}")
    elif zsize is not None:
        args.append(f"-JZ{zsize}")

    # Contour pen (-W option with c)
    if contourpen is not None:
        args.append(f"-Wc{contourpen}")

    # Mesh pen (-W option with m)
    if meshpen is not None:
        args.append(f"-Wm{meshpen}")

    # Facade pen (-W option with f)
    if facadepen is not None:
        args.append(f"-Wf{facadepen}")

    # Transparency (-t option)
    if transparency is not None:
        args.append(f"-t{transparency}")

    # Execute via nanobind session
    self._session.call_module("grdview", " ".join(args))
