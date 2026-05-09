"""
Integration Contract Tests — Desideriushogeschool Event Platform
================================================================

Each test validates that a simulated XML message from Team A can be validated
against the XSD schema defined by Team B (the receiver). This proves the
integration contract between teams is compatible.

Tests are grouped by FLOW (matching the Flow Visualisatie data.ts) and tagged
with the sender/receiver team so the readiness report can show per-team status.

Deadline: 10/05/2026 23:59 — Generale repetitie: 13/05 10:00 Aula 6
"""

import pytest
from pathlib import Path
from conftest import validate_xml_against_xsd, REPO_ROOT


# ═══════════════════════════════════════════════════════════════════════
# Helper paths
# ═══════════════════════════════════════════════════════════════════════
FRONTEND_XSD = REPO_ROOT / "IP-groep1-frontend" / "xsd"
KASSA_XSD = REPO_ROOT / "Kassa" / "integratie" / "schemas"
FACTURATIE_XSD = REPO_ROOT / "Facturatie" / "src" / "services" / "xsd"
PLANNING_XSD = REPO_ROOT / "Planning" / "xsd"
HEARTBEAT_XSD = REPO_ROOT / "heartbeat"
FIXTURES = Path(__file__).parent / "fixtures"


# ═══════════════════════════════════════════════════════════════════════
# R·1  REGISTREREN — Frontend → CRM (new_registration)
# ═══════════════════════════════════════════════════════════════════════

class TestR1_FrontendToCRM_NewRegistration:
    """
    Flow R·1: Frontend sends new_registration to CRM.
    Sender: Frontend | Receiver: CRM
    Queue: crm.incoming
    """

    def test_frontend_new_registration_validates_against_frontend_xsd(self):
        """Frontend's own XSD validates the new_registration it produces."""
        xml = (FIXTURES / "frontend" / "new_registration.xml").read_text()
        valid, err = validate_xml_against_xsd(xml, FRONTEND_XSD / "new_registration.xsd")
        assert valid, f"Frontend new_registration fails own XSD:\n{err}"


class TestR1_CRMToKassa_NewRegistration:
    """
    Flow R·1 step 2: CRM forwards new_registration to Kassa.
    Sender: CRM | Receiver: Kassa
    Queue: kassa.incoming (kassa.exchange)
    """

    def test_crm_new_registration_validates_against_kassa_xsd(self):
        """CRM's forwarded new_registration validates against Kassa's XSD."""
        xml = (FIXTURES / "crm" / "new_registration_to_kassa.xml").read_text()
        valid, err = validate_xml_against_xsd(xml, KASSA_XSD / "schema_new_registration.xsd")
        assert valid, f"CRM→Kassa new_registration fails Kassa XSD:\n{err}"


# ═══════════════════════════════════════════════════════════════════════
# S·1  SESSIE AANMAKEN — Frontend → Planning → CRM/Frontend
# ═══════════════════════════════════════════════════════════════════════

class TestS1_FrontendToPlanning_SessionCreateRequest:
    """
    Flow S·1: Frontend sends session_create_request to Planning.
    Sender: Frontend | Receiver: Planning
    """

    def test_frontend_session_create_request_validates_against_planning_xsd(self):
        xml = (FIXTURES / "frontend" / "session_create_request.xml").read_text()
        valid, err = validate_xml_against_xsd(xml, PLANNING_XSD / "session_create_request.xsd")
        assert valid, f"Frontend session_create_request fails Planning XSD:\n{err}"


class TestS1_PlanningToFrontend_SessionCreated:
    """
    Flow S·1: Planning broadcasts session_created to Frontend.
    Sender: Planning | Receiver: Frontend
    """

    def test_planning_session_created_validates_against_frontend_xsd(self):
        xml = (FIXTURES / "planning" / "session_created.xml").read_text()
        valid, err = validate_xml_against_xsd(xml, FRONTEND_XSD / "session_created.xsd")
        assert valid, f"Planning session_created fails Frontend XSD:\n{err}"

    def test_planning_session_created_validates_against_own_xsd(self):
        xml = (FIXTURES / "planning" / "session_created.xml").read_text()
        valid, err = validate_xml_against_xsd(xml, PLANNING_XSD / "session_created.xsd")
        assert valid, f"Planning session_created fails own XSD:\n{err}"


# ═══════════════════════════════════════════════════════════════════════
# S·2  SESSIE OPVRAGEN — Frontend ↔ Planning (RPC)
# ═══════════════════════════════════════════════════════════════════════

class TestS2_FrontendToPlanning_SessionViewRequest:
    """
    Flow S·2: Frontend sends session_view_request to Planning.
    """

    def test_frontend_session_view_request_validates_against_planning_xsd(self):
        xml = (FIXTURES / "frontend" / "session_view_request.xml").read_text()
        valid, err = validate_xml_against_xsd(xml, PLANNING_XSD / "session_view_request.xsd")
        assert valid, f"Frontend session_view_request fails Planning XSD:\n{err}"


class TestS2_PlanningToFrontend_SessionViewResponse:
    """
    Flow S·2: Planning replies with session_view_response.
    """

    def test_planning_session_view_response_validates_against_planning_xsd(self):
        xml = (FIXTURES / "planning" / "session_view_response.xml").read_text()
        valid, err = validate_xml_against_xsd(xml, PLANNING_XSD / "session_view_response.xsd")
        assert valid, f"Planning session_view_response fails own XSD:\n{err}"

    def test_planning_session_view_response_validates_against_frontend_xsd(self):
        xml = (FIXTURES / "planning" / "session_view_response.xml").read_text()
        valid, err = validate_xml_against_xsd(xml, FRONTEND_XSD / "session_view_response.xsd")
        assert valid, f"Planning session_view_response fails Frontend XSD:\n{err}"


# ═══════════════════════════════════════════════════════════════════════
# S·3  SESSIE VERPLAATSEN — Planning → Frontend/CRM
# ═══════════════════════════════════════════════════════════════════════

class TestS3_PlanningToFrontend_SessionUpdated:
    """
    Flow S·3: Planning broadcasts session_updated to Frontend.
    """

    def test_planning_session_updated_validates_against_frontend_xsd(self):
        xml = (FIXTURES / "planning" / "session_updated.xml").read_text()
        valid, err = validate_xml_against_xsd(xml, FRONTEND_XSD / "session_updated.xsd")
        assert valid, f"Planning session_updated fails Frontend XSD:\n{err}"


# ═══════════════════════════════════════════════════════════════════════
# S·4  SESSIE VERWIJDEREN — Frontend → Planning → Frontend
# ═══════════════════════════════════════════════════════════════════════

class TestS4_FrontendToPlanning_SessionDeleteRequest:
    """
    Flow S·4: Frontend sends session_delete_request to Planning.
    """

    def test_frontend_session_delete_request_validates_against_planning_xsd(self):
        xml = (FIXTURES / "frontend" / "session_delete_request.xml").read_text()
        valid, err = validate_xml_against_xsd(xml, PLANNING_XSD / "session_delete_request.xsd")
        assert valid, f"Frontend session_delete_request fails Planning XSD:\n{err}"


class TestS4_PlanningToFrontend_SessionDeleted:
    """
    Flow S·4: Planning broadcasts session_deleted to Frontend.
    """

    def test_planning_session_deleted_validates_against_frontend_xsd(self):
        xml = (FIXTURES / "planning" / "session_deleted.xml").read_text()
        valid, err = validate_xml_against_xsd(xml, FRONTEND_XSD / "session_deleted.xsd")
        assert valid, f"Planning session_deleted fails Frontend XSD:\n{err}"


# ═══════════════════════════════════════════════════════════════════════
# N·1  INSCHRIJVING — Frontend → CRM → Planning (calendar_invite)
# ═══════════════════════════════════════════════════════════════════════

class TestN1_FrontendToPlanning_CalendarInvite:
    """
    Flow N·1: Frontend sends calendar_invite to Planning.
    """

    def test_frontend_calendar_invite_validates_against_planning_xsd(self):
        xml = (FIXTURES / "frontend" / "calendar_invite.xml").read_text()
        valid, err = validate_xml_against_xsd(xml, PLANNING_XSD / "calendar_invite.xsd")
        assert valid, f"Frontend calendar_invite fails Planning XSD:\n{err}"

    def test_frontend_calendar_invite_validates_against_own_xsd(self):
        xml = (FIXTURES / "frontend" / "calendar_invite.xml").read_text()
        valid, err = validate_xml_against_xsd(xml, FRONTEND_XSD / "calendar_invite.xsd")
        assert valid, f"Frontend calendar_invite fails own XSD:\n{err}"


class TestN1_PlanningToFrontend_CalendarInviteConfirmed:
    """
    Flow N·1: Planning responds with calendar_invite_confirmed.
    """

    def test_planning_calendar_invite_confirmed_validates_against_frontend_xsd(self):
        xml = (FIXTURES / "planning" / "calendar_invite_confirmed.xml").read_text()
        valid, err = validate_xml_against_xsd(xml, FRONTEND_XSD / "calendar_invite_confirmed.xsd")
        assert valid, f"Planning calendar_invite_confirmed fails Frontend XSD:\n{err}"


# ═══════════════════════════════════════════════════════════════════════
# K·1  BETALING — Kassa → CRM → Facturatie (payment_registered)
# ═══════════════════════════════════════════════════════════════════════

class TestK1_KassaToCRM_PaymentRegistered:
    """
    Flow K·1: Kassa sends payment_registered to CRM.
    """

    def test_kassa_payment_registered_validates_against_kassa_xsd(self):
        xml = (FIXTURES / "kassa" / "payment_registered.xml").read_text()
        valid, err = validate_xml_against_xsd(xml, KASSA_XSD / "schema_payment_registered_v2.1.xsd")
        assert valid, f"Kassa payment_registered fails own XSD:\n{err}"


class TestK1_CRMToFacturatie_PaymentRegistered:
    """
    Flow K·1: CRM forwards payment_registered to Facturatie.
    """

    def test_crm_payment_registered_validates_against_facturatie_xsd(self):
        xml = (FIXTURES / "crm" / "payment_registered_to_facturatie.xml").read_text()
        valid, err = validate_xml_against_xsd(xml, FACTURATIE_XSD / "payment_registered.xsd")
        assert valid, f"CRM→Facturatie payment_registered fails Facturatie XSD:\n{err}"


# ═══════════════════════════════════════════════════════════════════════
# K·2  BAR CONSUMPTIE — Kassa → CRM → Facturatie (consumption_order)
# ═══════════════════════════════════════════════════════════════════════

class TestK2_KassaToCRM_ConsumptionOrder:
    """
    Flow K·2: Kassa sends consumption_order to CRM.
    """

    def test_kassa_consumption_order_validates_against_kassa_xsd(self):
        xml = (FIXTURES / "kassa" / "consumption_order.xml").read_text()
        valid, err = validate_xml_against_xsd(xml, KASSA_XSD / "schema_consumption_order_v2.3.xsd")
        assert valid, f"Kassa consumption_order fails own XSD:\n{err}"


class TestK2_CRMToFacturatie_ConsumptionOrder:
    """
    Flow K·2: CRM forwards consumption_order to Facturatie (company user).
    """

    def test_crm_consumption_order_validates_against_facturatie_xsd(self):
        xml = (FIXTURES / "crm" / "consumption_order_to_facturatie.xml").read_text()
        valid, err = validate_xml_against_xsd(xml, FACTURATIE_XSD / "consumption_order.xsd")
        assert valid, f"CRM→Facturatie consumption_order fails Facturatie XSD:\n{err}"


# ═══════════════════════════════════════════════════════════════════════
# F·1  FACTUUR — CRM → Facturatie (invoice_request)
# ═══════════════════════════════════════════════════════════════════════

class TestF1_CRMToFacturatie_InvoiceRequest:
    """
    Flow F·1: CRM sends invoice_request to Facturatie.
    """

    def test_crm_invoice_request_validates_against_facturatie_xsd(self):
        xml = (FIXTURES / "crm" / "invoice_request.xml").read_text()
        valid, err = validate_xml_against_xsd(xml, FACTURATIE_XSD / "invoice_request.xsd")
        assert valid, f"CRM invoice_request fails Facturatie XSD:\n{err}"


class TestF1_FacturatieToCRM_InvoiceStatus:
    """
    Flow F·1: Facturatie sends invoice_status back to CRM.
    """

    def test_facturatie_invoice_status_validates_against_facturatie_xsd(self):
        xml = (FIXTURES / "facturatie" / "invoice_status.xml").read_text()
        valid, err = validate_xml_against_xsd(xml, FACTURATIE_XSD / "invoice_status.xsd")
        assert valid, f"Facturatie invoice_status fails own XSD:\n{err}"


class TestF1_FacturatieToMailing_SendMailing:
    """
    Flow F·1: Facturatie sends send_mailing to Mailing (PDF invoice).
    """

    def test_facturatie_send_mailing_validates_against_facturatie_xsd(self):
        xml = (FIXTURES / "facturatie" / "send_mailing.xml").read_text()
        valid, err = validate_xml_against_xsd(xml, FACTURATIE_XSD / "send_mailing.xsd")
        assert valid, f"Facturatie send_mailing fails own XSD:\n{err}"


# ═══════════════════════════════════════════════════════════════════════
# F·2  FACTUUR ANNULEREN — CRM → Facturatie (invoice_cancelled)
# ═══════════════════════════════════════════════════════════════════════

class TestF2_CRMToFacturatie_InvoiceCancelled:
    """
    Flow F·2: CRM sends invoice_cancelled to Facturatie.
    """

    def test_crm_invoice_cancelled_validates_against_facturatie_xsd(self):
        xml = (FIXTURES / "crm" / "invoice_cancelled.xml").read_text()
        valid, err = validate_xml_against_xsd(xml, FACTURATIE_XSD / "invoice_cancelled.xsd")
        assert valid, f"CRM invoice_cancelled fails Facturatie XSD:\n{err}"


# ═══════════════════════════════════════════════════════════════════════
# O·1  HEARTBEAT — Sidecar → Monitoring
# ═══════════════════════════════════════════════════════════════════════

class TestO1_Heartbeat:
    """
    Flow O·1: Sidecar sends heartbeat to Monitoring.
    """

    def test_heartbeat_validates_against_heartbeat_xsd(self):
        xml = (FIXTURES / "heartbeat" / "heartbeat.xml").read_text()
        valid, err = validate_xml_against_xsd(xml, HEARTBEAT_XSD / "heartbeat.xsd")
        assert valid, f"Heartbeat fails heartbeat XSD:\n{err}"


# ═══════════════════════════════════════════════════════════════════════
# CROSS-TEAM XSD COMPATIBILITY — same message type, multiple teams
# ═══════════════════════════════════════════════════════════════════════

class TestCrossTeam_ConsumptionOrder_KassaVsFacturatie:
    """
    Verify Kassa and Facturatie agree on the consumption_order schema.
    The same XML should validate against both XSDs.
    """

    def test_same_consumption_order_validates_both_xsds(self):
        xml = (FIXTURES / "kassa" / "consumption_order.xml").read_text()
        valid_kassa, err_kassa = validate_xml_against_xsd(
            xml, KASSA_XSD / "schema_consumption_order_v2.3.xsd"
        )
        valid_facturatie, err_fac = validate_xml_against_xsd(
            xml, FACTURATIE_XSD / "consumption_order.xsd"
        )
        assert valid_kassa, f"Kassa XSD rejects:\n{err_kassa}"
        assert valid_facturatie, f"Facturatie XSD rejects:\n{err_fac}"


class TestCrossTeam_SessionCreated_PlanningVsFrontend:
    """
    Verify Planning and Frontend agree on the session_created schema.
    """

    def test_same_session_created_validates_both_xsds(self):
        xml = (FIXTURES / "planning" / "session_created.xml").read_text()
        valid_planning, err_p = validate_xml_against_xsd(
            xml, PLANNING_XSD / "session_created.xsd"
        )
        valid_frontend, err_f = validate_xml_against_xsd(
            xml, FRONTEND_XSD / "session_created.xsd"
        )
        assert valid_planning, f"Planning XSD rejects:\n{err_p}"
        assert valid_frontend, f"Frontend XSD rejects:\n{err_f}"


class TestCrossTeam_CalendarInvite_FrontendVsPlanning:
    """
    Verify Frontend and Planning agree on the calendar_invite schema.
    """

    def test_same_calendar_invite_validates_both_xsds(self):
        xml = (FIXTURES / "frontend" / "calendar_invite.xml").read_text()
        valid_frontend, err_f = validate_xml_against_xsd(
            xml, FRONTEND_XSD / "calendar_invite.xsd"
        )
        valid_planning, err_p = validate_xml_against_xsd(
            xml, PLANNING_XSD / "calendar_invite.xsd"
        )
        assert valid_frontend, f"Frontend XSD rejects:\n{err_f}"
        assert valid_planning, f"Planning XSD rejects:\n{err_p}"


class TestCrossTeam_SessionViewRequest_FrontendVsPlanning:
    """
    Verify Frontend and Planning agree on session_view_request.
    """

    def test_same_session_view_request_validates_both_xsds(self):
        xml = (FIXTURES / "frontend" / "session_view_request.xml").read_text()
        valid_f, err_f = validate_xml_against_xsd(
            xml, FRONTEND_XSD / "session_view_request.xsd"
        )
        valid_p, err_p = validate_xml_against_xsd(
            xml, PLANNING_XSD / "session_view_request.xsd"
        )
        assert valid_f, f"Frontend XSD rejects:\n{err_f}"
        assert valid_p, f"Planning XSD rejects:\n{err_p}"


class TestCrossTeam_SessionViewResponse_PlanningVsFrontend:
    """
    Verify Planning and Frontend agree on session_view_response.
    """

    def test_same_session_view_response_validates_both_xsds(self):
        xml = (FIXTURES / "planning" / "session_view_response.xml").read_text()
        valid_p, err_p = validate_xml_against_xsd(
            xml, PLANNING_XSD / "session_view_response.xsd"
        )
        valid_f, err_f = validate_xml_against_xsd(
            xml, FRONTEND_XSD / "session_view_response.xsd"
        )
        assert valid_p, f"Planning XSD rejects:\n{err_p}"
        assert valid_f, f"Frontend XSD rejects:\n{err_f}"


class TestR1_FrontendToCRM_UserCreated:
    def test_frontend_user_created_validates_against_crm_xsd(self):
        xml = (FIXTURES / "frontend" / "user_created.xml").read_text()
        valid, err = validate_xml_against_xsd(xml, REPO_ROOT / "CRM/xsd/user_created.xsd")
        assert valid, f"Validation failed: {err}"

class TestR1_FrontendToCRM_UserRegistered:
    def test_frontend_user_registered_validates_against_crm_xsd(self):
        xml = (FIXTURES / "frontend" / "user_registered.xml").read_text()
        valid, err = validate_xml_against_xsd(xml, REPO_ROOT / "CRM/xsd/user_registered.xsd")
        assert valid, f"Validation failed: {err}"

class TestR4_FrontendToCRM_UserUpdated:
    def test_frontend_user_updated_validates_against_crm_xsd(self):
        xml = (FIXTURES / "frontend" / "user_updated.xml").read_text()
        valid, err = validate_xml_against_xsd(xml, REPO_ROOT / "CRM/xsd/user_updated.xsd")
        assert valid, f"Validation failed: {err}"

class TestR5_FrontendToCRM_UserDeleted:
    def test_frontend_user_deleted_validates_against_crm_xsd(self):
        xml = (FIXTURES / "frontend" / "user_deleted.xml").read_text()
        valid, err = validate_xml_against_xsd(xml, REPO_ROOT / "CRM/xsd/user_deleted.xsd")
        assert valid, f"Validation failed: {err}"

class TestB1_FrontendToCRM_BusinessInvite:
    def test_frontend_business_invite_validates_against_crm_xsd(self):
        xml = (FIXTURES / "frontend" / "business_invite.xml").read_text()
        valid, err = validate_xml_against_xsd(xml, REPO_ROOT / "CRM/xsd/business_invite.xsd")
        assert valid, f"Validation failed: {err}"

class TestN2_FrontendToCRM_CancelRegistration:
    def test_frontend_cancel_registration_validates_against_crm_xsd(self):
        xml = (FIXTURES / "frontend" / "cancel_registration.xml").read_text()
        valid, err = validate_xml_against_xsd(xml, REPO_ROOT / "CRM/xsd/cancel_registration.xsd")
        assert valid, f"Validation failed: {err}"

class TestO4_FrontendToCRM_EventEnded:
    def test_frontend_event_ended_validates_against_crm_xsd(self):
        xml = (FIXTURES / "frontend" / "event_ended.xml").read_text()
        valid, err = validate_xml_against_xsd(xml, REPO_ROOT / "CRM/xsd/event_ended.xsd")
        assert valid, f"Validation failed: {err}"

class TestOps_Log:
    def test_frontend_log_validates_against_monitoring_xsd(self):
        xml = (FIXTURES / "frontend" / "log.xml").read_text()
        valid, err = validate_xml_against_xsd(xml, REPO_ROOT / "monitoring/xsd/log.xsd")
        assert valid, f"Validation failed: {err}"

class TestE1_KassaToMonitoring_SystemError:
    def test_kassa_system_error_validates_against_monitoring_xsd(self):
        xml = (FIXTURES / "kassa" / "system_error.xml").read_text()
        valid, err = validate_xml_against_xsd(xml, REPO_ROOT / "monitoring/xsd/system_error.xsd")
        assert valid, f"Validation failed: {err}"

class TestK5_CRMToKassa_WalletRemoteTopup:
    def test_crm_wallet_remote_topup_validates_against_kassa_xsd(self):
        xml = (FIXTURES / "crm" / "wallet_remote_topup.xml").read_text()
        valid, err = validate_xml_against_xsd(xml, REPO_ROOT / "Kassa/integratie/schemas/wallet_remote_topup.xsd")
        assert valid, f"Validation failed: {err}"

class TestK4_CRMToKassa_WalletLeaseGrant:
    def test_crm_wallet_lease_grant_validates_against_kassa_xsd(self):
        xml = (FIXTURES / "crm" / "wallet_lease_grant.xml").read_text()
        valid, err = validate_xml_against_xsd(xml, REPO_ROOT / "Kassa/integratie/schemas/wallet_lease_grant.xsd")
        assert valid, f"Validation failed: {err}"

class TestK2_CRMToFrontend_WalletBalanceUpdate:
    def test_crm_wallet_balance_update_validates_against_frontend_xsd(self):
        xml = (FIXTURES / "crm" / "wallet_balance_update.xml").read_text()
        valid, err = validate_xml_against_xsd(xml, REPO_ROOT / "IP-groep1-frontend/xsd/wallet_balance_update.xsd")
        assert valid, f"Validation failed: {err}"

class TestS5_PlanningToFrontend_SessionOccupancyUpdate:
    def test_planning_session_occupancy_update_validates_against_frontend_xsd(self):
        xml = (FIXTURES / "planning" / "session_occupancy_update.xml").read_text()
        valid, err = validate_xml_against_xsd(xml, REPO_ROOT / "IP-groep1-frontend/xsd/session_occupancy_update.xsd")
        assert valid, f"Validation failed: {err}"

class TestE2_CRMToFrontend_VatValidationError:
    def test_crm_vat_validation_error_validates_against_frontend_xsd(self):
        xml = (FIXTURES / "crm" / "vat_validation_error.xml").read_text()
        valid, err = validate_xml_against_xsd(xml, REPO_ROOT / "IP-groep1-frontend/xsd/vat_validation_error.xsd")
        assert valid, f"Validation failed: {err}"

class TestF1_FacturatieToFrontend_InvoiceAvailable:
    def test_facturatie_invoice_available_validates_against_frontend_xsd(self):
        xml = (FIXTURES / "facturatie" / "invoice_available.xml").read_text()
        valid, err = validate_xml_against_xsd(xml, REPO_ROOT / "IP-groep1-frontend/xsd/invoice_available.xsd")
        assert valid, f"Validation failed: {err}"

class TestR4_CRMToFacturatie_ProfileUpdate:
    def test_crm_profile_update_validates_against_facturatie_xsd(self):
        xml = (FIXTURES / "crm" / "profile_update.xml").read_text()
        valid, err = validate_xml_against_xsd(xml, REPO_ROOT / "Facturatie/xsd/profile_update.xsd")
        assert valid, f"Validation failed: {err}"

class TestM1_CRMToMailing_SendMailing:
    def test_crm_send_mailing_validates_against_mailing_xsd(self):
        xml = (FIXTURES / "crm" / "send_mailing.xml").read_text()
        valid, err = validate_xml_against_xsd(xml, REPO_ROOT / "Mailing/xsd/send_mailing.xsd")
        assert valid, f"Validation failed: {err}"

class TestE1_MonitoringToMailing_SystemAlert:
    def test_monitoring_system_alert_validates_against_mailing_xsd(self):
        xml = (FIXTURES / "monitoring" / "system_alert.xml").read_text()
        valid, err = validate_xml_against_xsd(xml, REPO_ROOT / "Mailing/xsd/system_alert.xsd")
        assert valid, f"Validation failed: {err}"

# ═══════════════════════════════════════════════════════════════════════
# NEGATIVE TESTS (REJECTIONS) — Contract Violations v2.3
# ═══════════════════════════════════════════════════════════════════════

class TestContractRejections:
    """
    These tests ensure that the XSD schemas correctly REJECT invalid payloads.
    If these tests fail, it means a team's XSD is too permissive.
    """

    def test_reject_xmlns_in_header(self):
        """Rule 1: xmlns namespaces are forbidden in v2.0"""
        xml = (
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<message xmlns="urn:integration:planning:v1">'
            '<header><message_id>123e4567-e89b-12d3-a456-426614174000</message_id>'
            '<timestamp>2026-01-01T00:00:00Z</timestamp>'
            '<source>crm</source><type>heartbeat</type><version>2.0</version></header>'
            '<body><status>online</status></body></message>'
        )
        valid, err = validate_xml_against_xsd(xml, HEARTBEAT_XSD / "heartbeat.xsd")
        assert not valid, "XSD allowed an xmlns namespace, which is forbidden in v2.3"

    def test_reject_version_1_0(self):
        """Contract requires version 2.0"""
        xml = (
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<heartbeat>'
            '<header><message_id>123e4567-e89b-12d3-a456-426614174000</message_id>'
            '<timestamp>2026-01-01T00:00:00Z</timestamp>'
            '<source>crm</source><type>heartbeat</type><version>1.0</version></header>'
            '<body><status>online</status></body></heartbeat>'
        )
        valid, err = validate_xml_against_xsd(xml, HEARTBEAT_XSD / "heartbeat.xsd")
        assert not valid, "XSD allowed <version>1.0</version>, must strictly enforce 2.0"

    def test_reject_age_instead_of_date_of_birth(self):
        """Rule 4: <date_of_birth> must be used, not <age>"""
        xml = (
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<new_registration>'
            '<header><message_id>123e4567-e89b-12d3-a456-426614174000</message_id>'
            '<timestamp>2026-01-01T00:00:00Z</timestamp>'
            '<source>frontend</source><type>new_registration</type><version>2.0</version></header>'
            '<body>'
            '<user_id>e8b27c1d-4f2a-4b3e-9c5f-000000000001</user_id>'
            '<type>private</type>'
            '<contact>'
            '<first_name>Jan</first_name><last_name>Peeters</last_name><email>j@j.be</email>'
            '<age>29</age>'
            '</contact>'
            '<payment_due currency="eur">0.00</payment_due>'
            '</body></new_registration>'
        )
        valid, err = validate_xml_against_xsd(xml, FRONTEND_XSD / "new_registration.xsd")
        assert not valid, "Frontend XSD allowed <age> field, must require <date_of_birth>"

    def test_reject_missing_currency_attribute(self):
        """Rule 3: Monetary fields must have currency='eur' attribute"""
        xml = (
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<consumption_order>'
            '<header><message_id>123e4567-e89b-12d3-a456-426614174000</message_id>'
            '<timestamp>2026-01-01T00:00:00Z</timestamp>'
            '<source>kassa</source><type>consumption_order</type><version>2.0</version></header>'
            '<body>'
            '<user_id>123</user_id>'
            '<badge_id>BADGE-001</badge_id>'
            '<items>'
            '<item>'
            '<name>Koffie</name><quantity>1</quantity><unit_price>3.00</unit_price><total_amount>3.00</total_amount>'
            '</item>'
            '</items>'
            '<total_order_amount>3.00</total_order_amount>'
            '</body></consumption_order>'
        )
        valid, err = validate_xml_against_xsd(xml, KASSA_XSD / "schema_consumption_order_v2.3.xsd")
        assert not valid, "Kassa XSD allowed missing currency attribute on monetary field"

# ═══════════════════════════════════════════════════════════════════════
# ADDITIONAL V2.3 FLOWS (Gap Analysis)
# ═══════════════════════════════════════════════════════════════════════

class TestK3_KassaToCRM_RefundProcessed:
    """
    Flow K·3: Kassa sends refund_processed to CRM.
    """
    def test_kassa_refund_processed_validates_against_kassa_xsd(self):
        xml = (FIXTURES / "kassa" / "refund_processed.xml").read_text()
        # Note: Kassa XSD has a known bug in UUID pattern in some versions
        valid, err = validate_xml_against_xsd(xml, KASSA_XSD / "schema_refund_processed.xsd")
        assert valid, f"Kassa refund_processed fails own XSD:\n{err}"

class TestK4_KassaToCRM_WalletLeaseRequest:
    """
    Flow K·4: Kassa sends wallet_lease_request to CRM.
    """
    def test_kassa_wallet_lease_request_exists(self):
        # We don't have a specific XSD for request yet, usually uses lease_grant schema or generic error
        # For now we check if it validates against a generic message structure if available
        xml = (FIXTURES / "kassa" / "wallet_lease_request.xml").read_text()
        # Placeholder for real XSD if team adds it
        xsd = KASSA_XSD / "schema_wallet_lease_request.xsd"
        if not xsd.exists():
            pytest.skip("Missing schema_wallet_lease_request.xsd")
        valid, err = validate_xml_against_xsd(xml, xsd)
        assert valid, err

class TestK6_KassaToCRM_WalletLeaseReturn:
    """
    Flow K·6: Kassa sends wallet_lease_return to CRM.
    """
    def test_kassa_wallet_lease_return_exists(self):
        xml = (FIXTURES / "kassa" / "wallet_lease_return.xml").read_text()
        xsd = KASSA_XSD / "schema_wallet_lease_return.xsd"
        if not xsd.exists():
            pytest.skip("Missing schema_wallet_lease_return.xsd")
        valid, err = validate_xml_against_xsd(xml, xsd)
        assert valid, err

class TestN1_CRMToPlanning_SessionRegistrationConfirmed:
    """
    Flow N·1: CRM sends session_registration_confirmed to Planning.
    """
    def test_crm_session_registration_confirmed_exists(self):
        xml = (FIXTURES / "crm" / "session_registration_confirmed.xml").read_text()
        valid, err = validate_xml_against_xsd(xml, PLANNING_XSD / "session_registration_confirmed.xsd")
        assert valid, f"CRM session_registration_confirmed fails Planning XSD:\n{err}"
