"""
legend - PyGMT-compatible plotting method.

Modern mode implementation using nanobind.
"""

from typing import Union, Optional, List
from pathlib import Path
import numpy as np


def legend(
    self,
    spec: Optional[Union[str, Path]] = None,
    position: str = "JTR+jTR+o0.2c",
    box: Union[bool, str] = True,
    **kwargs
):
    """
    Plot a legend on the map.

    Makes legends that can be overlaid on maps. Unless a legend specification
    is provided via `spec`, it will use the automatically generated legend
    entries from plotted symbols that have labels.

    Based on PyGMT's legend implementation for API compatibility.

    Parameters
    ----------
    spec : str or Path, optional
        Path to legend specification file. If None, uses automatically
        generated legend from labeled plot elements.
    position : str, default "JTR+jTR+o0.2c"
        Position of the legend on the map. Format: [g|j|J|n|x]refpoint.
        Default places legend at top-right corner with 0.2cm offset.
    box : bool or str, default True
        Draw a box around the legend. If True, uses default box.
        Can be a string with box specifications (e.g., "+gwhite+p1p").
    **kwargs
        Additional GMT options.

    Examples
    --------
    >>> fig = pygmt.Figure()
    >>> fig.basemap(region=[0, 10, 0, 10], projection="X10c", frame=True)
    >>> fig.plot(x=[2, 5, 8], y=[3, 7, 4], style="c0.3c", color="red", label="Data")
    >>> fig.legend()
    """
    # Build GMT command arguments
    args = []

    # Position (-D option)
    args.append(f"-D{position}")

    # Box around legend (-F option)
    if box:
        if isinstance(box, str):
            args.append(f"-F{box}")
        else:
            args.append("-F+gwhite+p1p")  # Default: white background, 1pt border

    # Legend specification file
    if spec is not None:
        spec_path = str(spec)
        args.append(spec_path)

    # Execute via nanobind
    self._session.call_module("legend", " ".join(args))
