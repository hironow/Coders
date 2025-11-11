"""
which - Find full path to specified files.

Module-level function (not a Figure method).
"""


def which(fname: str | list[str], **kwargs):
    """
    Find full path to specified files.

    Locates GMT data files, user files, or cache files and returns their
    full paths. Useful for finding GMT datasets, custom data, or checking
    file locations.

    Parameters
    ----------
    fname : str or list of str
        File name(s) to search for.
        Can be GMT remote files (e.g., "@earth_relief_01d")
        or local files.

    Returns
    -------
    str or list of str
        Full path(s) to the file(s). Returns None if not found.

    Examples
    --------
    >>> import pygmt
    >>> # Find GMT remote dataset
    >>> path = pygmt.which("@earth_relief_01d")
    >>> print(f"Earth relief grid: {path}")
    >>>
    >>> # Find multiple files
    >>> paths = pygmt.which(["@earth_relief_01d", "@earth_age_01d"])
    >>> for p in paths:
    ...     print(p)
    >>>
    >>> # Check if file exists
    >>> path = pygmt.which("my_data.txt")
    >>> if path:
    ...     print(f"File found: {path}")
    >>> else:
    ...     print("File not found")

    Notes
    -----
    This function is commonly used for:
    - Locating GMT datasets
    - Finding remote files
    - Checking file existence
    - Getting full paths for processing

    GMT data files:
    - Remote datasets start with "@"
    - @earth_relief: Global topography/bathymetry
    - @earth_age: Ocean crustal age
    - @earth_mask: Land/ocean masks
    - @earth_geoid: Geoid models
    - Many others available

    Search locations:
    1. Current directory
    2. GMT data directories
    3. GMT cache directories (~/.gmt/cache)
    4. Remote data servers (if @ prefix)

    Remote file handling:
    - Downloaded to cache on first use
    - Cached for future access
    - Automatically managed by GMT

    File types supported:
    - Grid files (.nc, .grd)
    - Dataset files (.txt, .dat)
    - CPT files (.cpt)
    - PostScript files (.ps)
    - Image files (.png, .jpg)

    Applications:
    - Script portability
    - Data validation
    - Path management
    - Resource location

    See Also
    --------
    grdinfo : Get grid information
    info : Get table information
    """
    import tempfile

    from pygmt_nb.clib import Session

    # Handle single file or list
    if isinstance(fname, str):
        files = [fname]
        single = True
    else:
        files = fname
        single = False

    results = []

    with Session() as session:
        for f in files:
            # Use gmtwhich module
            try:
                with tempfile.NamedTemporaryFile(mode="w+", suffix=".txt", delete=False) as tmp:
                    outfile = tmp.name

                session.call_module("gmtwhich", f"{f} ->{outfile}")

                # Read result
                with open(outfile) as tmp:
                    path = tmp.read().strip()

                results.append(path if path else None)

                import os

                if os.path.exists(outfile):
                    os.unlink(outfile)

            except Exception:
                results.append(None)

    return results[0] if single else results
