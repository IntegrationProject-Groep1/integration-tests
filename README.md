# Integration Readiness Tests

> **Deadline**: 10/05/2026 23:59  
> **Generale repetitie**: 13/05/2026 10:00 Aula 6

## What is this?

This directory contains **non-blocking CI tests** that verify whether the XML messages produced by one team can be validated against the XSD schemas defined by the receiving team.

It also includes **source-level contract checks** for the Identity Service so we can verify the real XML payloads that the repository creates, not just the example files.

- ✅ **Non-blocking**: These tests **never prevent merges**. You can always merge your code.
- 📊 **Informational**: Check the GitHub Actions summary to see what's working and what's not.
- 🔄 **Automatic**: Runs on every push and every PR.

## How it works

```
┌─────────────┐   XML fixture    ┌─────────────┐
│  Team A     │ ──────────────►  │  Team B     │
│  (sender)   │   validates?     │  (receiver) │
│  fixtures/  │                  │  xsd/       │
└─────────────┘                  └─────────────┘
```

1. Each team has **XSD schemas** in their own directory (e.g., `Planning/xsd/`, `Kassa/integratie/schemas/`)
2. We create **fixture XML files** in `fixtures/<team>/` that simulate what each team would send
3. The tests validate these fixtures against the **receiving team's XSD**
4. If both XSD schemas agree, the cross-team test passes

## Directory Structure

```
integration-tests/
├── conftest.py                    # Shared utilities (XSD loading, validation)
├── test_contracts.py              # Main integration contract tests
├── test_identity_service_contracts.py # Identity Service source/XML contract checks
├── generate_report.py             # Generates the Markdown readiness report
├── README.md                     # This file
└── fixtures/
    ├── frontend/            # XML messages produced by Frontend
    │   ├── new_registration.xml
    │   ├── session_create_request.xml
    │   ├── session_view_request.xml
    │   ├── session_delete_request.xml
    │   └── calendar_invite.xml
    ├── crm/                 # XML messages produced/forwarded by CRM
    │   ├── new_registration_to_kassa.xml
    │   ├── payment_registered_to_facturatie.xml
    │   ├── consumption_order_to_facturatie.xml
    │   ├── invoice_request.xml
    │   └── invoice_cancelled.xml
    ├── kassa/               # XML messages produced by Kassa
    │   ├── payment_registered.xml
    │   └── consumption_order.xml
    ├── planning/            # XML messages produced by Planning
    │   ├── session_created.xml
    │   ├── session_updated.xml
    │   ├── session_deleted.xml
    │   ├── session_view_response.xml
    │   └── calendar_invite_confirmed.xml
    ├── facturatie/           # XML messages produced by Facturatie
    │   ├── invoice_status.xml
    │   └── send_mailing.xml
    └── heartbeat/           # Heartbeat sidecar messages
        └── heartbeat.xml
```

## Running Locally

```bash
# Install dependencies
pip install lxml pytest
pip install -r ../identity-service/requirements.txt

# Run the tests
cd integration-tests
python -m pytest -v

# Generate the readiness report
python generate_report.py
```

## Understanding the Readiness Report

Every push runs the tests and generates a **readiness report** showing which integrations are working and which still need work.

### Overall Status
- **Passed**: ✅ Integration test passed — both teams' XSDs agree
- **Failed**: ❌ Integration test failed — message doesn't validate or XSD issue
- **Skipped**: ⏭️ XSD file not found — team hasn't created that schema yet

### Per-Team Status Table

Each team gets a status badge based on their integration contracts:

| Status | Meaning | Action |
|--------|---------|--------|
| 🟢 **Ready** | All tests passing, 100% | No action needed, keep it up! |
| 🟡 **Partial** | Most tests passing, <100% | Some XSDs missing or 1-2 failures — team needs to create XSDs |
| 🔴 **Needs work** | Failures or many skipped | Team needs to fix failing tests or create XSD files |

**Progress column**: Shows percentage of tests that passed or were skipped (not counting failures).

### What Each Team Needs to Do

**Teams marked 🔴 Needs work:**
- Check the "Detailed Results per Team" section
- For **skipped** tests: Create the missing XSD file in your team directory
- For **failed** tests: Fix the XSD or the XML fixture to match your receiver

**Teams marked 🟡 Partial:**
- Review which tests are skipped (missing XSDs)
- Work with sender/receiver teams to align schemas
- Each team that owns an XSD must maintain it

**Teams marked 🟢 Ready:**
- Keep your XSDs maintained and updated
- If other teams change their message format, you may need to update your XSD

### Definition of Done (DoD) Checks

The report also includes DoD checks for each team (like "Docker Compose exists", "DLQ configured", etc.). These verify project readiness beyond just XSD validation.

### Service Communication Matrix

The report now includes a sender→receiver matrix based on contract test outcomes:

- **✅ Can communicate**: one or more passing tests and no failures
- **🟡 Partial**: at least one pass and at least one failure
- **❌ Blocked**: failures and no successful communication proof
- **⏭️ Waiting**: only skipped/missing-schema tests

### Functional Progress

Functional status is grouped by requirement area (registration/profile, planning, kassa/consumption, facturatie, monitoring/error handling, mailing) so you can quickly see where functionality is already proven by tests and where it still fails or is missing.

### Team Progress Snapshot

A per-repository progress table is included in every run with:

- checkout availability (repo reachable)
- latest commit recency (activity signal)
- CI workflow count
- test file count
- XSD file count
- container readiness signal (Dockerfile/docker-compose presence)

This now also includes the shared `xml-xsd-contract` repository.

## How to Add Tests for Your Team

### If you're a **sender** (your team produces XML):

1. Create a fixture XML in `fixtures/<your-team>/` that matches your message format
2. Add a test in `test_contracts.py` that validates it against both:
   - Your own XSD (proves you produce valid XML)
   - The receiver's XSD (proves the integration works)

### If you're a **receiver** (your team consumes XML):

1. Make sure your XSD is in your team's directory
2. Check the CI report to see if the sender's fixture validates against your XSD
3. If it fails, **coordinate with the sender** to align the schemas

### If you want to add a new integration point:

1. Add the XSD to your team directory
2. Create a fixture XML in `fixtures/<sender-team>/`
3. Add a test class in `test_contracts.py` following the existing pattern, or add a dedicated source-contract test file when the repo itself must be executed
4. If the repository needs source-level verification, add a dedicated test file that imports the repo code
5. Add the class to `TEAM_MAP` in `generate_report.py`

## Viewing Results

- **GitHub Actions**: Check the "Integration Readiness" workflow in the Actions tab
- **PR Comments**: The readiness report is posted as a step summary on every run
- **Artifacts**: Download the `integration-readiness-report` artifact for the full report
