"""Order By node for query sorting."""

from typing import Optional

from comfy_api.latest import io

from ...core.types import OrderConfig

# Custom type
OrderConfigType = io.Custom("ORDER_CONFIG")


class OrderBy(io.ComfyNode):
    """Configure sorting for Supabase queries."""

    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="OrderBy",
            display_name="Order By",
            description="Configure query sorting",
            category="Supabase/Query",
            inputs=[
                io.String.Input(
                    id="column",
                    display_name="Column",
                    tooltip="Column name to sort by",
                ),
                io.Combo.Input(
                    id="direction",
                    display_name="Direction",
                    options=["asc", "desc"],
                    default="asc",
                    tooltip="Sort direction",
                ),
                io.Boolean.Input(
                    id="nulls_first",
                    display_name="Nulls First",
                    default=False,
                    tooltip="Put NULL values first",
                ),
                OrderConfigType.Input(
                    id="order_config",
                    optional=True,
                    tooltip="Connect to previous OrderBy to chain",
                ),
            ],
            outputs=[
                OrderConfigType.Output(id="order_config"),
            ],
        )

    @classmethod
    def execute(cls, column: str, direction: str, nulls_first: bool, order_config: Optional[OrderConfig] = None) -> io.NodeOutput:
        if order_config is not None:
            output = OrderConfig(orders=list(order_config.orders))
        else:
            output = OrderConfig()

        if column:
            output.add(column=column, ascending=(direction == "asc"), nulls_first=nulls_first)

        return io.NodeOutput(output)
