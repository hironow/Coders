"""
Core library interface

This module provides the Session class and low-level GMT API bindings.
"""

from pygmt_nb.clib._pygmt_nb_core import Session as _CoreSession


class Session(_CoreSession):
    """
    GMT Session wrapper with context manager support.

    This class wraps the C++ Session class and adds Python context manager
    protocol (__enter__ and __exit__).
    """

    def __enter__(self):
        """Enter the context manager."""
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Exit the context manager."""
        # Cleanup is handled by C++ destructor
        # Return None (False) to propagate exceptions
        return None


__all__ = ["Session"]
