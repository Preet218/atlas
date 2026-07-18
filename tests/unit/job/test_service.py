"""Unit tests for the job service."""

from __future__ import annotations

from unittest.mock import Mock

from atlas.job.service import JobService
from tests.fixtures.factories.job import create_job


def test_save_delegates_to_storage() -> None:
    """Verify save() delegates to storage."""

    storage = Mock()

    service = JobService(storage)

    job = create_job()

    service.save(job)

    storage.save.assert_called_once_with(job)


def test_get_delegates_to_storage() -> None:
    """Verify get() delegates to storage."""

    storage = Mock()

    service = JobService(storage)

    job = create_job()

    storage.load.return_value = job

    result = service.get(
        job.application.platform.value,
        job.id,
    )

    assert result == job

    storage.load.assert_called_once_with(
        job.application.platform.value,
        job.id,
    )


def test_exists_delegates_to_storage() -> None:
    """Verify exists() delegates to storage."""

    storage = Mock()

    service = JobService(storage)

    job = create_job()

    storage.exists.return_value = True

    assert service.exists(
        job.application.platform.value,
        job.id,
    )

    storage.exists.assert_called_once_with(
        job.application.platform.value,
        job.id,
    )


def test_delete_delegates_to_storage() -> None:
    """Verify delete() delegates to storage."""

    storage = Mock()

    service = JobService(storage)

    job = create_job()

    service.delete(
        job.application.platform.value,
        job.id,
    )

    storage.delete.assert_called_once_with(
        job.application.platform.value,
        job.id,
    )


def test_list_delegates_to_storage() -> None:
    """Verify list() delegates to storage."""

    storage = Mock()

    service = JobService(storage)

    storage.list.return_value = []

    assert service.list("company") == []

    storage.list.assert_called_once_with("company")
