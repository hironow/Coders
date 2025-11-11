"""
project - Project data onto lines or great circles.

Module-level function (not a Figure method).
"""

from typing import Union, Optional, List
from pathlib import Path
import numpy as np
import tempfile
import os

from pygmt_nb.clib import Session


def project(
    data: Union[np.ndarray, List, str, Path],
    center: Optional[Union[str, List[float]]] = None,
    endpoint: Optional[Union[str, List[float]]] = None,
    azimuth: Optional[float] = None,
    length: Optional[float] = None,
    width: Optional[float] = None,
    unit: Optional[str] = None,
    convention: Optional[str] = None,
    output: Optional[Union[str, Path]] = None,
    **kwargs
) -> Union[np.ndarray, None]:
    """
    Project data onto lines or great circles, or generate tracks.

    Project data points onto a line or great circle, or create a line
    defined by origin and either azimuth, second point, or pole.

    Based on PyGMT's project implementation for API compatibility.

    Parameters
    ----------
    data : array-like or str or Path
        Input data. Can be:
        - 2-D numpy array with columns for x, y (and optionally other data)
        - Path to ASCII data file
    center : str or list, optional
        Center point of projection line. Format: [lon, lat] or "lon/lat"
        Required unless generating a track.
    endpoint : str or list, optional
        End point of projection line. Format: [lon, lat] or "lon/lat"
        Use either endpoint or azimuth (not both).
    azimuth : float, optional
        Azimuth of projection line in degrees.
        Use either azimuth or endpoint (not both).
    length : float, optional
        Length of projection line (requires azimuth to be set).
    width : float, optional
        Width of projection corridor (perpendicular to line).
        Points outside this width are excluded.
    unit : str, optional
        Unit of distance. Options: "e" (meter), "k" (km), "m" (mile), etc.
    convention : str, optional
        Coordinate convention:
        - "p" : projected coordinates (along-track, cross-track)
        - "c" : original coordinates with distance information
    output : str or Path, optional
        Output file name. If not specified, returns numpy array.

    Returns
    -------
    result : ndarray or None
        Projected data array if output is None.
        None if data is saved to file.

    Examples
    --------
    >>> import numpy as np
    >>> import pygmt
    >>> # Project points onto a line
    >>> data = np.array([[1, 1], [2, 2], [3, 1], [4, 2]])
    >>> projected = pygmt.project(
    ...     data=data,
    ...     center=[0, 0],
    ...     endpoint=[5, 5]
    ... )
    >>> print(projected.shape)
    (4, 7)
    >>>
    >>> # Project with azimuth and width filtering
    >>> filtered = pygmt.project(
    ...     data=data,
    ...     center=[0, 0],
    ...     azimuth=45,
    ...     width=1.0
    ... )

    Notes
    -----
    The project module is useful for:
    - Creating profiles along lines
    - Projecting scattered data onto specific directions
    - Generating great circle tracks
    - Filtering data by distance from a line
    """
    # Build GMT command arguments
    args = []

    # Center point (-C option)
    if center is not None:
        if isinstance(center, list):
            args.append(f"-C{'/'.join(str(x) for x in center)}")
        else:
            args.append(f"-C{center}")

    # Endpoint (-E option) or Azimuth (-A option)
    if endpoint is not None:
        if isinstance(endpoint, list):
            args.append(f"-E{'/'.join(str(x) for x in endpoint)}")
        else:
            args.append(f"-E{endpoint}")
    elif azimuth is not None:
        args.append(f"-A{azimuth}")

    # Length (-L option)
    if length is not None:
        if isinstance(length, list):
            args.append(f"-L{'/'.join(str(x) for x in length)}")
        else:
            args.append(f"-L{length}")

    # Width (-W option)
    if width is not None:
        args.append(f"-W{width}")

    # Unit (-N option for flat Earth, -G for geodesic)
    if unit is not None:
        args.append(f"-G{unit}")

    # Convention (-F option for output format)
    if convention is not None:
        args.append(f"-F{convention}")

    # Prepare output
    if output is not None:
        outfile = str(output)
        return_array = False
    else:
        # Temp file for array output
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            outfile = f.name
        return_array = True

    try:
        with Session() as session:
            if isinstance(data, (str, Path)):
                # File input
                session.call_module("project", f"{data} " + " ".join(args) + f" ->{outfile}")
            else:
                # Array input - use virtual file
                data_array = np.atleast_2d(np.asarray(data, dtype=np.float64))

                # Create vectors for virtual file
                vectors = [data_array[:, i] for i in range(data_array.shape[1])]

                with session.virtualfile_from_vectors(*vectors) as vfile:
                    session.call_module("project", f"{vfile} " + " ".join(args) + f" ->{outfile}")

        # Read output if returning array
        if return_array:
            result = np.loadtxt(outfile)
            # Ensure 2D array (handle single point case)
            if result.ndim == 1:
                result = result.reshape(1, -1)
            return result
        else:
            return None
    finally:
        if return_array and os.path.exists(outfile):
            os.unlink(outfile)
