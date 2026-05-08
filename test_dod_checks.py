"""
Definition of Done (DoD) Checks — Desideriushogeschool Event Platform
======================================================================

These tests perform static analysis on the codebase to verify whether teams
have completed their required Definition of Done tasks as requested by the
project management.

It checks for the presence of specific files, the removal of deprecated
libraries (like Supabase in CRM), and the inclusion of required configurations
(like Logstash mappings for the Controlroom).

Deadline: 10/05/2026 23:59
"""

import os
import pytest
from pathlib import Path
import re

REPO_ROOT = Path(__file__).resolve().parent.parent

# ═══════════════════════════════════════════════════════════════════════
# TEAM INFRA
# ═══════════════════════════════════════════════════════════════════════
class TestDoD_Infra:
    def test_kubernetes_manifests_exist(self):
        """Check if Kubernetes manifests are present in the Infra folder."""
        infra_dir = REPO_ROOT / "Infra"
        k8s_files = list(infra_dir.rglob("*.yaml")) + list(infra_dir.rglob("*.yml"))
        # Exclude docker-compose files to ensure they have actual k8s manifests
        k8s_manifests = [f for f in k8s_files if "docker-compose" not in f.name.lower()]
        assert len(k8s_manifests) > 0, "No Kubernetes manifests found in the Infra directory. Expected k8s YAML files."

    def test_security_checks_documented(self):
        """Check if the security checklist has been documented."""
        docs_dir = REPO_ROOT / "Infra" / "docs"
        security_doc = docs_dir / "security.md"
        assert security_doc.exists() or (REPO_ROOT / "docs" / "security.md").exists(), \
            "Security checklist documentation is missing. Expected 'security.md' in Infra/docs or root docs."

    def test_rollback_procedure_documented(self):
        """Check if the rollback procedure is documented."""
        docs_dir = REPO_ROOT / "Infra" / "docs"
        rollback_doc = docs_dir / "rollback.md"
        assert rollback_doc.exists() or (REPO_ROOT / "docs" / "rollback.md").exists(), \
            "Rollback procedure documentation is missing. Expected 'rollback.md' in Infra/docs or root docs."


# ═══════════════════════════════════════════════════════════════════════
# TEAM CRM
# ═══════════════════════════════════════════════════════════════════════
class TestDoD_CRM:
    def test_supabase_references_removed(self):
        """Check that Supabase is completely replaced by MySQL (no supabase references in code)."""
        crm_dir = REPO_ROOT / "CRM"
        if not crm_dir.exists():
            pytest.skip("CRM directory not found.")
            
        found_supabase = []
        for filepath in crm_dir.rglob("*"):
            if filepath.is_file() and not "node_modules" in filepath.parts and filepath.suffix in [".js", ".ts", ".json", ".env"]:
                try:
                    content = filepath.read_text(encoding="utf-8").lower()
                    if "supabase" in content:
                        found_supabase.append(filepath.relative_to(crm_dir))
                except Exception:
                    pass
        
        assert len(found_supabase) == 0, f"Found deprecated Supabase references in CRM files: {', '.join(map(str, found_supabase))}. Please use MySQL."

    def test_unit_tests_exist(self):
        """Check if unit tests covering registration, consumption, and payment exist."""
        crm_dir = REPO_ROOT / "CRM"
        test_files = list(crm_dir.rglob("*.test.*")) + list(crm_dir.rglob("*.spec.*"))
        assert len(test_files) > 0, "No unit tests found in the CRM directory. Expected .test.js/.ts or .spec.js/.ts files."


# ═══════════════════════════════════════════════════════════════════════
# TEAM FRONTEND
# ═══════════════════════════════════════════════════════════════════════
class TestDoD_Frontend:
    def test_docker_compose_exists(self):
        """Check if docker-compose.yml exists for Drupal + RabbitMQ worker services."""
        fe_dir = REPO_ROOT / "IP-groep1-frontend"
        assert (fe_dir / "docker-compose.yml").exists() or (fe_dir / "docker-compose.yaml").exists(), \
            "docker-compose.yml not found in IP-groep1-frontend. Required for local Drupal/Worker setup."

    def test_user_unregistered_sender_exists(self):
        """Check if the user_unregistered logic has been implemented."""
        fe_dir = REPO_ROOT / "IP-groep1-frontend"
        found = False
        # Drupal logic can be in .php or .module files. 
        # The event might be called 'user_unregistered' or 'user_deleted' (synonym in some contracts).
        for ext in ["*.php", "*.module"]:
            for filepath in fe_dir.rglob(ext):
                try:
                    content = filepath.read_text(encoding="utf-8").lower()
                    if "user_unregistered" in content or "user_deleted" in content:
                        found = True
                        break
                except Exception:
                    pass
            if found: break
        
        assert found, "Could not find 'user_unregistered' (or 'user_deleted') event publication in the PHP codebase."


# ═══════════════════════════════════════════════════════════════════════
# TEAM FACTURATIE
# ═══════════════════════════════════════════════════════════════════════
class TestDoD_Facturatie:
    def test_dead_letter_queue_configured(self):
        """Check if a DLQ (Dead Letter Queue) is configured in Facturatie."""
        fact_dir = REPO_ROOT / "Facturatie"
        found = False
        for filepath in fact_dir.rglob("*.py"):
            try:
                content = filepath.read_text(encoding="utf-8").lower()
                if "dead" in content and "letter" in content or "dlq" in content:
                    found = True
                    break
            except Exception:
                pass
        assert found, "Dead Letter Queue (DLQ) configuration/handling not found in the Facturatie codebase."


# ═══════════════════════════════════════════════════════════════════════
# TEAM CONTROLROOM / MONITORING
# ═══════════════════════════════════════════════════════════════════════
class TestDoD_Controlroom:
    def test_logstash_maps_frontend_and_mailing(self):
        """Check if logstash.conf contains mapping for Frontend and Mailing."""
        logstash_conf = REPO_ROOT / "monitoring" / "logstash" / "pipeline" / "logstash.conf"
        if logstash_conf.exists():
            content = logstash_conf.read_text(encoding="utf-8").lower()
            assert "frontend" in content, "Frontend not found in logstash.conf system mappings."
            assert "mailing" in content, "Mailing not found in logstash.conf system mappings."
        else:
            # Fallback search if the path is slightly different
            mon_dir = REPO_ROOT / "monitoring"
            found_logstash = False
            for filepath in mon_dir.rglob("*.conf"):
                content = filepath.read_text(encoding="utf-8").lower()
                if "frontend" in content and "mailing" in content:
                    found_logstash = True
                    break
            assert found_logstash, "Could not find logstash.conf mapping for Frontend and Mailing."

    def test_error_handling_documented(self):
        """Check if the error handling approach is documented."""
        docs_dir = REPO_ROOT / "monitoring" / "docs"
        error_doc = docs_dir / "error_handling.md"
        assert error_doc.exists() or (REPO_ROOT / "docs" / "error_handling.md").exists(), \
            "Error handling documentation is missing. Expected 'error_handling.md'."


# ═══════════════════════════════════════════════════════════════════════
# TEAM PLANNING
# ═══════════════════════════════════════════════════════════════════════
class TestDoD_Planning:
    def test_microsoft_graph_api_integrated(self):
        """Check if Microsoft Graph API logic for Outlook is implemented."""
        plan_dir = REPO_ROOT / "Planning"
        found = False
        for filepath in plan_dir.rglob("*"):
            if filepath.is_file() and filepath.suffix in [".js", ".ts", ".py", ".cs", ".java"]:
                try:
                    content = filepath.read_text(encoding="utf-8").lower()
                    if "graph.microsoft.com" in content or "microsoft-graph" in content:
                        found = True
                        break
                except Exception:
                    pass
        assert found, "Microsoft Graph API integration not found in Planning codebase (expected references to graph.microsoft.com)."


# ═══════════════════════════════════════════════════════════════════════
# GLOBAL DOD CHECKS (V2.3)
# ═══════════════════════════════════════════════════════════════════════
class TestDoD_Global:
    TEAMS = [
        "IP-groep1-frontend", 
        "CRM", 
        "Facturatie", 
        "Kassa", 
        "Planning", 
        "Mailing", 
        "monitoring", 
        "Infra"
    ]

    @pytest.mark.parametrize("team", TEAMS)
    def test_dockerfile_exists(self, team):
        """Each team must have a Dockerfile for containerization."""
        team_dir = REPO_ROOT / team
        if not team_dir.exists():
            pytest.skip(f"Team directory {team} not found.")
            
        dockerfiles = list(team_dir.glob("Dockerfile*")) + list(team_dir.glob("docker/Dockerfile*"))
        assert len(dockerfiles) > 0, f"No Dockerfile found for team {team}."

    @pytest.mark.parametrize("team", TEAMS)
    def test_ci_cd_workflow_exists(self, team):
        """Each team must have a CI/CD workflow defined."""
        team_dir = REPO_ROOT / team
        if not team_dir.exists():
            pytest.skip(f"Team directory {team} not found.")
            
        workflow_dir = team_dir / ".github" / "workflows"
        workflows = list(workflow_dir.glob("*.yml")) + list(workflow_dir.glob("*.yaml"))
        
        # Check root as well for monorepo-style workflows
        root_workflows = list((REPO_ROOT / ".github" / "workflows").glob(f"*{team}*.yml"))
        
        assert len(workflows) > 0 or len(root_workflows) > 0, f"No CI/CD workflow found for team {team}."

    @pytest.mark.parametrize("team", TEAMS)
    def test_synthese_document_exists(self, team):
        """Each team must have a synthesis document (synthese.md)."""
        team_dir = REPO_ROOT / team
        if not team_dir.exists():
            pytest.skip(f"Team directory {team} not found.")
            
        possible_names = ["synthese.md", "SYNTHESE.md", "docs/synthese.md", "README.md"]
        found = any((team_dir / name).exists() for name in possible_names)
        assert found, f"No synthesis document found for team {team}. Expected synthese.md or README.md."

    @pytest.mark.parametrize("team", TEAMS)
    def test_timesheets_exist(self, team):
        """Each team must have timesheets for its members."""
        team_dir = REPO_ROOT / team
        if not team_dir.exists():
            pytest.skip(f"Team directory {team} not found.")
            
        possible_names = ["timesheets.md", "TIMESHEETS.md", "docs/timesheets.md", "timesheets/"]
        found = any((team_dir / name).exists() for name in possible_names)
        assert found, f"No timesheets found for team {team}."
