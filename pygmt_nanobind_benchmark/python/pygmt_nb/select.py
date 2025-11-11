"""
select - Select data table subsets based on spatial criteria.

Module-level function (not a Figure method).
"""

from typing import Union, Optional, List, Literal
from pathlib import Path
import numpy as np
import tempfile
import os

from pygmt_nb.clib import Session


def select(
    data: Union[np.ndarray, List, str, Path],
    region: Optional[Union[str, List[float]]] = None,
    reverse: bool = False,
    output: Optional[Union[str, Path]] = None,
    **kwargs
) -> Union[np.ndarray, None]:
    """
    Select data table subsets based on multiple spatial criteria.

    Filters input data based on spatial criteria like region bounds.
    Can output to file or return as array.

    Based on PyGMT's select implementation for API compatibility.

    Parameters
    ----------
    data : array-like or str or Path
        Input data to filter. Can be:
        - 2-D numpy array
        - Python list
        - Path to ASCII data file
    region : str or list, optional
        Select data within this region. Format: [xmin, xmax, ymin, ymax]
        Points outside this region are rejected (or kept if reverse=True).
    reverse : bool, default False
        Reverse the selection (keep points outside region).
    output : str or Path, optional
        File path to save filtered data. If None, returns numpy array.
    **kwargs
        Additional GMT options.

    Returns
    -------
    result : ndarray or None
        Filtered data as numpy array if output is None.
        None if data is saved to file.

    Examples
    --------
    >>> import numpy as np
    >>> import pygmt
    >>> # Filter data to region
    >>> data = np.array([[1, 5], [2, 6], [10, 15]])
    >>> result = pygmt.select(data, region=[0, 5, 0, 10])
    >>> print(result)
    [[1. 5.]
     [2. 6.]]
    """
    # Build GMT command arguments
    args = []

    # Region (-R option) - for filtering
    if region is not None:
        if isinstance(region, list):
            args.append(f"-R{'/'.join(str(x) for x in region)}")
        else:
            args.append(f"-R{region}")

    # Reverse selection (-I option)
    if reverse:
        args.append("-I")

    # Prepare output
    if output is not None:
        outfile = str(output)
    else:
        # Temp file for array output
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            outfile = f.name

    try:
        with Session() as session:
            if isinstance(data, (str, Path)):
                # File input
                session.call_module("select", f"{data} " + " ".join(args) + f" ->{outfile}")
            else:
                # Array input - use virtual file
                data_array = np.atleast_2d(np.asarray(data, dtype=np.float64))

                # Create vectors
                vectors = [data_array[:, i] for i in range(data_array.shape[1])]

                with session.virtualfile_from_vectors(*vectors) as vfile:
                    session.call_module("select", f"{vfile} " + " ".join(args) + f" ->{outfile}")

        # Read output if returning array
        if output is None:
            # Load filtered data
            result = np.loadtxt(outfile)
            return result
        else:
            return None
    finally:
        if output is None and os.path.exists(outfile):
            os.unlink(outfile)
