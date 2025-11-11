"""
grdlandmask - Create a \"wet-dry\" mask grid from shoreline data.

Module-level function (not a Figure method).
"""

from typing import Union, Optional, List
from pathlib import Path

from pygmt_nb.clib import Session


def grdlandmask(
    outgrid: Union[str, Path],
    region: Union[str, List[float]],
    spacing: Union[str, List[float]],
    resolution: Optional[str] = None,
    shorelines: Optional[Union[str, int]] = None,
    area_thresh: Optional[Union[str, int]] = None,
    registration: Optional[str] = None,
    maskvalues: Optional[Union[str, List[float]]] = None,
    **kwargs
):
    """
    Create a \"wet-dry\" mask grid from shoreline data.

    Reads the selected shoreline database and creates a grid where each
    node is set to 1 if on land or 0 if on water. Optionally can set
    custom values for ocean, land, lakes, islands in lakes, and ponds.

    Based on PyGMT's grdlandmask implementation for API compatibility.

    Parameters
    ----------
    outgrid : str or Path
        Output grid file name.
    region : str or list
        Grid bounds. Format: [lonmin, lonmax, latmin, latmax]
        Required parameter.
    spacing : str or list
        Grid spacing. Format: "xinc[unit][+e|n][/yinc[unit][+e|n]]" or [xinc, yinc]
        Required parameter.
    resolution : str, optional
        Shoreline database resolution:
        - "c" : crude
        - "l" : low (default)
        - "i" : intermediate
        - "h" : high
        - "f" : full
    shorelines : str or int, optional
        Shoreline level:
        - 1 : coastline (default)
        - 2 : lakeshore
        - 3 : island in lake
        - 4 : pond in island in lake
        Can specify multiple: "1/2" for coastline and lakeshore
    area_thresh : str or int, optional
        Minimum area threshold in km^2 or as level/area.
        Features smaller than this are not used.
        Examples: 0/0/1 (min 1 km^2 for coastlines)
    registration : str, optional
        Grid registration type:
        - "g" or None : gridline registration (default)
        - "p" : pixel registration
    maskvalues : str or list, optional
        Set values for different levels. Format: [ocean, land, lake, island, pond]
        Default: ocean=0, land=1, lake=0, island=1, pond=0
        Example: "0/1/0/1/0" or [0, 1, 0, 1, 0]

    Returns
    -------
    None
        Writes mask grid to file.

    Examples
    --------
    >>> import pygmt
    >>> # Basic land-sea mask
    >>> pygmt.grdlandmask(
    ...     outgrid="landmask.nc",
    ...     region=[120, 150, -50, -20],
    ...     spacing="5m",
    ...     resolution="i"
    ... )
    >>>
    >>> # High resolution mask for detailed coastline
    >>> pygmt.grdlandmask(
    ...     outgrid="coast_mask_hi.nc",
    ...     region=[-75, -70, 40, 45],
    ...     spacing="30s",
    ...     resolution="f"
    ... )
    >>>
    >>> # Include lakes as separate category
    >>> pygmt.grdlandmask(
    ...     outgrid="mask_with_lakes.nc",
    ...     region=[0, 20, 50, 70],
    ...     spacing="2m",
    ...     resolution="h",
    ...     shorelines="1/2",  # coastline + lakeshore
    ...     maskvalues="0/1/2/3/4"  # distinct values for each level
    ... )
    >>>
    >>> # Filter small features
    >>> pygmt.grdlandmask(
    ...     outgrid="major_landmasses.nc",
    ...     region=[-180, 180, -90, 90],
    ...     spacing="10m",
    ...     resolution="c",
    ...     area_thresh="0/0/1000"  # min 1000 km^2
    ... )
    >>>
    >>> # Pixel registration for exact grid alignment
    >>> pygmt.grdlandmask(
    ...     outgrid="mask_pixel.nc",
    ...     region=[100, 110, 0, 10],
    ...     spacing="1m",
    ...     resolution="i",
    ...     registration="p"
    ... )

    Notes
    -----
    This function is commonly used for:
    - Creating land-sea masks for analysis
    - Masking ocean/land data
    - Identifying coastal regions
    - Filtering data by land/water location

    Mask values (default):
    - 0 : Ocean (wet)
    - 1 : Land (dry)
    - 0 : Lakes (wet)
    - 1 : Islands in lakes (dry)
    - 0 : Ponds in islands in lakes (wet)

    Shoreline hierarchy:
    - Level 1: Coastlines (land vs ocean)
    - Level 2: Lakeshores (land vs lakes)
    - Level 3: Island shores (islands in lakes)
    - Level 4: Pond shores (ponds in islands in lakes)

    Resolution vs detail tradeoff:
    - crude (c): Fast, low detail, global use
    - low (l): Good for continental scale
    - intermediate (i): Regional studies
    - high (h): Detailed coastal work
    - full (f): Maximum detail, slow

    Applications:
    - Ocean data extraction
    - Land topography masking
    - Coastal zone identification
    - Geographic data filtering
    - Land-sea statistics

    Workflow:
    1. Select shoreline database resolution
    2. Define grid region and spacing
    3. Optionally filter by area threshold
    4. Create binary or multi-level mask
    5. Use mask to filter/select data

    Comparison with related functions:
    - grdlandmask: Binary/categorical land-sea mask
    - coast: Plot coastlines on maps
    - grdclip: Clip grid values at thresholds
    - select: Select data by location
    """
    # Build GMT command arguments
    args = []

    # Output grid (-G option)
    args.append(f"-G{outgrid}")

    # Region (-R option) - required
    if isinstance(region, list):
        args.append(f"-R{'/'.join(str(x) for x in region)}")
    else:
        args.append(f"-R{region}")

    # Spacing (-I option) - required
    if isinstance(spacing, list):
        args.append(f"-I{'/'.join(str(x) for x in spacing)}")
    else:
        args.append(f"-I{spacing}")

    # Resolution (-D option)
    if resolution is not None:
        args.append(f"-D{resolution}")

    # Shorelines (-E option)
    if shorelines is not None:
        args.append(f"-E{shorelines}")

    # Area threshold (-A option)
    if area_thresh is not None:
        args.append(f"-A{area_thresh}")

    # Registration (-r option for pixel)
    if registration is not None:
        if registration == "p":
            args.append("-r")

    # Mask values (-N option)
    if maskvalues is not None:
        if isinstance(maskvalues, list):
            args.append(f"-N{'/'.join(str(x) for x in maskvalues)}")
        else:
            args.append(f"-N{maskvalues}")

    # Execute via nanobind session
    with Session() as session:
        session.call_module("grdlandmask", " ".join(args))
