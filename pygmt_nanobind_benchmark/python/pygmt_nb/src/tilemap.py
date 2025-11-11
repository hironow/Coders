"""
tilemap - Plot raster tiles from XYZ tile servers.

Figure method (not a standalone module function).
"""


def tilemap(
    self,
    region: str | list[float],
    projection: str,
    zoom: int | None = None,
    source: str | None = None,
    lonlat: bool = True,
    **kwargs,
):
    """
    Plot raster tiles from XYZ tile servers.

    Downloads and plots map tiles from online tile servers (e.g., OpenStreetMap)
    as a basemap for other geographic data. Useful for adding context to maps.

    Parameters
    ----------
    region : str or list
        Map region in format [west, east, south, north].
    projection : str
        Map projection.
        Example: "M15c" for Mercator 15cm wide
    zoom : int, optional
        Zoom level for tiles (typically 1-18).
        Higher zoom = more detail but more tiles.
        Auto-calculated if not specified.
    source : str, optional
        Tile server URL template.
        Default: OpenStreetMap
        Format: "https://server.com/{z}/{x}/{y}.png"
        Variables: {z}=zoom, {x}=x-tile, {y}=y-tile
    lonlat : bool, optional
        If True, region is in longitude/latitude (default: True).
        If False, region is in projected coordinates.

    Examples
    --------
    >>> import pygmt
    >>> # Plot OpenStreetMap tiles for San Francisco
    >>> fig = pygmt.Figure()
    >>> fig.tilemap(
    ...     region=[-122.5, -122.3, 37.7, 37.9],
    ...     projection="M15c",
    ...     zoom=12,
    ...     source="OpenStreetMap"
    ... )
    >>> fig.savefig("sf_basemap.png")
    >>>
    >>> # Plot with custom tile server
    >>> fig = pygmt.Figure()
    >>> fig.tilemap(
    ...     region=[0, 10, 50, 55],
    ...     projection="M10c",
    ...     zoom=8,
    ...     source="https://tile.opentopomap.org/{z}/{x}/{y}.png"
    ... )
    >>> fig.savefig("topo_basemap.png")

    Notes
    -----
    This function is commonly used for:
    - Adding basemaps to scientific plots
    - Providing geographic context
    - Creating publication-ready maps
    - Interactive map backgrounds

    Tile servers:
    - OpenStreetMap: Street maps (default)
    - OpenTopoMap: Topographic maps
    - Stamen Terrain: Terrain visualization
    - ESRI World Imagery: Satellite imagery
    - Many others available

    Zoom levels:
    - 1-3: Continent scale
    - 4-6: Country scale
    - 7-10: Region/city scale
    - 11-14: Neighborhood scale
    - 15-18: Street/building scale

    Tile system:
    - Web Mercator projection
    - 256×256 pixel tiles
    - Organized in pyramid structure
    - Standard XYZ tile scheme

    Considerations:
    - Requires internet connection
    - Respect server usage policies
    - Cache tiles for repeated use
    - Zoom affects download size
    - Attribution requirements

    Applications:
    - Urban planning maps
    - Field site locations
    - Geological mapping
    - Ecological surveys
    - Transportation networks

    Performance:
    - Auto-detects needed tiles
    - Downloads only visible area
    - Can cache for offline use
    - Higher zoom = more tiles = slower

    Attribution:
    Most tile servers require attribution:
    - OpenStreetMap: © OpenStreetMap contributors
    - Check specific server requirements

    See Also
    --------
    basemap : Create map frame
    coast : Plot coastlines
    grdimage : Plot grid images
    """
    from pygmt_nb.clib import Session

    # Build GMT command
    args = []

    # Region (-R option)
    if isinstance(region, list):
        args.append(f"-R{'/'.join(str(x) for x in region)}")
    else:
        args.append(f"-R{region}")

    # Projection (-J option)
    args.append(f"-J{projection}")

    # Zoom level (-Z option)
    if zoom is not None:
        args.append(f"-Z{zoom}")

    # Tile source (-T option)
    if source is not None:
        args.append(f"-T{source}")

    # Execute via session
    with Session() as session:
        session.call_module("tilemap", " ".join(args))
