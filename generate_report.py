"""
Generate a Markdown readiness report from pytest test results.

This script is run after pytest and produces a visual per-team scoreboard
showing which integration contracts pass and which still need work.

Deadline: 10/05/2026 23:59 — Generale repetitie: 13/05 10:00 Aula 6
"""

import subprocess
import sys
import json
import re
from pathlib import Path
from datetime import datetime, timezone


def run_tests():
    """Run pytest with JSON output and capture results."""
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "test_contracts.py", "test_dod_checks.py", "-v", "--tb=line", "--no-header"],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent,
    )
    return result.stdout, result.stderr, result.returncode


def parse_results(stdout: str):
    """Parse pytest verbose output into structured results."""
    tests = []
    dod_tests = []
    for line in stdout.splitlines():
        # Match lines like: test_contracts.py::TestClass::test_method PASSED
        # Also handles potential path separators
        match = re.search(r"(test_contracts\.py|test_dod_checks\.py)::(\S+)\s+(PASSED|FAILED|ERROR|SKIPPED)", line)
        if match:
            file_type = match.group(1)
            full_name = match.group(2)
            status = match.group(3)
            if file_type == "test_contracts.py":
                tests.append({"name": full_name, "status": status})
            else:
                dod_tests.append({"name": full_name, "status": status})
    return tests, dod_tests


# Map test classes to team integration points
TEAM_MAP = {
    "TestR1_FrontendToCRM_NewRegistration": {
        "sender": "Frontend",
        "receiver": "CRM",
        "flow": "R·1 Registratie",
        "message": "new_registration",
    },
    "TestR1_CRMToKassa_NewRegistration": {
        "sender": "CRM",
        "receiver": "Kassa",
        "flow": "R·1 Registratie (forward)",
        "message": "new_registration",
    },
    "TestS1_FrontendToPlanning_SessionCreateRequest": {
        "sender": "Frontend",
        "receiver": "Planning",
        "flow": "S·1 Sessie aanmaken",
        "message": "session_create_request",
    },
    "TestS1_PlanningToFrontend_SessionCreated": {
        "sender": "Planning",
        "receiver": "Frontend",
        "flow": "S·1 Sessie aanmaken",
        "message": "session_created",
    },
    "TestS2_FrontendToPlanning_SessionViewRequest": {
        "sender": "Frontend",
        "receiver": "Planning",
        "flow": "S·2 Sessies opvragen",
        "message": "session_view_request",
    },
    "TestS2_PlanningToFrontend_SessionViewResponse": {
        "sender": "Planning",
        "receiver": "Frontend",
        "flow": "S·2 Sessies opvragen",
        "message": "session_view_response",
    },
    "TestS3_PlanningToFrontend_SessionUpdated": {
        "sender": "Planning",
        "receiver": "Frontend",
        "flow": "S·3 Sessie verplaatsen",
        "message": "session_updated",
    },
    "TestS4_FrontendToPlanning_SessionDeleteRequest": {
        "sender": "Frontend",
        "receiver": "Planning",
        "flow": "S·4 Sessie verwijderen",
        "message": "session_delete_request",
    },
    "TestS4_PlanningToFrontend_SessionDeleted": {
        "sender": "Planning",
        "receiver": "Frontend",
        "flow": "S·4 Sessie verwijderen",
        "message": "session_deleted",
    },
    "TestN1_FrontendToPlanning_CalendarInvite": {
        "sender": "Frontend",
        "receiver": "Planning",
        "flow": "N·1 Inschrijving",
        "message": "calendar_invite",
    },
    "TestN1_PlanningToFrontend_CalendarInviteConfirmed": {
        "sender": "Planning",
        "receiver": "Frontend",
        "flow": "N·1 Inschrijving",
        "message": "calendar_invite_confirmed",
    },
    "TestK1_KassaToCRM_PaymentRegistered": {
        "sender": "Kassa",
        "receiver": "CRM",
        "flow": "K·1 Betaling",
        "message": "payment_registered",
    },
    "TestK1_CRMToFacturatie_PaymentRegistered": {
        "sender": "CRM",
        "receiver": "Facturatie",
        "flow": "K·1 Betaling (forward)",
        "message": "payment_registered",
    },
    "TestK2_KassaToCRM_ConsumptionOrder": {
        "sender": "Kassa",
        "receiver": "CRM",
        "flow": "K·2 Bar consumptie",
        "message": "consumption_order",
    },
    "TestK2_CRMToFacturatie_ConsumptionOrder": {
        "sender": "CRM",
        "receiver": "Facturatie",
        "flow": "K·2 Bar consumptie (forward)",
        "message": "consumption_order",
    },
    "TestF1_CRMToFacturatie_InvoiceRequest": {
        "sender": "CRM",
        "receiver": "Facturatie",
        "flow": "F·1 Factuur",
        "message": "invoice_request",
    },
    "TestF1_FacturatieToCRM_InvoiceStatus": {
        "sender": "Facturatie",
        "receiver": "CRM",
        "flow": "F·1 Factuur",
        "message": "invoice_status",
    },
    "TestF1_FacturatieToMailing_SendMailing": {
        "sender": "Facturatie",
        "receiver": "Mailing",
        "flow": "F·1 Factuur (mail)",
        "message": "send_mailing",
    },
    "TestF2_CRMToFacturatie_InvoiceCancelled": {
        "sender": "CRM",
        "receiver": "Facturatie",
        "flow": "F·2 Factuur annuleren",
        "message": "invoice_cancelled",
    },
    "TestO1_Heartbeat": {
        "sender": "Sidecar",
        "receiver": "Monitoring",
        "flow": "O·1 Heartbeat",
        "message": "heartbeat",
    },
    "TestR1_FrontendToCRM_UserCreated": {
        "sender": "Frontend",
        "receiver": "CRM",
        "flow": "R·1 Registratie",
        "message": "user_created",
    },
    "TestR1_FrontendToCRM_UserRegistered": {
        "sender": "Frontend",
        "receiver": "CRM",
        "flow": "R·1 Registratie",
        "message": "user_registered",
    },
    "TestR4_FrontendToCRM_UserUpdated": {
        "sender": "Frontend",
        "receiver": "CRM",
        "flow": "R·4 Profiel wijzigen",
        "message": "user_updated",
    },
    "TestR5_FrontendToCRM_UserDeleted": {
        "sender": "Frontend",
        "receiver": "CRM",
        "flow": "R·5 Account verwijderen",
        "message": "user_deleted",
    },
    "TestB1_FrontendToCRM_BusinessInvite": {
        "sender": "Frontend",
        "receiver": "CRM",
        "flow": "B·1 Bedrijf nodigt collega uit",
        "message": "business_invite",
    },
    "TestN2_FrontendToCRM_CancelRegistration": {
        "sender": "Frontend",
        "receiver": "CRM",
        "flow": "N·2 Inschrijving annuleren",
        "message": "cancel_registration",
    },
    "TestO4_FrontendToCRM_EventEnded": {
        "sender": "Frontend",
        "receiver": "CRM",
        "flow": "O·4 Event beëindigd",
        "message": "event_ended",
    },
    "TestOps_Log": {
        "sender": "Alle teams",
        "receiver": "Monitoring",
        "flow": "O·3 Centraal loggen",
        "message": "log",
    },
    "TestE1_KassaToMonitoring_SystemError": {
        "sender": "Kassa",
        "receiver": "Monitoring",
        "flow": "E·1 Systeemfout",
        "message": "system_error",
    },
    "TestK5_CRMToKassa_WalletRemoteTopup": {
        "sender": "CRM",
        "receiver": "Kassa",
        "flow": "K·5 Wallet opladen",
        "message": "wallet_remote_topup",
    },
    "TestK4_CRMToKassa_WalletLeaseGrant": {
        "sender": "CRM",
        "receiver": "Kassa",
        "flow": "K·4 QR-scan inkom",
        "message": "wallet_lease_grant",
    },
    "TestK2_CRMToFrontend_WalletBalanceUpdate": {
        "sender": "CRM",
        "receiver": "Frontend",
        "flow": "K·2 Bar consumptie",
        "message": "wallet_balance_update",
    },
    "TestS5_PlanningToFrontend_SessionOccupancyUpdate": {
        "sender": "Planning",
        "receiver": "Frontend",
        "flow": "S·5 Bezettingsgraad",
        "message": "session_occupancy_update",
    },
    "TestE2_CRMToFrontend_VatValidationError": {
        "sender": "CRM",
        "receiver": "Frontend",
        "flow": "E·2 BTW-validatie mislukt",
        "message": "vat_validation_error",
    },
    "TestF1_FacturatieToFrontend_InvoiceAvailable": {
        "sender": "Facturatie",
        "receiver": "Frontend",
        "flow": "F·1 Factuur opstellen",
        "message": "invoice_available",
    },
    "TestR4_CRMToFacturatie_ProfileUpdate": {
        "sender": "CRM",
        "receiver": "Facturatie",
        "flow": "R·4 Profiel wijzigen",
        "message": "profile_update",
    },
    "TestM1_CRMToMailing_SendMailing": {
        "sender": "CRM",
        "receiver": "Mailing",
        "flow": "M·1 Mailinglijst",
        "message": "send_mailing",
    },
    "TestE1_MonitoringToMailing_SystemAlert": {
        "sender": "Monitoring",
        "receiver": "Mailing",
        "flow": "E·1 Systeemfout",
        "message": "system_alert",
    },
    "TestContractRejections": {
        "sender": "Alle teams",
        "receiver": "Architectuur",
        "flow": "DLQ Contract Rejections",
        "message": "negative_tests",
    },
    "TestCrossTeam_ConsumptionOrder_KassaVsFacturatie": {
        "sender": "Kassa ↔ Facturatie",
        "receiver": "Cross-team",
        "flow": "XSD Compatibility",
        "message": "consumption_order",
    },
    "TestCrossTeam_SessionCreated_PlanningVsFrontend": {
        "sender": "Planning ↔ Frontend",
        "receiver": "Cross-team",
        "flow": "XSD Compatibility",
        "message": "session_created",
    },
    "TestCrossTeam_CalendarInvite_FrontendVsPlanning": {
        "sender": "Frontend ↔ Planning",
        "receiver": "Cross-team",
        "flow": "XSD Compatibility",
        "message": "calendar_invite",
    },
    "TestCrossTeam_SessionViewRequest_FrontendVsPlanning": {
        "sender": "Frontend ↔ Planning",
        "receiver": "Cross-team",
        "flow": "XSD Compatibility",
        "message": "session_view_request",
    },
    "TestCrossTeam_SessionViewResponse_PlanningVsFrontend": {
        "sender": "Planning ↔ Frontend",
        "receiver": "Cross-team",
        "flow": "XSD Compatibility",
        "message": "session_view_response",
    },
}

# All teams
ALL_TEAMS = ["Frontend", "CRM", "Kassa", "Facturatie", "Planning", "Mailing", "Monitoring", "Sidecar"]


def classify_test(test_name: str):
    """Extract class name from pytest test identifier."""
    parts = test_name.split("::")
    if len(parts) >= 1:
        return parts[0]
    return test_name


def generate_report(tests, dod_tests):
    """Generate the markdown report."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    deadline = "2026-05-10 23:59 CET"

    total = len(tests) + len(dod_tests)
    passed = sum(1 for t in tests if t["status"] == "PASSED") + sum(1 for t in dod_tests if t["status"] == "PASSED")
    failed = sum(1 for t in tests if t["status"] == "FAILED") + sum(1 for t in dod_tests if t["status"] == "FAILED")
    skipped = sum(1 for t in tests if t["status"] == "SKIPPED") + sum(1 for t in dod_tests if t["status"] == "SKIPPED")

    lines = []
    lines.append("# 🔗 Integration Readiness Report")
    lines.append("")
    lines.append(f"> **Generated**: {now}  ")
    lines.append(f"> **Deadline**: {deadline}  ")
    lines.append(f"> **Generale repetitie**: 13/05/2026 10:00 Aula 6")
    lines.append("")

    # Overall progress bar
    pct = int((passed / total * 100)) if total > 0 else 0
    bar_filled = "█" * (pct // 5)
    bar_empty = "░" * (20 - pct // 5)
    lines.append(f"## Overall Progress: {passed}/{total} ({pct}%)")
    lines.append(f"```")
    lines.append(f"{bar_filled}{bar_empty} {pct}%")
    lines.append(f"```")
    lines.append(f"✅ Passed: {passed} | ❌ Failed: {failed} | ⏭️ Skipped: {skipped}")
    lines.append("")

    # Per-team breakdown
    lines.append("## Per-Team Status")
    lines.append("")

    # Collect per-team stats
    team_stats = {}
    for team in ALL_TEAMS:
        team_stats[team] = {"pass": 0, "fail": 0, "skip": 0, "total": 0, "details": []}

    for test in tests:
        class_name = classify_test(test["name"])
        info = TEAM_MAP.get(class_name, None)
        if not info:
            continue

        status_icon = {"PASSED": "✅", "FAILED": "❌", "SKIPPED": "⏭️", "ERROR": "💥"}.get(test["status"], "❓")

        for team_key in ["sender", "receiver"]:
            team_name = info[team_key]
            # Handle cross-team names
            for team in ALL_TEAMS:
                if team in team_name:
                    team_stats[team]["total"] += 1
                    if test["status"] == "PASSED":
                        team_stats[team]["pass"] += 1
                    elif test["status"] == "FAILED":
                        team_stats[team]["fail"] += 1
                    else:
                        team_stats[team]["skip"] += 1

                    method_name = test["name"].split("::")[-1] if "::" in test["name"] else test["name"]
                    team_stats[team]["details"].append(
                        f"  {status_icon} `{info['message']}` ({info['flow']}) — {method_name}"
                    )

    # Summary table
    lines.append("| Team | Status | Pass | Fail | Skip | Progress |")
    lines.append("|------|--------|------|------|------|----------|")

    for team in ALL_TEAMS:
        s = team_stats[team]
        if s["total"] == 0:
            lines.append(f"| **{team}** | ⚪ No tests | 0 | 0 | 0 | — |")
        else:
            team_pct = int(s["pass"] / s["total"] * 100)
            if s["fail"] == 0 and s["skip"] == 0:
                status = "🟢 Ready"
            elif s["fail"] > 0:
                status = "🔴 Needs work"
            else:
                status = "🟡 Partial"
            lines.append(f"| **{team}** | {status} | {s['pass']} | {s['fail']} | {s['skip']} | {team_pct}% |")

    lines.append("")

    # Detailed breakdown per team
    lines.append("## Detailed Results per Team")
    lines.append("")

    for team in ALL_TEAMS:
        s = team_stats[team]
        
        # Group DoD tests for this team
        team_dods = [t for t in dod_tests if classify_test(t["name"]) == f"TestDoD_{team}"]
        
        if s["total"] == 0 and len(team_dods) == 0:
            continue
            
        lines.append(f"### {team}")
        lines.append("")
        
        if len(team_dods) > 0:
            lines.append("#### Definition of Done Checks")
            for t in team_dods:
                status_icon = {"PASSED": "✅", "FAILED": "❌", "SKIPPED": "⏭️", "ERROR": "💥"}.get(t["status"], "❓")
                test_name = t["name"].split("::")[-1].replace("test_", "").replace("_", " ").title()
                lines.append(f"  {status_icon} **{test_name}**")
            lines.append("")

        if s["total"] > 0:
            lines.append("#### Integration Contracts")
            for detail in s["details"]:
                lines.append(detail)
            lines.append("")

    # Cross-team compatibility section
    lines.append("## Cross-Team XSD Compatibility")
    lines.append("")
    lines.append("These tests verify that when Team A sends a message and Team B receives it,")
    lines.append("the XML validates against **both** teams' XSD schemas.")
    lines.append("")

    for test in tests:
        class_name = classify_test(test["name"])
        if "CrossTeam" in class_name:
            info = TEAM_MAP.get(class_name, {})
            status_icon = {"PASSED": "✅", "FAILED": "❌", "SKIPPED": "⏭️"}.get(test["status"], "❓")
            lines.append(f"- {status_icon} **{info.get('message', '?')}** — {info.get('sender', '?')}")

    lines.append("")

    # What's missing
    lines.append("## ⚠️ Not Yet Covered by These Tests")
    lines.append("")
    lines.append("The following integration points are documented in the flows but don't have")
    lines.append("XSD schemas from both sides yet, so we can't test them:")
    lines.append("")
    lines.append("- `identity_request / identity_response` — RPC (Identity Service)")
    lines.append("- `wallet_lease_request` / `wallet_lease_return` — Kassa ↔ CRM")
    lines.append("- `session_registration_confirmed` — CRM → Planning")
    lines.append("- `refund_processed` — Kassa → CRM")
    lines.append("")
    lines.append("**Teams**: Add your XSD files to your team directory and create matching")
    lines.append("fixture XML files in `integration-tests/fixtures/<team>/` to enable testing.")
    lines.append("")
    lines.append("---")
    lines.append(f"*Report generated by integration-tests/generate_report.py*")

    return "\n".join(lines)


def main():
    stdout, stderr, returncode = run_tests()
    tests, dod_tests = parse_results(stdout)

    if not tests and not dod_tests:
        # Fallback: try to extract from stderr if stdout is empty
        tests, dod_tests = parse_results(stderr)

    report = generate_report(tests, dod_tests)

    report_path = Path(__file__).parent / "readiness-report.md"
    report_path.write_text(report, encoding="utf-8")
    print(f"Report written to {report_path}")
    
    total = len(tests) + len(dod_tests)
    passed = sum(1 for t in tests if t["status"] == "PASSED") + sum(1 for t in dod_tests if t["status"] == "PASSED")
    failed = sum(1 for t in tests if t["status"] == "FAILED") + sum(1 for t in dod_tests if t["status"] == "FAILED")
    print(f"Total tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")


if __name__ == "__main__":
    main()
