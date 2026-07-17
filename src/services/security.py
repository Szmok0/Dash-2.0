"""PIN i ustawienia bezpieczeństwa (tabela settings).

PIN 4-cyfrowy przechowywany jako hash PBKDF2 z solą (bez szyfrowania aplikacyjnego
całej bazy w MVP — BUILD.md). Blokada po bezczynności konfigurowalna.
"""
from __future__ import annotations

import hashlib
import os
import sqlite3

PIN_HASH_KEY = "pin_hash"
PIN_SALT_KEY = "pin_salt"
IDLE_LOCK_KEY = "idle_lock_minutes"
DEFAULT_IDLE_MINUTES = 5
_ITERATIONS = 120_000


class SecurityService:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def _get(self, key: str) -> str | None:
        row = self._conn.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
        return row["value"] if row else None

    def _set(self, key: str, value: str) -> None:
        self._conn.execute(
            "INSERT INTO settings (key, value) VALUES (?, ?)"
            " ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (key, value),
        )
        self._conn.commit()

    # ------------------------------------------------------------------
    def has_pin(self) -> bool:
        return self._get(PIN_HASH_KEY) is not None

    @staticmethod
    def _hash(pin: str, salt: bytes) -> str:
        return hashlib.pbkdf2_hmac("sha256", pin.encode("utf-8"), salt, _ITERATIONS).hex()

    def set_pin(self, pin: str) -> None:
        if not (pin.isdigit() and len(pin) == 4):
            raise ValueError("PIN musi mieć dokładnie 4 cyfry.")
        salt = os.urandom(16)
        self._set(PIN_SALT_KEY, salt.hex())
        self._set(PIN_HASH_KEY, self._hash(pin, salt))

    def verify_pin(self, pin: str) -> bool:
        stored = self._get(PIN_HASH_KEY)
        salt_hex = self._get(PIN_SALT_KEY)
        if not stored or not salt_hex:
            return False
        return self._hash(pin, bytes.fromhex(salt_hex)) == stored

    # ------------------------------------------------------------------
    def idle_lock_minutes(self) -> int:
        value = self._get(IDLE_LOCK_KEY)
        try:
            return int(value) if value is not None else DEFAULT_IDLE_MINUTES
        except ValueError:
            return DEFAULT_IDLE_MINUTES

    def set_idle_lock_minutes(self, minutes: int) -> None:
        self._set(IDLE_LOCK_KEY, str(max(1, int(minutes))))
