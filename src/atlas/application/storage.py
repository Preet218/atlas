"""Storage layer for applications."""

from __future__ import annotations

from pathlib import Path
from uuid import UUID

from atlas.config.paths import DATA_DIR

from .models import Application


class ApplicationStorage:
    """Handles persistence of applications."""

    def __init__(self, root: Path | None = None) -> None:
        """Initialize application storage.

        Args:
            root: Root directory for storing applications. If not
                provided, the default data directory is used.
        """
        self._root = root or DATA_DIR / "applications"
        self._root.mkdir(parents=True, exist_ok=True)

    def _application_path(self, application_id: UUID) -> Path:
        """Return the filesystem path for an application."""

        return self._root / f"{application_id}.json"

    def save(self, application: Application) -> None:
        """Persist an application."""

        path = self._application_path(application.id)

        path.write_text(
            application.model_dump_json(indent=4),
            encoding="utf-8",
        )

    def load(self, application_id: UUID) -> Application:
        """Load an application."""

        path = self._application_path(application_id)

        return Application.model_validate_json(path.read_text(encoding="utf-8"))

    def exists(self, application_id: UUID) -> bool:
        """Return True if the application exists."""

        return self._application_path(application_id).exists()

    def delete(self, application_id: UUID) -> None:
        """Delete an application if it exists."""

        path = self._application_path(application_id)

        if path.exists():
            path.unlink()

    def list(self) -> list[Path]:
        """Return all stored application files."""

        return sorted(self._root.glob("*.json"))

    def load_all(self) -> list[Application]:
        """Load every stored application."""

        return [
            Application.model_validate_json(path.read_text(encoding="utf-8"))
            for path in self.list()
        ]
