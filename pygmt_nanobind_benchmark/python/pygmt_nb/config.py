"""
config - Get and set GMT parameters.

Module-level function (not a Figure method).
"""

from typing import Union, Optional, Dict, Any
from pathlib import Path

from pygmt_nb.clib import Session


def config(**kwargs):
    """
    Get and set GMT default parameters.

    This function allows you to modify GMT defaults that affect plot
    appearance, behavior, and output. Changes are temporary and only
    affect the current Python session.

    Based on PyGMT's config implementation for API compatibility.

    Parameters
    ----------
    **kwargs : dict
        GMT parameter names and their new values.
        Examples: FONT_TITLE="12p,Helvetica,black", MAP_FRAME_TYPE="plain"

    Returns
    -------
    None
        Sets GMT parameters for the current session.

    Examples
    --------
    >>> import pygmt
    >>> # Set font for plot title
    >>> pygmt.config(FONT_TITLE="14p,Helvetica-Bold,red")
    >>>
    >>> # Set frame type
    >>> pygmt.config(MAP_FRAME_TYPE="fancy")
    >>>
    >>> # Set multiple parameters
    >>> pygmt.config(
    ...     FONT_ANNOT_PRIMARY="10p,Helvetica,black",
    ...     FONT_LABEL="12p,Helvetica,black",
    ...     MAP_FRAME_WIDTH="2p"
    ... )
    >>>
    >>> # Common settings
    >>> pygmt.config(
    ...     FORMAT_GEO_MAP="ddd:mm:ssF",  # Coordinate format
    ...     PS_MEDIA="A4",                 # Paper size
    ...     PS_PAGE_ORIENTATION="landscape" # Orientation
    ... )

    Notes
    -----
    This function is commonly used for:
    - Customizing plot appearance
    - Setting default fonts and colors
    - Configuring coordinate formats
    - Adjusting frame and annotation styles

    Common GMT parameters:

    **Fonts**:
    - FONT_ANNOT_PRIMARY: Annotation font
    - FONT_ANNOT_SECONDARY: Secondary annotation font
    - FONT_LABEL: Axis label font
    - FONT_TITLE: Title font

    **Pens and Lines**:
    - MAP_FRAME_PEN: Frame pen
    - MAP_GRID_PEN_PRIMARY: Primary grid pen
    - MAP_TICK_PEN_PRIMARY: Tick mark pen

    **Frame and Layout**:
    - MAP_FRAME_TYPE: "plain", "fancy", "fancy+", "graph", "inside"
    - MAP_FRAME_WIDTH: Frame width
    - MAP_TITLE_OFFSET: Title offset

    **Format**:
    - FORMAT_GEO_MAP: Geographic coordinate format
    - FORMAT_DATE_MAP: Date format
    - FORMAT_TIME_MAP: Time format

    **Color**:
    - COLOR_BACKGROUND: Background color
    - COLOR_FOREGROUND: Foreground color
    - COLOR_NAN: NaN color

    **PostScript**:
    - PS_MEDIA: Paper size (A4, Letter, etc.)
    - PS_PAGE_ORIENTATION: portrait/landscape
    - PS_LINE_CAP: Line cap style

    **Projection**:
    - PROJ_ELLIPSOID: Reference ellipsoid
    - PROJ_LENGTH_UNIT: Length unit (cm, inch, point)

    Parameter format:
    - Fonts: "size,fontname,color" (e.g., "12p,Helvetica,black")
    - Pens: "width,color,style" (e.g., "1p,black,solid")
    - Colors: Color names or RGB (e.g., "red", "128/0/0")
    - Sizes: Value with unit (e.g., "10p", "2c", "1i")

    Scope:
    - Changes are session-specific
    - Do not persist after Python exits
    - Override ~/.gmt/gmt.conf if exists
    - Can be reset with gmt.config(PARAMETER=default_value)

    Best practices:
    - Set at beginning of script for consistency
    - Group related settings together
    - Use comments to document choices
    - Test with different output formats

    Applications:
    - Publication-quality figures
    - Custom plotting styles
    - Multi-language support
    - Scientific notation control
    - Grid and coordinate display

    Comparison with gmt.conf:
    - config(): Temporary, Python session only
    - gmt.conf: Permanent, affects all GMT usage
    - config() overrides gmt.conf settings

    For full parameter list, see GMT documentation:
    https://docs.generic-mapping-tools.org/latest/gmt.conf.html
    """
    # Execute via nanobind session
    with Session() as session:
        for key, value in kwargs.items():
            # Use gmtset module to set configuration
            session.call_module("gmtset", f"{key}={value}")
