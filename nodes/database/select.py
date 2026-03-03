"""Supabase Select node for querying data."""

from typing import Any, Optional

from comfy_api.latest import io

from ...core.types import SupabaseClientWrapper, OrderConfig, PaginationConfig
from ...core.utils import build_query_with_filters, apply_ordering, apply_pagination, format_error

# Custom types
SupabaseClientType = io.Custom("SUPABASE_CLIENT")
FilterChainType = io.Custom("FILTER_CHAIN")
OrderConfigType = io.Custom("ORDER_CONFIG")
PaginationConfigType = io.Custom("PAGINATION_CONFIG")
JsonType = io.Custom("JSON")
ListType = io.Custom("LIST")


class SupabaseSelect(io.ComfyNode):
    """Query data from a Supabase table."""

    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="SupabaseSelect",
            display_name="Supabase Select",
            description="Query data from a Supabase table",
            category="Supabase/Database",
            inputs=[
                SupabaseClientType.Input(id="client", tooltip="Supabase client"),
                io.String.Input(id="table", display_name="Table", tooltip="Table name"),
                io.String.Input(id="columns", display_name="Columns", default="*", tooltip="Columns to select"),
                FilterChainType.Input(id="filters", optional=True, tooltip="Filters from FilterBuilder"),
                OrderConfigType.Input(id="order", optional=True, tooltip="Ordering from OrderBy"),
                PaginationConfigType.Input(id="pagination", optional=True, tooltip="Pagination config"),
                io.Boolean.Input(id="single", display_name="Single Row", default=False, tooltip="Return single row"),
                io.Boolean.Input(id="count_only", display_name="Count Only", default=False, tooltip="Return only count"),
            ],
            outputs=[
                JsonType.Output(id="data"),
                ListType.Output(id="rows"),
                io.Int.Output(id="count"),
                io.String.Output(id="error"),
                io.Boolean.Output(id="success"),
            ],
        )

    @classmethod
    def execute(cls, client: SupabaseClientWrapper, table: str, columns: str = "*",
                filters: Optional[list] = None, order: Optional[OrderConfig] = None,
                pagination: Optional[PaginationConfig] = None, single: bool = False,
                count_only: bool = False) -> io.NodeOutput:
        try:
            if count_only:
                query = client.client.table(table).select(columns, count="exact")
            else:
                query = client.client.table(table).select(columns)

            query = build_query_with_filters(query, filters)
            query = apply_ordering(query, order)
            query = apply_pagination(query, pagination)

            if single:
                response = query.single().execute()
            else:
                response = query.execute()

            data = response.data
            count = response.count if hasattr(response, 'count') and response.count is not None else len(data) if isinstance(data, list) else 1
            rows = data if isinstance(data, list) else [data] if data else []

            return io.NodeOutput(data, rows, count, "", True)
        except Exception as e:
            return io.NodeOutput(None, [], 0, format_error(e), False)
