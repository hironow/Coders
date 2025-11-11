"""
x2sys_init - Initialize a new X2SYS track database.

Module-level function (not a Figure method).
"""

from typing import Union, Optional


def x2sys_init(
    tag: str,
    suffix: str,
    units: Optional[str] = None,
    gap: Optional[float] = None,
    force: bool = False,
    **kwargs
):
    """
    Initialize a new X2SYS track database.

    Creates configuration for analyzing track data (ship tracks, flight lines,
    satellite ground tracks, etc.). Must be run before using other X2SYS tools
    like x2sys_cross.

    Parameters
    ----------
    tag : str
        Name for this X2SYS tag (database identifier).
        Examples: "SHIP", "FLIGHT", "MGD77"
    suffix : str
        File suffix for track data files.
        Examples: "txt", "dat", "nc"
    units : str, optional
        Distance units and data format:
        - "de" : Distance in meters, geographic coordinates
        - "df" : Distance in feet, geographic coordinates
        - "c" : Cartesian coordinates
        - "g" : Geographic coordinates
    gap : float, optional
        Maximum gap (in distance units) between points in a track.
        Points further apart start a new segment.
    force : bool, optional
        If True, overwrite existing tag (default: False).

    Returns
    -------
    None
        Creates X2SYS configuration files.

    Examples
    --------
    >>> import pygmt
    >>> # Initialize for ship tracks
    >>> pygmt.x2sys_init(
    ...     tag="SHIP",
    ...     suffix="txt",
    ...     units="de",
    ...     gap=10000  # 10 km
    ... )
    >>>
    >>> # Initialize for flight lines
    >>> pygmt.x2sys_init(
    ...     tag="FLIGHT",
    ...     suffix="dat",
    ...     units="de",
    ...     gap=5000  # 5 km
    ... )
    >>>
    >>> # Force overwrite existing tag
    >>> pygmt.x2sys_init(
    ...     tag="SHIP",
    ...     suffix="txt",
    ...     units="de",
    ...     force=True
    ... )

    Notes
    -----
    This function is commonly used for:
    - Setting up crossover analysis
    - Initializing survey databases
    - Configuring track data types
    - Quality control preparation

    X2SYS system:
    - Flexible framework for track data
    - Handles various data formats
    - Supports multiple data types
    - Tag-based configuration

    Tag configuration includes:
    - File suffix pattern
    - Distance units
    - Data column definitions
    - Gap tolerance
    - Coordinate system

    Data types supported:
    - Marine surveys (bathymetry, magnetics, gravity)
    - Airborne surveys (magnetics, gravity, radar)
    - Satellite altimetry
    - Any along-track data

    Gap handling:
    - Defines track segments
    - Prevents false crossovers
    - Important for data quality
    - Typical: 10-50 km for ships

    Directory structure:
    X2SYS creates directories in ~/.gmt/x2sys/
    - TAG/: Configuration directory
    - TAG.def: Definition file
    - TAG.tag: Tag file

    Workflow:
    1. x2sys_init: Set up database
    2. x2sys_cross: Find crossovers
    3. x2sys_list: List results
    4. Analysis and corrections

    Common tags:
    - SHIP: Ship-track bathymetry
    - MGD77: Marine geophysical data
    - FLIGHT: Airborne surveys
    - SAT: Satellite altimetry

    Units options:
    - de: meters + geographic (most common)
    - df: feet + geographic
    - c: Cartesian coordinates
    - g: Geographic only

    Applications:
    - Bathymetry quality control
    - Magnetic survey analysis
    - Gravity field mapping
    - Multi-campaign integration

    See Also
    --------
    x2sys_cross : Find track crossovers
    x2sys_list : List crossover information
    """
    from pygmt_nb.clib import Session

    # Build GMT command
    args = []

    # Tag (-T option)
    args.append(f"-T{tag}")

    # Suffix (-S option)
    args.append(f"-S{suffix}")

    # Units (-D option)
    if units is not None:
        args.append(f"-D{units}")

    # Gap (-G option)
    if gap is not None:
        args.append(f"-G{gap}")

    # Force (-F option)
    if force:
        args.append("-F")

    # Execute via session
    with Session() as session:
        session.call_module("x2sys_init", " ".join(args))
