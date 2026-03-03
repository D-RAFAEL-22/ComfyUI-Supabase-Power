"""Supabase Download node for downloading files from Storage."""

from typing import Any

from comfy_api.latest import io

from ...core.types import SupabaseClientWrapper
from ...core.utils import format_error, bytes_to_image

# Custom types
SupabaseClientType = io.Custom("SUPABASE_CLIENT")
BytesType = io.Custom("BYTES")


class SupabaseDownload(io.ComfyNode):
    """Download files from Supabase Storage."""

    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="SupabaseDownload",
            display_name="Supabase Download",
            description="Download files from Supabase Storage",
            category="Supabase/Storage",
            inputs=[
                SupabaseClientType.Input(id="client", tooltip="Supabase client"),
                io.String.Input(id="bucket", display_name="Bucket", tooltip="Storage bucket name"),
                io.String.Input(id="path", display_name="Path", tooltip="File path in bucket"),
                io.Combo.Input(id="output_type", display_name="Output Type", options=["image", "bytes", "string"], default="image"),
            ],
            outputs=[
                io.Image.Output(id="image"),
                BytesType.Output(id="bytes_data"),
                io.String.Output(id="as_string"),
                io.String.Output(id="error"),
                io.Boolean.Output(id="success"),
            ],
        )

    @classmethod
    def execute(cls, client: SupabaseClientWrapper, bucket: str, path: str, output_type: str = "image") -> io.NodeOutput:
        try:
            storage = client.client.storage.from_(bucket)
            data = storage.download(path)

            image_out = None
            bytes_out = data
            string_out = ""

            if output_type == "image":
                image_out = bytes_to_image(data)
            elif output_type == "string":
                try:
                    string_out = data.decode("utf-8")
                except UnicodeDecodeError:
                    string_out = data.decode("latin-1")

            return io.NodeOutput(image_out, bytes_out, string_out, "", True)
        except Exception as e:
            return io.NodeOutput(None, None, "", format_error(e), False)
