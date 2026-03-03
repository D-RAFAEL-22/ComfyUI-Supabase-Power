"""Response Parser node for extracting data from JSON responses."""

import json
from typing import Any

from comfy_api.latest import io

# Custom types
JsonType = io.Custom("JSON")
ListType = io.Custom("LIST")


class ResponseParser(io.ComfyNode):
    """Parse and extract values from JSON data."""

    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="ResponseParser",
            display_name="Response Parser",
            description="Extract values from JSON responses",
            category="Supabase/Utils",
            inputs=[
                JsonType.Input(id="data", tooltip="JSON data to parse"),
                io.String.Input(id="path", display_name="Path", default="", tooltip="Path (e.g., '0.name', 'user.email')"),
                io.String.Input(id="default", display_name="Default", default="", tooltip="Default if not found"),
            ],
            outputs=[
                JsonType.Output(id="value"),
                io.String.Output(id="as_string"),
                io.Int.Output(id="as_int"),
                io.Float.Output(id="as_float"),
                io.Boolean.Output(id="as_bool"),
                ListType.Output(id="as_list"),
                io.Boolean.Output(id="found"),
            ],
        )

    @classmethod
    def execute(cls, data: Any, path: str, default: str) -> io.NodeOutput:
        if not path or not path.strip():
            return cls._format_output(data, default, True)

        current = data
        found = True
        path = path.replace("[", ".").replace("]", "")
        parts = [p for p in path.split(".") if p]

        try:
            for part in parts:
                if current is None:
                    found = False
                    break
                if isinstance(current, (list, tuple)):
                    try:
                        idx = int(part)
                        if 0 <= idx < len(current):
                            current = current[idx]
                        else:
                            found = False
                            break
                    except ValueError:
                        found = False
                        break
                elif isinstance(current, dict):
                    if part in current:
                        current = current[part]
                    else:
                        found = False
                        break
                else:
                    found = False
                    break
        except Exception:
            found = False

        if not found:
            current = default

        return cls._format_output(current, default, found)

    @classmethod
    def _format_output(cls, value: Any, default: str, found: bool) -> io.NodeOutput:
        json_value = value

        if isinstance(value, str):
            as_string = value
        elif value is None:
            as_string = default or ""
        else:
            try:
                as_string = json.dumps(value)
            except (TypeError, ValueError):
                as_string = str(value)

        try:
            if isinstance(value, bool):
                as_int = 1 if value else 0
            elif isinstance(value, (int, float)):
                as_int = int(value)
            elif isinstance(value, str) and value.strip():
                as_int = int(float(value))
            else:
                as_int = int(default) if default.strip().lstrip("-").isdigit() else 0
        except (ValueError, TypeError):
            as_int = 0

        try:
            if isinstance(value, bool):
                as_float = 1.0 if value else 0.0
            elif isinstance(value, (int, float)):
                as_float = float(value)
            elif isinstance(value, str) and value.strip():
                as_float = float(value)
            else:
                as_float = float(default) if default.replace(".", "", 1).lstrip("-").isdigit() else 0.0
        except (ValueError, TypeError):
            as_float = 0.0

        if isinstance(value, bool):
            as_bool = value
        elif isinstance(value, (int, float)):
            as_bool = bool(value)
        elif isinstance(value, str):
            as_bool = value.lower().strip() in ("true", "1", "yes")
        else:
            as_bool = bool(value) if value is not None else False

        if isinstance(value, list):
            as_list = value
        elif isinstance(value, tuple):
            as_list = list(value)
        elif value is not None:
            as_list = [value]
        else:
            as_list = []

        return io.NodeOutput(json_value, as_string, as_int, as_float, as_bool, as_list, found)
