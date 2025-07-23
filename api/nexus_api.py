import json
import os
import sys
from pathlib import Path

import requests

# ---------------------------------------------------------------------------
# Configuration helpers
# ---------------------------------------------------------------------------

API_ENDPOINT_TEMPLATE = (
    "https://api.nexusmods.com/v1/games/witcher3/mods/{mod_id}.json"
)
USER_AGENT = "TW3-Mod-Manager-Test/1.0"


def get_api_key(cli_arg: str | None) -> str:
    """Return the API key from CLI argument or the ``NEXUS_API_KEY`` env var."""
    api_key = cli_arg or os.environ.get("NEXUS_API_KEY")
    if not api_key:
        sys.exit(
            "[ERROR] Provide an API key either as the second argument or via the NEXUS_API_KEY environment variable."
        )
    return api_key.strip()


# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------

def fetch_mod_json(mod_id: str, api_key: str) -> dict:
    """Fetch raw JSON for a single mod ID. Raises ``requests.HTTPError`` on failure."""
    url = API_ENDPOINT_TEMPLATE.format(mod_id=mod_id)
    headers = {
        "apikey": api_key,
        "User-Agent": USER_AGENT,
        "Application-Name": "TW3-Mod-Manager-Test",
        "Application-Version": "1.0",
    }

    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    return response.json()


# ---------------------------------------------------------------------------
# CLI entry‑point
# ---------------------------------------------------------------------------

def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python fetch_nexus_mod.py <mod_id> [api_key]")
        sys.exit(1)

    mod_id = sys.argv[1]
    api_key = get_api_key(sys.argv[2] if len(sys.argv) > 2 else None)

    try:
        data = fetch_mod_json(mod_id, api_key)
    except requests.HTTPError as exc:
        sys.exit(f"[ERROR] Nexus API returned {exc.response.status_code}: {exc.response.text}\n")
    except requests.RequestException as exc:
        sys.exit(f"[ERROR] Network error: {exc}\n")

    # Pretty‑print the result
    json.dump(data, sys.stdout, indent=2, ensure_ascii=False)
    print()  # final newline


if __name__ == "__main__":
    main()
