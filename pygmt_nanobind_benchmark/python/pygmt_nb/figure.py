"""
Figure class - PyGMT-compatible high-level plotting API using Modern Mode.

This module provides the Figure class which is designed to be a drop-in
replacement for pygmt.Figure, using GMT modern mode with nanobind for
high-performance C API calls (103x faster than subprocess).

Key features:
- Modern mode GMT commands (no -K/-O flags needed)
- Direct GMT C API via nanobind (103x speedup)
- Ghostscript-free PostScript generation
- PyGMT-compatible API
"""

import tempfile
import time
from pathlib import Path

from pygmt_nb.clib import Session


def _unique_figure_name() -> str:
    """Generate a unique figure name based on timestamp."""
    return f"pygmt_nb_{int(time.time() * 1000000)}"


def _escape_frame_spaces(value: str) -> str:
    """
    Escape spaces in GMT frame specifications by wrapping label text in double quotes.
    For example: x1p+lCrustal age → x1p+l"Crustal age"
    """
    if " " not in value:
        return value

    # Find +l or +L (label modifier) and wrap its content in double quotes
    import re

    # Pattern: +l or +L followed by any characters until the next + or end of string
    pattern = r"(\+[lLS])([^+]+)"

    def quote_label(match):
        prefix = match.group(1)  # +l, +L, or +S
        content = match.group(2)  # label text
        if " " in content:
            # Wrap in double quotes if it contains spaces
            return f'{prefix}"{content}"'
        return match.group(0)

    return re.sub(pattern, quote_label, value)


class Figure:
    """
    GMT Figure for creating maps and plots using modern mode.

    This class provides a high-level interface for creating GMT figures,
    compatible with PyGMT's Figure API. It uses GMT modern mode with
    nanobind for direct C API calls, providing 103x speedup over subprocess.

    Examples:
        >>> import pygmt_nb
        >>> fig = pygmt_nb.Figure()
        >>> fig.basemap(region=[0, 10, 0, 10], projection="X10c", frame=True)
        >>> fig.savefig("output.ps")
    """

    def __init__(self):
        """
        Create a new Figure using GMT modern mode.

        Initializes a GMT session and starts modern mode with a unique figure name.
        """
        self._session = Session()
        self._figure_name = _unique_figure_name()
        self._region = None
        self._projection = None

        # Start GMT modern mode
        self._session.call_module("begin", self._figure_name)

    def __del__(self):
        """Clean up resources when Figure is destroyed."""
        # Modern mode cleanup is handled by GMT automatically

    def _find_ps_minus_file(self) -> Path:
        """
        Find the .ps- file in GMT session directory.

        Returns:
            Path to the .ps- PostScript file.

        Raises:
            RuntimeError: If no .ps- file is found.
        """
        gmt_sessions = Path.home() / ".gmt" / "sessions"

        if not gmt_sessions.exists():
            raise RuntimeError("GMT sessions directory not found")

        # Find all .ps- files and return the most recent
        ps_minus_files = []
        for session_dir in gmt_sessions.glob("*"):
            for ps_file in session_dir.glob("*.ps-"):
                ps_minus_files.append((ps_file, ps_file.stat().st_mtime))

        if not ps_minus_files:
            raise RuntimeError(
                f"No PostScript file found for figure '{self._figure_name}'. Did you plot anything?"
            )

        # Return the most recently modified file
        ps_file, _ = max(ps_minus_files, key=lambda x: x[1])
        return ps_file

    def savefig(
        self,
        fname: str | Path,
        transparent: bool = False,
        dpi: int = 300,
        crop: bool = True,
        anti_alias: bool = True,
        **kwargs,
    ):
        """
        Save the figure to a file.

        Supports PostScript (.ps, .eps) and raster formats (.png, .jpg, .pdf, .tif)
        via GMT's psconvert command.

        Parameters:
            fname: Output filename (.ps, .eps, .png, .jpg, .jpeg, .pdf, .tif)
            transparent: Enable transparency (PNG only)
            dpi: Resolution in dots per inch (for raster formats)
            crop: Crop the figure canvas to the plot area (default: True)
            anti_alias: Use anti-aliasing for raster images (default: True)
            **kwargs: Additional options passed to psconvert

        Raises:
            ValueError: If unsupported format requested
            RuntimeError: If PostScript file not found or conversion fails
        """
        fname = Path(fname)
        suffix = fname.suffix.lower()

        # Format mapping (file extension -> GMT psconvert format code)
        fmt_map = {
            ".bmp": "b",
            ".eps": "e",
            ".jpg": "j",
            ".jpeg": "j",
            ".pdf": "f",
            ".png": "G" if transparent else "g",
            ".ppm": "m",
            ".tif": "t",
            ".ps": None,  # PS doesn't need conversion
        }

        if suffix not in fmt_map:
            raise ValueError(
                f"Unsupported file format: {suffix}. Supported formats: {', '.join(fmt_map.keys())}"
            )

        # Find the .ps- file
        ps_minus_file = self._find_ps_minus_file()

        # Read content
        content = ps_minus_file.read_text(errors="ignore")

        # GMT modern mode PS files redefine showpage to do nothing (/showpage {} def)
        # We need to restore the original showpage and call it for proper rendering
        # Use systemdict to access the original PostScript showpage operator
        if "%%EOF" in content:
            # Insert showpage restoration and call before %%EOF
            content = content.replace("%%EOF", "systemdict /showpage get exec\n%%EOF")
        else:
            content += "\nsystemdict /showpage get exec\n"

        # Add %%EOF marker if missing
        if not content.rstrip().endswith("%%EOF"):
            content += "%%EOF\n"

        # For PS format, save directly without conversion
        if suffix == ".ps":
            fname.write_text(content)
            return

        # For EPS and raster formats, use GMT psconvert via nanobind
        # Save PS content to temporary file first
        with tempfile.NamedTemporaryFile(mode="w", suffix=".ps", delete=False) as tmp_ps:
            tmp_ps_path = Path(tmp_ps.name)
            tmp_ps.write(content)

        try:
            # Use our psconvert implementation (which uses GMT C API via nanobind)
            from pygmt_nb.src.psconvert import psconvert

            # Prepare psconvert arguments
            prefix = fname.with_suffix("").as_posix()
            fmt = fmt_map[suffix]

            # Call psconvert (uses GMT C API, not subprocess!)
            psconvert(
                self,
                prefix=prefix,
                fmt=fmt,
                dpi=dpi,
                crop=crop,
                anti_alias="t2,g2" if anti_alias else None,
                **kwargs,
            )
        finally:
            # Clean up temporary file
            if tmp_ps_path.exists():
                tmp_ps_path.unlink()

    def show(self, **kwargs):
        """
        Display the figure.

        Note: This method is not yet implemented in modern mode.

        Raises:
            NotImplementedError: Always
        """
        raise NotImplementedError(
            "Figure.show() is not yet implemented. Use savefig() to save to a file instead."
        )

    # Import plotting methods from src/ (PyGMT pattern)
    from pygmt_nb.src import (  # noqa: E402, F401
        basemap,
        coast,
        colorbar,
        contour,
        grdcontour,
        grdimage,
        grdview,
        histogram,
        hlines,
        image,
        inset,
        legend,
        logo,
        meca,
        plot,
        plot3d,
        psconvert,
        rose,
        shift_origin,
        solar,
        subplot,
        ternary,
        text,
        tilemap,
        timestamp,
        velo,
        vlines,
        wiggle,
    )


__all__ = ["Figure"]
