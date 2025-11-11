"""
Test Suite for Session class

Following TDD principles: write tests first, then implement.
"""

import pytest


class TestSessionCreation:
    """Test session lifecycle management."""

    def test_session_can_be_created(self) -> None:
        """Test that a GMT session can be created."""
        from pygmt_nb.clib import Session

        session = Session()
        assert session is not None

    def test_session_can_be_used_as_context_manager(self) -> None:
        """Test that Session works as a context manager."""
        from pygmt_nb.clib import Session

        with Session() as session:
            assert session is not None

    def test_session_is_active_within_context(self) -> None:
        """Test that session is active within context manager."""
        from pygmt_nb.clib import Session

        with Session() as session:
            # Session should have some way to check if it's active
            # This will be implemented after we define the API
            assert hasattr(session, "session_pointer")


class TestSessionInfo:
    """Test session information methods."""

    def test_session_has_info_method(self) -> None:
        """Test that session has an info method."""
        from pygmt_nb.clib import Session

        with Session() as session:
            assert hasattr(session, "info")

    def test_session_info_returns_dict(self) -> None:
        """Test that session info returns a dictionary."""
        from pygmt_nb.clib import Session

        with Session() as session:
            info = session.info()
            assert isinstance(info, dict)
            assert "gmt_version" in info


class TestModuleExecution:
    """Test GMT module execution."""

    def test_session_can_call_module(self) -> None:
        """Test that session can execute GMT modules."""
        from pygmt_nb.clib import Session

        with Session() as session:
            # Try calling a simple GMT module like 'gmtset'
            # This should not raise an exception
            session.call_module("gmtset", "FORMAT_GEO_MAP=ddd:mm:ssF")

    def test_call_module_with_invalid_module_raises_error(self) -> None:
        """Test that calling non-existent module raises an error."""
        from pygmt_nb.clib import Session

        with Session() as session:
            with pytest.raises(Exception):  # noqa: B017 - Will define specific exception later
                session.call_module("nonexistent_module", "")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
