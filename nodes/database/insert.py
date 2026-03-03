"""Supabase Insert node for adding data."""

from typing import Any, Optional

from comfy_api.latest import io

from ...core.types import SupabaseClientWrapper
from ...core.utils import format_error, parse_json_safe

# Custom types
SupabaseClientType = io.Custom("SUPABASE_CLIENT")
JsonType = io.Custom("JSON")


class SupabaseInsert(io.ComfyNode):
    """Insert data into a Supabase table."""

    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="SupabaseInsert",
            display_name="Supabase Insert",
            description="Insert data into a Supabase table",
            category="Supabase/Database",
            inputs=[
                SupabaseClientType.Input(id="client", tooltip="Supabase client"),
                io.String.Input(id="table", display_name="Table", tooltip="Table name"),
                JsonType.Input(id="data", optional=True, tooltip="Data from JSONBuilder"),
                io.String.Input(id="data_string", display_name="Data (JSON)", default="", multiline=True, tooltip="JSON string data"),
                io.Boolean.Input(id="return_data", display_name="Return Data", default=True, tooltip="Return inserted rows"),
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
                data_string: str = "", return_data: bool = True) -> io.NodeOutput:
        try:
            insert_data = data
            if insert_data is None and data_string.strip():
                insert_data = parse_json_safe(data_string)

            if insert_data is None:
                return io.NodeOutput(None, "No data provided", False, 0)

            query = client.client.table(table).insert(insert_data)

            if not return_data:
                query.execute()
                return io.NodeOutput(None, "", True, 1 if isinstance(insert_data, dict) else len(insert_data))

            response = query.execute()
            result = response.data
            count = len(result) if isinstance(result, list) else 1

            return io.NodeOutput(result, "", True, count)
        except Exception as e:
            return io.NodeOutput(None, format_error(e), False, 0)
