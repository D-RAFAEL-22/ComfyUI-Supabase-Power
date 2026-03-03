"""Supabase Broadcast node for sending realtime messages."""

from typing import Any, Optional

from comfy_api.latest import io

from ...core.types import SupabaseClientWrapper, RealtimeChannelWrapper
from ...core.utils import format_error, parse_json_safe

# Custom types
SupabaseClientType = io.Custom("SUPABASE_CLIENT")
RealtimeChannelType = io.Custom("REALTIME_CHANNEL")
JsonType = io.Custom("JSON")


class SupabaseBroadcast(io.ComfyNode):
    """Send broadcast messages through Supabase Realtime."""

    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="SupabaseBroadcast",
            display_name="Supabase Broadcast",
            description="Send broadcast messages through Realtime",
            category="Supabase/Realtime",
            is_output_node=True,
            inputs=[
                SupabaseClientType.Input(id="client", tooltip="Supabase client"),
                RealtimeChannelType.Input(id="channel", optional=True, tooltip="Existing channel"),
                io.String.Input(id="channel_name", display_name="Channel Name", default="", tooltip="Channel name if not using existing"),
                io.String.Input(id="event", display_name="Event", default="message", tooltip="Event name"),
                JsonType.Input(id="payload", optional=True, tooltip="Payload data"),
                io.String.Input(id="payload_string", display_name="Payload (JSON)", default="", multiline=True),
            ],
            outputs=[
                io.String.Output(id="status"),
                io.Boolean.Output(id="success"),
                io.String.Output(id="error"),
            ],
        )

    @classmethod
    def execute(cls, client: SupabaseClientWrapper, channel: Optional[RealtimeChannelWrapper] = None,
                channel_name: str = "", event: str = "message",
                payload: Optional[Any] = None, payload_string: str = "") -> io.NodeOutput:
        try:
            if channel is not None:
                realtime_channel = channel.channel
                ch_name = channel.channel_name
            elif channel_name:
                realtime_channel = client.client.channel(channel_name)
                realtime_channel.subscribe()
                ch_name = channel_name
            else:
                return io.NodeOutput("error", False, "No channel specified")

            broadcast_payload = payload
            if broadcast_payload is None and payload_string.strip():
                broadcast_payload = parse_json_safe(payload_string, default={})
            if broadcast_payload is None:
                broadcast_payload = {}

            realtime_channel.send_broadcast(event=event, payload=broadcast_payload)

            return io.NodeOutput(f"broadcast sent to {ch_name}", True, "")
        except Exception as e:
            return io.NodeOutput("error", False, format_error(e))
