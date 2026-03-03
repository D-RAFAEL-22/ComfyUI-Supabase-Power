"""Error Handler node for graceful error management."""

import json
from typing import Any, Optional

from comfy_api.latest import io

# Custom type
JsonType = io.Custom("JSON")


class ErrorHandler(io.ComfyNode):
    """Handle errors gracefully in workflows."""

    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="ErrorHandler",
            display_name="Error Handler",
            description="Handle errors and provide fallbacks",
            category="Supabase/Utils",
            inputs=[
                JsonType.Input(id="input_value", optional=True, tooltip="Input value to check"),
                io.String.Input(id="error", display_name="Error", default="", tooltip="Error message"),
                io.String.Input(id="fallback", display_name="Fallback Value", default="", multiline=True, tooltip="Fallback JSON"),
                io.Boolean.Input(id="raise_on_error", display_name="Raise On Error", default=False, tooltip="Raise exception instead"),
            ],
            outputs=[
                JsonType.Output(id="output"),
                io.Boolean.Output(id="has_error"),
                io.String.Output(id="error_message"),
            ],
        )

    @classmethod
    def execute(cls, input_value: Optional[Any], error: str, fallback: str, raise_on_error: bool) -> io.NodeOutput:
        has_error = bool(error and error.strip())

        if has_error:
            if raise_on_error:
                raise RuntimeError(f"Supabase Error: {error}")

            try:
                if fallback.strip().startswith(("{", "[")):
                    output = json.loads(fallback)
                else:
                    output = fallback
            except json.JSONDecodeError:
                output = fallback
        else:
            output = input_value

        return io.NodeOutput(output, has_error, error if has_error else "")
