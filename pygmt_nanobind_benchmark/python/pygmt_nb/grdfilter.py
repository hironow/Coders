"""
grdfilter - Filter a grid in the space domain.

Module-level function (not a Figure method).
"""

from typing import Union, Optional, List, Literal
from pathlib import Path

from pygmt_nb.clib import Session


def grdfilter(
    grid: Union[str, Path],
    outgrid: Union[str, Path],
    filter: Optional[str] = None,
    distance: Optional[Union[str, float]] = None,
    region: Optional[Union[str, List[float]]] = None,
    spacing: Optional[Union[str, List[float]]] = None,
    nans: Optional[str] = None,
    **kwargs
):
    """
    Filter a grid file in the space (x,y) domain.

    Performs spatial filtering of grids using one of several filter types.
    Commonly used for smoothing, removing noise, or finding local extrema.

    Based on PyGMT's grdfilter implementation for API compatibility.

    Parameters
    ----------
    grid : str or Path
        Input grid file to be filtered.
    outgrid : str or Path
        Output filtered grid file.
    filter : str, optional
        Filter type and full width. Format: "type[width]"
        Filter types:
        - "b" : Boxcar (simple average)
        - "c" : Cosine arch
        - "g" : Gaussian
        - "m" : Median
        - "p" : Maximum likelihood (mode)
        Example: "g3" for Gaussian filter with 3 unit width
        Required parameter for filtering.
    distance : str or float, optional
        Distance flag for grid spacing units:
        - 0 : grid cells (default)
        - 1 : geographic distances (use if grid is in degrees)
        - 2 : actual distances in the grid's units
    region : str or list, optional
        Subregion to operate on. Format: [xmin, xmax, ymin, ymax]
    spacing : str or list, optional
        Output grid spacing (if different from input).
    nans : str, optional
        How to handle NaN values:
        - "i" : ignore NaNs in calculations
        - "p" : preserve NaNs (default behavior)
        - "r" : replace NaNs with filtered values where possible

    Examples
    --------
    >>> import pygmt
    >>> # Apply Gaussian filter
    >>> pygmt.grdfilter(
    ...     grid="@earth_relief_01d_g",
    ...     outgrid="smooth.nc",
    ...     filter="g100",  # 100 km Gaussian
    ...     distance=1,
    ...     region=[0, 10, 0, 10]
    ... )
    >>>
    >>> # Median filter for noise removal
    >>> pygmt.grdfilter(
    ...     grid="noisy_data.nc",
    ...     outgrid="cleaned.nc",
    ...     filter="m5"  # 5-unit median filter
    ... )

    Notes
    -----
    Spatial filters are useful for:
    - Smoothing noisy data (Gaussian, boxcar)
    - Removing outliers (median)
    - Finding local modes (maximum likelihood)

    The filter width should be appropriate for your data resolution
    and the spatial scale of features you want to preserve/remove.
    """
    # Build GMT command arguments
    args = []

    # Input grid
    args.append(str(grid))

    # Output grid (-G option)
    args.append(f"-G{outgrid}")

    # Filter type and width (-F option) - required
    if filter is not None:
        args.append(f"-F{filter}")
    else:
        raise ValueError("filter parameter is required for grdfilter()")

    # Distance flag (-D option)
    if distance is not None:
        args.append(f"-D{distance}")

    # Region (-R option)
    if region is not None:
        if isinstance(region, list):
            args.append(f"-R{'/'.join(str(x) for x in region)}")
        else:
            args.append(f"-R{region}")

    # Spacing (-I option)
    if spacing is not None:
        if isinstance(spacing, list):
            args.append(f"-I{'/'.join(str(x) for x in spacing)}")
        else:
            args.append(f"-I{spacing}")

    # NaN handling (-N option)
    if nans is not None:
        args.append(f"-N{nans}")

    # Execute via nanobind session
    with Session() as session:
        session.call_module("grdfilter", " ".join(args))
