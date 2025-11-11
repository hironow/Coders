"""
x2sys_cross - Calculate crossover errors between track data files.

Module-level function (not a Figure method).
"""

from typing import Union, Optional, List
from pathlib import Path


def x2sys_cross(
    tracks: Union[str, List[str], Path, List[Path]],
    tag: str,
    output: Optional[Union[str, Path]] = None,
    interpolation: Optional[str] = None,
    **kwargs
):
    """
    Calculate crossover errors between track data files.

    Finds locations where tracks intersect (crossovers) and calculates
    the differences in measured values. Used for quality control of
    survey data and systematic error detection.

    Parameters
    ----------
    tracks : str or list or Path or list of Path
        Track file name(s) to analyze for crossovers.
        Can be single file or list of files.
    tag : str
        X2SYS tag name defining the track data type.
        Must be initialized with x2sys_init first.
    output : str or Path, optional
        Output file for crossover results.
        If not specified, returns as array/string.
    interpolation : str, optional
        Interpolation method at crossovers:
        - "l" : Linear interpolation (default)
        - "a" : Akima spline
        - "c" : Cubic spline

    Returns
    -------
    array or None
        If output is None, returns crossover data as array.
        Otherwise writes to file and returns None.

    Examples
    --------
    >>> import pygmt
    >>> # Initialize X2SYS for ship tracks
    >>> pygmt.x2sys_init(
    ...     tag="SHIP",
    ...     suffix="txt",
    ...     units="de",
    ...     gap=10
    ... )
    >>>
    >>> # Find crossovers in tracks
    >>> crossovers = pygmt.x2sys_cross(
    ...     tracks=["track1.txt", "track2.txt"],
    ...     tag="SHIP"
    ... )
    >>>
    >>> # Save crossovers to file
    >>> pygmt.x2sys_cross(
    ...     tracks="track*.txt",
    ...     tag="SHIP",
    ...     output="crossovers.txt"
    ... )

    Notes
    -----
    This function is commonly used for:
    - Survey quality control
    - Systematic error detection
    - Data consistency checking
    - Calibration verification

    Crossover analysis:
    - Identifies where tracks intersect
    - Computes value differences at crossovers
    - Statistics reveal systematic errors
    - Used to adjust/correct data

    Crossover types:
    - Internal: Same track crosses itself
    - External: Different tracks cross
    - Both are important for QC

    Applications:
    - Marine surveys: Ship-track bathymetry
    - Aeromagnetics: Flight-line data
    - Gravity surveys: Profile data
    - Satellite altimetry: Ground tracks

    Output columns:
    - Track IDs
    - Crossover location (lon, lat)
    - Time/distance along each track
    - Value difference
    - Statistics

    Quality indicators:
    - Mean crossover error (bias)
    - RMS crossover error (precision)
    - Number of crossovers
    - Spatial distribution

    Workflow:
    1. Initialize X2SYS with x2sys_init
    2. Run x2sys_cross to find crossovers
    3. Analyze crossover statistics
    4. Apply corrections if needed
    5. Re-run to verify improvement

    X2SYS system:
    - Flexible track data framework
    - Handles various data types
    - Supports different formats
    - Tag system for configuration

    See Also
    --------
    x2sys_init : Initialize X2SYS database
    x2sys_list : Get information about crossovers
    """
    from pygmt_nb.clib import Session
    import numpy as np
    import tempfile

    # Build GMT command
    args = []

    # Tag (-T option)
    args.append(f"-T{tag}")

    # Interpolation (-I option)
    if interpolation is not None:
        args.append(f"-I{interpolation}")

    # Handle track files
    if isinstance(tracks, str):
        track_list = [tracks]
    elif isinstance(tracks, (list, tuple)):
        track_list = [str(t) for t in tracks]
    else:
        track_list = [str(tracks)]

    # Execute via session
    with Session() as session:
        if output is not None:
            # Write to file
            session.call_module("x2sys_cross", " ".join(track_list) + " " + " ".join(args) + f" ->{output}")
            return None
        else:
            # Return as array
            with tempfile.NamedTemporaryFile(mode='w+', suffix='.txt', delete=False) as tmp:
                outfile = tmp.name

            try:
                session.call_module("x2sys_cross", " ".join(track_list) + " " + " ".join(args) + f" ->{outfile}")

                # Read result
                result = np.loadtxt(outfile)
                return result
            except Exception as e:
                print(f"Note: x2sys_cross requires initialized X2SYS tag: {e}")
                return None
            finally:
                import os
                if os.path.exists(outfile):
                    os.unlink(outfile)
