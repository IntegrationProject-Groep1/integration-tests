"""Initial E2E flows test suite.

Usage:
  - Start the full stack with docker-compose (docker-compose up)
  - Export RUN_E2E=1 (Windows PowerShell: $env:RUN_E2E = '1')
  - Run pytest -k e2e or pytest -m e2e

Notes:
  - Tests are gated behind RUN_E2E to avoid accidental runs on CI without infra.
  - Exchange and routing defaults can be overridden via env vars if your setup
    uses different names.
"""
import os
import pytest
from helpers import e2e_utils as utils  # type: ignore


@pytest.mark.e2e
def test_registration_to_mailing_happy_path():
    """Publish a `new_registration` and assert a mailing/invoice event is emitted.

    Preconditions: RabbitMQ + services (CRM, Facturatie, Mailing, Identity) are running
    as defined in the repository `docker-compose.yml`.
    """
    if os.getenv("RUN_E2E", "0") != "1":
        pytest.skip("E2E tests are gated. Set RUN_E2E=1 to execute against real infra.")

    # Configurable exchange/routing names
    frontend_exchange = os.getenv("E2E_FRONTEND_EXCHANGE", "frontend.exchange")
    frontend_routing = os.getenv("E2E_FRONTEND_ROUTING", "frontend.to.crm.new_registration")

    facturatie_exchange = os.getenv("E2E_FACTURATIE_EXCHANGE", "facturatie.exchange")
    facturatie_routing = os.getenv("E2E_FACTURATIE_TO_MAILING_ROUTING", "facturatie.to.mailing")

    # Load fixture and publish
    xml = utils.load_fixture("frontend", "new_registration.xml")
    utils.publish(frontend_exchange, frontend_routing, xml)

    # Wait for Facturatie -> Mailing message (invoice send) as evidence the flow progressed
    received = utils.wait_for_message(facturatie_exchange, facturatie_routing, timeout=20)

    assert received is not None, (
        f"Did not observe expected downstream message on {facturatie_exchange}:{facturatie_routing} — "
        "ensure services are up and routing keys match your environment"
    )

    # Basic sanity check on message content
    assert "send_mailing" in received or "invoice" in received.lower() or "mail" in received.lower()
