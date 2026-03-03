"""Supabase client management."""

from __future__ import annotations

import base64
import json
from typing import Optional, Tuple
from supabase import create_client, Client

from .types import SupabaseClientWrapper


class SupabaseClientManager:
    """Manages Supabase client instances."""

    _instances: dict[str, SupabaseClientWrapper] = {}

    @classmethod
    def get_or_create(cls, url: str, key: str) -> SupabaseClientWrapper:
        """Get existing client or create new one."""
        cache_key = f"{url}:{key[:20]}"

        if cache_key not in cls._instances:
            client = create_client(url, key)
            is_service_role = cls._is_service_role_key(key)
            cls._instances[cache_key] = SupabaseClientWrapper(
                client=client,
                url=url,
                is_service_role=is_service_role,
            )

        return cls._instances[cache_key]

    @classmethod
    def create_fresh(cls, url: str, key: str) -> SupabaseClientWrapper:
        """Create a fresh client instance (not cached)."""
        client = create_client(url, key)
        is_service_role = cls._is_service_role_key(key)
        return SupabaseClientWrapper(
            client=client,
            url=url,
            is_service_role=is_service_role,
        )

    @staticmethod
    def _is_service_role_key(key: str) -> bool:
        """Check if key is a service_role key by examining JWT payload."""
        try:
            parts = key.split(".")
            if len(parts) != 3:
                return False

            payload_b64 = parts[1]
            # Add padding if needed
            padding = '=' * (-len(payload_b64) % 4)
            payload = base64.urlsafe_b64decode((payload_b64 + padding).encode()).decode()
            data = json.loads(payload)
            return data.get("role") == "service_role"
        except Exception:
            return False

    @staticmethod
    def validate_credentials(url: str, key: str) -> Tuple[bool, Optional[str]]:
        """Validate Supabase credentials format."""
        errors = []

        # Validate URL
        if not url:
            errors.append("URL is required")
        elif not url.startswith("https://") or "supabase.co" not in url:
            errors.append("URL should be in format: https://xxx.supabase.co")

        # Validate key (JWT format)
        if not key:
            errors.append("API key is required")
        elif key.count(".") != 2:
            errors.append("API key must be a valid JWT (anon or service_role key)")

        if errors:
            return False, "; ".join(errors)
        return True, None

    @classmethod
    def clear_cache(cls) -> None:
        """Clear all cached client instances."""
        cls._instances.clear()
