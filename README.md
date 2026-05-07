# Integration Readiness Tests

> **Deadline**: 10/05/2026 23:59  
> **Generale repetitie**: 13/05/2026 10:00 Aula 6

## What is this?

This directory contains **non-blocking CI tests** that verify whether the XML messages produced by one team can be validated against the XSD schemas defined by the receiving team.

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
├── conftest.py              # Shared utilities (XSD loading, validation)
├── test_contracts.py        # All integration contract tests
├── generate_report.py       # Generates the Markdown readiness report
├── README.md                # This file
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

# Run the tests
cd integration-tests
python -m pytest test_contracts.py -v

# Generate the readiness report
python generate_report.py
```

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
3. Add a test class in `test_contracts.py` following the existing pattern
4. Add the class to `TEAM_MAP` in `generate_report.py`

## Viewing Results

- **GitHub Actions**: Check the "Integration Readiness" workflow in the Actions tab
- **PR Comments**: The readiness report is posted as a step summary on every run
- **Artifacts**: Download the `integration-readiness-report` artifact for the full report
