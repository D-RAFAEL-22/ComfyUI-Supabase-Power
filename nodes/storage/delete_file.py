"""Supabase DeleteFile node for removing files from Storage."""

from comfy_api.latest import io

from ...core.types import SupabaseClientWrapper
from ...core.utils import format_error

# Custom types
SupabaseClientType = io.Custom("SUPABASE_CLIENT")


class SupabaseDeleteFile(io.ComfyNode):
    """Delete files from Supabase Storage."""

    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="SupabaseDeleteFile",
            display_name="Supabase Delete File",
            description="Delete files from Storage",
            category="Supabase/Storage",
            inputs=[
                SupabaseClientType.Input(id="client", tooltip="Supabase client"),
                io.String.Input(id="bucket", display_name="Bucket", tooltip="Storage bucket name"),
                io.String.Input(id="path", display_name="Path", tooltip="File path(s) comma-separated"),
            ],
            outputs=[
                io.Boolean.Output(id="success"),
                io.String.Output(id="error"),
                io.Int.Output(id="deleted_count"),
            ],
        )

    @classmethod
    def execute(cls, client: SupabaseClientWrapper, bucket: str, path: str) -> io.NodeOutput:
        try:
            storage = client.client.storage.from_(bucket)
            paths = [p.strip() for p in path.split(",") if p.strip()]

            if not paths:
                return io.NodeOutput(False, "No path provided", 0)

            storage.remove(paths)
            return io.NodeOutput(True, "", len(paths))
        except Exception as e:
            return io.NodeOutput(False, format_error(e), 0)
