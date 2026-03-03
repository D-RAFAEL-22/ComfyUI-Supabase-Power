"""Pagination node for query limits and offsets."""

from comfy_api.latest import io

from ...core.types import PaginationConfig

# Custom type
PaginationConfigType = io.Custom("PAGINATION_CONFIG")


class Pagination(io.ComfyNode):
    """Configure pagination for Supabase queries."""

    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="Pagination",
            display_name="Pagination",
            description="Configure query pagination",
            category="Supabase/Query",
            inputs=[
                io.Int.Input(
                    id="limit",
                    display_name="Limit",
                    default=100,
                    min=1,
                    max=10000,
                    tooltip="Maximum rows to return",
                ),
                io.Int.Input(
                    id="offset",
                    display_name="Offset",
                    default=0,
                    min=0,
                    tooltip="Rows to skip",
                ),
                io.Int.Input(
                    id="range_start",
                    display_name="Range Start",
                    default=-1,
                    min=-1,
                    tooltip="Start index (-1 to disable)",
                ),
                io.Int.Input(
                    id="range_end",
                    display_name="Range End",
                    default=-1,
                    min=-1,
                    tooltip="End index (-1 to disable)",
                ),
            ],
            outputs=[
                PaginationConfigType.Output(id="pagination"),
            ],
        )

    @classmethod
    def execute(cls, limit: int, offset: int, range_start: int, range_end: int) -> io.NodeOutput:
        config = PaginationConfig(
            limit=limit if limit > 0 else None,
            offset=offset if offset > 0 else None,
            range_start=range_start if range_start >= 0 else None,
            range_end=range_end if range_end >= 0 else None,
        )
        return io.NodeOutput(config)
