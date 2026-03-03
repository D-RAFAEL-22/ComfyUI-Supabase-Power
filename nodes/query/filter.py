"""Filter Builder node for chainable query filters."""

from typing import Any, Optional

from comfy_api.latest import io

# Custom type
FilterChainType = io.Custom("FILTER_CHAIN")


class FilterBuilder(io.ComfyNode):
    """Build chainable filters for Supabase queries."""

    OPERATORS = [
        "eq", "neq", "gt", "gte", "lt", "lte",
        "like", "ilike", "is", "in",
        "contains", "containedBy", "overlaps", "textSearch",
    ]

    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="FilterBuilder",
            display_name="Filter Builder",
            description="Build chainable filters for database queries",
            category="Supabase/Query",
            inputs=[
                io.String.Input(
                    id="column",
                    display_name="Column",
                    tooltip="Column name to filter on",
                ),
                io.Combo.Input(
                    id="operator",
                    display_name="Operator",
                    options=cls.OPERATORS,
                    default="eq",
                    tooltip="Filter operator",
                ),
                io.String.Input(
                    id="value",
                    display_name="Value",
                    tooltip="Value to compare against",
                ),
                FilterChainType.Input(
                    id="filters",
                    optional=True,
                    tooltip="Connect to previous FilterBuilder to chain",
                ),
            ],
            outputs=[
                FilterChainType.Output(id="filters"),
            ],
        )

    @classmethod
    def execute(cls, column: str, operator: str, value: str, filters: Optional[list] = None) -> io.NodeOutput:
        output = list(filters) if filters else []
        parsed_value: Any = value

        if operator == "is":
            lower_val = value.lower().strip()
            if lower_val == "null":
                parsed_value = None
            elif lower_val == "true":
                parsed_value = True
            elif lower_val == "false":
                parsed_value = False
        elif operator == "in":
            parsed_value = [v.strip() for v in value.split(",") if v.strip()]
        elif operator in ("gt", "gte", "lt", "lte"):
            try:
                parsed_value = float(value) if "." in value else int(value)
            except ValueError:
                pass

        if column:
            output.append({"column": column, "op": operator, "value": parsed_value})

        return io.NodeOutput(output)
