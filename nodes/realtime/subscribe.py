"""Supabase Subscribe node for realtime subscriptions."""

from comfy_api.latest import io

from ...core.types import SupabaseClientWrapper, RealtimeChannelWrapper
from ...core.utils import format_error

# Custom types
SupabaseClientType = io.Custom("SUPABASE_CLIENT")
RealtimeChannelType = io.Custom("REALTIME_CHANNEL")


class SupabaseSubscribe(io.ComfyNode):
    """Subscribe to realtime changes on a Supabase table."""

    EVENT_TYPES = ["*", "INSERT", "UPDATE", "DELETE"]

    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="SupabaseSubscribe",
            display_name="Supabase Subscribe",
            description="Subscribe to realtime database changes",
            category="Supabase/Realtime",
            inputs=[
                SupabaseClientType.Input(id="client", tooltip="Supabase client"),
                io.String.Input(id="channel_name", display_name="Channel Name", tooltip="Unique channel name"),
                io.String.Input(id="table", display_name="Table", default="", tooltip="Table to subscribe"),
                io.Combo.Input(id="event_type", display_name="Event Type", options=cls.EVENT_TYPES, default="*"),
                io.String.Input(id="filter", display_name="Filter", default="", tooltip="Optional filter"),
                io.String.Input(id="schema", display_name="Schema", default="public"),
            ],
            outputs=[
                RealtimeChannelType.Output(id="channel"),
                io.String.Output(id="status"),
                io.String.Output(id="error"),
                io.Boolean.Output(id="success"),
            ],
        )

    @classmethod
    def execute(cls, client: SupabaseClientWrapper, channel_name: str, table: str = "",
                event_type: str = "*", filter: str = "", schema: str = "public") -> io.NodeOutput:
        try:
            channel = client.client.channel(channel_name)
            subscriptions = []

            if table:
                channel.on_postgres_changes(
                    event=event_type if event_type != "*" else "*",
                    schema=schema,
                    table=table,
                    filter=filter if filter else None,
                    callback=lambda payload: print(f"[Realtime] {channel_name}: {payload}")
                )
                subscriptions.append(f"postgres:{table}:{event_type}")

            channel.subscribe()

            wrapper = RealtimeChannelWrapper(
                channel=channel,
                channel_name=channel_name,
                subscriptions=subscriptions,
            )

            return io.NodeOutput(wrapper, "subscribed", "", True)
        except Exception as e:
            return io.NodeOutput(None, "error", format_error(e), False)
