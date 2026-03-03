"""Supabase Upsert node for insert-or-update operations."""

from typing import Any, Optional

from comfy_api.latest import io

from ...core.types import SupabaseClientWrapper
from ...core.utils import format_error, parse_json_safe

# Custom types
SupabaseClientType = io.Custom("SUPABASE_CLIENT")
JsonType = io.Custom("JSON")


class SupabaseUpsert(io.ComfyNode):
    """Upsert (insert or update) data in a Supabase table."""

    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="SupabaseUpsert",
            display_name="Supabase Upsert",
            description="Insert or update data in a Supabase table",
            category="Supabase/Database",
            inputs=[
                SupabaseClientType.Input(id="client", tooltip="Supabase client"),
                io.String.Input(id="table", display_name="Table", tooltip="Table name"),
                JsonType.Input(id="data", optional=True, tooltip="Data from JSONBuilder"),
                io.String.Input(id="data_string", display_name="Data (JSON)", default="", multiline=True, tooltip="JSON string data"),
                io.String.Input(id="on_conflict", display_name="On Conflict", default="", tooltip="Conflict columns (comma-separated)"),
                io.Boolean.Input(id="ignore_duplicates", display_name="Ignore Duplicates", default=False, tooltip="Don't update on conflict"),
            ],
            outputs=[
                JsonType.Output(id="result"),
                io.String.Output(id="error"),
                io.Boolean.Output(id="success"),
                io.Int.Output(id="count"),
            ],
        )

    @classmethod
    def execute(cls, client: SupabaseClientWrapper, table: str, data: Optional[Any] = None,
                data_string: str = "", on_conflict: str = "",
                ignore_duplicates: bool = False) -> io.NodeOutput:
        try:
            upsert_data = data
            if upsert_data is None and data_string.strip():
                upsert_data = parse_json_safe(data_string)

            if upsert_data is None:
                return io.NodeOutput(None, "No data provided", False, 0)

            upsert_kwargs = {}
            if on_conflict.strip():
                upsert_kwargs["on_conflict"] = on_conflict.strip()
            if ignore_duplicates:
                upsert_kwargs["ignore_duplicates"] = True

            response = client.client.table(table).upsert(upsert_data, **upsert_kwargs).execute()
            result = response.data
            count = len(result) if isinstance(result, list) else 1

            return io.NodeOutput(result, "", True, count)
        except Exception as e:
            return io.NodeOutput(None, format_error(e), False, 0)
