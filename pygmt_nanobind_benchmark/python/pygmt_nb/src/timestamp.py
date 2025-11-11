"""
timestamp - Plot timestamp on maps.

Figure method (not a standalone module function).
"""



def timestamp(
    self,
    text: str | None = None,
    position: str | None = None,
    offset: str | None = None,
    font: str | None = None,
    justify: str | None = None,
    **kwargs,
):
    """
    Plot timestamp on maps.

    Adds a timestamp (date/time) label to the map, typically in a corner
    to document when the map was created. Useful for version control and
    documentation.

    Parameters
    ----------
    text : str, optional
        Custom text to display. Can include special codes:
        - "%Y" : 4-digit year
        - "%y" : 2-digit year
        - "%m" : Month (01-12)
        - "%d" : Day (01-31)
        - "%H" : Hour (00-23)
        - "%M" : Minute (00-59)
        - "%S" : Second (00-59)
        If not specified, uses default GMT timestamp format.
    position : str, optional
        Position on the map.
        Format: "corner" where corner is one of:
        - "TL" : Top Left
        - "TC" : Top Center
        - "TR" : Top Right
        - "ML" : Middle Left
        - "MC" : Middle Center
        - "MR" : Middle Right
        - "BL" : Bottom Left (default)
        - "BC" : Bottom Center
        - "BR" : Bottom Right
    offset : str, optional
        Offset from position anchor point.
        Format: "xoffset/yoffset" with units (c=cm, i=inch, p=point)
        Example: "0.5c/0.5c"
    font : str, optional
        Font specification.
        Format: "size,fontname,color"
        Example: "8p,Helvetica,black"
        Default: GMT default annotation font
    justify : str, optional
        Text justification relative to anchor.
        Examples: "BL" (bottom-left), "TR" (top-right), "MC" (middle-center)

    Examples
    --------
    >>> import pygmt
    >>> fig = pygmt.Figure()
    >>> fig.basemap(region=[0, 10, 0, 10], projection="X10c", frame=True)
    >>> # Add timestamp in bottom-left
    >>> fig.timestamp()
    >>> fig.savefig("map_with_timestamp.png")
    >>>
    >>> # Custom timestamp with formatting
    >>> fig = pygmt.Figure()
    >>> fig.basemap(region=[0, 10, 0, 10], projection="X10c", frame=True)
    >>> fig.timestamp(
    ...     text="Created: %Y-%m-%d %H:%M",
    ...     position="BR",
    ...     offset="0.5c/0.5c",
    ...     font="10p,Helvetica,gray"
    ... )
    >>> fig.savefig("map_custom_timestamp.png")
    >>>
    >>> # Simple text label
    >>> fig = pygmt.Figure()
    >>> fig.basemap(region=[0, 10, 0, 10], projection="X10c", frame=True)
    >>> fig.timestamp(
    ...     text="Version 1.0",
    ...     position="TL",
    ...     font="12p,Helvetica-Bold,black"
    ... )
    >>> fig.savefig("map_version.png")

    Notes
    -----
    This function is commonly used for:
    - Documenting map creation time
    - Version labeling
    - Data currency indication
    - Quality control tracking

    Timestamp purposes:
    - Show when map was generated
    - Track map versions
    - Document data freshness
    - Audit trail for analysis

    Position codes:
    ```
    TL----TC----TR
    |            |
    ML    MC    MR
    |            |
    BL----BC----BR
    ```

    Date/time format codes:
    - %Y: 2024 (4-digit year)
    - %y: 24 (2-digit year)
    - %m: 01-12 (month)
    - %b: Jan-Dec (month name)
    - %d: 01-31 (day)
    - %H: 00-23 (hour)
    - %M: 00-59 (minute)
    - %S: 00-59 (second)

    Best practices:
    - Place in corner for minimal interference
    - Use small, gray font for subtlety
    - Include year-month-day for clarity
    - Consider map purpose (publication vs. internal)

    Applications:
    - Research publications
    - Report generation
    - Automated mapping
    - Quality assurance
    - Version control

    Alternative uses:
    - Copyright notices
    - Data source attribution
    - Processing notes
    - Map metadata

    See Also
    --------
    text : General text plotting
    logo : Plot GMT logo
    """
    from pygmt_nb.clib import Session

    # Build GMT command
    args = []

    # Text content (-T option)
    if text is not None:
        args.append(f'-T"{text}"')
    else:
        # Default GMT timestamp
        args.append("-T")

    # Position (-D option)
    if position is not None:
        pos_str = f"-D{position}"
        if offset is not None:
            pos_str += f"+o{offset}"
        args.append(pos_str)

    # Font (-F option)
    if font is not None:
        args.append(f"-F{font}")

    # Justification (-j option)
    if justify is not None:
        args.append(f"-j{justify}")

    # Execute via session
    with Session() as session:
        session.call_module("timestamp", " ".join(args))
