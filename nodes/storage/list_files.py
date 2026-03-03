"""Supabase ListFiles node for listing files in Storage."""

from comfy_api.latest import io

from ...core.types import SupabaseClientWrapper
from ...core.utils import format_error

# Custom types
SupabaseClientType = io.Custom("SUPABASE_CLIENT")
ListType = io.Custom("LIST")
JsonType = io.Custom("JSON")


class SupabaseListFiles(io.ComfyNode):
    """List files in a Supabase Storage bucket."""

    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="SupabaseListFiles",
            display_name="Supabase List Files",
            description="List files in a Storage bucket",
            category="Supabase/Storage",
            inputs=[
                SupabaseClientType.Input(id="client", tooltip="Supabase client"),
                io.String.Input(id="bucket", display_name="Bucket", tooltip="Storage bucket name"),
                io.String.Input(id="folder", display_name="Folder", default="", tooltip="Folder path"),
                io.Int.Input(id="limit", display_name="Limit", default=100, min=1, max=1000),
                io.Int.Input(id="offset", display_name="Offset", default=0, min=0),
            ],
            outputs=[
                ListType.Output(id="files"),
                JsonType.Output(id="files_json"),
                io.Int.Output(id="count"),
                io.String.Output(id="error"),
                io.Boolean.Output(id="success"),
            ],
        )

    @classmethod
    def execute(cls, client: SupabaseClientWrapper, bucket: str, folder: str = "",
                limit: int = 100, offset: int = 0) -> io.NodeOutput:
        try:
            storage = client.client.storage.from_(bucket)
            response = storage.list(path=folder if folder else "", limit=limit, offset=offset)

            files = []
            for item in response:
                file_info = {
                    "name": item.get("name", ""),
                    "id": item.get("id", ""),
                    "created_at": item.get("created_at", ""),
                    "updated_at": item.get("updated_at", ""),
                    "path": f"{folder}/{item.get('name', '')}" if folder else item.get("name", ""),
                }
                files.append(file_info)

            return io.NodeOutput(files, files, len(files), "", True)
        except Exception as e:
            return io.NodeOutput([], [], 0, format_error(e), False)
