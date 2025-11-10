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
