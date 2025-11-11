"""
grdhisteq - Perform histogram equalization for a grid.

Module-level function (not a Figure method).
"""

from typing import Union, Optional, List
from pathlib import Path

from pygmt_nb.clib import Session


def grdhisteq(
    grid: Union[str, Path],
    outgrid: Union[str, Path],
    divisions: Optional[int] = None,
    quadratic: bool = False,
    gaussian: Optional[float] = None,
    region: Optional[Union[str, List[float]]] = None,
    **kwargs
):
    """
    Perform histogram equalization for a grid.

    Reads a grid and performs histogram equalization to produce a grid
    with a flat (uniform) histogram or Gaussian distribution. This is useful
    for enhancing contrast in grid visualizations.

    Based on PyGMT's grdhisteq implementation for API compatibility.

    Parameters
    ----------
    grid : str or Path
        Input grid file name.
    outgrid : str or Path
        Output grid file name with equalized values.
    divisions : int, optional
        Number of divisions in the cumulative distribution function.
        Default is 16. Higher values give smoother equalization.
    quadratic : bool, optional
        Perform quadratic equalization rather than linear (default: False).
        This can produce better results for some data distributions.
    gaussian : float, optional
        Normalize to a Gaussian distribution with given standard deviation
        instead of uniform distribution. If not specified, produces uniform
        distribution (flat histogram).
    region : str or list, optional
        Subregion of grid to use. Format: [xmin, xmax, ymin, ymax]
        If not specified, uses entire grid.

    Returns
    -------
    None
        Writes equalized grid to file.

    Examples
    --------
    >>> import pygmt
    >>> # Basic histogram equalization
    >>> pygmt.grdhisteq(
    ...     grid="@earth_relief_01d",
    ...     outgrid="relief_equalized.nc"
    ... )
    >>>
    >>> # More divisions for smoother result
    >>> pygmt.grdhisteq(
    ...     grid="data.nc",
    ...     outgrid="data_eq.nc",
    ...     divisions=32
    ... )
    >>>
    >>> # Quadratic equalization
    >>> pygmt.grdhisteq(
    ...     grid="data.nc",
    ...     outgrid="data_quad_eq.nc",
    ...     divisions=20,
    ...     quadratic=True
    ... )
    >>>
    >>> # Normalize to Gaussian distribution
    >>> pygmt.grdhisteq(
    ...     grid="data.nc",
    ...     outgrid="data_gaussian.nc",
    ...     gaussian=1.0  # std dev = 1.0
    ... )
    >>>
    >>> # Equalize subregion only
    >>> pygmt.grdhisteq(
    ...     grid="global.nc",
    ...     outgrid="pacific_eq.nc",
    ...     region=[120, 240, -60, 60]
    ... )

    Notes
    -----
    This function is commonly used for:
    - Enhancing visual contrast in grid images
    - Normalizing data distributions
    - Preparing grids for visualization
    - Creating uniform or Gaussian distributions

    Histogram equalization:
    - Transforms data to have flat (uniform) histogram
    - Spreads out frequent values more evenly
    - Enhances contrast by redistributing values
    - Particularly useful for visualization

    Equalization types:
    - Linear (default): Simple cumulative distribution function
    - Quadratic (-Q): Better for skewed distributions
    - Gaussian (-N): Normalize to Gaussian with specified std dev

    Workflow:
    1. Compute cumulative distribution function (CDF)
    2. Divide CDF into N divisions
    3. Remap grid values to equalized values
    4. Output has uniform or Gaussian distribution

    Applications:
    - Topography visualization enhancement
    - Geophysical data normalization
    - Image processing for grids
    - Statistical data transformation

    Comparison with other grid operations:
    - grdhisteq: Changes data distribution to uniform/Gaussian
    - grdclip: Clips values at thresholds
    - grdfilter: Spatial filtering/smoothing
    - grdmath: Arbitrary mathematical operations
    """
    # Build GMT command arguments
    args = []

    # Input grid
    args.append(str(grid))

    # Output grid (-G option)
    args.append(f"-G{outgrid}")

    # Divisions (-C option)
    if divisions is not None:
        args.append(f"-C{divisions}")

    # Quadratic (-Q option)
    if quadratic:
        args.append("-Q")

    # Gaussian normalization (-N option)
    if gaussian is not None:
        args.append(f"-N{gaussian}")

    # Region (-R option)
    if region is not None:
        if isinstance(region, list):
            args.append(f"-R{'/'.join(str(x) for x in region)}")
        else:
            args.append(f"-R{region}")

    # Execute via nanobind session
    with Session() as session:
        session.call_module("grdhisteq", " ".join(args))
