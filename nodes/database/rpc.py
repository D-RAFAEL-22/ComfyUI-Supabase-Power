"""Supabase RPC node for calling PostgreSQL functions."""

from typing import Any, Optional

from comfy_api.latest import io

from ...core.types import SupabaseClientWrapper
from ...core.utils import format_error, parse_json_safe

# Custom types
SupabaseClientType = io.Custom("SUPABASE_CLIENT")
JsonType = io.Custom("JSON")


class SupabaseRPC(io.ComfyNode):
    """Call a PostgreSQL function via Supabase RPC."""

    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="SupabaseRPC",
            display_name="Supabase RPC",
            description="Call a PostgreSQL function",
            category="Supabase/Database",
            inputs=[
                SupabaseClientType.Input(id="client", tooltip="Supabase client"),
                io.String.Input(id="function_name", display_name="Function Name", tooltip="PostgreSQL function name"),
                JsonType.Input(id="params", optional=True, tooltip="Function parameters"),
                io.String.Input(id="params_string", display_name="Params (JSON)", default="", multiline=True, tooltip="JSON string params"),
                io.Boolean.Input(id="single", display_name="Single Result", default=False, tooltip="Return single value"),
            ],
            outputs=[
                JsonType.Output(id="result"),
                io.String.Output(id="error"),
                io.Boolean.Output(id="success"),
            ],
        )

    @classmethod
    def execute(cls, client: SupabaseClientWrapper, function_name: str,
                params: Optional[Any] = None, params_string: str = "",
                single: bool = False) -> io.NodeOutput:
        try:
            rpc_params = params
            if rpc_params is None and params_string.strip():
                rpc_params = parse_json_safe(params_string, default={})
            if rpc_params is None:
                rpc_params = {}

            query = client.client.rpc(function_name, rpc_params)

            if single:
                response = query.single().execute()
            else:
                response = query.execute()

            return io.NodeOutput(response.data, "", True)
        except Exception as e:
            return io.NodeOutput(None, format_error(e), False)
