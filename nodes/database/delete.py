"""Supabase Delete node for removing data."""

from typing import Optional

from comfy_api.latest import io

from ...core.types import SupabaseClientWrapper
from ...core.utils import format_error, build_query_with_filters

# Custom types
SupabaseClientType = io.Custom("SUPABASE_CLIENT")
FilterChainType = io.Custom("FILTER_CHAIN")
JsonType = io.Custom("JSON")


class SupabaseDelete(io.ComfyNode):
    """Delete data from a Supabase table."""

    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="SupabaseDelete",
            display_name="Supabase Delete",
            description="Delete data from a Supabase table",
            category="Supabase/Database",
            inputs=[
                SupabaseClientType.Input(id="client", tooltip="Supabase client"),
                io.String.Input(id="table", display_name="Table", tooltip="Table name"),
                FilterChainType.Input(id="filters", optional=True, tooltip="Filters (REQUIRED for safety)"),
                io.Boolean.Input(id="allow_no_filter", display_name="Allow No Filter", default=False, tooltip="Allow delete without filters (VERY dangerous!)"),
                io.Boolean.Input(id="return_deleted", display_name="Return Deleted", default=True, tooltip="Return deleted rows"),
            ],
            outputs=[
                JsonType.Output(id="deleted"),
                io.String.Output(id="error"),
                io.Boolean.Output(id="success"),
                io.Int.Output(id="count"),
            ],
        )

    @classmethod
    def execute(cls, client: SupabaseClientWrapper, table: str, filters: Optional[list] = None,
                allow_no_filter: bool = False, return_deleted: bool = True) -> io.NodeOutput:
        try:
            if not filters and not allow_no_filter:
                return io.NodeOutput(None, "Filters required for DELETE. Use FilterBuilder or enable Allow No Filter.", False, 0)

            query = client.client.table(table).delete()
            query = build_query_with_filters(query, filters)

            response = query.execute()
            result = response.data if return_deleted else None
            count = len(response.data) if isinstance(response.data, list) else (1 if response.data else 0)

            return io.NodeOutput(result, "", True, count)
        except Exception as e:
            return io.NodeOutput(None, format_error(e), False, 0)
