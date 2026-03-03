"""Supabase UserInfo node for getting current user information."""

from comfy_api.latest import io

from ...core.types import SupabaseClientWrapper
from ...core.utils import format_error

# Custom types
SupabaseClientType = io.Custom("SUPABASE_CLIENT")
JsonType = io.Custom("JSON")


class SupabaseUserInfo(io.ComfyNode):
    """Get information about the currently authenticated user."""

    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="SupabaseUserInfo",
            display_name="Supabase User Info",
            description="Get current user information",
            category="Supabase/Auth",
            inputs=[
                SupabaseClientType.Input(id="client", tooltip="Supabase client"),
            ],
            outputs=[
                JsonType.Output(id="user"),
                io.String.Output(id="user_id"),
                io.String.Output(id="email"),
                io.Boolean.Output(id="is_authenticated"),
                io.String.Output(id="error"),
            ],
        )

    @classmethod
    def execute(cls, client: SupabaseClientWrapper) -> io.NodeOutput:
        try:
            response = client.client.auth.get_user()

            if response and response.user:
                user = {
                    "id": response.user.id,
                    "email": response.user.email,
                    "created_at": response.user.created_at,
                    "role": response.user.role,
                }
                return io.NodeOutput(user, response.user.id, response.user.email or "", True, "")
            else:
                return io.NodeOutput(None, "", "", False, "")
        except Exception as e:
            error_msg = format_error(e)
            if "not authenticated" in error_msg.lower():
                return io.NodeOutput(None, "", "", False, "")
            return io.NodeOutput(None, "", "", False, error_msg)
