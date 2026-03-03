"""Supabase SignedURL node for creating temporary access URLs."""

from comfy_api.latest import io

from ...core.types import SupabaseClientWrapper
from ...core.utils import format_error

# Custom types
SupabaseClientType = io.Custom("SUPABASE_CLIENT")


class SupabaseSignedURL(io.ComfyNode):
    """Create a signed URL for temporary file access."""

    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="SupabaseSignedURL",
            display_name="Supabase Signed URL",
            description="Create temporary access URL",
            category="Supabase/Storage",
            inputs=[
                SupabaseClientType.Input(id="client", tooltip="Supabase client"),
                io.String.Input(id="bucket", display_name="Bucket", tooltip="Storage bucket name"),
                io.String.Input(id="path", display_name="Path", tooltip="File path"),
                io.Int.Input(id="expires_in", display_name="Expires In (sec)", default=3600, min=1, max=604800),
            ],
            outputs=[
                io.String.Output(id="signed_url"),
                io.String.Output(id="error"),
                io.Boolean.Output(id="success"),
            ],
        )

    @classmethod
    def execute(cls, client: SupabaseClientWrapper, bucket: str, path: str, expires_in: int = 3600) -> io.NodeOutput:
        try:
            storage = client.client.storage.from_(bucket)
            response = storage.create_signed_url(path, expires_in)
            signed_url = response.get("signedURL", "") if isinstance(response, dict) else str(response)

            if not signed_url:
                return io.NodeOutput("", "Failed to create signed URL", False)

            return io.NodeOutput(signed_url, "", True)
        except Exception as e:
            return io.NodeOutput("", format_error(e), False)
