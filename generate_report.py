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
import os
from pathlib import Path
from datetime import datetime, timezone
import xml.etree.ElementTree as ET


def run_tests():
    """Run pytest with JSON output and capture results."""
    junit_path = Path(__file__).parent / "pytest_junit.xml"
    reuse_existing = os.getenv("READINESS_USE_EXISTING_JUNIT", "0") == "1"

    # Reuse an existing JUnit XML only when explicitly requested via env var.
    # This prevents stale committed artifacts from masking current test results.
    if reuse_existing and junit_path.exists():
        # Provide empty stdout/stderr but return the existing path
        return "", "", 0, junit_path

    # Remove any stale file just in case
    try:
        if junit_path.exists():
            junit_path.unlink()
    except Exception:
        pass

    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "-v",
        "--tb=line",
        "--no-header",
        "--junitxml",
        str(junit_path),
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, cwd=Path(__file__).parent)
    return result.stdout, result.stderr, result.returncode, junit_path


def parse_results(stdout: str, junit_path: Path = None):
    """Parse pytest results. Prefer JUnit XML if available, fallback to stdout parsing."""
    tests = []
    dod_tests = []

    def build_failure_details(element):
        message = (element.get("message") or "").strip()
        text = (element.text or "").strip()
        if message and text:
            return f"{message} — {text.splitlines()[0].strip()}"
        return message or text

    # If junit xml exists, parse it for reliable results
    if junit_path and junit_path.exists():
        try:
            tree = ET.parse(str(junit_path))
            root = tree.getroot()
            # pytest junitxml uses <testcase> elements
            for tc in root.findall('.//testcase'):
                classname = tc.get('classname') or ''
                name = tc.get('name') or ''
                # Normalize to pytest-like identifier
                identifier = f"{classname}::{name}" if classname else name

                status = 'PASSED'
                details = ""
                failure_element = tc.find('failure')
                error_element = tc.find('error')
                if failure_element is not None or error_element is not None:
                    status = 'FAILED'
                    failure_element = failure_element if failure_element is not None else error_element
                    details = build_failure_details(failure_element) if failure_element is not None else ""
                elif tc.find('skipped') is not None:
                    status = 'SKIPPED'

                if 'test_dod_checks' in (classname or '') or identifier.startswith('TestDoD_'):
                    dod_tests.append({'name': identifier, 'status': status, 'details': details})
                else:
                    tests.append({'name': identifier, 'status': status, 'details': details})

            return tests, dod_tests
        except Exception:
            # fallback to stdout parsing below
            pass

    # Fallback: parse verbose stdout
    for line in stdout.splitlines():
        match = re.search(r"(test_[^:]+\.py)::(\S+)\s+(PASSED|FAILED|ERROR|SKIPPED)", line)
        if match:
            file_type = match.group(1)
            full_name = match.group(2)
            status = match.group(3)
            if file_type == "test_dod_checks.py":
                dod_tests.append({"name": full_name, "status": status, "details": ""})
            else:
                tests.append({"name": full_name, "status": status, "details": ""})
    return tests, dod_tests


def format_finding(test):
    """Format a failing test as a concise finding line."""
    details = test.get("details", "").strip()
    if details:
        return f"- ❌ `{test['name']}` — {details}"
    return f"- ❌ `{test['name']}`"


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
    "TestIdentityServiceContract": {
        "sender": "Identity Service",
        "receiver": "Identity Service",
        "flow": "I·1 Identity service contract",
        "message": "identity_service_contract",
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
    "TestK3_KassaToCRM_RefundProcessed": {
        "sender": "Kassa",
        "receiver": "CRM",
        "flow": "K·3 Refund verwerkt",
        "message": "refund_processed",
    },
    "TestK4_KassaToCRM_WalletLeaseRequest": {
        "sender": "Kassa",
        "receiver": "CRM",
        "flow": "K·4 QR-scan inkom (request)",
        "message": "wallet_lease_request",
    },
    "TestK6_KassaToCRM_WalletLeaseReturn": {
        "sender": "Kassa",
        "receiver": "CRM",
        "flow": "K·6 Badges inleveren",
        "message": "wallet_lease_return",
    },
    "TestN1_CRMToPlanning_SessionRegistrationConfirmed": {
        "sender": "CRM",
        "receiver": "Planning",
        "flow": "N·1 Inschrijving bevestigen",
        "message": "session_registration_confirmed",
    },
}

# All teams (matches directory names)
ALL_TEAMS = [
    "IP-groep1-frontend", 
    "CRM", 
    "Kassa", 
    "Facturatie", 
    "Planning", 
    "Mailing", 
    "monitoring", 
    "Infra",
    "Sidecar",
    "Identity Service"
]

# Display names for the report
TEAM_DISPLAY_NAMES = {
    "IP-groep1-frontend": "Frontend",
    "monitoring": "Monitoring",
    "CRM": "CRM",
    "Kassa": "Kassa",
    "Facturatie": "Facturatie",
    "Planning": "Planning",
    "Mailing": "Mailing",
    "Infra": "Infra",
    "Sidecar": "Sidecar",
    "Identity Service": "Identity Service"
}

TEAM_REPOS = [
    {"team": "Frontend", "repo_dir": "IP-groep1-frontend", "repo_name": "IP-groep1-frontend"},
    {"team": "CRM", "repo_dir": "CRM", "repo_name": "CRM"},
    {"team": "Kassa", "repo_dir": "Kassa", "repo_name": "Kassa"},
    {"team": "Facturatie", "repo_dir": "Facturatie", "repo_name": "Facturatie"},
    {"team": "Planning", "repo_dir": "Planning", "repo_name": "Planning"},
    {"team": "Mailing", "repo_dir": "Mailing", "repo_name": "Mailing"},
    {"team": "Monitoring", "repo_dir": "monitoring", "repo_name": "monitoring"},
    {"team": "Infra", "repo_dir": "Infra", "repo_name": "Infra"},
    {"team": "Heartbeat", "repo_dir": "heartbeat", "repo_name": "heartbeat"},
    {"team": "Identity Service", "repo_dir": "identity-service", "repo_name": "identity-service"},
    {"team": "Contract (shared)", "repo_dir": "xml-xsd-contract", "repo_name": "xml-xsd-contract"},
]

FUNCTIONAL_REQUIREMENTS = [
    {"name": "Registratie & profiel", "flow_prefixes": ["R·", "N·", "B·"]},
    {"name": "Planning (sessies)", "flow_prefixes": ["S·"]},
    {"name": "Kassa & consumpties", "flow_prefixes": ["K·"]},
    {"name": "Facturatie", "flow_prefixes": ["F·"]},
    {"name": "Monitoring & foutafhandeling", "flow_prefixes": ["O·", "E·"]},
    {"name": "Mailing", "flow_prefixes": ["M·"]},
]


def _collect_repo_signal(repo_root: Path, team_repo: dict) -> dict:
    repo_dir = repo_root / team_repo["repo_dir"]
    exists = repo_dir.exists() and repo_dir.is_dir()
    data = {
        "team": team_repo["team"],
        "repo_name": team_repo["repo_name"],
        "checkout": "✅" if exists else "❌",
        "last_commit": "—",
        "activity": "Missing",
        "workflows": 0,
        "tests": 0,
        "xsds": 0,
        "docker": "—",
    }

    if not exists:
        return data

    workflow_dir = repo_dir / ".github" / "workflows"
    data["workflows"] = len(list(workflow_dir.glob("*.yml"))) + len(list(workflow_dir.glob("*.yaml")))
    data["tests"] = len(list(repo_dir.rglob("test_*.py"))) + len(list(repo_dir.rglob("*.test.*"))) + len(list(repo_dir.rglob("*.spec.*")))
    data["xsds"] = len(list(repo_dir.rglob("*.xsd")))

    has_docker = len(list(repo_dir.glob("Dockerfile*"))) > 0 or len(list(repo_dir.rglob("docker-compose*.yml"))) > 0 or len(list(repo_dir.rglob("docker-compose*.yaml"))) > 0
    data["docker"] = "✅" if has_docker else "⚠️"

    git_dir = repo_dir / ".git"
    if not git_dir.exists():
        data["activity"] = "No git metadata"
        return data

    try:
        result = subprocess.run(
            ["git", "-C", str(repo_dir), "log", "-1", "--format=%cI"],
            capture_output=True,
            text=True,
            check=False,
            timeout=10,
        )
        commit_iso = (result.stdout or "").strip()
        if commit_iso:
            dt = datetime.fromisoformat(commit_iso.replace("Z", "+00:00"))
            days_ago = (datetime.now(timezone.utc) - dt.astimezone(timezone.utc)).days
            data["last_commit"] = dt.astimezone(timezone.utc).strftime("%Y-%m-%d")
            if days_ago <= 2:
                data["activity"] = "Active"
            elif days_ago <= 7:
                data["activity"] = "Recent"
            else:
                data["activity"] = "Stale"
        else:
            data["activity"] = "Unknown"
    except Exception:
        data["activity"] = "Unknown"

    return data


def _build_communication_matrix(tests):
    matrix = {}
    for test in tests:
        class_name = classify_test(test["name"])
        info = TEAM_MAP.get(class_name)
        if not info:
            continue

        sender = info.get("sender", "")
        receiver = info.get("receiver", "")
        if not sender or not receiver:
            continue
        if sender == receiver or "↔" in sender or sender == "Alle teams" or receiver in {"Architectuur", "Cross-team"}:
            continue

        key = (sender, receiver)
        if key not in matrix:
            matrix[key] = {"pass": 0, "fail": 0, "skip": 0}
        if test["status"] == "PASSED":
            matrix[key]["pass"] += 1
        elif test["status"] in {"FAILED", "ERROR"}:
            matrix[key]["fail"] += 1
        else:
            matrix[key]["skip"] += 1
    return matrix


def _build_functionality_progress(tests):
    req_stats = {req["name"]: {"pass": 0, "fail": 0, "skip": 0} for req in FUNCTIONAL_REQUIREMENTS}
    for test in tests:
        class_name = classify_test(test["name"])
        info = TEAM_MAP.get(class_name)
        if not info:
            continue
        flow = info.get("flow", "")
        for req in FUNCTIONAL_REQUIREMENTS:
            if any(flow.startswith(prefix) for prefix in req["flow_prefixes"]):
                if test["status"] == "PASSED":
                    req_stats[req["name"]]["pass"] += 1
                elif test["status"] in {"FAILED", "ERROR"}:
                    req_stats[req["name"]]["fail"] += 1
                else:
                    req_stats[req["name"]]["skip"] += 1
                break
    return req_stats


def classify_test(test_name: str):
    """Extract class name from pytest test identifier.
    
    Converts pytest JUnit identifiers like:
      'test_contracts.TestR1_FrontendToCRM_NewRegistration::test_method'
    To:
      'TestR1_FrontendToCRM_NewRegistration'
      
    Also handles parametrized global tests like:
      'test_dod_checks.TestDoD_Global::test_dockerfile_exists[CRM]'
    To:
      'TestDoD_CRM'
    """
    # Handle parametrization [TeamName]
    match = re.search(r"\[([^\]]+)\]", test_name)
    if match:
        team_param = match.group(1)
        # We only want to remap TestDoD_Global to TestDoD_TeamName
        if "TestDoD_Global" in test_name:
            return f"TestDoD_{team_param}"

    parts = test_name.split("::")
    classname_with_module = parts[0] if len(parts) >= 1 else test_name
    # Remove module prefix (everything before the last dot)
    if "." in classname_with_module:
        result = classname_with_module.split(".")[-1]
        return result
    return classname_with_module


def generate_report(tests, dod_tests):
    """Generate the markdown report."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    deadline = "2026-05-10 23:59 CET"

    total = len(tests) + len(dod_tests)
    passed = sum(1 for t in tests if t["status"] == "PASSED") + sum(1 for t in dod_tests if t["status"] == "PASSED")
    failed = sum(1 for t in tests if t["status"] == "FAILED") + sum(1 for t in dod_tests if t["status"] == "FAILED")
    skipped = sum(1 for t in tests if t["status"] == "SKIPPED") + sum(1 for t in dod_tests if t["status"] == "SKIPPED")
    
    # Debug: Show test classification
    import sys
    print(f"DEBUG: Total tests={total}, passed={passed}, failed={failed}, skipped={skipped}", file=sys.stderr)
    print(f"DEBUG: Contract tests count={len(tests)}, DoD tests count={len(dod_tests)}", file=sys.stderr)
    if tests:
        sample_test = tests[0]
        class_name = classify_test(sample_test['name'])
        print(f"DEBUG: Sample test name='{sample_test['name']}' → classified='{class_name}' → in TEAM_MAP={class_name in TEAM_MAP}", file=sys.stderr)

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

    # High-signal summary of actual failures
    failing_findings = [t for t in tests + dod_tests if t["status"] in {"FAILED", "ERROR"}]
    if failing_findings:
        lines.append("## Findings")
        lines.append("")
        lines.append("The following checks failed in the most recent run:")
        lines.append("")
        for test in failing_findings:
            lines.append(format_finding(test))
        lines.append("")

    # Collect per-team stats
    team_stats = {}
    for team in ALL_TEAMS:
        team_stats[team] = {"pass": 0, "fail": 0, "skip": 0, "total": 0, "details": []}

    unmatched_tests = []
    for test in tests:
        class_name = classify_test(test["name"])
        info = TEAM_MAP.get(class_name, None)
        if not info:
            unmatched_tests.append(class_name)
            continue

        status_icon = {"PASSED": "✅", "FAILED": "❌", "SKIPPED": "⏭️", "ERROR": "💥"}.get(test["status"], "❓")
        matched_teams = set()

        for team_key in ["sender", "receiver"]:
            team_name = info[team_key]
            # Handle cross-team names
            for team in ALL_TEAMS:
                display = TEAM_DISPLAY_NAMES.get(team, team)
                if display in team_name and team not in matched_teams:
                    matched_teams.add(team)
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
    
    # Debug: Show unmatched tests
    if unmatched_tests:
        import sys
        print(f"DEBUG: Unmatched test classes (not in TEAM_MAP): {unmatched_tests[:5]}", file=sys.stderr)
    for team, s in team_stats.items():
        if s["total"] == 0:
            import sys
            print(f"DEBUG: Team '{team}' has 0 tests in team_stats", file=sys.stderr)
            break

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

    communication_matrix = _build_communication_matrix(tests)
    lines.append("## Service Communication Matrix")
    lines.append("")
    lines.append("| Sender | Receiver | Pass | Fail | Skip | Status |")
    lines.append("|--------|----------|------|------|------|--------|")
    if communication_matrix:
        for (sender, receiver), stats in sorted(communication_matrix.items()):
            if stats["pass"] > 0 and stats["fail"] == 0:
                status = "✅ Can communicate"
            elif stats["pass"] > 0 and stats["fail"] > 0:
                status = "🟡 Partial"
            elif stats["fail"] > 0:
                status = "❌ Blocked"
            else:
                status = "⏭️ Waiting"
            lines.append(f"| {sender} | {receiver} | {stats['pass']} | {stats['fail']} | {stats['skip']} | {status} |")
    else:
        lines.append("| — | — | 0 | 0 | 0 | No integration test data |")
    lines.append("")

    functionality_progress = _build_functionality_progress(tests)
    lines.append("## Functional Progress")
    lines.append("")
    lines.append("| Requirement area | Pass | Fail | Skip | Status |")
    lines.append("|------------------|------|------|------|--------|")
    for req_name, stats in functionality_progress.items():
        total_req = stats["pass"] + stats["fail"] + stats["skip"]
        if total_req == 0:
            status = "⚪ Not covered"
        elif stats["fail"] == 0 and stats["pass"] > 0:
            status = "🟢 Good"
        elif stats["pass"] > 0:
            status = "🟡 In progress"
        else:
            status = "🔴 Needs attention"
        lines.append(f"| {req_name} | {stats['pass']} | {stats['fail']} | {stats['skip']} | {status} |")
    lines.append("")

    repo_root = Path(os.getenv("INTEGRATION_REPO_ROOT", Path(__file__).resolve().parent.parent))
    lines.append("## Team Progress Snapshot")
    lines.append("")
    lines.append("| Team | Repository | Checkout | Last commit (UTC) | Activity | CI workflows | Tests | XSD files | Container readiness |")
    lines.append("|------|------------|----------|-------------------|----------|--------------|-------|-----------|---------------------|")
    for team_repo in TEAM_REPOS:
        signal = _collect_repo_signal(repo_root, team_repo)
        lines.append(
            f"| {signal['team']} | {signal['repo_name']} | {signal['checkout']} | {signal['last_commit']} | {signal['activity']} | "
            f"{signal['workflows']} | {signal['tests']} | {signal['xsds']} | {signal['docker']} |"
        )
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
            
        display_name = TEAM_DISPLAY_NAMES.get(team, team)
        lines.append(f"### {display_name}")
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
    lines.append("The following integration points are documented in the flows but are still in development")
    lines.append("or missing specific XSD schemas:")
    lines.append("")
    lines.append("- `user_checkin` — Kassa → CRM")
    lines.append("- `wallet_topup_request` — Frontend → CRM")
    lines.append("- `invoice_created_notification` — Facturatie → CRM")
    lines.append("- `mailing_status` — Mailing → CRM")
    lines.append("")
    lines.append("**Teams**: Add your XSD files to your team directory and create matching")
    lines.append("fixture XML files in `integration-tests/fixtures/<team>/` to enable testing.")
    lines.append("")
    lines.append("---")
    lines.append(f"*Report generated by integration-tests/generate_report.py*")

    return "\n".join(lines)


def main():
    stdout, stderr, returncode, junit_path = run_tests()
    tests, dod_tests = parse_results(stdout, junit_path)

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
