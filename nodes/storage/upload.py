"""Supabase Upload node for uploading files to Storage."""

import datetime
from typing import Any, Optional

from comfy_api.latest import io

from ...core.types import SupabaseClientWrapper
from ...core.utils import format_error, image_to_bytes

# Custom types
SupabaseClientType = io.Custom("SUPABASE_CLIENT")


class SupabaseUpload(io.ComfyNode):
    """Upload files to Supabase Storage."""

    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="SupabaseUpload",
            display_name="Supabase Upload",
            description="Upload files to Supabase Storage",
            category="Supabase/Storage",
            is_output_node=True,
            inputs=[
                SupabaseClientType.Input(id="client", tooltip="Supabase client"),
                io.String.Input(id="bucket", display_name="Bucket", tooltip="Storage bucket name"),
                io.String.Input(id="path", display_name="Path", default="", tooltip="File path (empty=auto-generate)"),
                io.Image.Input(id="image", optional=True, tooltip="Image to upload"),
                io.Combo.Input(id="image_format", display_name="Format", options=["PNG", "JPEG", "WEBP"], default="PNG"),
                io.Int.Input(id="quality", display_name="Quality", default=95, min=1, max=100, tooltip="JPEG/WEBP quality"),
                io.Boolean.Input(id="upsert", display_name="Upsert", default=True, tooltip="Overwrite if exists"),
                io.String.Input(id="update_table", display_name="Update Table", default="", tooltip="Table to update with URL"),
                io.String.Input(id="update_column", display_name="Update Column", default="", tooltip="Column for URL"),
                io.String.Input(id="update_id_column", display_name="ID Column", default="id"),
                io.String.Input(id="update_id_value", display_name="ID Value", default="", tooltip="Row ID value"),
            ],
            outputs=[
                io.String.Output(id="public_url"),
                io.String.Output(id="path"),
                io.String.Output(id="error"),
                io.Boolean.Output(id="success"),
            ],
        )

    @classmethod
    def execute(cls, client: SupabaseClientWrapper, bucket: str, path: str = "",
                image: Optional[Any] = None, image_format: str = "PNG", quality: int = 95,
                upsert: bool = True, update_table: str = "", update_column: str = "",
                update_id_column: str = "id", update_id_value: str = "") -> io.NodeOutput:
        try:
            if image is None:
                return io.NodeOutput("", "", "No image provided", False)

            file_bytes, content_type = image_to_bytes(image, image_format, quality)
            ext = image_format.lower()

            if not path or not path.strip():
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                path = f"upload_{timestamp}.{ext}"

            if not path.lower().endswith(f".{ext}"):
                path = f"{path}.{ext}"

            storage = client.client.storage.from_(bucket)
            file_options = {"content-type": content_type}
            if upsert:
                file_options["upsert"] = "true"

            storage.upload(path=path, file=file_bytes, file_options=file_options)
            public_url = storage.get_public_url(path)

            if update_table and update_column and update_id_value:
                try:
                    client.client.table(update_table).update({update_column: public_url}).eq(update_id_column, update_id_value).execute()
                except Exception as db_error:
                    print(f"[SupabaseUpload] Warning: DB update failed: {db_error}")

            return io.NodeOutput(public_url, path, "", True)
        except Exception as e:
            return io.NodeOutput("", "", format_error(e), False)
