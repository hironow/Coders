"""
solar - Plot day-light terminators and other sun-related parameters.

Figure method (not a standalone module function).
"""


def solar(
    self,
    terminator: str | None = None,
    datetime: str | None = None,
    pen: str | None = None,
    fill: str | None = None,
    sun_position: bool = False,
    **kwargs,
):
    """
    Plot day-light terminators and other sun-related parameters.

    Plots the day/night terminator line showing where on Earth it is
    currently day or night. Can also show civil, nautical, and astronomical
    twilight zones, and the sun's current position.

    Parameters
    ----------
    terminator : str, optional
        Type of terminator to plot:
        - "day_night" or "d" : Day/night terminator (default)
        - "civil" or "c" : Civil twilight (Sun 6° below horizon)
        - "nautical" or "n" : Nautical twilight (Sun 12° below horizon)
        - "astronomical" or "a" : Astronomical twilight (Sun 18° below horizon)
    datetime : str, optional
        Date and time for terminator calculation.
        Format: "YYYY-MM-DDTHH:MM:SS"
        If not specified, uses current time.
        Examples: "2024-01-15T12:00:00", "2024-06-21T00:00:00"
    pen : str, optional
        Pen attributes for terminator line.
        Format: "width,color,style"
        Examples: "1p,black", "2p,blue,dashed"
    fill : str, optional
        Fill color for night side.
        Examples: "gray", "black@50" (50% transparent)
    sun_position : bool, optional
        If True, plot sun symbol at current sub-solar point (default: False).

    Examples
    --------
    >>> import pygmt
    >>> # Plot current day/night terminator
    >>> fig = pygmt.Figure()
    >>> fig.basemap(region="d", projection="W15c", frame="a")
    >>> fig.coast(land="tan", water="lightblue")
    >>> fig.solar(terminator="day_night", pen="1p,black", fill="gray@30")
    >>> fig.savefig("terminator.png")
    >>>
    >>> # Plot civil twilight for specific date
    >>> fig = pygmt.Figure()
    >>> fig.basemap(region="d", projection="W15c", frame="a")
    >>> fig.coast(land="tan", water="lightblue")
    >>> fig.solar(
    ...     terminator="civil",
    ...     datetime="2024-06-21T12:00:00",  # Summer solstice noon
    ...     pen="2p,orange",
    ...     fill="navy@20"
    ... )
    >>> fig.savefig("twilight.png")
    >>>
    >>> # Show sun position
    >>> fig = pygmt.Figure()
    >>> fig.basemap(region="d", projection="W15c", frame="a")
    >>> fig.coast(land="tan", water="lightblue")
    >>> fig.solar(
    ...     terminator="day_night",
    ...     pen="1p,black",
    ...     sun_position=True
    ... )
    >>> fig.savefig("sun_position.png")

    Notes
    -----
    This function is commonly used for:
    - Day/night visualization on global maps
    - Twilight zone illustration
    - Solar position tracking
    - Astronomical event planning
    - Photography golden hour planning

    Terminator types:
    - Day/night: Where sun is exactly at horizon (0°)
    - Civil twilight: Sun 6° below horizon (can still see)
    - Nautical twilight: Sun 12° below horizon (horizon visible at sea)
    - Astronomical twilight: Sun 18° below horizon (full astronomical darkness)

    Twilight zones:
    - Civil: Enough light for outdoor activities
    - Nautical: Horizon visible for navigation
    - Astronomical: Sky dark enough for astronomy

    Solar calculations:
    - Uses astronomical algorithms
    - Accounts for Earth's tilt and orbit
    - Sub-solar point: Where sun is directly overhead
    - Varies by date and time

    Applications:
    - Satellite imagery: Distinguish day/night passes
    - Aviation: Flight planning with daylight
    - Photography: Golden hour planning
    - Astronomy: Darkness for observations
    - Solar energy: Daylight availability
    - Navigation: Twilight for celestial navigation

    Special dates:
    - Equinoxes (Mar 20, Sep 22): Terminator passes through poles
    - Solstices (Jun 21, Dec 21): Maximum terminator tilt
    - Polar regions: Midnight sun / polar night

    See Also
    --------
    coast : Plot coastlines and fill land/water
    basemap : Create map frame
    """
    from pygmt_nb.clib import Session

    # Build GMT command
    args = []

    # Terminator type (-T option)
    if terminator is not None:
        # Map user-friendly names to GMT codes
        term_map = {
            "day_night": "d",
            "civil": "c",
            "nautical": "n",
            "astronomical": "a",
        }
        code = term_map.get(terminator, terminator)
        args.append(f"-T{code}")
    else:
        args.append("-Td")  # Default to day/night

    # Date/time (-I option)
    if datetime is not None:
        args.append(f"-I{datetime}")

    # Pen (-W option)
    if pen is not None:
        args.append(f"-W{pen}")

    # Fill (-G option)
    if fill is not None:
        args.append(f"-G{fill}")

    # Sun position (-S option)
    if sun_position:
        args.append("-S")

    # Execute via session
    with Session() as session:
        session.call_module("solar", " ".join(args))
