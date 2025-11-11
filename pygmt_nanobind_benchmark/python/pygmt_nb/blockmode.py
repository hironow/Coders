"""
blockmode - Block average (x,y,z) data tables by mode estimation.

Module-level function (not a Figure method).
"""

import os
import tempfile
from pathlib import Path

import numpy as np

from pygmt_nb.clib import Session


def blockmode(
    data: np.ndarray | list | str | Path | None = None,
    x: np.ndarray | None = None,
    y: np.ndarray | None = None,
    z: np.ndarray | None = None,
    output: str | Path | None = None,
    region: str | list[float] | None = None,
    spacing: str | list[float] | None = None,
    registration: str | None = None,
    **kwargs,
) -> np.ndarray | None:
    """
    Block average (x,y,z) data tables by mode estimation.

    Reads arbitrarily located (x,y,z) data and computes the mode
    (most common value) position and value for each block in a grid
    region. Useful for categorical or discrete data.

    Based on PyGMT's blockmode implementation for API compatibility.

    Parameters
    ----------
    data : array-like or str or Path, optional
        Input data. Can be:
        - 2-D numpy array with x, y, z columns
        - Path to ASCII data file with x, y, z columns
    x, y, z : array-like, optional
        x, y, and z coordinates as separate 1-D arrays.
    output : str or Path, optional
        Output file name. If not specified, returns numpy array.
    region : str or list, optional
        Grid bounds. Format: [xmin, xmax, ymin, ymax] or "xmin/xmax/ymin/ymax"
        Required parameter.
    spacing : str or list, optional
        Block size. Format: "xinc[unit][+e|n][/yinc[unit][+e|n]]" or [xinc, yinc]
        Required parameter.
    registration : str, optional
        Grid registration type:
        - "g" or None : gridline registration (default)
        - "p" : pixel registration

    Returns
    -------
    result : ndarray or None
        Array with block mode values (x, y, z) if output is None.
        None if data is saved to file.

    Examples
    --------
    >>> import numpy as np
    >>> import pygmt
    >>> # Create scattered categorical data
    >>> x = np.random.rand(1000) * 10
    >>> y = np.random.rand(1000) * 10
    >>> # Categorical z values (e.g., land types: 1, 2, 3)
    >>> z = np.random.choice([1, 2, 3], size=1000)
    >>> # Block mode to find most common category per block
    >>> modes = pygmt.blockmode(
    ...     x=x, y=y, z=z,
    ...     region=[0, 10, 0, 10],
    ...     spacing=1.0
    ... )
    >>> print(f"Reduced {len(x)} points to {len(modes)} blocks")
    >>> print(f"Mode values: {np.unique(modes[:, 2])}")
    >>>
    >>> # From data array
    >>> data = np.column_stack([x, y, z])
    >>> modes = pygmt.blockmode(
    ...     data=data,
    ...     region=[0, 10, 0, 10],
    ...     spacing=0.5
    ... )
    >>>
    >>> # From file
    >>> pygmt.blockmode(
    ...     data="categorical_data.txt",
    ...     output="mode_averaged.txt",
    ...     region=[0, 10, 0, 10],
    ...     spacing=1.0
    ... )

    Notes
    -----
    This function is commonly used for:
    - Categorical data aggregation
    - Land cover classification
    - Discrete value consensus
    - Majority voting in spatial bins

    Comparison with related functions:
    - blockmean: Mean value per block (for continuous data)
    - blockmedian: Median value per block (robust to outliers)
    - blockmode: Mode value per block (most common, for categorical data)

    Mode characteristics:
    - Returns most frequently occurring value
    - Ideal for categorical/discrete data
    - Not affected by outliers
    - May not be unique if multiple modes exist

    Use blockmode when:
    - Data is categorical (land types, classes, etc.)
    - Want majority value per block
    - Dealing with discrete classifications
    - Need consensus value from multiple observations

    Important note:
    - For continuous data, mode may not be meaningful
    - Works best with discrete or binned values
    - If no clear mode, results may be arbitrary
    """
    # Build GMT command arguments
    args = []

    # Region (-R option) - required
    if region is not None:
        if isinstance(region, list):
            args.append(f"-R{'/'.join(str(x) for x in region)}")
        else:
            args.append(f"-R{region}")
    else:
        raise ValueError("region parameter is required for blockmode()")

    # Spacing (-I option) - required
    if spacing is not None:
        if isinstance(spacing, list):
            args.append(f"-I{'/'.join(str(x) for x in spacing)}")
        else:
            args.append(f"-I{spacing}")
    else:
        raise ValueError("spacing parameter is required for blockmode()")

    # Registration (-r option for pixel)
    if registration is not None:
        if registration == "p":
            args.append("-r")

    # Prepare output
    if output is not None:
        outfile = str(output)
        return_array = False
    else:
        # Temp file for array output
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            outfile = f.name
        return_array = True

    try:
        with Session() as session:
            # Handle data input
            if data is not None:
                if isinstance(data, (str, Path)):
                    # File input
                    session.call_module("blockmode", f"{data} " + " ".join(args) + f" ->{outfile}")
                else:
                    # Array input - use virtual file
                    data_array = np.atleast_2d(np.asarray(data, dtype=np.float64))

                    # Check for 3 columns (x, y, z)
                    if data_array.shape[1] < 3:
                        raise ValueError(
                            f"data array must have at least 3 columns (x, y, z), got {data_array.shape[1]}"
                        )

                    # Create vectors for virtual file (x, y, z)
                    vectors = [data_array[:, i] for i in range(min(3, data_array.shape[1]))]

                    with session.virtualfile_from_vectors(*vectors) as vfile:
                        session.call_module(
                            "blockmode", f"{vfile} " + " ".join(args) + f" ->{outfile}"
                        )

            elif x is not None and y is not None and z is not None:
                # Separate x, y, z arrays
                x_array = np.asarray(x, dtype=np.float64).ravel()
                y_array = np.asarray(y, dtype=np.float64).ravel()
                z_array = np.asarray(z, dtype=np.float64).ravel()

                with session.virtualfile_from_vectors(x_array, y_array, z_array) as vfile:
                    session.call_module("blockmode", f"{vfile} " + " ".join(args) + f" ->{outfile}")
            else:
                raise ValueError("Must provide either 'data' or 'x', 'y', 'z' parameters")

        # Read output if returning array
        if return_array:
            result = np.loadtxt(outfile)
            # Ensure 2D array
            if result.ndim == 1:
                result = result.reshape(1, -1)
            return result
        else:
            return None
    finally:
        if return_array and os.path.exists(outfile):
            os.unlink(outfile)
