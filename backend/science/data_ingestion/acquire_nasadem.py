"""Secure NASADEM acquisition entry point; never logs Earthdata secrets."""

import argparse
import json
from pathlib import Path

from .cmr import write_cmr_manifest
from .earthdata_auth import diagnose_earthdata_auth, login_interactive


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strategy", choices=("environment", "netrc", "interactive"), default="environment")
    parser.add_argument("--login", action="store_true", help="Start local Earthdata interactive login")
    parser.add_argument("--manifest", type=Path, default=Path("data/metadata/earth_nasadem_cmr.json"))
    parser.add_argument("--diagnostic", type=Path, default=Path("data/metadata/earthdata_authentication_diagnostic.json"))
    args = parser.parse_args()

    if args.login:
        login_interactive()
    diagnostic = diagnose_earthdata_auth(args.strategy)
    args.diagnostic.parent.mkdir(parents=True, exist_ok=True)
    args.diagnostic.write_text(json.dumps(diagnostic.as_dict(), indent=2) + "\n", encoding="utf-8")
    manifest = write_cmr_manifest(args.manifest)
    print(json.dumps({"authentication": diagnostic.as_dict(), "granule_count": len(manifest["granules"]), "manifest": str(args.manifest), "diagnostic": str(args.diagnostic)}, indent=2))
    if diagnostic.status != "authenticated":
        raise SystemExit(2)


if __name__ == "__main__":
    main()