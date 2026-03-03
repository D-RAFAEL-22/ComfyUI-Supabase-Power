"""Custom ComfyUI types for Supabase Power nodes."""

from comfy_api.latest import io

# Define all custom types used across nodes
SupabaseClientType = io.Custom("SUPABASE_CLIENT")
FilterChainType = io.Custom("FILTER_CHAIN")
OrderConfigType = io.Custom("ORDER_CONFIG")
PaginationConfigType = io.Custom("PAGINATION_CONFIG")
RealtimeChannelType = io.Custom("REALTIME_CHANNEL")
JsonType = io.Custom("JSON")
ListType = io.Custom("LIST")
BytesType = io.Custom("BYTES")
