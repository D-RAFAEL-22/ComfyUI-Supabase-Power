"""JSON Builder node for chainable JSON construction."""

import json
from typing import Any, Optional

from comfy_api.latest import io

# Custom type
JsonType = io.Custom("JSON")


class JSONBuilder(io.ComfyNode):
    """Build JSON objects by chaining key-value pairs."""

    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="JSONBuilder",
            display_name="JSON Builder",
            description="Build JSON objects from key-value pairs",
            category="Supabase/Utils",
            inputs=[
                io.String.Input(id="key", display_name="Key", tooltip="JSON key name"),
                io.String.Input(id="value", display_name="Value", multiline=True, tooltip="Value (string, number, JSON)"),
                io.Combo.Input(id="value_type", display_name="Value Type", options=["auto", "string", "number", "boolean", "json", "null"], default="auto"),
                JsonType.Input(id="json_input", optional=True, tooltip="Connect to previous JSONBuilder"),
            ],
            outputs=[
                JsonType.Output(id="json_output"),
                io.String.Output(id="as_string"),
            ],
        )

    @classmethod
    def execute(cls, key: str, value: str, value_type: str, json_input: Optional[dict] = None) -> io.NodeOutput:
        output = dict(json_input) if json_input else {}
        parsed_value: Any = value

        if value_type == "null" or (value_type == "auto" and value.lower().strip() == "null"):
            parsed_value = None
        elif value_type == "boolean":
            parsed_value = value.lower().strip() in ("true", "1", "yes")
        elif value_type == "number":
            try:
                parsed_value = float(value) if "." in value else int(value)
            except ValueError:
                parsed_value = 0
        elif value_type == "json":
            try:
                parsed_value = json.loads(value)
            except json.JSONDecodeError:
                parsed_value = value
        elif value_type == "auto":
            stripped = value.strip()
            if stripped.lower() in ("true", "false"):
                parsed_value = stripped.lower() == "true"
            elif stripped.lower() == "null":
                parsed_value = None
            elif stripped.lstrip("-").replace(".", "", 1).isdigit():
                try:
                    parsed_value = float(stripped) if "." in stripped else int(stripped)
                except ValueError:
                    parsed_value = value
            elif (stripped.startswith("{") and stripped.endswith("}")) or (stripped.startswith("[") and stripped.endswith("]")):
                try:
                    parsed_value = json.loads(stripped)
                except json.JSONDecodeError:
                    parsed_value = value

        if key:
            output[key] = parsed_value

        return io.NodeOutput(output, json.dumps(output, indent=2))
