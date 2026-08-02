from pathlib import Path

from src.api.production_server import (
    API_TOKEN_ENVIRONMENT_VARIABLE,
    MINIMUM_API_TOKEN_LENGTH,
)


PROJECT_ROOT = (
    Path(__file__).resolve().parents[2]
)
DEPLOY_DIRECTORY = PROJECT_ROOT / "deploy"


def test_systemd_service_keeps_waitress_private(
) -> None:
    service = (
        DEPLOY_DIRECTORY
        / "ai-research-lab.service"
    ).read_text(
        encoding="utf-8"
    )
    lines = set(service.splitlines())

    assert (
        "User=ai-research-lab"
        in lines
    )
    assert (
        "Group=ai-research-lab"
        in lines
    )
    assert (
        "EnvironmentFile=/etc/ai-research-lab/"
        "ai-research-lab.env"
        in lines
    )
    assert "--host 127.0.0.1" in service
    assert "--port 8080" in service
    assert "0.0.0.0" not in service
    assert "::" not in service
    assert (
        "AI_RESEARCH_LAB_API_TOKEN="
        not in service
    )

    expected_hardening = {
        "NoNewPrivileges=true",
        "PrivateTmp=true",
        "PrivateDevices=true",
        "ProtectSystem=strict",
        "ProtectHome=true",
        (
            "ReadWritePaths="
            "/var/lib/ai-research-lab"
        ),
        "ProtectKernelTunables=true",
        "ProtectKernelModules=true",
        "ProtectControlGroups=true",
        "LockPersonality=true",
        "RestrictSUIDSGID=true",
        (
            "RestrictAddressFamilies="
            "AF_UNIX AF_INET AF_INET6"
        ),
        "UMask=0077",
    }

    assert expected_hardening <= lines


def test_caddy_terminates_tls_before_loopback_backend(
) -> None:
    caddyfile = (
        DEPLOY_DIRECTORY
        / "Caddyfile.example"
    ).read_text(
        encoding="utf-8"
    )

    assert (
        "research.example.com {"
        in caddyfile
    )
    assert (
        "reverse_proxy 127.0.0.1:8080"
        in caddyfile
    )
    assert "health_uri /health" in caddyfile
    assert (
        "Strict-Transport-Security"
        in caddyfile
    )
    assert "0.0.0.0" not in caddyfile
    assert (
        "tls_insecure_skip_verify"
        not in caddyfile
    )
    assert (
        "http://research.example.com"
        not in caddyfile
    )


def test_operations_runbook_covers_private_vps_lifecycle(
) -> None:
    runbook = (
        PROJECT_ROOT / "OPERATIONS.md"
    ).read_text(
        encoding="utf-8"
    )
    readme = (
        PROJECT_ROOT / "README.md"
    ).read_text(
        encoding="utf-8"
    )

    required_sections = {
        "## Deployment topology",
        "## API token",
        "## Caddy and TLS",
        "## Health and readiness",
        "## Logs",
        "## Online backup",
        "## Restore",
        "## Controlled application update",
        "## Token rotation",
        "## Explicitly deferred scope",
    }

    for section in required_sections:
        assert runbook.count(section) == 1

    assert (
        "src.storage.sqlite_backup_cli"
        in runbook
    )
    assert "sudo systemctl stop" in runbook
    assert "caddy validate" in runbook
    assert "0.0.0.0" not in runbook
    assert runbook.count("```") % 2 == 0
    assert (
        "[OPERATIONS.md](OPERATIONS.md)"
        in readme
    )
    assert (
        "AI_RESEARCH_LAB_API_TOKEN"
        in readme
    )
    assert (
        "src.storage.sqlite_backup_cli"
        in readme
    )


def test_environment_example_fails_closed(
) -> None:
    environment_file = (
        DEPLOY_DIRECTORY
        / "ai-research-lab.env.example"
    ).read_text(
        encoding="utf-8"
    ).strip()

    variable_name, separator, value = (
        environment_file.partition("=")
    )

    assert separator == "="
    assert variable_name == (
        API_TOKEN_ENVIRONMENT_VARIABLE
    )
    assert value == "CHANGE_ME"
    assert len(value) < MINIMUM_API_TOKEN_LENGTH
