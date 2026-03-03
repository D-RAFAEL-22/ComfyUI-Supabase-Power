"""Custom type definitions for Supabase Power nodes."""

from typing import Any, Dict, List, TypedDict, Optional
from dataclasses import dataclass, field


# Custom type names for ComfyUI type system
CUSTOM_TYPES = [
    "SUPABASE_CLIENT",
    "FILTER_CHAIN",
    "ORDER_CONFIG",
    "PAGINATION_CONFIG",
    "REALTIME_CHANNEL",
]


@dataclass
class SupabaseClientWrapper:
    """Wrapper for Supabase client with metadata."""
    client: Any
    url: str
    is_service_role: bool = False

    def __repr__(self) -> str:
        role = "service_role" if self.is_service_role else "anon"
        return f"<SupabaseClient url={self.url} role={role}>"


class FilterItem(TypedDict):
    """Single filter condition."""
    column: str
    op: str
    value: Any


FilterChain = List[FilterItem]


@dataclass
class OrderConfig:
    """Ordering configuration."""
    orders: List[Dict[str, Any]] = field(default_factory=list)

    def add(self, column: str, ascending: bool = True, nulls_first: bool = False) -> "OrderConfig":
        """Add ordering clause."""
        self.orders.append({
            "column": column,
            "ascending": ascending,
            "nulls_first": nulls_first,
        })
        return self


@dataclass
class PaginationConfig:
    """Pagination configuration."""
    limit: Optional[int] = None
    offset: Optional[int] = None
    range_start: Optional[int] = None
    range_end: Optional[int] = None


@dataclass
class RealtimeChannelWrapper:
    """Wrapper for Realtime channel."""
    channel: Any
    channel_name: str
    subscriptions: List[str] = field(default_factory=list)

    def __repr__(self) -> str:
        return f"<RealtimeChannel name={self.channel_name} subs={len(self.subscriptions)}>"
