"""Unit tests for the job storage layer."""

from __future__ import annotations

from atlas.job.storage import JobStorage
from tests.fixtures.factories.job import create_job


def test_save_and_load_job(tmp_path) -> None:
    """Verify a saved job can be loaded."""

    storage = JobStorage(root=tmp_path)

    job = create_job()

    storage.save(job)

    loaded = storage.load(
        job.application.platform.value,
        job.id,
    )

    assert loaded == job


def test_exists_returns_true_after_save(tmp_path) -> None:
    """Verify exists() returns True after saving."""

    storage = JobStorage(root=tmp_path)

    job = create_job()

    assert not storage.exists(
        job.application.platform.value,
        job.id,
    )

    storage.save(job)

    assert storage.exists(
        job.application.platform.value,
        job.id,
    )


def test_delete_job(tmp_path) -> None:
    """Verify a saved job can be deleted."""

    storage = JobStorage(root=tmp_path)

    job = create_job()

    storage.save(job)

    storage.delete(
        job.application.platform.value,
        job.id,
    )

    assert not storage.exists(
        job.application.platform.value,
        job.id,
    )


def test_list_jobs(tmp_path) -> None:
    """Verify list() returns all stored jobs."""

    storage = JobStorage(root=tmp_path)

    jobs = [
        create_job(),
        create_job(),
        create_job(),
    ]

    for job in jobs:
        storage.save(job)

    files = storage.list(
        jobs[0].application.platform.value,
    )

    assert len(files) == 3


def test_delete_missing_job_is_noop(tmp_path) -> None:
    """Deleting a missing job should not raise."""

    storage = JobStorage(root=tmp_path)

    job = create_job()

    storage.delete(
        job.application.platform.value,
        job.id,
    )

    assert not storage.exists(
        job.application.platform.value,
        job.id,
    )
