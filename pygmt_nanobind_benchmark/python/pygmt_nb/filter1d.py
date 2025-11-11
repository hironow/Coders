"""
filter1d - Time domain filtering of 1-D data tables.

Module-level function (not a Figure method).
"""

import os
import tempfile
from pathlib import Path

import numpy as np

from pygmt_nb.clib import Session


def filter1d(
    data: np.ndarray | list | str | Path,
    output: str | Path | None = None,
    filter_type: str | None = None,
    filter_width: float | str | None = None,
    high_pass: float | None = None,
    low_pass: float | None = None,
    time_col: int = 0,
    **kwargs,
) -> np.ndarray | None:
    """
    Time domain filtering of 1-D data tables.

    Reads a table with one or more time series and applies a
    time-domain filter. Multiple filter types are available including
    boxcar, cosine arch, Gaussian, and median.

    Based on PyGMT's filter1d implementation for API compatibility.

    Parameters
    ----------
    data : array-like or str or Path
        Input data. Can be:
        - 2-D numpy array with time and data columns
        - Path to ASCII data file
    output : str or Path, optional
        Output file name. If not specified, returns numpy array.
    filter_type : str, optional
        Filter type:
        - "b" : Boxcar (simple moving average)
        - "c" : Cosine arch
        - "g" : Gaussian
        - "m" : Median
        - "p" : Maximum likelihood (mode)
        - "l" : Lower (minimum)
        - "u" : Upper (maximum)
        Default: "g" (Gaussian)
    filter_width : float or str, optional
        Full width of filter. Required parameter.
        Can include units (e.g., "5k" for 5000).
    high_pass : float, optional
        High-pass filter wavelength.
        Remove variations longer than this wavelength.
    low_pass : float, optional
        Low-pass filter wavelength.
        Remove variations shorter than this wavelength.
    time_col : int, optional
        Column number for time/distance (0-indexed).
        Default: 0 (first column).

    Returns
    -------
    result : ndarray or None
        Filtered data array if output is None.
        None if data is saved to file.

    Examples
    --------
    >>> import numpy as np
    >>> import pygmt
    >>> # Create noisy time series
    >>> t = np.linspace(0, 10, 100)
    >>> signal = np.sin(t)
    >>> noise = np.random.randn(100) * 0.2
    >>> data = np.column_stack([t, signal + noise])
    >>>
    >>> # Apply Gaussian filter
    >>> filtered = pygmt.filter1d(
    ...     data=data,
    ...     filter_type="g",
    ...     filter_width=0.5
    ... )
    >>> print(filtered.shape)
    (100, 2)
    >>>
    >>> # Median filter for outlier removal
    >>> filtered = pygmt.filter1d(
    ...     data=data,
    ...     filter_type="m",
    ...     filter_width=1.0
    ... )
    >>>
    >>> # From file with output to file
    >>> pygmt.filter1d(
    ...     data="timeseries.txt",
    ...     output="filtered.txt",
    ...     filter_type="b",
    ...     filter_width=2.0
    ... )

    Notes
    -----
    This function is commonly used for:
    - Smoothing noisy time series
    - Removing high-frequency noise
    - Removing low-frequency trends
    - Outlier detection and removal (median filter)

    Filter types comparison:
    - Boxcar: Simple, fast, sharp edges in frequency domain
    - Gaussian: Smooth, no ringing, good general-purpose filter
    - Cosine: Similar to Gaussian but faster
    - Median: Robust to outliers, preserves edges

    Filter width:
    - Full width of filter window
    - Units match time column units
    - Larger width = more smoothing

    High-pass vs Low-pass:
    - High-pass: Remove long wavelengths (trends)
    - Low-pass: Remove short wavelengths (noise)
    - Can combine both for band-pass filtering
    """
    # Build GMT command arguments
    args = []

    # Filter type and width (-F option)
    if filter_type is not None and filter_width is not None:
        args.append(f"-F{filter_type}{filter_width}")
    elif filter_width is not None:
        # Default to Gaussian if only width specified
        args.append(f"-Fg{filter_width}")
    else:
        raise ValueError("filter_width parameter is required for filter1d()")

    # High-pass filter (-F option with h)
    if high_pass is not None:
        args.append(f"-Fh{high_pass}")

    # Low-pass filter (-F option with l)
    if low_pass is not None:
        args.append(f"-Fl{low_pass}")

    # Time column (-N option for number of columns, but -T for time column in some versions)
    # GMT filter1d uses first column as independent variable by default

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
            if isinstance(data, (str, Path)):
                # File input
                session.call_module("filter1d", f"{data} " + " ".join(args) + f" ->{outfile}")
            else:
                # Array input - use virtual file
                data_array = np.atleast_2d(np.asarray(data, dtype=np.float64))

                # Create vectors for virtual file
                vectors = [data_array[:, i] for i in range(data_array.shape[1])]

                with session.virtualfile_from_vectors(*vectors) as vfile:
                    session.call_module("filter1d", f"{vfile} " + " ".join(args) + f" ->{outfile}")

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
