"""
dimfilter - Directional median filtering of grids.

Module-level function (not a Figure method).
"""

from typing import Union, Optional, List
from pathlib import Path

from pygmt_nb.clib import Session


def dimfilter(
    grid: Union[str, Path],
    outgrid: Union[str, Path],
    distance: Union[str, float],
    sectors: int = 4,
    filter_type: Optional[str] = None,
    region: Optional[Union[str, List[float]]] = None,
    **kwargs
):
    """
    Perform directional median filtering of grids.

    Reads a grid and performs directional filtering by calculating
    median values in sectors radiating from each node. This is useful
    for removing noise while preserving directional features.

    Based on PyGMT's dimfilter implementation for API compatibility.

    Parameters
    ----------
    grid : str or Path
        Input grid file name.
    outgrid : str or Path
        Output filtered grid file name.
    distance : str or float
        Filter diameter. Specify value and optional unit.
        Examples: "5k" (5 km), "0.5" (grid units), "300e" (300 meters)
    sectors : int, optional
        Number of sectors (default: 4).
        Each node is filtered using median of values in each sector.
        Common values: 4, 6, 8
    filter_type : str, optional
        Filter type:
        - None or "m" : Median filter (default, robust)
        - "l" : Lower (minimum) value
        - "u" : Upper (maximum) value
        - "p" : Mode (most common value)
    region : str or list, optional
        Subregion of grid to filter. Format: [xmin, xmax, ymin, ymax]
        If not specified, filters entire grid.

    Returns
    -------
    None
        Writes filtered grid to file.

    Examples
    --------
    >>> import pygmt
    >>> # Basic directional median filter
    >>> pygmt.dimfilter(
    ...     grid="@earth_relief_01d",
    ...     outgrid="relief_filtered.nc",
    ...     distance="5k",  # 5 km diameter
    ...     sectors=6
    ... )
    >>>
    >>> # Stronger filtering with more sectors
    >>> pygmt.dimfilter(
    ...     grid="noisy_data.nc",
    ...     outgrid="smoothed.nc",
    ...     distance="10k",
    ...     sectors=8
    ... )
    >>>
    >>> # Directional minimum filter
    >>> pygmt.dimfilter(
    ...     grid="data.nc",
    ...     outgrid="local_minima.nc",
    ...     distance="2k",
    ...     sectors=4,
    ...     filter_type="l"
    ... )
    >>>
    >>> # Filter subregion only
    >>> pygmt.dimfilter(
    ...     grid="global.nc",
    ...     outgrid="pacific_filtered.nc",
    ...     distance="3k",
    ...     sectors=6,
    ...     region=[120, 240, -60, 60]
    ... )

    Notes
    -----
    This function is commonly used for:
    - Noise reduction while preserving linear features
    - Removing outliers with directional bias
    - Smoothing grids with preferred orientations
    - Cleaning geophysical data

    Directional filtering:
    - Divides area around each node into sectors
    - Calculates statistic (median, min, max) per sector
    - Takes median of sector values as final result
    - Preserves features aligned with sectors
    - Removes isolated noise points

    Sector geometry:
    - sectors=4: North, East, South, West
    - sectors=6: 60° sectors
    - sectors=8: 45° sectors (N, NE, E, SE, S, SW, W, NW)
    - More sectors = better angular resolution

    Filter diameter:
    - Larger distance = stronger smoothing
    - Should be larger than noise wavelength
    - Should be smaller than features to preserve
    - Typical: 2-10x grid spacing

    Applications:
    - Remove ship-track noise in bathymetry
    - Preserve linear features (faults, ridges)
    - Clean magnetic/gravity anomaly grids
    - Reduce along-track artifacts

    Comparison with other filters:
    - dimfilter: Directional, preserves linear features
    - grdfilter: Isotropic, smooths all directions equally
    - filter1d: 1-D filtering along tracks
    - grdmath: Arbitrary mathematical operations

    Advantages over grdfilter:
    - Better preserves linear features
    - More robust to directional artifacts
    - Good for data with acquisition patterns
    - Reduces "striping" effects

    Workflow:
    1. Identify noise characteristics and directionality
    2. Choose appropriate filter diameter
    3. Select number of sectors (4-8 typical)
    4. Apply filter and verify results
    5. Iterate if needed
    """
    # Build GMT command arguments
    args = []

    # Input grid
    args.append(str(grid))

    # Output grid (-G option)
    args.append(f"-G{outgrid}")

    # Filter (-F option) with type and distance
    # Format: -FX<width> where X is filter type (m=median by default)
    ftype = filter_type if filter_type is not None else "m"
    args.append(f"-F{ftype}{distance}")

    # Number of sectors (-N option)
    args.append(f"-N{sectors}")

    # Region (-R option)
    if region is not None:
        if isinstance(region, list):
            args.append(f"-R{'/'.join(str(x) for x in region)}")
        else:
            args.append(f"-R{region}")

    # Execute via nanobind session
    with Session() as session:
        session.call_module("dimfilter", " ".join(args))
