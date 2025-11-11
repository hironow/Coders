"""
Figure class - PyGMT-compatible high-level plotting API.

This module provides the Figure class which is designed to be a drop-in
replacement for pygmt.Figure, using the high-performance pygmt_nb backend.
"""

from typing import Union, Optional, List
from pathlib import Path
import tempfile
import os
import subprocess

from pygmt_nb.clib import Session, Grid


class Figure:
    """
    GMT Figure for creating maps and plots.

    This class provides a high-level interface for creating GMT figures,
    compatible with PyGMT's Figure API.

    Examples:
        >>> import pygmt_nb
        >>> fig = pygmt_nb.Figure()
        >>> fig.grdimage(grid="grid.nc")
        >>> fig.savefig("output.png")
    """

    def __init__(self):
        """
        Create a new Figure.

        Initializes an internal GMT session for managing figure operations.
        """
        self._session = Session()
        self._activated = False
        self._psfile = None  # Internal PostScript file
        self._tempdir = None  # Temporary directory for PS file

        # Initialize GMT modern mode session
        # Use gmtset to configure session for PostScript output
        self._ps_name = "gmt_figure"  # Base name for PS file

    def __del__(self):
        """Clean up resources when Figure is destroyed."""
        self._cleanup()

    def _cleanup(self):
        """Clean up temporary files and session."""
        if self._psfile and os.path.exists(self._psfile):
            try:
                os.unlink(self._psfile)
            except Exception:
                pass

        if self._tempdir and os.path.exists(self._tempdir):
            try:
                import shutil
                shutil.rmtree(self._tempdir)
            except Exception:
                pass

    def _ensure_tempdir(self):
        """Ensure temporary directory exists."""
        if self._tempdir is None:
            self._tempdir = tempfile.mkdtemp(prefix="pygmt_nb_")
        return self._tempdir

    def _get_psfile_path(self) -> str:
        """Get path to internal PostScript file."""
        if self._psfile is None:
            tempdir = self._ensure_tempdir()
            self._psfile = os.path.join(tempdir, "figure.ps")
        return self._psfile

    def grdimage(
        self,
        grid: Union[str, Path, Grid],
        projection: Optional[str] = None,
        region: Optional[List[float]] = None,
        cmap: Optional[str] = None,
        **kwargs
    ):
        """
        Plot a grid as an image.

        This method wraps GMT's grdimage module to create an image from
        a 2D grid file.

        Parameters:
            grid: Grid file path (str/Path) or Grid object
            projection: Map projection (e.g., "X10c", "M15c")
                       If None, uses automatic projection
            region: Map region as [west, east, south, north]
                   If None, uses grid's full extent
            cmap: Color palette name (e.g., "viridis", "geo")
            **kwargs: Additional GMT module options (not yet implemented)

        Examples:
            >>> fig = Figure()
            >>> fig.grdimage(grid="@earth_relief_01d")
            >>> fig.grdimage(grid="data.nc", projection="X10c")
            >>> fig.grdimage(grid="data.nc", region=[0, 10, 0, 10])
        """
        # Build GMT grdimage command
        args = []

        # Input grid
        if isinstance(grid, Grid):
            # If Grid object, we need to save it temporarily
            # For now, require file path (Grid object support in future)
            raise NotImplementedError(
                "Grid object support not yet implemented. "
                "Please provide grid file path as string."
            )
        else:
            # File path
            grid_path = str(grid)
            args.append(grid_path)

        # Projection
        if projection:
            args.append(f"-J{projection}")
        else:
            # Default: Cartesian with automatic size
            args.append("-JX10c")

        # Region
        if region:
            if len(region) != 4:
                raise ValueError("Region must be [west, east, south, north]")
            west, east, south, north = region
            args.append(f"-R{west}/{east}/{south}/{north}")
        # If no region specified, GMT will use grid's extent

        # Color palette
        if cmap:
            args.append(f"-C{cmap}")

        # Output to PostScript
        psfile = self._get_psfile_path()
        if self._activated:
            # Append to existing PS
            args.append("-O")
            args.append("-K")
        else:
            # Start new PS
            args.append("-K")
            self._activated = True

        # Execute GMT grdimage via subprocess with output redirection
        # This is necessary because call_module doesn't support I/O redirection
        cmd = ["gmt", "grdimage"] + args

        try:
            # Open file in appropriate mode
            mode = "ab" if self._activated and os.path.exists(psfile) and os.path.getsize(psfile) > 0 else "wb"
            with open(psfile, mode) as f:
                result = subprocess.run(
                    cmd,
                    stdout=f,
                    stderr=subprocess.PIPE,
                    check=True,
                    text=True
                )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(
                f"GMT grdimage failed: {e.stderr}"
            ) from e

    def basemap(
        self,
        region: Optional[List[float]] = None,
        projection: Optional[str] = None,
        frame: Union[bool, str, List[str], None] = None,
        **kwargs
    ):
        """
        Draw a basemap (map frame, axes, and optional grid).

        This method wraps GMT's basemap module to draw map frames
        and coordinate axes.

        Parameters:
            region: Map region as [west, east, south, north]
                   Required parameter
            projection: Map projection (e.g., "X10c", "M15c")
                       Required parameter
            frame: Frame and axis settings
                  - True: automatic frame with annotations
                  - False or None: no frame
                  - str: GMT frame specification (e.g., "a", "afg", "WSen")
                  - list: List of frame specifications
            **kwargs: Additional GMT module options (not yet implemented)

        Examples:
            >>> fig = Figure()
            >>> fig.basemap(region=[0, 10, 0, 10], projection="X10c", frame=True)
            >>> fig.basemap(region=[0, 10, 0, 10], projection="X10c", frame="a")
            >>> fig.basemap(region=[0, 10, 0, 10], projection="X10c", frame="WSen+tTitle")
        """
        # Validate required parameters
        if region is None:
            raise ValueError("region parameter is required for basemap()")
        if projection is None:
            raise ValueError("projection parameter is required for basemap()")

        # Build GMT basemap command
        args = []

        # Region
        if len(region) != 4:
            raise ValueError("Region must be [west, east, south, north]")
        west, east, south, north = region
        args.append(f"-R{west}/{east}/{south}/{north}")

        # Projection
        args.append(f"-J{projection}")

        # Frame
        if frame is True:
            # Automatic frame with annotations
            args.append("-Ba")
        elif frame is False:
            # Minimal frame (no annotations, just border)
            args.append("-B0")
        elif frame is None:
            # Default: minimal frame (required by psbasemap)
            args.append("-B0")
        elif isinstance(frame, str):
            # String frame specification
            args.append(f"-B{frame}")
        elif isinstance(frame, list):
            # Multiple frame specifications
            for f in frame:
                if f is True:
                    args.append("-Ba")
                elif f is False:
                    args.append("-B0")
                elif isinstance(f, str):
                    args.append(f"-B{f}")
                else:
                    raise ValueError(
                        f"frame list element must be bool or str, not {type(f).__name__}"
                    )
        else:
            raise ValueError(
                f"frame must be bool, str, or list, not {type(frame).__name__}"
            )

        # Output to PostScript
        psfile = self._get_psfile_path()
        if self._activated:
            # Append to existing PS
            args.append("-O")
            args.append("-K")
        else:
            # Start new PS
            args.append("-K")
            self._activated = True

        # Execute GMT psbasemap via subprocess with output redirection
        # Note: Using psbasemap (classic mode) instead of basemap (modern mode)
        # because we're using -K/-O flags for PostScript output
        cmd = ["gmt", "psbasemap"] + args

        try:
            # Open file in appropriate mode
            mode = "ab" if self._activated and os.path.exists(psfile) and os.path.getsize(psfile) > 0 else "wb"
            with open(psfile, mode) as f:
                result = subprocess.run(
                    cmd,
                    stdout=f,
                    stderr=subprocess.PIPE,
                    check=True,
                    text=True
                )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(
                f"GMT psbasemap failed: {e.stderr}"
            ) from e

    def coast(
        self,
        region: Optional[Union[str, List[float]]] = None,
        projection: Optional[str] = None,
        land: Optional[str] = None,
        water: Optional[str] = None,
        shorelines: Union[bool, str, int, None] = None,
        resolution: Optional[str] = None,
        borders: Union[str, List[str], None] = None,
        frame: Union[bool, str, List[str], None] = None,
        dcw: Union[str, List[str], None] = None,
        **kwargs
    ):
        """
        Draw coastlines, borders, and water bodies.

        This method wraps GMT's pscoast module to plot coastlines,
        land, ocean, and political boundaries.

        Parameters:
            region: Map region
                   - str: Region code (e.g., "JP", "US", "EG")
                   - list: [west, east, south, north]
            projection: Map projection (e.g., "X10c", "M15c")
                       Required parameter
            land: Land color (e.g., "gray", "#aaaaaa", "brown")
            water: Water/ocean color (e.g., "lightblue", "white")
            shorelines: Shoreline settings
                      - True: Draw shorelines with default pen
                      - str/int: Shoreline type and pen (e.g., "1", "1/0.5p")
            resolution: Shoreline resolution
                      - "crude" (c): Crude resolution
                      - "low" (l): Low resolution
                      - "intermediate" (i): Intermediate resolution
                      - "high" (h): High resolution
                      - "full" (f): Full resolution
            borders: Political boundary settings
                   - str: Border type (e.g., "1" for national borders)
                   - list: Multiple border types
            frame: Frame and axis settings (same as basemap)
            dcw: Digital Chart of the World country codes
                - str: Single country code (e.g., "ES+gbisque+pblue")
                - list: Multiple country codes
            **kwargs: Additional GMT module options (not yet implemented)

        Examples:
            >>> fig = Figure()
            >>> fig.coast(region="JP", projection="M10c", land="gray")
            >>> fig.coast(region=[-180, 180, -80, 80], projection="M15c",
            ...           land="#aaaaaa", water="white")
        """
        # Validate required parameters
        if projection is None:
            raise ValueError("projection parameter is required for coast()")

        # Build GMT pscoast command
        args = []

        # Region
        if region is not None:
            if isinstance(region, str):
                # Region code (e.g., "JP")
                args.append(f"-R{region}")
            elif isinstance(region, list):
                if len(region) != 4:
                    raise ValueError("Region must be [west, east, south, north]")
                west, east, south, north = region
                args.append(f"-R{west}/{east}/{south}/{north}")
            else:
                raise ValueError("region must be str or list")
        else:
            raise ValueError("region parameter is required for coast()")

        # Projection
        args.append(f"-J{projection}")

        # Land color
        if land:
            args.append(f"-G{land}")

        # Water color
        if water:
            args.append(f"-S{water}")

        # Shorelines
        if shorelines is not None:
            if shorelines is True:
                args.append("-W")
            elif isinstance(shorelines, (str, int)):
                args.append(f"-W{shorelines}")

        # Resolution
        if resolution:
            # Map long form to short form
            resolution_map = {
                "crude": "c",
                "low": "l",
                "intermediate": "i",
                "high": "h",
                "full": "f",
                # Also accept short forms directly
                "c": "c",
                "l": "l",
                "i": "i",
                "h": "h",
                "f": "f",
            }
            if resolution in resolution_map:
                args.append(f"-D{resolution_map[resolution]}")
            else:
                raise ValueError(
                    f"Invalid resolution: {resolution}. "
                    f"Must be one of: {', '.join(resolution_map.keys())}"
                )

        # Borders
        if borders is not None:
            if isinstance(borders, str):
                args.append(f"-N{borders}")
            elif isinstance(borders, list):
                for border in borders:
                    args.append(f"-N{border}")

        # DCW (Digital Chart of the World)
        if dcw is not None:
            if isinstance(dcw, str):
                args.append(f"-E{dcw}")
            elif isinstance(dcw, list):
                # Multiple DCW codes
                for code in dcw:
                    args.append(f"-E{code}")

        # Frame
        if frame is True:
            args.append("-Ba")
        elif frame is False:
            pass  # No frame
        elif frame is None:
            pass  # No frame by default for coast
        elif isinstance(frame, str):
            args.append(f"-B{frame}")
        elif isinstance(frame, list):
            for f in frame:
                args.append(f"-B{f}")

        # Ensure at least one drawing option is specified
        # pscoast requires at least one of -C, -G, -S, -E, -I, -N, -Q, -W
        has_drawing_option = any([
            land,  # -G
            water,  # -S
            shorelines is not None,  # -W
            borders is not None,  # -N
            dcw is not None,  # -E
        ])

        if not has_drawing_option:
            # Default: draw shorelines
            args.append("-W")

        # Output to PostScript
        psfile = self._get_psfile_path()
        if self._activated:
            # Append to existing PS
            args.append("-O")
            args.append("-K")
        else:
            # Start new PS
            args.append("-K")
            self._activated = True

        # Execute GMT pscoast via subprocess with output redirection
        # Note: Using pscoast (classic mode) instead of coast (modern mode)
        # because we're using -K/-O flags for PostScript output
        cmd = ["gmt", "pscoast"] + args

        try:
            # Open file in appropriate mode
            mode = "ab" if self._activated and os.path.exists(psfile) and os.path.getsize(psfile) > 0 else "wb"
            with open(psfile, mode) as f:
                result = subprocess.run(
                    cmd,
                    stdout=f,
                    stderr=subprocess.PIPE,
                    check=True,
                    text=True
                )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(
                f"GMT pscoast failed: {e.stderr}"
            ) from e

    def savefig(
        self,
        fname: Union[str, Path],
        dpi: int = 300,
        transparent: bool = False,
        **kwargs
    ):
        """
        Save the figure to a file.

        Converts the internal PostScript to the requested format (PNG, PDF, JPG).

        Parameters:
            fname: Output filename (extension determines format)
                  Supported: .png, .pdf, .jpg, .jpeg, .ps, .eps
            dpi: Resolution in dots per inch (default: 300)
            transparent: Make background transparent (PNG only)
            **kwargs: Additional conversion options (not yet implemented)

        Examples:
            >>> fig.savefig("output.png")
            >>> fig.savefig("output.pdf", dpi=600)
            >>> fig.savefig("output.png", transparent=True)
        """
        fname = Path(fname)
        psfile = self._get_psfile_path()

        # Close the PostScript file if it's open
        if self._activated:
            # Finalize PS file with -O -T flags (end PS file)
            cmd = ["gmt", "psxy", "-O", "-T"]
            try:
                with open(psfile, "ab") as f:
                    subprocess.run(
                        cmd,
                        stdout=f,
                        stderr=subprocess.PIPE,
                        check=True
                    )
            except subprocess.CalledProcessError as e:
                # If psxy fails, it's not critical (file might still be usable)
                pass
            self._activated = False

        # Check if PS file exists
        if not os.path.exists(psfile):
            raise RuntimeError(
                "No figure content to save. "
                "Please add content with methods like grdimage() before saving."
            )

        # Determine output format from extension
        ext = fname.suffix.lower()
        format_map = {
            ".png": "g",  # PNG (raster)
            ".pdf": "f",  # PDF (vector)
            ".jpg": "j",  # JPEG (raster)
            ".jpeg": "j",
            ".ps": "s",   # PostScript (just copy)
            ".eps": "e",  # EPS (encapsulated PostScript)
        }

        if ext not in format_map:
            raise ValueError(
                f"Unsupported format: {ext}. "
                f"Supported formats: {', '.join(format_map.keys())}"
            )

        # For PS, just copy the file
        if ext in [".ps", ".eps"]:
            import shutil
            shutil.copy(psfile, fname)
            return

        # Use GMT psconvert to convert PS to desired format
        cmd = ["gmt", "psconvert"]
        cmd.append(psfile)
        cmd.append(f"-T{format_map[ext]}")  # Format
        cmd.append(f"-E{dpi}")  # DPI
        cmd.append("-A")  # Tight bounding box

        if transparent and ext == ".png":
            cmd.append("-Qt")  # Transparent PNG

        # Output directory
        cmd.append(f"-D{fname.parent}")
        # Output filename (without extension, psconvert adds it)
        cmd.append(f"-F{fname.stem}")

        try:
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
                text=True
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(
                f"GMT psconvert failed: {e.stderr}"
            ) from e

        # Verify output file was created
        if not fname.exists():
            raise RuntimeError(
                f"Failed to create output file: {fname}. "
                "Check GMT psconvert output for errors."
            )

    def show(self, **kwargs):
        """
        Display the figure in a window or inline (Jupyter).

        Note: This method is not yet implemented.

        Parameters:
            **kwargs: Display options (not yet implemented)

        Raises:
            NotImplementedError: Always (not yet implemented)
        """
        raise NotImplementedError(
            "Figure.show() is not yet implemented. "
            "Use savefig() to save to a file instead."
        )


__all__ = ["Figure"]
