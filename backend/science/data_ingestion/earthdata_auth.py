"""Non-secret NASA Earthdata authentication diagnostics and login helpers."""

from dataclasses import asdict, dataclass
from typing import Any

import certifi


@dataclass(frozen=True)
class AuthenticationDiagnostic:
    status: str
    client_installed: bool
    credential_strategy: str
    message: str

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def diagnose_earthdata_auth(strategy: str = "environment") -> AuthenticationDiagnostic:
    """Report client/credential state without logging credentials or tokens."""
    try:
        import earthaccess
    except ImportError:
        return AuthenticationDiagnostic(
            status="missing_client",
            client_installed=False,
            credential_strategy=strategy,
            message="earthaccess is not installed; install backend requirements before authentication.",
        )

    try:
        authenticated = earthaccess.login(strategy=strategy, persist=False)
    except Exception as error:
        error_name = type(error).__name__
        status = "credentials_unavailable" if error_name == "LoginStrategyUnavailable" else "authentication_error"
        return AuthenticationDiagnostic(
            status=status,
            client_installed=True,
            credential_strategy=strategy,
            message=f"earthaccess login failed with {error_name}; secret values are intentionally omitted.",
        )
    return AuthenticationDiagnostic(
        status="authenticated" if authenticated else "unauthenticated",
        client_installed=True,
        credential_strategy=strategy,
        message="Earthdata authentication state obtained without persisting credentials." if authenticated else "No usable Earthdata credentials were found.",
    )


def earthdata_ssl_cafile() -> str:
    """Return the CA bundle used by Terra Twin network clients."""
    return certifi.where()


def login_interactive() -> object:
    """Start earthaccess interactive login; callers must run this locally."""
    import earthaccess

    return earthaccess.login(strategy="interactive", persist=True)