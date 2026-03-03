"""
ComfyUI-Supabase-Power

A powerful node package for Supabase integration in ComfyUI.
Provides nodes for Database, Storage, Realtime, Auth, and Edge Functions.

Uses the modern ComfyExtension API (2025+).
"""

from typing_extensions import override

from comfy_api.latest import ComfyExtension, io

from .nodes import ALL_NODES


WEB_DIRECTORY = "./web/js"


class SupabasePowerExtension(ComfyExtension):
    """Main extension class for Supabase Power nodes."""

    @override
    async def get_node_list(self) -> list[type[io.ComfyNode]]:
        return ALL_NODES


async def comfy_entrypoint() -> SupabasePowerExtension:
    """ComfyUI calls this to load the extension and its nodes."""
    return SupabasePowerExtension()


# Version info
__version__ = "1.0.0"
__author__ = "ComfyUI-Supabase-Power Contributors"
