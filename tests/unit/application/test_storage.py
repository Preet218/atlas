"""Unit tests for the application storage layer."""

from __future__ import annotations

from atlas.application.storage import ApplicationStorage
from tests.fixtures.factories.application import create_application


def test_save_and_load_application(tmp_path) -> None:
    storage = ApplicationStorage(root=tmp_path)

    application = create_application()

    storage.save(application)

    loaded = storage.load(application.id)

    assert loaded == application


def test_exists_returns_true_after_save(tmp_path) -> None:
    storage = ApplicationStorage(root=tmp_path)

    application = create_application()

    assert not storage.exists(application.id)

    storage.save(application)

    assert storage.exists(application.id)


def test_delete_application(tmp_path) -> None:
    storage = ApplicationStorage(root=tmp_path)

    application = create_application()

    storage.save(application)
    storage.delete(application.id)

    assert not storage.exists(application.id)


def test_delete_missing_application_is_noop(tmp_path) -> None:
    storage = ApplicationStorage(root=tmp_path)

    application = create_application()

    storage.delete(application.id)  # should not raise

    assert not storage.exists(application.id)


def test_list_applications(tmp_path) -> None:
    storage = ApplicationStorage(root=tmp_path)

    applications = [create_application() for _ in range(3)]

    for application in applications:
        storage.save(application)

    assert len(storage.list()) == 3


def test_load_all_applications(tmp_path) -> None:
    storage = ApplicationStorage(root=tmp_path)

    applications = [create_application() for _ in range(3)]

    for application in applications:
        storage.save(application)

    loaded = storage.load_all()

    assert {a.id for a in loaded} == {a.id for a in applications}
