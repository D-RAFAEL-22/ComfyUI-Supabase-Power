"""Supabase Edge Function node for invoking edge functions."""

import json
from typing import Any, Optional

from comfy_api.latest import io

from ...core.types import SupabaseClientWrapper
from ...core.utils import format_error, parse_json_safe

# Custom types
SupabaseClientType = io.Custom("SUPABASE_CLIENT")
JsonType = io.Custom("JSON")


class SupabaseEdgeFunction(io.ComfyNode):
    """Invoke a Supabase Edge Function."""

    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="SupabaseEdgeFunction",
            display_name="Supabase Edge Function",
            description="Invoke a Supabase Edge Function",
            category="Supabase/Edge",
            inputs=[
                SupabaseClientType.Input(id="client", tooltip="Supabase client"),
                io.String.Input(id="function_name", display_name="Function Name", tooltip="Edge Function name"),
                JsonType.Input(id="body", optional=True, tooltip="Request body"),
                io.String.Input(id="body_string", display_name="Body (JSON)", default="", multiline=True),
                JsonType.Input(id="headers", optional=True, tooltip="Additional headers"),
                io.Combo.Input(id="method", display_name="Method", options=["POST", "GET", "PUT", "DELETE"], default="POST"),
            ],
            outputs=[
                JsonType.Output(id="response"),
                io.String.Output(id="response_text"),
                io.Int.Output(id="status_code"),
                io.String.Output(id="error"),
                io.Boolean.Output(id="success"),
            ],
        )

    @classmethod
    def execute(cls, client: SupabaseClientWrapper, function_name: str,
                body: Optional[Any] = None, body_string: str = "",
                headers: Optional[dict] = None, method: str = "POST") -> io.NodeOutput:
        try:
            request_body = body
            if request_body is None and body_string.strip():
                request_body = parse_json_safe(body_string)

            invoke_options = {}
            if request_body is not None:
                invoke_options["body"] = request_body
            if headers:
                invoke_options["headers"] = headers

            response = client.client.functions.invoke(function_name, invoke_options=invoke_options)

            response_json = None
            response_text = ""

            if isinstance(response, (dict, list)):
                response_json = response
                response_text = json.dumps(response)
            elif isinstance(response, str):
                try:
                    response_json = json.loads(response)
                    response_text = response
                except json.JSONDecodeError:
                    response_json = {"raw": response}
                    response_text = response
            elif isinstance(response, bytes):
                try:
                    response_text = response.decode("utf-8")
                    response_json = json.loads(response_text)
                except (UnicodeDecodeError, json.JSONDecodeError):
                    response_json = {"raw": str(response)}
                    response_text = str(response)
            else:
                response_json = response
                response_text = str(response)

            return io.NodeOutput(response_json, response_text, 200, "", True)
        except Exception as e:
            error_msg = format_error(e)
            status_code = 500
            if "404" in error_msg:
                status_code = 404
            elif "401" in error_msg or "403" in error_msg:
                status_code = 401
            return io.NodeOutput(None, "", status_code, error_msg, False)
