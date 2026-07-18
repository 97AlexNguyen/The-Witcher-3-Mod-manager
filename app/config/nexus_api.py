from __future__ import annotations

import requests

from app.config.validation import CheckLevel, CheckResult

# Nexus Mods validates a personal API key via this endpoint. A 200 returns the
# account JSON; a 401 means the key is wrong. Docs: https://app.swaggerhub.com/apis-docs/NexusMods/nexus-mods_public_api_params_in_form_data/1.0
VALIDATE_URL = "https://api.nexusmods.com/v1/users/validate.json"

# Nexus asks callers to identify themselves. Purely courtesy headers today; they
# also make our traffic legible in their logs when debugging rate limits later.
_APP_HEADERS = {
    "Application-Name": "The Witcher 3 Mod Manager",
    "Application-Version": "0.1.0",
}

DEFAULT_TIMEOUT = 10.0


def check_nexus_api_key(key: str | None, *, timeout: float = DEFAULT_TIMEOUT) -> CheckResult:
    """Validate a Nexus API key by calling the users/validate endpoint.

    Pure and synchronous (no Qt) so it is trivially testable — callers on the UI
    thread must run it off-thread, since it makes a blocking HTTP request.
    """
    cleaned = (key or "").strip()
    if not cleaned:
        return CheckResult(CheckLevel.UNKNOWN, "Enter an API key to check.")

    try:
        response = requests.get(
            VALIDATE_URL,
            headers={"apikey": cleaned, "Accept": "application/json", **_APP_HEADERS},
            timeout=timeout,
        )
    except requests.Timeout:
        return CheckResult(CheckLevel.ERROR, "Nexus did not respond in time — try again.")
    except requests.RequestException:
        return CheckResult(CheckLevel.ERROR, "Could not reach Nexus — check your connection.")

    if response.status_code == 401:
        return CheckResult(CheckLevel.ERROR, "Invalid API key — Nexus rejected it.")
    if response.status_code == 429:
        return CheckResult(CheckLevel.WARNING, "Rate limited by Nexus — try again shortly.")
    if response.status_code != 200:
        return CheckResult(CheckLevel.ERROR, f"Nexus returned HTTP {response.status_code}.")

    try:
        data = response.json()
    except ValueError:
        return CheckResult(CheckLevel.WARNING, "Unexpected response from Nexus.")

    name = (data.get("name") or "").strip() or "your account"
    suffix = " · Premium" if data.get("is_premium") else ""
    return CheckResult(CheckLevel.OK, f"Valid — signed in as {name}{suffix}.")
