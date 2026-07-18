from __future__ import annotations

import keyring
from keyring.errors import KeyringError

# The Nexus API key is a secret, so it is kept out of config.json and stored in
# the OS credential store (Windows Credential Manager via keyring's WinVault
# backend). config.json — which users may back up or sync — never sees it.

SERVICE_NAME = "The Witcher 3 Mod Manager"
NEXUS_API_KEY_USERNAME = "nexus-api-key"


def get_nexus_api_key() -> str | None:
    """Return the stored Nexus API key, or None if unset or the store is unavailable."""
    try:
        value = keyring.get_password(SERVICE_NAME, NEXUS_API_KEY_USERNAME)
    except KeyringError:
        return None
    value = (value or "").strip()
    return value or None


def set_nexus_api_key(value: str | None) -> None:
    """Store the Nexus API key, or clear it when given empty/None."""
    cleaned = (value or "").strip()
    if not cleaned:
        clear_nexus_api_key()
        return
    keyring.set_password(SERVICE_NAME, NEXUS_API_KEY_USERNAME, cleaned)


def clear_nexus_api_key() -> None:
    """Remove the stored key. A missing entry is not an error."""
    try:
        keyring.delete_password(SERVICE_NAME, NEXUS_API_KEY_USERNAME)
    except KeyringError:
        pass
