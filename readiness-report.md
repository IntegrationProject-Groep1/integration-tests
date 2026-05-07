# 🔗 Integration Readiness Report

> **Generated**: 2026-05-07 12:41 UTC  
> **Deadline**: 2026-05-10 23:59 CET  
> **Generale repetitie**: 13/05/2026 10:00 Aula 6

## Overall Progress: 56/61 (91%)
```
██████████████████░░ 91%
```
✅ Passed: 56 | ❌ Failed: 5 | ⏭️ Skipped: 0

## Per-Team Status

| Team | Status | Pass | Fail | Skip | Progress |
|------|--------|------|------|------|----------|
| **Frontend** | 🟢 Ready | 28 | 0 | 0 | 100% |
| **CRM** | 🟢 Ready | 22 | 0 | 0 | 100% |
| **Kassa** | 🟢 Ready | 7 | 0 | 0 | 100% |
| **Facturatie** | 🟢 Ready | 9 | 0 | 0 | 100% |
| **Planning** | 🟢 Ready | 17 | 0 | 0 | 100% |
| **Mailing** | 🟢 Ready | 3 | 0 | 0 | 100% |
| **Monitoring** | 🟢 Ready | 4 | 0 | 0 | 100% |
| **Sidecar** | 🟢 Ready | 1 | 0 | 0 | 100% |

## Detailed Results per Team

### Frontend

#### Definition of Done Checks
  ✅ **Docker Compose Exists**
  ❌ **User Unregistered Sender Exists**

#### Integration Contracts
  ✅ `new_registration` (R·1 Registratie) — test_frontend_new_registration_validates_against_frontend_xsd
  ✅ `session_create_request` (S·1 Sessie aanmaken) — test_frontend_session_create_request_validates_against_planning_xsd
  ✅ `session_created` (S·1 Sessie aanmaken) — test_planning_session_created_validates_against_frontend_xsd
  ✅ `session_created` (S·1 Sessie aanmaken) — test_planning_session_created_validates_against_own_xsd
  ✅ `session_view_request` (S·2 Sessies opvragen) — test_frontend_session_view_request_validates_against_planning_xsd
  ✅ `session_view_response` (S·2 Sessies opvragen) — test_planning_session_view_response_validates_against_planning_xsd
  ✅ `session_view_response` (S·2 Sessies opvragen) — test_planning_session_view_response_validates_against_frontend_xsd
  ✅ `session_updated` (S·3 Sessie verplaatsen) — test_planning_session_updated_validates_against_frontend_xsd
  ✅ `session_delete_request` (S·4 Sessie verwijderen) — test_frontend_session_delete_request_validates_against_planning_xsd
  ✅ `session_deleted` (S·4 Sessie verwijderen) — test_planning_session_deleted_validates_against_frontend_xsd
  ✅ `calendar_invite` (N·1 Inschrijving) — test_frontend_calendar_invite_validates_against_planning_xsd
  ✅ `calendar_invite` (N·1 Inschrijving) — test_frontend_calendar_invite_validates_against_own_xsd
  ✅ `calendar_invite_confirmed` (N·1 Inschrijving) — test_planning_calendar_invite_confirmed_validates_against_frontend_xsd
  ✅ `session_created` (XSD Compatibility) — test_same_session_created_validates_both_xsds
  ✅ `calendar_invite` (XSD Compatibility) — test_same_calendar_invite_validates_both_xsds
  ✅ `session_view_request` (XSD Compatibility) — test_same_session_view_request_validates_both_xsds
  ✅ `session_view_response` (XSD Compatibility) — test_same_session_view_response_validates_both_xsds
  ✅ `user_created` (R·1 Registratie) — test_frontend_user_created_validates_against_crm_xsd
  ✅ `user_registered` (R·1 Registratie) — test_frontend_user_registered_validates_against_crm_xsd
  ✅ `user_updated` (R·4 Profiel wijzigen) — test_frontend_user_updated_validates_against_crm_xsd
  ✅ `user_deleted` (R·5 Account verwijderen) — test_frontend_user_deleted_validates_against_crm_xsd
  ✅ `business_invite` (B·1 Bedrijf nodigt collega uit) — test_frontend_business_invite_validates_against_crm_xsd
  ✅ `cancel_registration` (N·2 Inschrijving annuleren) — test_frontend_cancel_registration_validates_against_crm_xsd
  ✅ `event_ended` (O·4 Event beëindigd) — test_frontend_event_ended_validates_against_crm_xsd
  ✅ `wallet_balance_update` (K·2 Bar consumptie) — test_crm_wallet_balance_update_validates_against_frontend_xsd
  ✅ `session_occupancy_update` (S·5 Bezettingsgraad) — test_planning_session_occupancy_update_validates_against_frontend_xsd
  ✅ `vat_validation_error` (E·2 BTW-validatie mislukt) — test_crm_vat_validation_error_validates_against_frontend_xsd
  ✅ `invoice_available` (F·1 Factuur opstellen) — test_facturatie_invoice_available_validates_against_frontend_xsd

### CRM

#### Definition of Done Checks
  ✅ **Supabase References Removed**
  ✅ **Unit Tests Exist**

#### Integration Contracts
  ✅ `new_registration` (R·1 Registratie) — test_frontend_new_registration_validates_against_frontend_xsd
  ✅ `new_registration` (R·1 Registratie (forward)) — test_crm_new_registration_validates_against_kassa_xsd
  ✅ `payment_registered` (K·1 Betaling) — test_kassa_payment_registered_validates_against_kassa_xsd
  ✅ `payment_registered` (K·1 Betaling (forward)) — test_crm_payment_registered_validates_against_facturatie_xsd
  ✅ `consumption_order` (K·2 Bar consumptie) — test_kassa_consumption_order_validates_against_kassa_xsd
  ✅ `consumption_order` (K·2 Bar consumptie (forward)) — test_crm_consumption_order_validates_against_facturatie_xsd
  ✅ `invoice_request` (F·1 Factuur) — test_crm_invoice_request_validates_against_facturatie_xsd
  ✅ `invoice_status` (F·1 Factuur) — test_facturatie_invoice_status_validates_against_facturatie_xsd
  ✅ `invoice_cancelled` (F·2 Factuur annuleren) — test_crm_invoice_cancelled_validates_against_facturatie_xsd
  ✅ `user_created` (R·1 Registratie) — test_frontend_user_created_validates_against_crm_xsd
  ✅ `user_registered` (R·1 Registratie) — test_frontend_user_registered_validates_against_crm_xsd
  ✅ `user_updated` (R·4 Profiel wijzigen) — test_frontend_user_updated_validates_against_crm_xsd
  ✅ `user_deleted` (R·5 Account verwijderen) — test_frontend_user_deleted_validates_against_crm_xsd
  ✅ `business_invite` (B·1 Bedrijf nodigt collega uit) — test_frontend_business_invite_validates_against_crm_xsd
  ✅ `cancel_registration` (N·2 Inschrijving annuleren) — test_frontend_cancel_registration_validates_against_crm_xsd
  ✅ `event_ended` (O·4 Event beëindigd) — test_frontend_event_ended_validates_against_crm_xsd
  ✅ `wallet_remote_topup` (K·5 Wallet opladen) — test_crm_wallet_remote_topup_validates_against_kassa_xsd
  ✅ `wallet_lease_grant` (K·4 QR-scan inkom) — test_crm_wallet_lease_grant_validates_against_kassa_xsd
  ✅ `wallet_balance_update` (K·2 Bar consumptie) — test_crm_wallet_balance_update_validates_against_frontend_xsd
  ✅ `vat_validation_error` (E·2 BTW-validatie mislukt) — test_crm_vat_validation_error_validates_against_frontend_xsd
  ✅ `profile_update` (R·4 Profiel wijzigen) — test_crm_profile_update_validates_against_facturatie_xsd
  ✅ `send_mailing` (M·1 Mailinglijst) — test_crm_send_mailing_validates_against_mailing_xsd

### Kassa

#### Integration Contracts
  ✅ `new_registration` (R·1 Registratie (forward)) — test_crm_new_registration_validates_against_kassa_xsd
  ✅ `payment_registered` (K·1 Betaling) — test_kassa_payment_registered_validates_against_kassa_xsd
  ✅ `consumption_order` (K·2 Bar consumptie) — test_kassa_consumption_order_validates_against_kassa_xsd
  ✅ `consumption_order` (XSD Compatibility) — test_same_consumption_order_validates_both_xsds
  ✅ `system_error` (E·1 Systeemfout) — test_kassa_system_error_validates_against_monitoring_xsd
  ✅ `wallet_remote_topup` (K·5 Wallet opladen) — test_crm_wallet_remote_topup_validates_against_kassa_xsd
  ✅ `wallet_lease_grant` (K·4 QR-scan inkom) — test_crm_wallet_lease_grant_validates_against_kassa_xsd

### Facturatie

#### Definition of Done Checks
  ❌ **Dead Letter Queue Configured**

#### Integration Contracts
  ✅ `payment_registered` (K·1 Betaling (forward)) — test_crm_payment_registered_validates_against_facturatie_xsd
  ✅ `consumption_order` (K·2 Bar consumptie (forward)) — test_crm_consumption_order_validates_against_facturatie_xsd
  ✅ `invoice_request` (F·1 Factuur) — test_crm_invoice_request_validates_against_facturatie_xsd
  ✅ `invoice_status` (F·1 Factuur) — test_facturatie_invoice_status_validates_against_facturatie_xsd
  ✅ `send_mailing` (F·1 Factuur (mail)) — test_facturatie_send_mailing_validates_against_facturatie_xsd
  ✅ `invoice_cancelled` (F·2 Factuur annuleren) — test_crm_invoice_cancelled_validates_against_facturatie_xsd
  ✅ `consumption_order` (XSD Compatibility) — test_same_consumption_order_validates_both_xsds
  ✅ `invoice_available` (F·1 Factuur opstellen) — test_facturatie_invoice_available_validates_against_frontend_xsd
  ✅ `profile_update` (R·4 Profiel wijzigen) — test_crm_profile_update_validates_against_facturatie_xsd

### Planning

#### Definition of Done Checks
  ✅ **Microsoft Graph Api Integrated**

#### Integration Contracts
  ✅ `session_create_request` (S·1 Sessie aanmaken) — test_frontend_session_create_request_validates_against_planning_xsd
  ✅ `session_created` (S·1 Sessie aanmaken) — test_planning_session_created_validates_against_frontend_xsd
  ✅ `session_created` (S·1 Sessie aanmaken) — test_planning_session_created_validates_against_own_xsd
  ✅ `session_view_request` (S·2 Sessies opvragen) — test_frontend_session_view_request_validates_against_planning_xsd
  ✅ `session_view_response` (S·2 Sessies opvragen) — test_planning_session_view_response_validates_against_planning_xsd
  ✅ `session_view_response` (S·2 Sessies opvragen) — test_planning_session_view_response_validates_against_frontend_xsd
  ✅ `session_updated` (S·3 Sessie verplaatsen) — test_planning_session_updated_validates_against_frontend_xsd
  ✅ `session_delete_request` (S·4 Sessie verwijderen) — test_frontend_session_delete_request_validates_against_planning_xsd
  ✅ `session_deleted` (S·4 Sessie verwijderen) — test_planning_session_deleted_validates_against_frontend_xsd
  ✅ `calendar_invite` (N·1 Inschrijving) — test_frontend_calendar_invite_validates_against_planning_xsd
  ✅ `calendar_invite` (N·1 Inschrijving) — test_frontend_calendar_invite_validates_against_own_xsd
  ✅ `calendar_invite_confirmed` (N·1 Inschrijving) — test_planning_calendar_invite_confirmed_validates_against_frontend_xsd
  ✅ `session_created` (XSD Compatibility) — test_same_session_created_validates_both_xsds
  ✅ `calendar_invite` (XSD Compatibility) — test_same_calendar_invite_validates_both_xsds
  ✅ `session_view_request` (XSD Compatibility) — test_same_session_view_request_validates_both_xsds
  ✅ `session_view_response` (XSD Compatibility) — test_same_session_view_response_validates_both_xsds
  ✅ `session_occupancy_update` (S·5 Bezettingsgraad) — test_planning_session_occupancy_update_validates_against_frontend_xsd

### Mailing

#### Integration Contracts
  ✅ `send_mailing` (F·1 Factuur (mail)) — test_facturatie_send_mailing_validates_against_facturatie_xsd
  ✅ `send_mailing` (M·1 Mailinglijst) — test_crm_send_mailing_validates_against_mailing_xsd
  ✅ `system_alert` (E·1 Systeemfout) — test_monitoring_system_alert_validates_against_mailing_xsd

### Monitoring

#### Integration Contracts
  ✅ `heartbeat` (O·1 Heartbeat) — test_heartbeat_validates_against_heartbeat_xsd
  ✅ `log` (O·3 Centraal loggen) — test_frontend_log_validates_against_monitoring_xsd
  ✅ `system_error` (E·1 Systeemfout) — test_kassa_system_error_validates_against_monitoring_xsd
  ✅ `system_alert` (E·1 Systeemfout) — test_monitoring_system_alert_validates_against_mailing_xsd

### Sidecar

#### Integration Contracts
  ✅ `heartbeat` (O·1 Heartbeat) — test_heartbeat_validates_against_heartbeat_xsd

## Cross-Team XSD Compatibility

These tests verify that when Team A sends a message and Team B receives it,
the XML validates against **both** teams' XSD schemas.

- ✅ **consumption_order** — Kassa ↔ Facturatie
- ✅ **session_created** — Planning ↔ Frontend
- ✅ **calendar_invite** — Frontend ↔ Planning
- ✅ **session_view_request** — Frontend ↔ Planning
- ✅ **session_view_response** — Planning ↔ Frontend

## ⚠️ Not Yet Covered by These Tests

The following integration points are documented in the flows but don't have
XSD schemas from both sides yet, so we can't test them:

- `identity_request / identity_response` — RPC (Identity Service)
- `wallet_lease_request` / `wallet_lease_return` — Kassa ↔ CRM
- `session_registration_confirmed` — CRM → Planning
- `refund_processed` — Kassa → CRM

**Teams**: Add your XSD files to your team directory and create matching
fixture XML files in `integration-tests/fixtures/<team>/` to enable testing.

---
*Report generated by integration-tests/generate_report.py*