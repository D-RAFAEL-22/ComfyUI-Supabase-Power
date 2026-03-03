"""Supabase Update node for modifying data."""

from typing import Any, Optional

from comfy_api.latest import io

from ...core.types import SupabaseClientWrapper
from ...core.utils import format_error, parse_json_safe, build_query_with_filters

# Custom types
SupabaseClientType = io.Custom("SUPABASE_CLIENT")
FilterChainType = io.Custom("FILTER_CHAIN")
JsonType = io.Custom("JSON")


class SupabaseUpdate(io.ComfyNode):
    """Update data in a Supabase table."""

    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="SupabaseUpdate",
            display_name="Supabase Update",
            description="Update data in a Supabase table",
            category="Supabase/Database",
            inputs=[
                SupabaseClientType.Input(id="client", tooltip="Supabase client"),
                io.String.Input(id="table", display_name="Table", tooltip="Table name"),
                JsonType.Input(id="data", optional=True, tooltip="Data from JSONBuilder"),
                io.String.Input(id="data_string", display_name="Data (JSON)", default="", multiline=True, tooltip="JSON string data"),
                FilterChainType.Input(id="filters", optional=True, tooltip="Filters (REQUIRED for safety)"),
                io.Boolean.Input(id="allow_no_filter", display_name="Allow No Filter", default=False, tooltip="Allow update without filters (dangerous!)"),
            ],
            outputs=[
                JsonType.Output(id="result"),
                io.String.Output(id="error"),
                io.Boolean.Output(id="success"),
                io.Int.Output(id="affected_rows"),
            ],
        )

    @classmethod
    def execute(cls, client: SupabaseClientWrapper, table: str, data: Optional[Any] = None,
                data_string: str = "", filters: Optional[list] = None,
                allow_no_filter: bool = False) -> io.NodeOutput:
        try:
            if not filters and not allow_no_filter:
                return io.NodeOutput(None, "Filters required for UPDATE. Use FilterBuilder or enable Allow No Filter.", False, 0)

            update_data = data
            if update_data is None and data_string.strip():
                update_data = parse_json_safe(data_string)

            if update_data is None:
                return io.NodeOutput(None, "No data provided", False, 0)

            query = client.client.table(table).update(update_data)
            query = build_query_with_filters(query, filters)

            response = query.execute()
            result = response.data
            affected = len(result) if isinstance(result, list) else (1 if result else 0)

            return io.NodeOutput(result, "", True, affected)
        except Exception as e:
            return io.NodeOutput(None, format_error(e), False, 0)
