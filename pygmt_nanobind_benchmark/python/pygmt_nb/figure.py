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

    def plot(
        self,
        x=None,
        y=None,
        data=None,
        region: Optional[Union[str, List[float]]] = None,
        projection: Optional[str] = None,
        style: Optional[str] = None,
        fill: Optional[str] = None,
        pen: Optional[str] = None,
        frame: Union[bool, str, List[str], None] = None,
        **kwargs
    ):
        """
        Plot lines, polygons, and symbols.

        This method wraps GMT's psxy module to plot data points,
        lines, and symbols.

        Parameters:
            x: x-coordinates (array-like)
            y: y-coordinates (array-like)
            data: 2D array with columns [x, y, ...] (not yet implemented)
            region: Map region
                   - str: Region code (e.g., "g" for global)
                   - list: [west, east, south, north]
            projection: Map projection (e.g., "X10c", "M15c")
                       Required parameter
            style: Symbol style (e.g., "c0.2c" = circle 0.2cm diameter,
                  "s0.3c" = square 0.3cm)
                  If not specified, draws lines connecting points
            fill: Fill color (e.g., "red", "#aaaaaa")
            pen: Pen specification (e.g., "1p,black", "2p,blue")
                Default pen if not specified
            frame: Frame and axis settings (same as basemap)
            **kwargs: Additional GMT module options (not yet implemented)

        Examples:
            >>> fig = Figure()
            >>> fig.plot(x=[1, 2, 3], y=[2, 4, 3], region=[0, 4, 0, 5],
            ...          projection="X10c", style="c0.2c", fill="red")
            >>> fig.plot(x=[1, 2, 3], y=[2, 4, 3], region=[0, 4, 0, 5],
            ...          projection="X10c", pen="2p,blue")
        """
        # Validate input data
        if x is None and y is None and data is None:
            raise ValueError("Must provide x and y, or data parameter")

        if data is not None:
            raise NotImplementedError(
                "data parameter not yet implemented. "
                "Please provide x and y arrays."
            )

        if x is None or y is None:
            raise ValueError("Both x and y must be provided")

        # Validate required parameters
        if region is None:
            raise ValueError("region parameter is required for plot()")
        if projection is None:
            raise ValueError("projection parameter is required for plot()")

        # Import numpy for array handling
        import numpy as np

        # Convert to numpy arrays
        x = np.atleast_1d(np.asarray(x))
        y = np.atleast_1d(np.asarray(y))

        if x.shape != y.shape:
            raise ValueError(f"x and y must have same shape: {x.shape} vs {y.shape}")

        # Build GMT psxy command
        args = []

        # Region
        if isinstance(region, str):
            args.append(f"-R{region}")
        elif isinstance(region, list):
            if len(region) != 4:
                raise ValueError("Region must be [west, east, south, north]")
            west, east, south, north = region
            args.append(f"-R{west}/{east}/{south}/{north}")
        else:
            raise ValueError("region must be str or list")

        # Projection
        args.append(f"-J{projection}")

        # Style (symbol)
        if style:
            args.append(f"-S{style}")

        # Fill color
        if fill:
            args.append(f"-G{fill}")

        # Pen
        if pen:
            args.append(f"-W{pen}")
        elif not fill and not style:
            # Default pen for lines
            args.append("-W0.5p,black")

        # Frame
        if frame is True:
            args.append("-Ba")
        elif frame is False:
            pass  # No frame
        elif frame is None:
            pass  # No frame by default
        elif isinstance(frame, str):
            args.append(f"-B{frame}")
        elif isinstance(frame, list):
            for f in frame:
                if f is True:
                    args.append("-Ba")
                elif f is False:
                    args.append("-B0")
                elif isinstance(f, str):
                    args.append(f"-B{f}")

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

        # Execute GMT psxy via subprocess with data input
        # psxy reads data from stdin
        cmd = ["gmt", "psxy"] + args

        # Prepare input data (x y format, one pair per line)
        input_data = "\n".join(f"{xi} {yi}" for xi, yi in zip(x, y))

        try:
            # Open file in appropriate mode
            mode = "ab" if self._activated and os.path.exists(psfile) and os.path.getsize(psfile) > 0 else "wb"
            with open(psfile, mode) as f:
                result = subprocess.run(
                    cmd,
                    input=input_data,
                    stdout=f,
                    stderr=subprocess.PIPE,
                    check=True,
                    text=True
                )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(
                f"GMT psxy failed: {e.stderr}"
            ) from e

    def text(
        self,
        x=None,
        y=None,
        text=None,
        region: Optional[Union[str, List[float]]] = None,
        projection: Optional[str] = None,
        font: Optional[str] = None,
        angle: Optional[Union[int, float]] = None,
        justify: Optional[str] = None,
        fill: Optional[str] = None,
        frame: Union[bool, str, List[str], None] = None,
        **kwargs
    ):
        """
        Plot text strings.

        This method wraps GMT's pstext module to place text strings
        at specified locations.

        Parameters:
            x: x-coordinate(s) (scalar or array-like)
            y: y-coordinate(s) (scalar or array-like)
            text: Text string(s) (scalar str or array-like)
            region: Map region
                   - str: Region code (e.g., "g" for global)
                   - list: [west, east, south, north]
            projection: Map projection (e.g., "X10c", "M15c")
                       Required parameter
            font: Font specification (e.g., "12p,Helvetica,black",
                 "18p,Helvetica-Bold,red")
                 Format: size,fontname,color
            angle: Text rotation angle in degrees
            justify: Text justification (e.g., "MC" = Middle Center,
                    "TL" = Top Left, "BR" = Bottom Right)
            fill: Background fill color
            frame: Frame and axis settings (same as basemap)
            **kwargs: Additional GMT module options (not yet implemented)

        Examples:
            >>> fig = Figure()
            >>> fig.text(x=2, y=1, text="Hello", region=[0, 4, 0, 2],
            ...          projection="X10c")
            >>> fig.text(x=[1, 2, 3], y=[0.5, 1.0, 1.5],
            ...          text=["A", "B", "C"], region=[0, 4, 0, 2],
            ...          projection="X10c", font="14p,Helvetica-Bold,red")
        """
        # Validate input data
        if x is None or y is None or text is None:
            raise ValueError("Must provide x, y, and text parameters")

        # Validate required parameters
        if region is None:
            raise ValueError("region parameter is required for text()")
        if projection is None:
            raise ValueError("projection parameter is required for text()")

        # Import numpy for array handling
        import numpy as np

        # Convert to arrays
        x = np.atleast_1d(np.asarray(x))
        y = np.atleast_1d(np.asarray(y))

        # Handle text input (may be string or array)
        if isinstance(text, str):
            text = [text]
        text = np.atleast_1d(np.asarray(text, dtype=str))

        if x.shape != y.shape or x.shape != text.shape:
            raise ValueError(
                f"x, y, and text must have same shape: {x.shape} vs {y.shape} vs {text.shape}"
            )

        # Build GMT pstext command
        args = []

        # Region
        if isinstance(region, str):
            args.append(f"-R{region}")
        elif isinstance(region, list):
            if len(region) != 4:
                raise ValueError("Region must be [west, east, south, north]")
            west, east, south, north = region
            args.append(f"-R{west}/{east}/{south}/{north}")
        else:
            raise ValueError("region must be str or list")

        # Projection
        args.append(f"-J{projection}")

        # Build -F option with font, angle, and justify modifiers
        f_option = "-F"
        if font:
            f_option += f"+f{font}"
        else:
            # Default font
            f_option += "+f12p,Helvetica,black"

        # Angle (must be part of -F option)
        if angle is not None:
            f_option += f"+a{angle}"

        # Justify (must be part of -F option)
        if justify:
            f_option += f"+j{justify}"

        args.append(f_option)

        # Fill (background)
        if fill:
            args.append(f"-G{fill}")

        # Frame
        if frame is True:
            args.append("-Ba")
        elif frame is False:
            pass  # No frame
        elif frame is None:
            pass  # No frame by default
        elif isinstance(frame, str):
            args.append(f"-B{frame}")
        elif isinstance(frame, list):
            for f in frame:
                if f is True:
                    args.append("-Ba")
                elif f is False:
                    args.append("-B0")
                elif isinstance(f, str):
                    args.append(f"-B{f}")

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

        # Execute GMT pstext via subprocess with data input
        # pstext reads data from stdin: x y [angle justify font] text
        cmd = ["gmt", "pstext"] + args

        # Prepare input data
        # Simple format: x y text (one per line)
        input_data = "\n".join(f"{xi} {yi} {ti}" for xi, yi, ti in zip(x, y, text))

        try:
            # Open file in appropriate mode
            mode = "ab" if self._activated and os.path.exists(psfile) and os.path.getsize(psfile) > 0 else "wb"
            with open(psfile, mode) as f:
                result = subprocess.run(
                    cmd,
                    input=input_data,
                    stdout=f,
                    stderr=subprocess.PIPE,
                    check=True,
                    text=True
                )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(
                f"GMT pstext failed: {e.stderr}"
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

    def colorbar(
        self,
        position: Optional[str] = None,
        frame: Union[bool, str, List[str], None] = None,
        cmap: Optional[str] = None,
        **kwargs
    ):
        """
        Add a color scale bar to the figure.

        Typically used after grdimage() to show the color scale.
        Uses GMT's psscale command.

        Parameters:
            position: Position specification using absolute coordinates
                     Format: x/y+wLength[+h][+jJustify]
                     - x/y: Position in plot units (cm)
                     - +w: Width (e.g., +w8c for 8cm)
                     - +h: Horizontal orientation (vertical by default)
                     - +j: Justification (e.g., +jBC for bottom center)
                     If None, uses default position (13c/8c+w8c+jML - middle left at 13cm,8cm)
            frame: Frame/axis settings
                  - bool: True for automatic frame, False for no frame
                  - str: Single frame specification (e.g., "af")
                  - list: Multiple specifications (e.g., ["af", "x+lLabel"])
            cmap: Color palette name (e.g., "viridis"). If None, uses current palette from grdimage.
            **kwargs: Additional GMT options (not yet implemented)

        Examples:
            >>> fig = pygmt_nb.Figure()
            >>> fig.grdimage(grid="data.nc", cmap="viridis")
            >>> fig.colorbar()  # Default position
            >>> fig.colorbar(position="5c/1c+w8c+h")  # Bottom, horizontal, 5cm from left, 1cm from bottom
            >>> fig.colorbar(frame="af")  # With annotations
            >>> fig.colorbar(frame=["af", "x+lElevation", "y+lm"])  # With label
        """
        # Build GMT psscale command
        args = []

        # Color palette (optional - psscale can inherit from previous grdimage)
        if cmap:
            args.append(f"-C{cmap}")

        # Position - use absolute positioning (Dx) instead of justify-based (DJ)
        # DJ requires -R and -J which complicates things
        if position:
            args.append(f"-D{position}")
        else:
            # Default: horizontal colorbar at bottom center
            # Position at 5cm from left, 1cm from bottom, 8cm wide, horizontal
            args.append("-D5c/1c+w8c+h+jBC")

        # Frame
        if frame is True:
            args.append("-Ba")
        elif frame is False:
            args.append("-B0")
        elif frame is None:
            # Default frame with annotations
            args.append("-Ba")
        elif isinstance(frame, str):
            args.append(f"-B{frame}")
        elif isinstance(frame, list):
            for f in frame:
                if f is True:
                    args.append("-Ba")
                elif isinstance(f, str):
                    args.append(f"-B{f}")

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

        # Execute GMT psscale via subprocess
        cmd = ["gmt", "psscale"] + args

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
                f"GMT psscale failed: {e.stderr}"
            ) from e

    def grdcontour(
        self,
        grid: Union[str, Path],
        region: Optional[Union[str, List[float]]] = None,
        projection: Optional[str] = None,
        interval: Optional[Union[int, float, str]] = None,
        annotation: Optional[Union[int, float, str]] = None,
        pen: Optional[str] = None,
        limit: Optional[List[float]] = None,
        frame: Union[bool, str, List[str], None] = None,
        **kwargs
    ):
        """
        Draw contour lines from a grid file.

        Uses GMT's grdcontour command to create contour lines from gridded data.

        Parameters:
            grid: Grid file path (str/Path)
            region: Map region as [west, east, south, north] or region code
                   If None, uses grid's full extent
            projection: Map projection (e.g., "X10c", "M15c")
                       If None, uses automatic projection
            interval: Contour interval (e.g., 100 for contours every 100 units)
                     Can be a number or string with unit (e.g., "100")
                     If None, GMT chooses automatically
            annotation: Annotation interval (e.g., 500 for labels every 500 units)
                       If None, no annotations
            pen: Pen specification for contour lines (e.g., "0.5p,blue")
                If None, uses GMT defaults
            limit: Contour limits as [low, high] (only draw contours in this range)
                  If None, draws all contours
            frame: Frame/axis settings (same as basemap)
            **kwargs: Additional GMT module options (not yet implemented)

        Examples:
            >>> fig = pygmt_nb.Figure()
            >>> fig.grdcontour(grid="data.nc", region=[0, 10, 0, 10], projection="X10c")
            >>> fig.grdcontour(grid="data.nc", interval=100, annotation=500)
            >>> fig.grdcontour(grid="data.nc", pen="0.5p,blue", limit=[-1000, 1000])
        """
        # Convert grid path to string
        if isinstance(grid, Path):
            grid = str(grid)

        # Build GMT grdcontour command
        args = []

        # Grid file
        args.append(grid)

        # Region
        if region:
            if isinstance(region, str):
                args.append(f"-R{region}")
            else:
                if len(region) != 4:
                    raise ValueError("Region must be [west, east, south, north]")
                west, east, south, north = region
                args.append(f"-R{west}/{east}/{south}/{north}")

        # Projection
        if projection:
            args.append(f"-J{projection}")

        # Contour interval
        if interval is not None:
            args.append(f"-C{interval}")

        # Annotation
        if annotation is not None:
            args.append(f"-A{annotation}")

        # Pen
        if pen:
            args.append(f"-W{pen}")

        # Contour limits
        if limit:
            if len(limit) != 2:
                raise ValueError("Limit must be [low, high]")
            low, high = limit
            args.append(f"-L{low}/{high}")

        # Frame
        if frame is not None:
            if frame is True:
                args.append("-Ba")
            elif frame is False:
                args.append("-B0")
            elif isinstance(frame, str):
                args.append(f"-B{frame}")
            elif isinstance(frame, list):
                for f in frame:
                    if f is True:
                        args.append("-Ba")
                    elif isinstance(f, str):
                        args.append(f"-B{f}")

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

        # Execute GMT grdcontour via subprocess
        cmd = ["gmt", "grdcontour"] + args

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
                f"GMT grdcontour failed: {e.stderr}"
            ) from e

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
