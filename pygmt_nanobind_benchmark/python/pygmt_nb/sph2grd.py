"""
sph2grd - Compute grid from spherical harmonic coefficients.

Module-level function (not a Figure method).
"""

from pathlib import Path

from pygmt_nb.clib import Session


def sph2grd(
    data: str | Path,
    outgrid: str | Path,
    region: str | list[float] = None,
    spacing: str | list[float] = None,
    normalize: str | None = None,
    **kwargs,
):
    """
    Compute grid from spherical harmonic coefficients.

    Reads spherical harmonic coefficients and evaluates the spherical
    harmonic model on a regular geographic grid.

    Based on PyGMT's sph2grd implementation for API compatibility.

    Parameters
    ----------
    data : str or Path
        Input file with spherical harmonic coefficients.
        Format: degree order cos-coefficient sin-coefficient
    outgrid : str or Path
        Output grid file name.
    region : str or list
        Grid bounds. Format: [lonmin, lonmax, latmin, latmax]
        Required parameter.
    spacing : str or list
        Grid spacing. Format: "xinc[unit][/yinc[unit]]" or [xinc, yinc]
        Required parameter.
    normalize : str, optional
        Normalization type for coefficients:
        - None : No normalization (default)
        - "g" : Geodesy normalization (4π normalized)
        - "s" : Schmidt normalization

    Returns
    -------
    None
        Writes grid to file.

    Examples
    --------
    >>> import pygmt
    >>> # Convert spherical harmonic coefficients to grid
    >>> pygmt.sph2grd(
    ...     data="coefficients.txt",
    ...     outgrid="harmonics_grid.nc",
    ...     region=[-180, 180, -90, 90],
    ...     spacing=1
    ... )
    >>>
    >>> # With geodesy normalization
    >>> pygmt.sph2grd(
    ...     data="geoid_coeffs.txt",
    ...     outgrid="geoid.nc",
    ...     region=[0, 360, -90, 90],
    ...     spacing=0.5,
    ...     normalize="g"
    ... )
    >>>
    >>> # Regional grid from global coefficients
    >>> pygmt.sph2grd(
    ...     data="global_model.txt",
    ...     outgrid="pacific.nc",
    ...     region=[120, 240, -60, 60],
    ...     spacing=0.25
    ... )

    Notes
    -----
    This function is commonly used for:
    - Geoid model evaluation
    - Gravity/magnetic field modeling
    - Topography/bathymetry from harmonic models
    - Climate/atmospheric field reconstruction

    Spherical harmonics:
    - Mathematical basis functions on sphere
    - Degree n, order m coefficients
    - Complete orthogonal set
    - Efficient for global smooth fields

    Input format:
    Each line contains:
    - Degree (n)
    - Order (m)
    - Cosine coefficient (Cnm)
    - Sine coefficient (Snm)

    Example coefficient file:
    ```
    0 0 1.0 0.0
    1 0 0.5 0.0
    1 1 0.2 0.3
    2 0 0.1 0.0
    ...
    ```

    Normalization:
    - Unnormalized: Standard mathematical definition
    - Geodesy (4π): Used in gravity/geoid models
    - Schmidt: Used in geomagnetic field models

    Applications:
    - EGM2008/WGS84 geoid evaluation
    - IGRF geomagnetic field models
    - Topography models (e.g., SRTM harmonics)
    - Satellite gravity missions (GRACE, GOCE)

    Comparison with related functions:
    - sph2grd: Evaluate harmonics on grid
    - grdspectrum: Compute spectrum from grid
    - sphinterpolate: Interpolate scattered data
    - surface: Cartesian surface fitting

    Advantages:
    - Compact representation of smooth global fields
    - Easy to filter by degree (wavelength)
    - Analytically differentiable
    - No edge effects or boundaries

    Workflow:
    1. Obtain spherical harmonic coefficients
    2. Choose evaluation region and resolution
    3. Select appropriate normalization
    4. Generate grid from coefficients
    5. Visualize or analyze results

    Maximum degree considerations:
    - Higher degree = finer spatial resolution
    - Degree n wavelength ≈ 40000km / (n+1)
    - Computation time increases with degree²
    - Typical: n=360 for 0.5° resolution
    """
    # Build GMT command arguments
    args = []

    # Input data file
    args.append(str(data))

    # Output grid (-G option)
    args.append(f"-G{outgrid}")

    # Region (-R option) - required
    if region is not None:
        if isinstance(region, list):
            args.append(f"-R{'/'.join(str(x) for x in region)}")
        else:
            args.append(f"-R{region}")
    else:
        raise ValueError("region parameter is required for sph2grd()")

    # Spacing (-I option) - required
    if spacing is not None:
        if isinstance(spacing, list):
            args.append(f"-I{'/'.join(str(x) for x in spacing)}")
        else:
            args.append(f"-I{spacing}")
    else:
        raise ValueError("spacing parameter is required for sph2grd()")

    # Normalization (-N option)
    if normalize is not None:
        args.append(f"-N{normalize}")

    # Execute via nanobind session
    with Session() as session:
        session.call_module("sph2grd", " ".join(args))
