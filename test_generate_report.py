from pathlib import Path

from generate_report import generate_report, parse_results


def test_generate_report_includes_failed_findings(tmp_path: Path):
    junit_xml = tmp_path / "pytest_junit.xml"
    junit_xml.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<testsuite name="pytest" tests="2" failures="1" errors="0" skipped="0">
  <testcase classname="test_dod_checks.TestDoD_Infra" name="test_security_checks_documented" time="0.01">
    <failure message="Security checklist documentation is missing.">AssertionError: Security checklist documentation is missing.</failure>
  </testcase>
  <testcase classname="test_contracts.TestR1_FrontendToCRM_NewRegistration" name="test_frontend_new_registration_validates_against_frontend_xsd" time="0.01" />
</testsuite>
""",
        encoding="utf-8",
    )

    tests, dod_tests = parse_results("", junit_xml)
    report = generate_report(tests, dod_tests)

    assert "## Findings" in report
    assert "Security checklist documentation is missing." in report
    assert "test_dod_checks.TestDoD_Infra::test_security_checks_documented" in report
    assert "Overall Progress" in report
