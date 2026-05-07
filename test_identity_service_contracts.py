from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import importlib
import sys
from pathlib import Path
from types import ModuleType
from uuid import UUID

import pytest
from xml.etree import ElementTree as ET

REPO_ROOT = Path(__file__).resolve().parent.parent
IDENTITY_ROOT = REPO_ROOT / "identity-service"


@dataclass(slots=True)
class FakeChannel:
    exchange_declarations: list[tuple[str, str, bool, bool]] = field(default_factory=list)
    published_messages: list[tuple[str, str, bytes, object]] = field(default_factory=list)
    is_closed: bool = False

    def exchange_declare(self, *, exchange: str, exchange_type: str, durable: bool, auto_delete: bool) -> None:
        self.exchange_declarations.append((exchange, exchange_type, durable, auto_delete))

    def basic_publish(self, *, exchange: str, routing_key: str, body: bytes, properties: object) -> None:
        self.published_messages.append((exchange, routing_key, body, properties))

    def close(self) -> None:
        self.is_closed = True


@dataclass(slots=True)
class FakeConnection:
    channel_instance: FakeChannel
    is_closed: bool = False

    def channel(self) -> FakeChannel:
        return self.channel_instance

    def close(self) -> None:
        self.is_closed = True


@dataclass(slots=True)
class IdentityModules:
    database: ModuleType
    models: ModuleType
    services: ModuleType
    rabbitmq_service: ModuleType


class FakeUser:
    def __init__(self, master_uuid: UUID, email: str, created_by: str, created_at: datetime) -> None:
        self.master_uuid = master_uuid
        self.email = email
        self.created_by = created_by
        self.created_at = created_at


def _ensure_identity_import_path() -> None:
    identity_path = str(IDENTITY_ROOT)
    if identity_path not in sys.path:
        sys.path.insert(0, identity_path)


def _reload_identity_modules(monkeypatch: pytest.MonkeyPatch) -> IdentityModules:
    _ensure_identity_import_path()

    monkeypatch.setenv("DB_DRIVER", "sqlite")
    monkeypatch.setenv("DB_NAME", ":memory:")
    monkeypatch.setenv("DB_HOST", "localhost")
    monkeypatch.setenv("DB_PORT", "5432")
    monkeypatch.setenv("DB_USER", "identity")
    monkeypatch.setenv("DB_PASSWORD", "identity")
    monkeypatch.setenv("RABBITMQ_HOST", "localhost")
    monkeypatch.setenv("RABBITMQ_PORT", "5672")
    monkeypatch.setenv("RABBIT_USER", "guest")
    monkeypatch.setenv("RABBIT_PASS", "guest")
    monkeypatch.setenv("RABBITMQ_VHOST", "/")

    for module_name in ("rabbitmq_service", "services", "models", "database"):
        sys.modules.pop(module_name, None)

    database = importlib.import_module("database")
    models = importlib.import_module("models")
    services = importlib.import_module("services")
    rabbitmq_service = importlib.import_module("rabbitmq_service")
    return IdentityModules(database=database, models=models, services=services, rabbitmq_service=rabbitmq_service)


def _xml_text(element: ET.Element, path: str) -> str | None:
    return element.findtext(path)


class TestIdentityServiceContract:
    def test_create_user_is_idempotent_and_normalizes_email(self, monkeypatch: pytest.MonkeyPatch) -> None:
        modules = _reload_identity_modules(monkeypatch)

        modules.database.init_db()
        session = modules.database.SessionLocal()
        try:
            monkeypatch.setattr(modules.services, "publish_user_created", lambda *args, **kwargs: None)

            created_user = modules.services.create_user("  User@Example.COM  ", "CRM", session)
            repeated_user = modules.services.create_user("user@example.com", "crm", session)

            assert created_user.email == "user@example.com"
            assert created_user.created_by == "crm"
            assert repeated_user.master_uuid == created_user.master_uuid
            assert session.query(modules.models.UserRegistry).count() == 1
        finally:
            session.close()

    def test_build_ok_response_contains_master_uuid_contract(self, monkeypatch: pytest.MonkeyPatch) -> None:
        modules = _reload_identity_modules(monkeypatch)
        fake_user = FakeUser(
            master_uuid=UUID("01890a5d-ac96-7ab2-80e2-4536629c90de"),
            email="user@example.com",
            created_by="crm",
            created_at=datetime(2026, 5, 7, 12, 0, 0, tzinfo=timezone.utc),
        )

        response_xml = modules.rabbitmq_service._build_ok_response(fake_user)
        response = ET.fromstring(response_xml)

        assert response.tag == "identity_response"
        assert _xml_text(response, "status") == "ok"
        assert _xml_text(response, "user/master_uuid") == "01890a5d-ac96-7ab2-80e2-4536629c90de"
        assert _xml_text(response, "user/email") == "user@example.com"
        assert _xml_text(response, "user/created_by") == "crm"
        assert _xml_text(response, "user/created_at") == "2026-05-07T12:00:00+00:00"

    def test_build_error_response_contains_expected_fields(self, monkeypatch: pytest.MonkeyPatch) -> None:
        modules = _reload_identity_modules(monkeypatch)

        response_xml = modules.rabbitmq_service._build_error_response("NOT_FOUND", "User not found")
        response = ET.fromstring(response_xml)

        assert response.tag == "identity_response"
        assert _xml_text(response, "status") == "error"
        assert _xml_text(response, "error_code") == "NOT_FOUND"
        assert _xml_text(response, "message") == "User not found"

    def test_publish_user_created_emits_expected_identity_event(self, monkeypatch: pytest.MonkeyPatch) -> None:
        modules = _reload_identity_modules(monkeypatch)
        channel = FakeChannel()
        connection = FakeConnection(channel_instance=channel)

        monkeypatch.setattr(modules.rabbitmq_service, "get_rabbitmq_connection", lambda: connection)

        modules.rabbitmq_service.publish_user_created(
            UUID("01890a5d-ac96-7ab2-80e2-4536629c90de"),
            "user@example.com",
            "crm",
        )

        assert channel.exchange_declarations == [("user.events", "fanout", True, False)]
        assert len(channel.published_messages) == 1

        exchange, routing_key, body, _properties = channel.published_messages[0]
        assert exchange == "user.events"
        assert routing_key == ""

        payload = ET.fromstring(body.decode("utf-8"))
        assert payload.tag == "user_event"
        assert _xml_text(payload, "event") == "UserCreated"
        assert _xml_text(payload, "master_uuid") == "01890a5d-ac96-7ab2-80e2-4536629c90de"
        assert _xml_text(payload, "email") == "user@example.com"
        assert _xml_text(payload, "source_system") == "crm"
        assert _xml_text(payload, "timestamp") is not None
        assert channel.is_closed is True
        assert connection.is_closed is True
